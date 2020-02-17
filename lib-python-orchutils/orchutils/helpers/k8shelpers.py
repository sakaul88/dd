import json
import logging
import time

from orchutils import k8s

logger = logging.getLogger(__name__)


def set_cluster_autoscaler(enabled, worker_pool_names=None, new_worker_pool_names=None):
    """
    Enables or disables the cluster autoscaler in a cluster.
    This will neither install nor uninstall the autoscaler, merely update the configuration of the autoscaler if present.
    If the autoscaler is installed but a given worker pool is not already present in the autoscaler config, it will not be added.
    Args:
        enabled: Whether to enable or disable the cluster autoscaler. True = enable, False = disable
        worker_pool_names: If present, only the passed list of pools will be enabled/disabled(Optional, default: all worker pools currently configured)
        new_worker_pool_names: If worker_pool_names is also specified, element n in worker_pool_names will be renamed to element n in new_worker_pool_names.
                               Each element in worker_pool_names must have a corresponding entry in new_worker_pool_names and at the same index (Optional)
    Returns: A list of the worker pools that had their configuration changed
    """
    modified_pools = []
    if k8s.exists('configmap', 'kube-system', 'iks-ca-configmap'):
        config_map = k8s.get('configmap', 'kube-system', 'iks-ca-configmap')
        worker_pools_config = json.loads(config_map['data']['workerPoolsConfig.json'])
        rename_worker_pools = new_worker_pool_names and worker_pool_names and len(new_worker_pool_names) == len(worker_pool_names)
        for pool_config in worker_pools_config:
            if not worker_pool_names or pool_config['name'] in worker_pool_names:
                if rename_worker_pools:
                    pool_config['name'] = new_worker_pool_names[worker_pool_names.index(pool_config['name'])]
                    pool_config['enabled'] = enabled
                    modified_pools.append(pool_config['name'])
                elif pool_config['enabled'] != enabled:
                    pool_config['enabled'] = enabled
                    modified_pools.append(pool_config['name'])
        if modified_pools:
            config_map['data']['workerPoolsConfig.json'] = json.dumps(worker_pools_config, ensure_ascii=False)  # TODO: Remove ensure_ascii when migration to py3 is complete
            k8s.apply(config_map)
    else:
        logger.info('Cluster autoscaler is not present')
    return modified_pools


def set_recovery_tool(enabled):
    """
    Sets ibm-worker-recovery tool "Enabled" attribute, which governs whether it monitors nodes for failures.
    This can be used to disable the tool when performing maintenance on IKS nodes. Otherwise an intermediate state of a node could trigger the tool to queue up a reload.
    If the recovery tool is not present in an environment, nothing will be done.
    Currently only KUBEAPI checks are enabled/disabled.
    Args:
        enabled: Boolean value to define if the ibm-worker-recovery tool should be enabled.
    """
    if k8s.exists('configmap', 'kube-system', 'ibm-worker-recovery-checks'):
        config_map = k8s.get('configmap', 'kube-system', 'ibm-worker-recovery-checks')
        for check in config_map['data']:
            check_config = json.loads(config_map['data'][check])
            if check_config['Check'] == 'KUBEAPI':
                check_config['Enabled'] = enabled
                config_map['data'][check] = json.dumps(check_config, ensure_ascii=False)  # TODO: Remove ensure_ascii when migration to py3 is complete
        k8s.apply(config_map)
    else:
        logger.info('IBM Auto-Recovery tool is not present')


def wait_for_node_namespace_pods(node, namespace):
    """
    Waits until the pods in a particular namespace on a specified node node are Running.
    This can be useful when perform node maintenance when some namespaces do not utilise PodDisruptionBudgets.
    This function continually polls for the status of pods in the namespace assigned to a given node and returns when they are all Running or Completed.
    I the node is scaled out during the process, the function will return without error.
    Args:
        node: The name of the node to wait on. This is generally the IP of the node
        namespace: The namespace to poll
    """
    pods_ready = False
    while not pods_ready:
        pods_ready = True
        time.sleep(15)
        pods = k8s.get('pod', namespace=namespace)
        for pod in pods:
            pod_status = pod['status']
            if pod_status.get('hostIP') == node:  # We are not checking pods with an empty hostIP as we can't tell if it's actually waiting for the current host
                # Pod is located on the host we are monitoring
                pod_phase = pod_status['phase']
                if pod_phase != 'Succeeded':  # A succeeded pod is successfully complete
                    if pod_phase == 'Running':
                        for container_status in pod_status['containerStatuses']:
                            if not container_status['ready']:
                                pods_ready = False
                                break
                    else:  # A non-running, non-succeeded pod is not ready
                        pods_ready = False
                        break
