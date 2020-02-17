import json
import logging
import os

import baseutils

logger = logging.getLogger(__name__)
kubectl_binary = '/usr/local/bin/kubectl'
if 'P2PAAS_ORCH_DIR' in os.environ:
    # Support customisation of the kubectl binary path to facilitate simultaneous management of multiple clusters of differing versions from a single server
    os.environ['KUBECONFIG'] = os.path.join(os.environ['P2PAAS_ORCH_DIR'], '.kube', 'config')
    kubectl_binary = baseutils.shell_escape(os.path.join(os.environ['P2PAAS_ORCH_DIR'], 'kubectl'))


def apply(resource):
    """
    Executes a "kubectl apply" on a passed resource definition.
    The definition should be a python dictionary in a valid Kubernetes manifest format. It will be dumped to json before being passed to kubectl.
    Args:
        resource: The resource to apply to Kubernetes
    """
    (rc, output) = baseutils.exe_cmd('{kubectl} apply -f -'.format(kubectl=kubectl_binary), stdin=json.dumps(resource))


def cordon(node=None, labels=None):
    """
    Cordons a specified Kubernetes node by name or a selection of nodes based on label.
    Args:
        node: The node to cordon (Optional)
        labels: A label selector query for nodes to cordon. Can either be a string of the form "label1=value1,labe2=value2" or a dictionary with "key: value" pairs (Optional)
    """
    if isinstance(labels, dict):
        labels = ','.join('{key}={value}'.format(key=key, value=value) for (key, value) in labels.items())
    baseutils.exe_cmd('{kubectl} cordon {node} {labels}'.format(
        kubectl=kubectl_binary,
        node=baseutils.shell_escape(node) if node else '',
        labels='-l {labels}'.format(labels=baseutils.shell_escape(labels)) if labels else ''))


def delete(kind, namespace=None, name=None, wait=True, grace_period=None):
    """
    Delete one or more resources of a specific kind in Kubernetes.
    Args:
        kind: The kind of the resource, eg. deployment
        namespace: The namespace of the resources (Optional, default is as per kubecfg configuration)
        name: The name of an individual resource (Optional)
        wait: Wait for the resource to be completed removed before returning (Optional, default: True)
        grace_period: The grace period to pass for resources that support grace periods
    """
    (rc, output) = baseutils.exe_cmd('{kubectl} delete {kind} {name} {namespace} --wait={wait} --grace_period={grace_period}'.format(
        kubectl=kubectl_binary,
        kind=baseutils.shell_escape(kind),
        name=baseutils.shell_escape(name) if name else '',
        namespace='-n {namespace}'.format(namespace=baseutils.shell_escape(namespace)) if namespace else '',
        wait='true' if wait else 'false',
        grace_period=int(grace_period) if grace_period else '-1'))


def describe(kind, namespace=None, name=None, labels=None):
    """
    Describe one or more resources of a specific kind in Kubernetes.
    An exception is thrown for invalid types or a name of a resource that does not exist.
    Args:
        kind: The kind of the resource, eg. deployment
        namespace: The namespace of the resources. Setting to "all" triggers the flag --all-namespaces (Optional, default is as per kubecfg configuration)
        name: The name of an individual resource (Optional, default: retrieve all)
        labels: A label selector query to be passed to kubectl. Can either be a string of the form "label1=value1,labe2=value2" or a dictionary with "key: value" pairs (Optional)
    Returns: Human readable output from the describe sub-command of kubectl
    """
    if isinstance(labels, dict):
        labels = ','.join('{key}={value}'.format(key=key, value=value) for (key, value) in labels.items())
    (rc, output) = baseutils.exe_cmd('{kubectl} describe {kind} {name} {namespace} {labels}'.format(
        kubectl=kubectl_binary,
        kind=baseutils.shell_escape(kind),
        name=baseutils.shell_escape(name) if name else '',
        namespace='--all-namespaces' if namespace == 'all' else ('-n {namespace}'.format(namespace=baseutils.shell_escape(namespace)) if namespace else ''),
        labels='-l {labels}'.format(labels=baseutils.shell_escape(labels)) if labels else ''), log_level=logging.NOTSET if 'secret' in kind.lower() else logging.INFO)
    return output


def drain(node, force=True, delete_local_data=True, ignore_daemonsets=True):
    """
    Drains a node in Kubernetes. The node is left in a cordoned state where new pods cannot be scheduled to it.
    Args:
        node: The node to be drained
        force: Drain pods even if they are not managed by a ReplicationController, ReplicaSet, Job, DaemonSet or StatefulSet (Optional, default: True)
        delete_local_data: Drain pods even if they use emptyDir. Data belonging to these pods will be lost (Optional, default: True)
        igrnore_daemonsets: Skip pods managed by DaemonSets. These pods are undrainable. Otherwise, a daemonset pod would cause the command to fail (Optional, default: True)
    """
    cmd = '{kubectl} drain {node} {force} {delete_local_data} {ignore_daemonsets}'.format(
        kubectl=kubectl_binary,
        node=baseutils.shell_escape(node),
        force='--force' if force else '',
        delete_local_data='--delete-local-data' if delete_local_data else '',
        ignore_daemonsets='--ignore-daemonsets' if ignore_daemonsets else '')
    baseutils.retry(baseutils.exe_cmd, cmd, interval=10, retry=6)


def exists(kind, namespace, name):
    """
    Checks is a specific Kubernetes resource, identified by name, exists.
    Args:
        kind: The kind of the resource, eg. deployment
        namespace: The namespace of the resource
        name: The name of the resource
    Returns: True if the resource exists, otherwise False
    """
    resources = get(kind, namespace=namespace)
    resource_exists = False
    for resource in resources:
        if resource.get('metadata', {}).get('name') == name:
            resource_exists = True
            break
    return resource_exists


def get(kind, namespace=None, name=None, labels=None):
    """
    Retrieve one or more resources of a specific kind in Kubernetes.
    An exception is thrown for invalid types or the name of a resource that does not exist.
    Args:
        kind: The kind of the resources, eg. deployment
        namespace: The namespace of the resources. Setting to "all" triggers the flag --all-namespaces (Optional, default is as per kubecfg configuration)
        name: The name of an individual resource (Optional, default: retrieve all)
        labels: A label selector query to be passed to kubectl. Can either be a string of the form "label1=value1,labe2=value2" or a dictionary with "key: value" pairs (Optional)
    Returns: List of dictionary resources. If name is specified, a single resource as a dictionary (this is actually defined by whether kubectl returns kind=List)
    """
    if isinstance(labels, dict):
        labels = ','.join('{key}={value}'.format(key=key, value=value) for (key, value) in labels.items())
    cmd = '{kubectl} get {kind} {name} {namespace} {labels} -o json'.format(
        kubectl=kubectl_binary,
        kind=baseutils.shell_escape(kind),
        name=baseutils.shell_escape(name) if name else '',
        namespace='--all-namespaces' if namespace == 'all' else ('-n {namespace}'.format(namespace=baseutils.shell_escape(namespace)) if namespace else ''),
        labels='-l {labels}'.format(labels=baseutils.shell_escape(labels)) if labels else '')
    (rc, output) = baseutils.retry(baseutils.exe_cmd, cmd, log_level=logging.NOTSET if 'secret' in kind.lower() else logging.INFO, interval=10, retry=6)
    try:
        resources = json.loads(output)
    except Exception:
        # Sometimes the json is preceded with error messages but kubectl retries and completes. We will retry parsing after removing any error messages
        output = output.splitlines()
        while output and output[0].startswith('E'):
            del(output[0])
        output = '\n'.join(output)
        resources = json.loads(output)
    if resources.get('kind') == 'List':
        resources = resources['items']
    return resources


def label(label, kind, namespace=None, name=None):
    """
    Applies labels to a Kubernetes resource.
    Args:
        kind: The type of resource to label
        namespace: The namespace of the resource to label. Not all resources will be namespaced (Optional)
        name: The name of the resource to label (Optional)
    """
    baseutils.exe_cmd('{kubectl} label {kind} {name} {namespace} {label} --overwrite'.format(
        kubectl=kubectl_binary,
        kind=baseutils.shell_escape(kind),
        name=baseutils.shell_escape(name) if name else '',
        namespace='-n {namespace}'.format(namespace=baseutils.shell_escape(namespace)) if namespace else '',
        label=baseutils.shell_escape(label)))


def logs(name, namespace=None, container=None):
    """
    Retrieve the logs for a specified pod.
    A container will also need to be specified if the pod contains more than 1 container.
    Args:
        name: The name of the pod
        namespace: The namespace of the pod (Optional)
        container: The container to pull logs for (Optional)
    Returns: The logs from a pod/container
    """
    (rc, output) = baseutils.exe_cmd('{kubectl} logs {container} {name} {namespace}'.format(
        kubectl=kubectl_binary,
        container='-c {container}'.format(container=baseutils.shell_escape(container)) if container else '',
        name=baseutils.shell_escape(name),
        namespace='-n {namespace}'.format(namespace=baseutils.shell_escape(namespace)) if namespace else ''))
    return output


def rollout_status(kind, name, namespace=None, watch=False):
    """
    Queries a resource for its rollout status.
    By default, it will not follow (watch) the status.
    If kubectl exits with non-zero, an exception will be raised. The exception will still contain the output from kubectl for upstream parsing.
    Args:
        kind: The type of resource to check. Must be either deployment, statefulset or daemonset
        name: The name of the resource to query
        namespace: The namespace of the resource to query (Optional)
        watch: If True, kubectl will wait for the rollout to complete
    Returns: The output from kubectl
    """
    (rc, output) = baseutils.exe_cmd('{kubectl} rollout status {kind} {name} {namespace} --watch={watch}'.format(
        kubectl=kubectl_binary,
        kind=baseutils.shell_escape(kind),
        name=baseutils.shell_escape(name),
        namespace='-n {namespace}'.format(namespace=baseutils.shell_escape(namespace)) if namespace else '',
        watch='true' if watch else 'false'), raise_exception=False)
    if rc:
        # If an error occurred, put the error message in the exception
        raise Exception(output)
    return output


def taint(taints, node=None, labels=None):
    """
    Applies a taint to a Kubernetes node.
    A specific taint syntax can be used to remove taints as per kubectl documentation.
    Args:
        taints: A list of taints to apply in the format ['key=value:taint', ..]
        node: The node name to taint (Optional)
        labels: A label selector query for nodes to taint. Can either be a string of the form "label1=value1,labe2=value2" or a dictionary with "key: value" pairs (Optional)
    """
    if isinstance(labels, dict):
        labels = ','.join('{key}={value}'.format(key=key, value=value) for (key, value) in labels.items())
    baseutils.exe_cmd('{kubectl} taint node {node} {labels} {taints} --overwrite'.format(
        kubectl=kubectl_binary,
        node=baseutils.shell_escape(node) if node else '',
        labels='-l {labels}'.format(labels=baseutils.shell_escape(labels)) if labels else '',
        taints=' '.join([baseutils.shell_escape(taint) for taint in taints])))


def uncordon(node=None, labels=None):
    """
    Uncordons a specified Kubernetes node by name or a selection of nodes based on label.
    Args:
        node: The node to uncordon (Optional)
        labels: A label selector query for nodes to uncordon. Can either be a string of the form "label1=value1,labe2=value2" or a dictionary with "key: value" pairs (Optional)
    """
    if isinstance(labels, dict):
        labels = ','.join('{key}={value}'.format(key=key, value=value) for (key, value) in labels.items())
    baseutils.exe_cmd('{kubectl} uncordon {node} {labels}'.format(
        kubectl=kubectl_binary,
        node=baseutils.shell_escape(node) if node else '',
        labels='-l {labels}'.format(labels=baseutils.shell_escape(labels)) if labels else ''))


def install_kubectl(kubectl_version):
    """
    Install the kubectl binary locally.
    It is safe to call this function multiple times. If the version is already correct, replacement will not be attempted.
    Args:
        kubectl_version: The version of kubectl that should be installed, eg: v1.11.3
    """
    (rc, output) = baseutils.exe_cmd('{kubectl} version --client --short'.format(kubectl=kubectl_binary), raise_exception=False, log_level=logging.NOTSET)
    if rc or kubectl_version not in output:
        baseutils.exe_cmd('/usr/bin/curl -L {url} -o {kubectl}'.format(
            url=baseutils.shell_escape('https://storage.googleapis.com/kubernetes-release/release/{version}/bin/linux/amd64/kubectl'.format(version=kubectl_version)),
            kubectl=kubectl_binary))
        os.chmod(kubectl_binary.strip('\''), 0o755)
