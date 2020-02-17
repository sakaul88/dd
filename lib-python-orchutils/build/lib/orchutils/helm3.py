import json
import logging
import os
import shutil
import tempfile
import time
import yaml
from datetime import datetime

from baseutils import baseutils
from orchutils import k8s
from orchutils.helmmodels.releaserevision import ReleaseRevision

logger = logging.getLogger(__name__)
helm_binary = '/usr/local/bin/helm'

def set_helm_home(helm_home):
    """
    Allows customisation of the Helm home directory that will be used by all Helm calls in the currentl os environment.
    This function places passed path into a HELM_HOME environment variable. The same can be achieved by directly populating the environment variable
    without calling this function.
    If HELM_HOME is not already in the environment variables but P2PAAS_ORCH_DIR, the default HELM_HOME directory will have been set to "${P2PAAS_ORCH_DIR}/.helm"
    Args:
        helm_home: The home directory to use for storing helm configuration data
    """
    os.environ['HELM_HOME'] = helm_home


def add_repo(name, username, password, repo_url='https://na.artifactory.swg-devops.com/artifactory/wce-p2paas-helm-virtual'):
    """
    Adds a new helm repository to the helm configuration. It is safe to re-add an already existing repository.
    Args:
        name: The name of the repository to add. This is the local name which will be used to reference the repository
        username: The username for authentication to the repository
        password: The password for authentication to the repository
        repo_url: The url to the repository. This is the full remote url to the Helm repository (Optional, default is corporate artifactory wce-p2paas-helm-virtual repository)
    """
    logger.info('Configuring Helm repository {repo}'.format(repo=name))
    baseutils.exe_cmd('{helm} repo add {repo} {repo_url} --username {username} --password {password}'.format(
        helm=helm_binary,
        repo=baseutils.shell_escape(name),
        repo_url=baseutils.shell_escape(repo_url),
        username=baseutils.shell_escape(username),
        password=baseutils.shell_escape(password)), obfuscate=baseutils.shell_escape(password))
    baseutils.exe_cmd('{helm} repo update {repo}'.format(helm=helm_binary, repo=baseutils.shell_escape(name)))


def update_repos():
    """
    Updates locally cached metadata for all available chart repositories.
    """
    logger.info('Updating Helm repository metadata')
    baseutils.exe_cmd('{helm} repo update'.format(helm=helm_binary))
    logger.info('Helm repository metadata updated')


def delete(release_name, purge=True):
    """
    Deletes a deployed release.
    Args:
        release_name: The release to delete
        purge: Whether to purge all Helm history for the release (Optional, default: True)
    """
    baseutils.exe_cmd('{helm} delete {release_name} {purge}'.format(
        helm=helm_binary,
        release_name=baseutils.shell_escape(release_name),
        purge='--purge' if purge else ''))

def uninstall(release_name):
    """
    Deletes a deployed release.
    Args:
        release_name: The release to delete
        purge: Whether to purge all Helm history for the release (Optional, default: True)
    """
    baseutils.exe_cmd('{helm} uninstall {release_name'.format(
        helm=helm_binary,
        release_name=baseutils.shell_escape(release_name)))


def install_chart(chart, version, valuesFile, release, namespace, validate_manifest=False, dry_run=False, debug=False):
    """
    Install a new chart with a specified release name.
    Args:
        chart: The name of the chart to install
        version: The version of the chart to install
        valuesFile: A file containing chart values
        release: The name to assign to the deployed release
        namespace: The namespace to deploy the release into
        validate_manifest: Validate the manifest meets a predermined set of criteria. See #validate_manifest_requirements for details (Optional, default: True)
        dry_run: Perform the install in dry-run mode. No changes will be made in the Kubernetes cluster (Optional, default: False)
        debug: Perform the install in debug mode, increasing logging output (Optional, default: False)
    """
    logger.info('Installing chart {chart} (release: {release}) valuesFile: {valuesFile} with version {version} {dry_run}'.format(chart=chart, release=release, valuesFile=valuesFile, version=version, dry_run=dry_run))
    validate_manifest = False
    try:
        (rc, output) = baseutils.exe_cmd('{helm} install {release} {chart} --values {valuesFile} --version {version} --namespace {namespace} --dry-run'.format(
            helm=helm_binary,
            release=baseutils.shell_escape(release),
            chart=baseutils.shell_escape(chart),
            valuesFile=baseutils.shell_escape(valuesFile),
            version=baseutils.shell_escape(version),
            namespace=baseutils.shell_escape(namespace),
            working_dir=os.environ.get('HELM_HOME'), log_level=logging.NOTSET, raise_exception=False))  # Logging is disabled as output can contain secrets

        if rc:
            helm_error = output.strip().splitlines()[-1] if output else ''
            if helm_error:
                logger.error(helm_error)
            raise Exception('Failed to parse Helm template. {helm_error}'.format(helm_error=helm_error))
        elif validate_manifest:
            # Remove non-yaml output, everything above first "MANIFEST:"
            manifest = output.partition('MANIFEST:')[2]
            # Remove non-yaml output after the manifest
            manifest = manifest.partition('[{year}'.format(year=datetime.now().year))[0]
            errors = validate_manifest_requirements(manifest)
            if len(errors) > 0:
                for error in errors:
                    logger.error(error)
                raise Exception('Chart pre-approval validation failed. Reason: {failure_reasons}'.format(failure_reasons='. '.join(errors)))
        deploy_cmd = '{helm} install {release} {chart} --values {valuesFile} --version {version} --namespace {namespace}'.format(
            helm=helm_binary,
            release=baseutils.shell_escape(release),
            chart=baseutils.shell_escape(chart),
            valuesFile=baseutils.shell_escape(valuesFile),
            version=baseutils.shell_escape(version),
            namespace=baseutils.shell_escape(namespace),
            dry_run='--dry-run' if dry_run else '',
            debug='--debug' if debug else '')
        _attempt_chart_deploy(deploy_cmd)
    finally:
        logger.info("completed")
    logger.info('Install request for chart {chart} (release: {release}) valuesFile: {valuesFile} with version {version} passed to Kubernetes'.format(chart=chart, release=release, valuesFile=valuesFile, version=version))


def upgrade_chart(chart, version, valuesFile, release, namespace, dry_run=False, debug=False):
    """
    Upgrade a specific release of a chart. This could be due to a new chart version being available or updated values for the chart.
    Args:
        chart: The name of the chart to upgrade
        version: The version of the chart to upgrade to
        valuesFile: A file used to relace chart values
        release: The name of the deployed release to upgrade
        namespace: The namespace to deploy the release into
        dry_run: Perform the upgrade in dry-run mode. No changes will be made in the Kubernetes cluster (Optional, default: False)
        debug: Perform the upgrade in debug mode, increasing logging output (Optional, default: False)
    """
    logger.info('Upgrading chart {chart} (release: {release}) values {valuesFile} to version {version}'.format(chart=chart, release=release, valuesFile=valuesFile, version=version))
    try:
        deploy_cmd = '{helm} upgrade --values {values_file} {release} {chart} --values {valuesFile} --version {version} --namespace {namespace}'.format(
            helm=helm_binary,
            values_file=baseutils.shell_escape(values_file),
            release=baseutils.shell_escape(release),
            chart=baseutils.shell_escape(chart),
            valuesFile=baseutils.shell_escape(valuesFile),
            version=baseutils.shell_escape(version),
            namespace=baseutils.shell_escape(namespace),
            dry_run='--dry-run' if dry_run else '',
            debug='--debug' if debug else '')
        _attempt_chart_deploy(deploy_cmd)
    finally:
        os.remove(values_file)
    logger.info('Upgrade request for chart {chart} (release: {release}) values {valuesFile} to version {version} passed to Kubernetes'.format(chart=chart, release=release, valuesFile=valuesFile, version=version))


def _attempt_chart_deploy(deploy_cmd, attempt=0):
    """
    Attempts to perofrm a chart deployment. The actual deploy command must be passed as an argument.
    Retries will be attempted if the failure reason can be calculated as being "safe to retry".
    Args:
        deploy_cmd: The command to use to deploy (install/upgrade) the chart
    """
    try:
        baseutils.exe_cmd(deploy_cmd, working_dir=os.environ.get('HELM_HOME'))
    except Exception as e:
        exc_message = str(e)
        if 'Could not get apiVersions from Kubernetes: unable to retrieve the complete list of server APIs' in exc_message and attempt < 5:
            time.sleep(10)
            _attempt_chart_deploy(deploy_cmd, attempt=attempt+1)
        else:
            raise


def list_releases(filter=None):
    """
    Executes helm list and returns the output. A filter can be optionally specified.
    Args:
        filter: A regex filter that will be passed through to the "helm list <filter>" command
    Returns: The output from the helm list command
    """
    cmd = '{helm} list {filter}'.format(helm=helm_binary, filter=baseutils.shell_escape(filter or ''))
    (rc, output) = baseutils.retry(baseutils.exe_cmd, cmd, interval=10, retry=6)
    return output


def search_charts(search_term):
    """
    Triggers a helm search command using the passed search term and returns the output.
    Args:
        search_term: A search term that will be passed through to the "helm search <search_term>" command
    Returns: The output from the helm search command
    """
    (rc, output) = baseutils.exe_cmd('{helm} search {search_term}'.format(helm=helm_binary, search_term=baseutils.shell_escape(search_term)))
    return output


def get_latest_chart_version(chart):
    """
    Looks up the latest available version of a chart.
    Args:
        chart: The chart to search for. It must be specified as "<repo>/<chart_name>", eg. "p2paas/p2paas-console-ui"
    Returns: The latest available version of the chart
    """
    search_output = search_charts(chart)
    for line in search_output.splitlines():
        line = line.split()
        if line[0] == chart:
            return line[1]
    raise Exception('Chart {chart} was not found in Helm'.format(chart=chart))


def validate_manifest_requirements(manifest):
    """
    Validates that a manifest meets our requirements. The current requirements are:
    Deployment, StatefulSet
        replicas >= 3
        Contains all of memory/cpu limits/requests
        Liveness/readiness probe on every container
        Key names for env vars not referencing secrets do no contain the strings secret/pass/pw UNLESS they also contain the string "name" (trying to flag accidental exposure)
    Service
        spec.ports entries cannot contain the field nodePort

    Args:
         manifest: The entire manifest for a release as a string. This can come from the output of a dry-run also
    Returns: A list of error messages
    """
    errors = []
    for resource in yaml.safe_load_all(manifest):
        if not resource:
            continue

        kind = resource.get('kind')
        if kind in ['Deployment', 'StatefulSet']:
            name = resource['metadata']['name']
            spec = resource.get('spec', None)
            replicas = spec.get('replicas', None)
            if replicas < 3:
                errors.append('{kind} {name} has less than 3 replicas. At least 3 replicas is required'.format(kind=kind, name=name))
            probes_flag = False
            for container in spec['template']['spec']['containers']:
                _validate_manifest_resources(kind, name, container, errors)
                probes_flag = probes_flag or (container.get('livenessProbe', False) and container.get('readinessProbe', False))
                _validate_manifest_envvars(kind, name, container.get('env', []), errors)
            if not probes_flag:
                errors.append('{kind} {name} must have at least one container with both a liveness and a readiness probe'.format(kind=kind, name=name))
        elif kind == 'Service':
            name = resource['metadata']['name']
            spec = resource['spec']
            ports = spec.get('ports', [])
            for port in ports:
                if 'nodePort' in port:
                    errors.append('{kind} {name} explicitly sets a nodePort number. Must allow Kubernetes to auto-assign nodePort values'.format(kind=kind, name=name))
    return errors


def _validate_manifest_resources(kind, name, container, errors):
    """
    Helper method for performing validation of a container's resources in a manifest. See #validate_manifest_requirements for details.
    Args:
        kind: The kind of resource being analysed (for use in any error messages)
        name: The name of the resource being analysed (for use in any error messages)
        container: A container in a resource, taken from a release's manifest
        errors: An array to append any error messages into
    """
    container_resources = container.get('resources')
    if container_resources:
        cpu_word_count = str(container_resources).count('cpu')
        memory_word_count = str(container_resources).count('memory')
        if cpu_word_count < 2 or memory_word_count < 2:
            errors.append('{kind} {name} has a container that is missing one or more of requests/limits for memory or cpu'.format(kind=kind, name=name))
    else:
        errors.append('{kind} {name} has a container with no resource requests/limits for memory and CPU'.format(kind=kind, name=name))


def _validate_manifest_envvars(kind, name, envvars, errors):
    """
    Helper method for performing validation of environment variables in a manifest. See #validate_manifest_requirements for details.
    Args:
        kind: The kind of resource being analysed (for use in any error messages)
        name: The name of the resource being analysed (for use in any error messages)
        envvars: A list of environment variables for a container, taken from a release's manifest
        errors: An array to append any error messages into
    """
    secret_keywords = ['secret', 'pass', 'pw']
    for var in envvars:
        var_name = var['name'].lower()
        for keyword in secret_keywords:
            if keyword in var_name and 'name' not in var_name:
                if 'secretKeyRef' not in str(var):
                    errors.append('{kind} {name} environment variable "{var}" has keyword "{keyword}". This value should be loaded via secretKeyRef'.format(
                        kind=kind, name=name, var=var_name, keyword=keyword))


def get_max_replicas_count_in_manifest(manifest):
    """
    Identifies the largest replica count accross all resources in a manifest.
    This facilitates, for example, the calculation of timeouts when waiting of resources to initialise.
    Args:
        manifest: A Helm manifest describing a release
     Returns: The highest replica count inside the passed manifest
    """
    replica_counts = set([0])
    for resource in manifest:
        if 'spec' in resource and 'replicas' in resource['spec']:
            replica_counts.add(resource['spec']['replicas'])
    return max(replica_counts)


def get_manifest(release, resource_type=None):
    """
    Retrieves the Helm manifest for a deployed release as an array of resources.
    Args:
        release: The name of the release to retrieve manifest for
        resource_type: Limits the returned resources to the specified resource type (Optional)
    Returns: A list of manifest resources
    """
    full_manifest = None
    manifest = []
    cmd = '{helm} get manifest {release}'.format(helm=helm_binary, release=baseutils.shell_escape(release))
    (rc, output) = baseutils.retry(baseutils.exe_cmd, cmd, log_level=logging.NOTSET, interval=10, retry=6)  # Output can contain secrets so don't log
    full_manifest = yaml.safe_load_all(output)
    for resource in full_manifest:
        if resource and 'kind' in resource:  # This implies the resource is a valid k8s manifest
            if not resource_type or resource_type == resource['kind']:
                manifest.append(resource)
    return manifest


def get_hooks(release, resource_types=None, hook_types=None):
    """
    Retrieves the Helm hooks for a deployed release as a list of resources.
    Args:
        release: The name of the release to retrieve the hooks for
        resource_types: A list of resource types resource types to limit the returned hooks to (Optional)
        hook_types: A list of hook types to limit the returned hooks to (Optional)
    Returns: A list of Kubernetes resources
    """
    cmd = '{helm} get hooks {release}'.format(helm=helm_binary, release=baseutils.shell_escape(release))
    (rc, output) = baseutils.retry(baseutils.exe_cmd, cmd, log_level=logging.NOTSET, interval=10, retry=6)  # Output can contain secrets so don't log
    hooks = list(yaml.safe_load_all(output))
    if resource_types:
        hooks = [hook for hook in hooks if hook['kind'] in resource_types]
    if hook_types:
        hooks = [hook for hook in hooks if hook['metadata']['annotations']['helm.sh/hook'] in hook_types]
    return hooks


def history(release):
    """
    Retrieves the revision history for a specified release.
    Args:
        release: The name of the release to retrieve the revision history for
    Returns: A list of ReleaseRevision objects
    """
    cmd = '{helm} history {release} -o json'.format(helm=helm_binary, release=baseutils.shell_escape(release))
    (rc, output) = baseutils.retry(baseutils.exe_cmd, cmd, interval=10, retry=6)
    return ReleaseRevision.parse_release_revisions(json.loads(output))


def rollback(release, revision):
    """
    Rolls a release back to a specified revision.
    Args:
        release: The name of the release to rollback
        revision: The revision number to roll back to
    """
    baseutils.exe_cmd('{helm} rollback {release} {revision}'.format(
        helm=helm_binary,
        release=baseutils.shell_escape(release),
        revision=int(revision)))


def test(release, seconds=1260):
    """
    Execute Helm tests associated to a deployed release.
    An exception is raised if the tests fail.
    Args:
        release: The name of the release to test
        seconds: The timeout to apply to the tests in seconds (Optional, default: 1260)
    """
    (rc, output) = baseutils.exe_cmd('{helm} test {release} --timeout {timeout}'.format(
        helm=helm_binary,
        release=baseutils.shell_escape(release),
        timeout=int(seconds)))


def get_tiller_version():
    """
    Retrieves the current version of Tiller in the environment.
    If Tiller is not present, an exception will be triggered by the underlying Kubernetes apis.
    Returns: The installed version of Tiller
    """
    tiller_deployment = k8s.get('deployment', namespace='kube-system', name='tiller-deploy')
    return tiller_deployment['spec']['template']['spec']['containers'][0]['image'].split(':')[-1]


def wait_for_release_resources(release):
    """
    Waits until a release's resources are all initalised.
    For resources with replicas, this means all pods must be started and passing their probes.
    For load_balancer services, this means waiting until the ingresses are initialised.
    If this is an upgrade of a release with replicas, the pre-upgrade state of the pods is required to know when they have been replaced.
    Pods will only be waited upon if their Deployment or Statefule set is configured for RollingUpdate and either their image tag or env vars have been updated.
    Args:
        release: The name of the release to wait on
    """
    manifest = get_manifest(release)
    time.sleep(2)  # Waiting to ensure new replica values has been rolled our from manifest to the deployed resources
    max_replicas = get_max_replicas_count_in_manifest(manifest)
    timeout_value = max(900, (max_replicas * 300) + 60)  # Minimum timeout value is 900. Otherwise, define it base on max number of replicas of any resource
    logger.info('Configuring timeout period set to {timeout} seconds for release "{release}"'.format(timeout=timeout_value, release=release))
    with baseutils.timeout(seconds=timeout_value):
        logger.info('Waiting for resources in release "{release}" to enter ready state'.format(release=release))
        for resource in manifest:
            kind = resource['kind'].lower()
            name = resource['metadata']['name']
            namespace = resource['metadata'].get('namespace')
            if kind in ['deployment', 'daemonset', 'statefulset']:
                logger.info('Tracking rollout status of "{kind}" "{name}"'.format(kind=kind, name=name))
                rollout_status = ''
                try:
                    while ('rolling update complete' not in rollout_status
                           and 'successfully rolled out' not in rollout_status
                           and 'roll out complete' not in rollout_status):
                        time.sleep(5)
                        rollout_status = k8s.rollout_status(kind, name, namespace=namespace)
                        _check_for_resource_pod_errors(kind, namespace, name)
                    logger.info('Pods for "{kind}" "{name}" have been rolled out'.format(kind=kind, name=name))
                except Exception as e:
                    if 'Status is available only for RollingUpdate strategy type' in str(e):
                        logger.info('"{kind}" "{name}" is not configured for rolling updates'.format(kind=kind, name=name))
                    else:
                        raise
            elif kind == 'service' and resource['spec'].get('type') == 'LoadBalancer':
                resource_ready = False
                while not resource_ready:
                    time.sleep(5)
                    live_resource = k8s.get(kind, namespace=namespace, name=name)
                    ingress = live_resource['status']['loadBalancer'].get('ingress')
                    if ingress and 'ip' in ingress[0] and 'clusterIP' in live_resource['spec']:
                        resource_ready = True


def _check_for_resource_pod_errors(kind, namespace, name):
    """
    Checks if pods from a resource enter an error state.
    If an error state is detected, an exception is raised.
    Args:
        kind: The kind of the resource owning the pods
        namespace: The namespace of the resource owning the pods
        name: The name of the resource owning the pods
    """
    live_resource = k8s.get(kind, namespace=namespace, name=name)
    # Evaluate pods specific to the new converging state only. Do not include pods that may have been in a bad state pre-upgrade
    if kind == 'deployment':
        replica_sets = k8s.get('replicaset', namespace=namespace, labels=live_resource['spec']['selector']['matchLabels'])
        for replica_set in replica_sets:
            if live_resource['metadata']['annotations']['deployment.kubernetes.io/revision'] == replica_set['metadata']['annotations']['deployment.kubernetes.io/revision']:
                match_labels = replica_set['spec']['selector']['matchLabels']
                break
    elif kind == 'daemonset':
        match_labels = live_resource['spec']['selector']['matchLabels']
        match_labels['pod-template-generation'] = live_resource['metadata']['generation']
    elif kind == 'statefulset':
        match_labels = live_resource['spec']['selector']['matchLabels']
        match_labels['controller-revision-hash'] = live_resource['status']['updateRevision']
    pods = k8s.get('pod', namespace=namespace, labels=match_labels)
    for pod in pods:
        pod_name = pod['metadata']['name']
        for container_status in pod['status'].get('containerStatuses', []):
            wait_reason = container_status['state'].get('waiting', {}).get('reason')
            if wait_reason and (wait_reason == 'CrashLoopBackOff' or wait_reason == 'ErrImagePull' or wait_reason == 'InvalidImageName' or wait_reason == 'RunContainerError' or
                                wait_reason == 'ImagePullBackOff' or wait_reason.endswith(' not found') or wait_reason.startswith('Couldn\'t find ')):
                # A failed container has been identified. Log useful information before raising exception
                k8s.describe('pod', namespace=namespace, name=pod_name)
                k8s.logs(pod_name, namespace=namespace, container=container_status['name'])
                raise Exception('The pod {pod} has entered the failed waiting state "{state}" during chart upgrade. {message}'.format(
                    pod=pod_name, state=wait_reason, message=container_status['state']['waiting'].get('message', '')))
            if container_status.get('restartCount', 0) > 0:
                k8s.describe('pod', namespace=namespace, name=pod_name)
                k8s.logs(pod_name, namespace=namespace, container=container_status['name'])
                raise Exception('The pod {pod} has restarted (failed) during chart upgrade'.format(pod=pod_name))


def install_helm(helm_version):
    """
    Install Helm and Tiller into the Kubernetes infrastructure.
    This assumes Tiller is to be installed in the kube-system namespace. It will upgrade Tiller if it is already present.
    It is safe to call this function multiple times. There are checks for understanding the current state of the Helm/Tiller deployment and only necessary updates are made.
    Args:
        helm_version: The version of helm that should be installed, eg: v2.11.1
    """
    # First check and ensure that the correct client version is present
    (rc, output) = baseutils.exe_cmd('{helm} version --client'.format(helm=helm_binary), raise_exception=False, log_level=logging.NOTSET)
    if rc or helm_version not in output:
        tmp_dir = tempfile.mkdtemp()
        try:
            helm_tar = baseutils.shell_escape(os.path.join(tmp_dir, 'helm.tar.gz'))
            baseutils.exe_cmd('/usr/bin/curl -L {url} -o {helm_tar}'.format(
                url=baseutils.shell_escape('https://storage.googleapis.com/kubernetes-helm/helm-{version}-linux-amd64.tar.gz'.format(version=helm_version)), helm_tar=helm_tar))
            baseutils.exe_cmd('/bin/tar -xzvf {helm_tar} -C {tmp_dir} && rm -f {helm_tar}'.format(helm_tar=helm_tar, tmp_dir=baseutils.shell_escape(tmp_dir)))
            os.rename(os.path.join(tmp_dir, 'linux-amd64', 'helm'), helm_binary.strip('\''))
            os.chmod(helm_binary.strip('\''), 0o755)
        finally:
            shutil.rmtree(tmp_dir)
    # Secondly check that the correct version of Tiller is installed into the Kubernetes cluster
    (rc, output) = baseutils.exe_cmd('{helm} version'.format(helm=helm_binary), raise_exception=False, log_level=logging.NOTSET)
    if rc:
        # Tiller is not installed. We must check if the service account exists yet
        service_accounts = k8s.get('serviceaccount', namespace='kube-system')
        if 'tiller' not in [service_account['metadata']['name'] for service_account in service_accounts]:
            k8s.apply({
                'apiVersion': 'v1',
                'kind': 'ServiceAccount',
                'metadata': {
                    'name': 'tiller',
                    'namespace': 'kube-system'
                }
            })
        cluster_role_bindings = k8s.get('clusterrolebinding')
        if 'tiller' not in [cluster_role_binding['metadata']['name'] for cluster_role_binding in cluster_role_bindings]:
            k8s.apply({
                'apiVersion': 'rbac.authorization.k8s.io/v1',
                'kind': 'ClusterRoleBinding',
                'metadata': {
                    'name': 'tiller',
                },
                'roleRef': {
                    'apiGroup': 'rbac.authorization.k8s.io',
                    'kind': 'ClusterRole',
                    'name': 'cluster-admin'
                },
                'subjects': [{
                    'kind': 'ServiceAccount',
                    'name': 'tiller',
                    'namespace': 'kube-system'
                }]
            })
        baseutils.exe_cmd('{helm} init  --history-max 20 --service-account tiller --override "spec.template.spec.containers[0].command"="{{/tiller,--storage=secret}}"'
                          .format(helm=helm_binary))
    elif output.count(helm_version) != 2:
        # Tiller is installed but it is an old version. Upgrade it
        baseutils.exe_cmd('{helm} init --history-max 20 --service-account tiller --override "spec.template.spec.containers[0].command"="{{/tiller,--storage=secret}}" --upgrade'
                          .format(helm=helm_binary))
    else:
        # Tiller is correctly configured. We still need to init the client to facilitate the usage of helm repositories
        baseutils.exe_cmd('{helm} init --client-only'.format(helm=helm_binary))


def upgrade_tiller(namespace):
    """
    Updates the version of Tiller in a namespace to match the currently configured Helm client.
    An exception will be thrown if Tiller is not present.
    Args:
        namespace: The namespace of the Tiller deployment
    """
    # Check if Tiller is already at the correct version
    (rc, output) = baseutils.exe_cmd('{helm} version --tiller-namespace {namespace} --short'.format(
            helm=helm_binary,
            namespace=baseutils.shell_escape(namespace)))
    output = output.strip().splitlines()
    client_version = output[0].strip().split()[1]
    tiller_version = output[1].strip().split()[1]
    if client_version != tiller_version:
        deployment = k8s.get('deployment', namespace=namespace, name='tiller-deploy')
        pod_spec = deployment['spec']['template']['spec']
        service_account_name = pod_spec['serviceAccountName']
        container_spec = pod_spec['containers'][0]
        override = None
        if 'command' in container_spec:
            override = '"spec.template.spec.containers[0].command"="{{{{{command}}}}}"'.format(command=','.join(container_spec['command']))
        baseutils.exe_cmd('{helm} init --history-max 20 --tiller-namespace {namespace} --service-account {service_account_name} {override} --upgrade'.format(
            helm=helm_binary,
            namespace=baseutils.shell_escape(namespace),
            service_account_name=baseutils.shell_escape(service_account_name),
            override='--override {override}'.format(override=baseutils.shell_escape(override)) if override else ''))
