import json
import logging
import os
import re
import requests
import semver
import shutil
import tempfile
import time

import baseutils
from orchutils import k8s
from orchutils.helpers import k8shelpers
from orchutils.ibmcloudmodels.albcertificate import ALBCertificate
from orchutils.ibmcloudmodels.clusteralbs import ClusterALBs
from orchutils.ibmcloudmodels.ikscluster import IKSCluster
from orchutils.ibmcloudmodels.iksworker import IKSWorker
from orchutils.ibmcloudmodels.iksworkerpool import IKSWorkerPool
from orchutils.ibmcloudmodels.kpkey import KPKey
from orchutils.ibmcloudmodels.serviceinstance import ServiceInstance
from orchutils.ibmcloudmodels.servicekey import ServiceKey
from orchutils.ibmcloudmodels.servicepolicy import ServicePolicy
from orchutils.ibmcloudmodels.subnet import Subnet
from orchutils.ibmcloudmodels.target import Target
from orchutils.ibmcloudmodels.volume import Volume


logger = logging.getLogger(__name__)
os.environ['IKS_BETA_VERSION'] = '1'  # Remove when new behaviour released for "cluster config". http://ibm.biz/iks-cli-v1
if 'P2PAAS_ORCH_DIR' in os.environ and 'IBMCLOUD_HOME' not in os.environ:
    # Support customisation of the IBMCLOUD_HOME path to facilitate simultaneous management of multiple clusters from a single server
    os.environ['IBMCLOUD_HOME'] = os.environ['P2PAAS_ORCH_DIR']
cli_update_lock_name = 'ibmcloud_cli_update'


def set_config_dir(home_dir):
    """
    By default, ibmcloud saves and uses configuration data in the user's home directory. This function allows changing the directory being used.
    All subsequent calls to any ibmcloud function will use the directory passed into this function.
    This function places the config directory into a IBMCLOUD_HOME environment variable. The same can be achieved by directly populating the environment variable
    without calling this function.
    All configuration data will be stored in a .bluemix sub-directory of the passed home directory.
    Args:
        home_dir: The home directory to use for storing ibmcloud configuration data
    """
    os.environ['IBMCLOUD_HOME'] = home_dir


def apply_pull_secret(cluster_name):
    """
    Triggers the application of default image pull secrets to an IKS cluster.
    Args:
        cluster_name: The name of the cluster to apply the pull secrets to
    """
    baseutils.exe_cmd('/usr/local/bin/ibmcloud ks cluster pull-secret apply --cluster {cluster}'.format(cluster=baseutils.shell_escape(cluster_name)))


def configure_kubecfg(cluster_name):
    """
    Configures the current kubecfg file (based on KUBECONFIG env var) for the specified cluster.
    Args:
        environment: The name of the IKS environment to configure locally
    """
    cmd = '/usr/local/bin/ibmcloud ks cluster config --cluster {cluster_name}'.format(cluster_name=baseutils.shell_escape(cluster_name))
    (rc, output) = baseutils.retry(baseutils.exe_cmd, cmd, interval=10, retry=6)


def configure_alb(alb_id, enable=True):
    """
    Configures (enables or disables) an IKS ALB.
    Args:
        alb_id: The ID of the ALB to configure
        enable: Whether to enable or disable the ALB. True enabled, False disables (Optional, default: True)
    """
    baseutils.exe_cmd('/usr/local/bin/ibmcloud ks alb configure classic --alb-id {alb} {enable}'.format(
        alb=baseutils.shell_escape(alb_id),
        enable='--enable' if enable else '--disable'))


def get_albs(cluster_name):
    """
    Retrieves a list of ALBs for a given IKS cluster.
    Args:
        cluster_name: The name of the cluster to retrieve ALBs for or its ID
    Returns: A list of ALB objects
    """
    (rc, output) = baseutils.exe_cmd('/usr/local/bin/ibmcloud ks alb ls --cluster {cluster} --json'.format(cluster=baseutils.shell_escape(cluster_name)))
    return ClusterALBs(json.loads(output))


def get_iks_clusters(cluster_name=None):
    """
    NOTE: REMOVE THIS FUNCTION when playbook repo is updated to directly reference child functions.
    Retrieves a list of accessible IKS clusters. This will be limited by targeted resource group and region.
    If cluster_name is provided, only that cluster will be returned or None if it is not found.
    Args:
        cluster_name: The name of a particular cluster to look for or its ID (Optional)
    Returns: A list of IKSCluster objects. If cluster_name is specified, a single cluster object or None
    """
    result = None
    if cluster_name:
        result = ks_cluster_get(cluster_name)
    else:
        result = ks_cluster_ls()
    return result


def replace_iks_workers(cluster_name, workers):
    """
    Drain and replace a series of workers, 1 at a time, in an IKS cluster.
    A pod's terminationGracePeriodSeconds is obeyed during the draining of a node.
    Args:
        cluster_name. The name of the cluster to replace workers in or its ID
        workers: A list of one or more worker objects to sequentially replace
    """
    for worker in workers:
        # Ensure worker still exists, for example, in case of an auto-scaling cluster
        worker = baseutils.retry(ks_worker_get, cluster_name, worker.id, interval=30, retry=40)
        if not worker or worker.state == 'deleted':
            continue
        k8s.drain(worker.private_ip)
        if worker.kube_version == worker.target_version:
            cmd = '/usr/local/bin/ibmcloud ks worker reload --cluster {cluster} --worker {worker} -f'.format(
                cluster=baseutils.shell_escape(cluster_name),
                worker=baseutils.shell_escape(worker.id))
        elif 'pending' not in worker.kube_version:  # pending will be in the version field if the update has already been triggered
            cmd = '/usr/local/bin/ibmcloud ks worker update --cluster {cluster} --worker {worker} -f'.format(
                cluster=baseutils.shell_escape(cluster_name),
                worker=baseutils.shell_escape(worker.id))
        try:
            baseutils.retry(baseutils.exe_cmd, cmd, interval=30, retry=40)
        except Exception as e:
            exc_message = str(e)
            if 'The specified worker has already been deleted' in exc_message:
                continue
            elif 'The worker node is already up to date with the latest version' not in exc_message:
                # It's possible that a call to reload can return a failure from the api but still go through. Subsequent retries from the baseutils.retry
                # function will then get this error message back. If the error is present, we can continue as normal.
                raise
        worker.state = 'reload_pending'
        wait_for_worker(cluster_name, worker)


def wait_for_worker(cluster_name, worker, seconds=5400):
    """
    Waits until a worker becomes ready, typically due to a reload or new provision.
    This function continually polls for the worker status and returns when the worker is Ready.
    A worker can be scaled-out during the polling without issue.
    The wait will time out after a specified time, resulting in an exception.
    In addition to waiting for the worker, the function also waits for all kube-system pods scheduled to the node to be ready.
    Args:
        cluster_name: The name of the cluster that the worker belongs to
        worker: The worker to wait on as an IKSWorker model
        seconds: The timeout before failing a node (Optional, default: 5400)
    """
    logger.info('Waiting for worker {worker_ip} to become ready'.format(worker_ip=worker.private_ip))
    with baseutils.timeout(seconds=seconds):
        worker_still_exists = True  # For tolerating a worker being scaled out during the reload
        while worker_still_exists and (worker.state != 'normal' or worker.status != 'Ready' or worker.kube_version != worker.target_version or worker.pending_operation):
            time.sleep(30)
            worker = baseutils.retry(ks_worker_get, cluster_name, worker.id, interval=30, retry=40)
            worker_still_exists = worker and worker.state != 'deleted' and worker.state != 'provision_failed'
        if worker_still_exists:
            k8s.uncordon(worker.private_ip)  # The reload should automatically uncordon but we have observed an issue where the uncordon sometimes doesn't run
            logger.info('Worker {worker_ip} has completed reloading. Waiting for kube-system pods'.format(worker_ip=worker.private_ip))
            k8shelpers.wait_for_node_namespace_pods(worker.private_ip, 'kube-system')
            logger.info('Worker {worker_ip} is ready'.format(worker_ip=worker.private_ip))
        else:
            logger.info('Worker {worker_ip} was scaled out. Finished waiting'.format(worker_ip=worker.private_ip))


def update_iks_cluster(cluster_name, kube_version):
    """
    Updates the version of an IKS cluster.
    Specifically, this updates the master nodes only.
    The current version of the master servers is first checked and if they are already up to date, no action is taken.
    Args:
        cluster_name: The name of the cluster to update
        kube_version: The version to upgrade Kubernetes to in the form major.minor.patch
    """
    cluster = baseutils.retry(ks_cluster_get, cluster_name, interval=30, retry=40)
    upgrade_version = semver.parse_version_info(kube_version.split('_', 1)[0])
    current_version = semver.parse_version_info(cluster.master_kube_version.split('_', 1)[0])
    if upgrade_version > current_version:
        master_kube_version_prefix = '{version}_'.format(version=kube_version)
        if not cluster.master_kube_version.startswith(master_kube_version_prefix) and 'pending' not in cluster.master_kube_version:
            cmd = '/usr/local/bin/ibmcloud ks cluster master update --cluster {cluster} --kube-version {version} -f'.format(
                cluster=baseutils.shell_escape(cluster_name),
                version=baseutils.shell_escape(kube_version))
            (rc, output) = baseutils.retry(baseutils.exe_cmd, cmd, interval=30, retry=40)
        while not cluster.master_kube_version.startswith(master_kube_version_prefix) or 'pending' in cluster.master_kube_version:
            time.sleep(30)
            cluster = baseutils.retry(ks_cluster_get, cluster_name, interval=30, retry=40)


def ks_cluster_get(cluster_name):
    """
    Retrieves the details of an IKS cluster.
    Args:
        cluster_name: The name of the cluster to retrieve or its ID
    Returns: An IKSCluster object representing the cluster or None if it cannot be found
    """
    cluster = None
    (rc, output) = baseutils.exe_cmd('/usr/local/bin/ibmcloud ks cluster get --cluster {cluster} --json'.format(
        cluster=baseutils.shell_escape(cluster_name)), raise_exception=False)
    if rc:
        if '(A0006)' not in output and '(G0004)' not in output:  # The specified cluster could not be found
            raise Exception('Error during call to ibmcloud cli')
    else:
        cluster = IKSCluster(json.loads(output))
    return cluster


def ks_cluster_ls():
    """
    Retrieves a list of available IKS clusters.
    Returns: A list of IKSCluster objects
    """
    (rc, output) = baseutils.exe_cmd('/usr/local/bin/ibmcloud ks cluster ls --json')
    return IKSCluster.parse_iks_clusters(json.loads(output))


def ks_worker_get(cluster_name, worker_id):
    """
    Retrieves a specific worker for an IKS cluster.
    Args:
        cluster_name. The name of the cluster to retrieve worker from
        worker_id. The id of the worker to look up
    Returns: An IKSWorker object representing the worker or None if it cannot be found
    """
    worker = None
    (rc, output) = baseutils.exe_cmd('/usr/local/bin/ibmcloud ks worker get --cluster {cluster} --worker {worker} --json'.format(
        cluster=baseutils.shell_escape(cluster_name),
        worker=baseutils.shell_escape(worker_id)), raise_exception=False)
    if rc:
        if '(E0011)' not in output:  # The specified worker node could not be found. (E0011)
            raise Exception('Error during call to ibmcloud cli')
    else:
        worker = IKSWorker(json.loads(output))
    return worker


def ks_worker_ls(cluster_name, worker_pool_name=None):
    """
    Retrieves a list of worker nodes in an IKS cluster.
    If worker_pool is provided, only workers belonging to that pool will be returned.
    Args:
        cluster_name. The name of the cluster to retrieve workers for
        worker_pool. The name of a worker pool to limit the retrieval for (Optional, default: all pools)
    Returns: A list of IKSWroker objects
    """
    (rc, output) = baseutils.exe_cmd('/usr/local/bin/ibmcloud ks worker ls --cluster {cluster} {worker_pool} --json'.format(
        cluster=baseutils.shell_escape(cluster_name),
        worker_pool='--worker-pool {pool_name}'.format(pool_name=baseutils.shell_escape(worker_pool_name)) if worker_pool_name else ''))
    return IKSWorker.parse_iks_workers(json.loads(output))


def ks_worker_pool_create_classic(cluster_name, worker_pool_name, machine_type, size_per_zone, hardware, labels=None):
    """
    Creates a new worker pool for a cluster.
    Args:
        cluster_name: The name of the cluster
        worker_pool_name: The name of the worker pool to create
        machine_type: The machine type for the worker pool. See "ibmcloud ks flavors --zone <zone>"
        size_per_zone: The number of nodes per zone in the worker pool
        hardware: Deploy the nodes to either "dedicated" or "shared" infrastructure servers
        labels: A dictionary of key-value pairs representing labels to apply to workers in the worker pool (Optional)
    Returns: The IKSWorkerPool model for the newly created worker pool
    """
    baseutils.exe_cmd(('/usr/local/bin/ibmcloud ks worker-pool create classic --cluster {cluster_name} --machine-type {machine_type} --name {worker_pool_name} '
                       '--size-per-zone {size_per_zone} --hardware {hardware} {labels}').format(
                       cluster_name=baseutils.shell_escape(cluster_name),
                       worker_pool_name=baseutils.shell_escape(worker_pool_name),
                       machine_type=baseutils.shell_escape(machine_type),
                       size_per_zone=int(size_per_zone),
                       hardware=baseutils.shell_escape(hardware),
                       labels=' '.join(['--label {label}'.format(
                           label=baseutils.shell_escape('{key}={value}'.format(key=key, value=value))) for (key, value) in labels.items()]) if labels else ''
                       ))


def ks_worker_pool_get(cluster_name, worker_pool_name):
    """
    Retrieve a worker pools for a cluster.
    Args:
        cluster_name: The name of the cluster to query
        worker_pool_name: The name of the worker pool to retrieve
    Returns: An IKSWorkerPool model representing the worker pool
    """
    (rc, output) = baseutils.exe_cmd('/usr/local/bin/ibmcloud ks worker-pool get --cluster {cluster} --worker-pool {worker_pool} --json'.format(
        cluster=baseutils.shell_escape(cluster_name),
        worker_pool=baseutils.shell_escape(worker_pool_name)))
    return IKSWorkerPool(json.loads(output))


def ks_worker_pool_ls(cluster_name):
    """
    Retrieve all worker pools for a cluster.
    Args:
        cluster_name: The name of the cluster to query
    Returns: A list of IKSWorkerPool models
    """
    (rc, output) = baseutils.exe_cmd('/usr/local/bin/ibmcloud ks worker-pool ls --cluster {cluster} --json'.format(cluster=baseutils.shell_escape(cluster_name)))
    return IKSWorkerPool.parse_iks_worker_pools(json.loads(output))


def ks_worker_pool_rm(cluster_name, worker_pool_name):
    """
    Delete a worker pool from a cluster.
    Args:
        cluster_name: The name of the cluster to process
        worker_pool_name: The name of the worker pool to remove
    """
    baseutils.exe_cmd('/usr/local/bin/ibmcloud ks worker-pool rm --cluster {cluster} --worker-pool {worker_pool} -f'.format(
        cluster=baseutils.shell_escape(cluster_name),
        worker_pool=baseutils.shell_escape(worker_pool_name)))


def ks_worker_pool_labels(cluster_name, worker_pool_name, labels):
    """
    Add, remove or update labels for an IKS worker pool.
    Args:
        cluster_name: The name of the cluster containing the worker pool
        worker_pool_name: The name of the worker pool to modify
        labels: A dictionary of key-value pairs representing labels. Leave the value of a label blank to remove it
    """
    response = requests.patch('https://containers.cloud.ibm.com/global/v1/clusters/{cluster_name}/workerpools/{worker_pool_name}'.format(
            cluster_name=cluster_name,
            worker_pool_name=worker_pool_name
        ),
        headers={
            'Authorization': iam_oauth_tokens()['iam_token']
        },
        json={
            'state': 'labels',
            'labels': labels
        }
    )
    response.raise_for_status()


def ks_zone_add_classic(cluster_name, zone, worker_pool_name, private_vlan_id, public_vlan_id=None):
    """
    Add a zone to a worker pool in a classic IKS environment.
    Args:
        cluster_name: The name of the cluster to update
        zone: The name of the zone to expand the pool into
        worker_pool: The name of the worker pool to expand to a new zone
        private_vlan_id: The ID of the private vlan in the new zone to deploy the IKS pool to
        public_vlan_id: The ID of the public vlan in the new zone to deploy the IKS pool to. (Optional, default: no public vlan)
    """
    baseutils.exe_cmd('/usr/local/bin/ibmcloud ks  zone add classic --cluster {cluster} --zone {zone} --worker-pool {pool} --private-vlan {private_vlan_id} {public_vlan}'.format(
        cluster=baseutils.shell_escape(cluster_name),
        zone=baseutils.shell_escape(zone),
        pool=baseutils.shell_escape(worker_pool_name),
        private_vlan_id=baseutils.shell_escape(private_vlan_id),
        public_vlan='--public-vlan {public_vlan_id}'.format(public_vlan_id=baseutils.shell_escape(public_vlan_id)) if public_vlan_id else '--private-only'))


def ks_cluster_remove(cluster_name):
    """
    Destroy an IKS cluster.
    This action is irreversible.
    Args:
        cluster_name: The name of the cluster to destroy
    """
    baseutils.exe_cmd('/usr/local/bin/ibmcloud ks cluster rm --cluster {cluster} -f'.format(cluster=baseutils.shell_escape(cluster_name)))


def ks_enable_key_protect(cluster_name, region, key_protect_instance_guid, key_id):
    """
    Enables Key Protect on a given IKS cluster.
    Key Protect will add additional security to the use of Kubernetes secrets.
    If Key Protect is already enabled for the cluster, no action will be taken.
    This function will wait until Key Protect is fully enabled in the environment before returning.
    Args:
        cluster_name: The name of the cluster to update
        region: The region of the Key Protect instance
        key_protect_instance_guid; The GUID of the Key Protect instance
        key_id: The ID of the key inside Key Protect to use. This should be a root key
    """
    cluster = baseutils.retry(ks_cluster_get, cluster_name, interval=30, retry=40)
    if not cluster.key_protect_enabled:
        baseutils.exe_cmd('/usr/local/bin/ibmcloud ks key-protect-enable --cluster {cluster} --key-protect-url {kp_url} --key-protect-instance {kp_guid} --crk {key_id}'.format(
            cluster=baseutils.shell_escape(cluster_name),
            kp_url=baseutils.shell_escape('{region}.kms.cloud.ibm.com'.format(region=region)),
            kp_guid=baseutils.shell_escape(key_protect_instance_guid),
            key_id=baseutils.shell_escape(key_id)))
    while not cluster.key_protect_enabled or cluster.master_status != 'Ready':
        time.sleep(30)
        cluster = baseutils.retry(ks_cluster_get, cluster_name, interval=30, retry=40)


def get_resource_service_instances(name=None, service=None, type=None, location=None):
    """
    Retrieves a list of resource service instances from IBM Cloud using "ibmcloud resource service-instances".
    The output is scoped to the currently configured resource group.
    If name, type or location is provided, the resultant list is filtered to those that match.
    Args:
        name: The name of the service instance to filter by. Names are non-unique (Optional)
        service: The service that the instance is an instance of, eg. logdna, kms, cloud-object-storage (Optional)
        location: The location of the instances to query. "global" is a valid location (Optional)
    Returns: A list of ServiceInstance objects
    """
    (rc, output) = baseutils.exe_cmd('/usr/local/bin/ibmcloud resource service-instances {service} {location} --output json'.format(
        service='--service-name {service}'.format(service=baseutils.shell_escape(service)) if service else '',
        location='--location {location}'.format(location=baseutils.shell_escape(location)) if location else ''))
    instances = ServiceInstance.parse_service_instances(json.loads(output) or [])
    if name:
        instances = [instance for instance in instances if instance.name == name]
    return instances


def create_resource_service_instance(name, service, plan, location, parameters=None):
    """
    Creates a resource service instance via the ibmcli.
    Many different types of service instance are supported.
    Args:
        name: The name of the service instance to create
        service: The name or ID of the type of service to instantiate, for example, cloud-object-storage
        plan: The service plan to use in terms of billing
        location: The location of the instance create. The location can be "global"
        paramaters: JSON paramaters (as a dictionary) that can be passed to the instance creation call (Optional)
    """
    (rc, output) = baseutils.exe_cmd('/usr/local/bin/ibmcloud resource service-instance-create {name} {service} {plan} {location} {parameters}'.format(
        name=baseutils.shell_escape(name),
        service=baseutils.shell_escape(service),
        plan=baseutils.shell_escape(plan),
        location=baseutils.shell_escape(location),
        parameters='--parameters {parameters}'.format(parameters=baseutils.shell_escape(json.dumps(parameters))) if parameters else ''))


def get_user_access_groups(user_email):
    """
    Retrieves a list of resources that a user has editor access to from IBM Cloud using
    "ibmcloud iam access-groups" and then filtering the output.
    Args:
        user_email: The email of the user to fetch environments for
    Returns: A list of environments that the user has editor access to
    """
    (rc, output) = baseutils.exe_cmd('ibmcloud iam access-groups {user}'
                                     .format(user='-u {user_email}'.format(user_email=user_email)))
    # Ignore the status and table header lines
    output_lines = output.splitlines()[2:]
    access_groups_list = []
    for access_group in output_lines:
        match = re.match(r'^([\w-]+ )+', access_group)
        if match:
            access_groups_list.append(match.group(0).strip())
    return access_groups_list


def get_resource_service_keys(name=None, instance_id=None):
    """
    Retrieves a list of resource service keys from IBM Cloud using "ibmcloud resource service-keys".
    The output is scoped to the currently configured resource group.
    If name or instance_id is provided, the resultant list is filtered to those that match.
    Args:
        name: The name of the service key to filter the key by (Optional)
        instance_id: The ID of the service instance to filter the keys by. A service instance can still have multiple keys (Optional)
    Returns: A list of ServiceKey objects
    """
    (rc, output) = baseutils.exe_cmd('/usr/local/bin/ibmcloud resource service-keys {instance} --output json'.format(
        instance='--instance-id {instance}'.format(instance=baseutils.shell_escape(instance_id)) if instance_id else ''), log_level=logging.NOTSET)  # Don't log the keys
    keys = ServiceKey.parse_service_keys(json.loads(output) or [])
    if name:
        keys = [key for key in keys if key.name == name]
    return keys


def create_resource_service_key(name, role, instance_id, service_endpoint=None, parameters=None):
    """
    Creates a resource service key via the ibmcli.
    A service key is attached to a service instance and there can be many keys to a single instance.
    Args:
        name: The name of the service key to create
        role: The role to grant the key. This will be service type-specific. Examples are Reader, Writer, Manager
        instance_id: The ID of the service instance to associate the key to
        service_endpoint: Type of service endpoint, 'public' or 'private' (Optional)
        paramaters: JSON paramaters (as a dictionary) that can be passed to the key creation call (Optional)
    """
    (rc, output) = baseutils.exe_cmd('/usr/local/bin/ibmcloud resource service-key-create {name} {role} --instance-id  {instance_id} {service_endpoint} {parameters}'.format(
        name=baseutils.shell_escape(name),
        role=baseutils.shell_escape(role),
        instance_id=baseutils.shell_escape(instance_id),
        service_endpoint='--service-endpoint {service_endpoint}'.format(service_endpoint=baseutils.shell_escape(service_endpoint)) if service_endpoint else '',
        parameters='--parameters {parameters}'.format(parameters=baseutils.shell_escape(json.dumps(parameters))) if parameters else ''))


def get_subnets(ids=None, note=None):
    """
    Retrieves a list of subnets specific to the currently configured cli region.
    If note is provided, only subnets with that note will be returned. Note is used to identify purpose/ownership of the subnet.
    Args:
        ids: If provided, retrieved subnets are limted to the provided ids (Optional)
        note: A particular note value to look for (Optional)
    Returns: A list of subnet objects
    """
    (rc, output) = baseutils.exe_cmd('/usr/local/bin/ibmcloud ks subnets --provider=classic --json')
    subnets = Subnet.parse_subnets(json.loads(output))
    if ids:
        subnets = [subnet for subnet in subnets if subnet.id in ids]
    if note:
        subnets = [subnet for subnet in subnets if subnet.note == note]
    return subnets


def add_cluster_subnet(cluster_name, subnet_id):
    """
    Add (binds) a subnet to an IKS cluster.
    Args:
        cluster_name: The name of the IKS cluster to bind it to or its ID
        subnet_id: The ID of the subnet to add
    """
    baseutils.exe_cmd('/usr/local/bin/ibmcloud ks cluster subnet add --cluster {cluster_name} --subnet-id {subnet_id}'.format(
        cluster_name=baseutils.shell_escape(cluster_name),
        subnet_id=baseutils.shell_escape(subnet_id)))


def get_kube_versions(version_to_match=None):
    """
    Retrieves a list of available Kubernetes versions for IKS.
    If version is provided, only the version that matches the supplied major and minor version will be returned or None if it is not found.
    Args:
        version: A version for which the major and minor version should be matched for the returned supported version (Optional)
    Returns: A list of supported K8s versions. If version_to_match is specified, a single supported version or None
    """
    (rc, output) = baseutils.exe_cmd('/usr/local/bin/ibmcloud ks versions --json')
    kube_versions = json.loads(output)['kubernetes']
    if version_to_match:
        result = None
        version_to_match = version_to_match.split('.')
        major = int(version_to_match[0])
        minor = int(version_to_match[1])
        for kube_version in kube_versions:
            if kube_version['major'] == major and kube_version['minor'] == minor:
                result = '{major}.{minor}.{patch}'.format(major=major, minor=minor, patch=kube_version['patch'])
                break
    else:
        result = []
        for kube_version in kube_versions:
            result.append('{major}.{minor}.{patch}'.format(major=kube_version['major'], minor=kube_version['minor'], patch=kube_version['patch']))
        result.sort()  # Ensure versions are returned in ascending order
    return result


def login(api_key, region=None, resource_group=None):
    """
    Logs in to IBM Cloud using the cli, optionally setting org, space and infrastructure credentials.
    Args:
        api_key: API key for access to IBM Cloud
        region: The region of IBM Cloud to access (Optional)
        resource_group: IBMCloud resource group to target (Optional)
        infra_username: Username for access to SoftLayer infrastructure (Optional)
        infra_api_key: API key for SoftLayer infrastructure (Optional)
    """
    baseutils.exe_cmd('/usr/local/bin/ibmcloud login -a https://cloud.ibm.com {region} {resource_group} --apikey {api_key}'.format(
        region='-r {region}'.format(region=baseutils.shell_escape(region)) if region else '--no-region',
        resource_group='-g {resource_group}'.format(resource_group=baseutils.shell_escape(resource_group)) if resource_group else '',
        api_key=baseutils.shell_escape(api_key)), obfuscate=baseutils.shell_escape(api_key))


def target(region=None, resource_group=None, org=None, space=None):
    """
    Configure the cli to target a specific aspect such as a resource group or region.
    Args:
        region: The region of IBM Cloud to target (Optional)
        resource_group: IBMCloud resource group to target (Optional)
        target_org: Cloud Foundary org to use (Optional)
        target_space: Cloud Foundary space to use (Optional)
    Returns: If no parameters are passed, a Target object representing the currently configured target information, otherwise None
    """
    target = None
    if region or resource_group or (org and space):
        baseutils.exe_cmd('/usr/local/bin/ibmcloud target {region} {resource_group} {cf}'.format(
            region='-r {region}'.format(region=baseutils.shell_escape(region)) if region else '',
            resource_group='-g {resource_group}'.format(resource_group=baseutils.shell_escape(resource_group)) if resource_group else '',
            cf='--cf -o {org} -s {space}'.format(org=baseutils.shell_escape(org), space=baseutils.shell_escape(space)) if (org and space) else ''))
    else:
        (rc, output) = baseutils.exe_cmd('/usr/local/bin/ibmcloud target --output json')
        target = Target(json.loads(output))
    return target


def ks_alb_cert_ls(cluster_name):
    """
    List the current ALB certificates deployed for a cluster.
    Args:
        cluster_name: The name of the IKS cluster to check
    """
    (rc, output) = baseutils.exe_cmd('/usr/local/bin/ibmcloud ks alb cert ls --cluster {cluster_name} --json'.format(cluster_name=baseutils.shell_escape(cluster_name)))
    return ALBCertificate.parse_alb_certificates(json.loads(output) or [])


def ks_alb_cert_deploy(cluster_name, secret_name, cert_crn):
    """
    Create or update a certificate from IBM Cloud Certificate Manager as a secret in the Kubernetes cluster for to the Ingress Controller.
    This creates a secret containing the cert in the ibm-cert-store namespace and a reference to it in the default namespace.
    The ALB follows the reference in the default namespace to find the certificate.
    Args:
        cluster_name: The name of the IKS cluster to configure
        secret_name: The name to assign to the secret that is created to contain the certificate
        cert_crn: The CRN of the certificate in Certificate Manager
    """
    current_alb_certificates = ks_alb_cert_ls(cluster_name)
    update_flow = any(alb_certificate.secret_name == secret_name for alb_certificate in current_alb_certificates)
    baseutils.exe_cmd('/usr/local/bin/ibmcloud ks alb cert deploy --cluster {cluster_name} --secret-name {secret_name} --cert-crn {cert_crn} {update}'.format(
        cluster_name=baseutils.shell_escape(cluster_name),
        secret_name=baseutils.shell_escape(secret_name),
        cert_crn=baseutils.shell_escape(cert_crn),
        update='--update' if update_flow else ''))


def ks_infra_credentials(username, api_key):
    """
    Set classic infrastructure credentials for the kubernetes service sub-command.
    This requires that a region has been previously set in the cli.
    Args:
        infra_username: Username for access to SoftLayer infrastructure (Optional)
        infra_api_key: API key for SoftLayer infrastructure (Optional)
    """
    baseutils.exe_cmd('/usr/local/bin/ibmcloud ks credential set classic --infrastructure-username {username} --infrastructure-api-key {api_key}'.format(
        username=baseutils.shell_escape(username),
        api_key=baseutils.shell_escape(api_key)), obfuscate=baseutils.shell_escape(api_key))


def ks_cluster_master_auditwebhook_set(cluster_name, remote_url):
    """
    Set the audit webhook configuration for a cluster's Kubernetes API server.
    The webhook backend forwards API server audit logs to a remote server.
    Args:
        cluster_name: The name of the IKS cluster to configure
        remote_url: The remove url to send webhooks to, including http:// as appropriate
    """
    baseutils.exe_cmd('/usr/local/bin/ibmcloud ks cluster master audit-webhook set --cluster {cluster_name} --remote-server {remote_url}'.format(
        cluster_name=baseutils.shell_escape(cluster_name),
        remote_url=baseutils.shell_escape(remote_url)))


def ks_cluster_master_refresh(cluster_name):
    """
    Triggers a refresh of the master components of an IKS cluster to apply new configuration.
    There is no outage of the applications in the cluster.
    Args:
        cluster_name: The name of the IKS cluster to refresh
    """
    baseutils.exe_cmd('/usr/local/bin/ibmcloud ks cluster master refresh --cluster {cluster_name}'.format(cluster_name=baseutils.shell_escape(cluster_name)))


def iam_oauth_tokens():
    """
    Set classic infrastructure credentials for the kubernetes service sub-command.
    This requires that a region has been previously set in the cli.
    Args:
        infra_username: Username for access to SoftLayer infrastructure (Optional)
        infra_api_key: API key for SoftLayer infrastructure (Optional)
    """
    (rc, output) = baseutils.exe_cmd('/usr/local/bin/ibmcloud iam oauth-tokens --output json', log_level=logging.NOTSET)  # Don't log the oauth tokens
    return json.loads(output)


def iam_service_policies(service_id_name):
    """
    List and return all policies associated to a service ID.
    Args:
        service_id_name: The name of the Service ID to query
    Returns: A list of ServicePolicy objects
    """
    (rc, output) = baseutils.exe_cmd('/usr/local/bin/ibmcloud iam service-policies {service_id_name} --output json'.format(
        service_id_name=baseutils.shell_escape(service_id_name)))
    policies = ServicePolicy.parse_service_policies(json.loads(output))
    return policies


def iam_service_policy_update(service_id_name, service_policy):
    """
    Updates an existing service policy in IAM.
    Args:
        service_id_name: The name of the Service ID the policy is associated to
        service_policy: The ServicePolicy object to update back in IBM Cloud
    """
    tmp_dir = tempfile.mkdtemp()
    policy_file = '{tmp_dir}/policy.json'.format(tmp_dir=tmp_dir)
    try:
        with open(policy_file, 'w') as fh:
            json.dump(service_policy, fh, default=lambda o: getattr(o, 'to_json')())
        (rc, output) = baseutils.exe_cmd('/usr/local/bin/ibmcloud iam service-policy-update {service_id_name} {policy_id} --file {policy} -f --output json'.format(
            service_id_name=baseutils.shell_escape(service_id_name),
            policy_id=baseutils.shell_escape(service_policy.id),
            policy=baseutils.shell_escape(policy_file)))
    finally:
        shutil.rmtree(tmp_dir)


def kp_create(instance_id, key_name, key_material=None, standard_key=False):
    """
    Create or update a key in Key Protect.
    Args:
        instance_id: The ID of the Key Protect instance to update
        key_name: The name of the key to create
        key_material: The base64 encoded value of the key (Optional, default: create a new key)
        standard_key: Set True if this should be a standard key. Otherwise it will be a root key (Optional, default: False)
    Returns: The ID of the new key
    """
    cmd = '/usr/local/bin/ibmcloud kp create {key_name} --instance-id {instance_id} {key_material} {standard_key} --output json'.format(
        key_name=baseutils.shell_escape(key_name),
        instance_id=baseutils.shell_escape(instance_id),
        key_material='--key-material {key_material}'.format(key_material=baseutils.shell_escape(key_material)) if key_material else '',
        standard_key='--standard-key' if standard_key else '')
    (rc, output) = baseutils.retry(baseutils.exe_cmd, cmd, interval=10, retry=5)
    return KPKey(json.loads(output))


def kp_list(instance_id, name=None):
    """
    List and return all keys in a Key Protect instance.
    Args:
        instance_id: The ID of the Key Protect instance to query
        name: Filters the resultant key list to keys with a specified name (Optional)
    Returns: A list of KPKey objects
    """
    cmd = '/usr/local/bin/ibmcloud kp list --instance-id {instance_id} --output json'.format(instance_id=baseutils.shell_escape(instance_id))
    (rc, output) = baseutils.retry(baseutils.exe_cmd, cmd, interval=10, retry=5)
    keys = KPKey.parse_kp_keys(json.loads(output) or [])
    if name:
        keys = [key for key in keys if key.name == name]
    return keys


def file_volume_list():
    """List all instances of file volumes with given command
    Args: None
    Returns: Returns a list of all file volumes with column headers specified in call
    """
    cmd = '/usr/local/bin/ibmcloud sl file volume-list --column id --column username --column datacenter --column storage_type --column capacity_gb --column bytes_used --column ip_addr --column mount_addr --column notes'  # noqa
    (rc, output) = baseutils.retry(baseutils.exe_cmd, cmd, interval=10, retry=5)
    file_volume_model_list = Volume.parse_volumes(output, 'file')
    return file_volume_model_list


def block_volume_list():
    """List all instances of block volumes with given command
    Args: None
    Returns: Returns a list of all block volumes with column headers specified in call
    """
    cmd = '/usr/local/bin/ibmcloud sl block volume-list --column id --column username --column datacenter --column storage_type --column capacity_gb --column bytes_used --column ip_addr --column notes'  # noqa
    (rc, output) = baseutils.retry(baseutils.exe_cmd, cmd, interval=10, retry=5)
    block_volume_model_list = Volume.parse_volumes(output, 'block')
    return block_volume_model_list


def sl_volume_detail(volume_id, volume_type):
    """Describe an instance of block volumes with given command
    Args:
        volume_id: The ID of the block volume
    Returns: Returns a description of the block volume
    """
    cmd = '/usr/local/bin/ibmcloud sl {volume_type} volume-detail {volume_id}'.format(
        volume_type=baseutils.shell_escape(volume_type), volume_id=baseutils.shell_escape(volume_id))
    (rc, output) = baseutils.retry(baseutils.exe_cmd, cmd, interval=10, retry=5)
    output = output.split('\n')[1:]
    volume_details = {}
    for line in output:
        if line:
            line = re.split(r'\s\s+', line)
            key = line[0].lower()
            if 'active transactions' in key:
                key = 'active_transactions'
            else:
                key = key.replace('(', '').replace(')', '').replace(' ', '_')
            value = line[1]
            volume_details[key] = value

    volume = Volume(volume_type=volume_type)
    volume.id = volume_details.get('id')
    volume.name = volume_details.get('user_name')
    volume.datacenter = volume_details.get('datacenter')
    volume.storage_type = volume_details.get('type')
    volume.capacity_gb = volume_details.get('capacity_gb')
    volume.ip_addr = volume_details.get('target_ip')
    volume.active_transactions = int(volume_details.get('active_transactions'))
    volume.replicant_count = volume_details.get('replicant_count')
    volume.bytes_used = None
    volume.notes = None

    return volume


def sl_file_volume_cancel(volume_id):
    """Delete file volume
    Args:
        Volume IDs taken from flagged orphans
    EXAMPLE:
    ibmcloud.sl_file_volume_cancel(12345678)
    This command cancels volume with ID 12345678 immediately and without asking for confirmation"""
    baseutils.exe_cmd('/usr/local/bin/ibmcloud sl file volume-cancel {volume_id} --immediate -f'.format(volume_id=baseutils.shell_escape(volume_id)))


def sl_block_volume_cancel(volume_id):
    """Delete block volume
    Args:
        Volume IDs taken from flagged orphans
    EXAMPLE:
    ibmcloud.sl_block_volume_cancel(12345678)
    This command cancels volume with ID 12345678 immediately and without asking for confirmation"""
    baseutils.exe_cmd('/usr/local/bin/ibmcloud sl block volume-cancel {volume_id} --immediate -f'.format(volume_id=baseutils.shell_escape(volume_id)))


def sl_call_api(service, method, init, mask='', parameters='', limit='', offset=''):
    """Performs a call to the SoftLayer API
    Args:
        service: The SoftLayer service to be called
        method: A method of the SL service
        init:  Init parameter (default: 0)
        mask (optional): Object mask: use to limit fields returned
        parameters (optional): Append parameters to web call
        limit (optional): Result limit (default: 0)
        offset (optional): Result offset (default: 0)
    Returns: The JSON result parsed as a python dict
    """
    if mask:
        mask = '--mask {mask}'.format(mask=baseutils.shell_escape(mask))
    if parameters:
        parameters = '--parameters {parameters}'.format(parameters=baseutils.shell_escape(parameters))
    if limit:
        limit = '--limit {limit}'.format(limit=baseutils.shell_escape(limit))
    if offset:
        offset = '--offset {offset}'.format(offset=baseutils.shell_escape(offset))
    options = '--init {init} {mask} {parameters} {limit} {offset}'.format(init=baseutils.shell_escape(init), mask=mask, parameters=parameters,
                                                                          limit=limit, offset=offset)
    cmd = '/usr/local/bin/ibmcloud sl call-api {service} {method} {options}'.format(service=service, method=method, options=options)
    (rc, output) = baseutils.exe_cmd(cmd)
    if output:
        return json.loads(output)
    return {}


def setup_cli(update=True):
    """
    Downloads and installs the current version of the ibmcloud CLI as well as some commonly used plugins.
    Args:
        update: If True and the cli is already present, it will be updated.
    """
    logger.info('Acquiring log to query and insall/update IBM Cloud CLI')
    with baseutils.local_lock(lock_name=cli_update_lock_name):
        if not os.path.exists('/usr/local/bin/ibmcloud'):
            logger.info('Installing IBM Cloud CLI')
            tmp_dir = tempfile.mkdtemp()
            try:
                baseutils.exe_cmd('/usr/bin/curl -L https://clis.cloud.ibm.com/download/bluemix-cli/latest/linux64/archive -o {tmp_dir}/ibmcloud-cli.tar.gz'.format(
                    tmp_dir=tmp_dir))
                baseutils.exe_cmd('/bin/tar -xzvf {tmp_dir}/ibmcloud-cli.tar.gz -C {tmp_dir}'.format(tmp_dir=tmp_dir))
                baseutils.exe_cmd('sudo mv {tmp_dir}/IBM_Cloud_CLI/ibmcloud /usr/local/bin/ibmcloud'.format(tmp_dir=tmp_dir))  # Travis needs sudo
            finally:
                shutil.rmtree(tmp_dir)
            baseutils.exe_cmd('/usr/local/bin/ibmcloud config --check-version=false')
        elif update:
            logger.info('Updating IBM Cloud CLI...')
            baseutils.exe_cmd('/usr/local/bin/ibmcloud update --force')
            baseutils.exe_cmd('/usr/local/bin/ibmcloud plugin update -r "IBM Cloud" --all')
        else:
            logger.info('IBMCloud CLI is already present')
    for plugin_name in ['container-service', 'container-registry', 'key-protect']:
        plugin_install(plugin_name)
    logger.info('IBMCloud CLI configuration complete')


def plugin_install(plugin_name, repository='IBM Cloud', version=None):
    """
    Installs a plugin into the IBM Cloud cli.
    This is a no-op if the plugin is already installed.
    Args:
        plugin_name: The name of the plugin to install
        repository: The repository containing the plugin. If None is passed, no repository flag will be passed to the CLI (Optional, default: IBM Cloud)
        version: The version to install. This does not need to be an exact match, for example, it can just specify the major.minor version
                 to pull in the latest associated patch version (Optional, default: latest available if no version present, otherwise no action)
    """
    plugins_dir = os.path.join(os.environ.get('IBMCLOUD_HOME', os.environ['HOME']), '.bluemix', 'plugins')
    logger.info('Acquiring lock to query status of IBM Cloud plugin "{plugin}"'.format(plugin=plugin_name))
    with baseutils.local_lock(lock_name=cli_update_lock_name):
        if version or plugin_name.startswith('/') or not os.path.exists(os.path.join(plugins_dir, plugin_name)):
            baseutils.exe_cmd('/usr/local/bin/ibmcloud plugin install {plugin_name} {repository} {version} -f'.format(
                plugin_name=baseutils.shell_escape(plugin_name),
                repository='-r {repository}'.format(repository=baseutils.shell_escape(repository)) if repository else '',
                version='-v {version}'.format(version=baseutils.shell_escape(version)) if version else ''))
