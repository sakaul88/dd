import logging
import os
import shutil
import tempfile

import baseutils
from orchutils import k8s
from orchutils import vault

logger = logging.getLogger(__name__)
helm_binary = '/usr/local/bin/helm'
if 'P2PAAS_ORCH_DIR' in os.environ and 'HELM_HOME' not in os.environ:
    # Support customisation of the HEML_HOME path to facilitate simultaneous management of multiple clusters from a single server
    os.environ['HELM_HOME'] = os.path.join(os.environ['P2PAAS_ORCH_DIR'], '.helm')
    helm_binary = baseutils.shell_escape(os.path.join(os.environ['P2PAAS_ORCH_DIR'], 'helm'))
iks_ovpn_reservation_lock_name = 'sos_iks_ovpn_reservation'
vault_iks_ovpn_path = 'secret/ansible/sos/iks/ovpn'


def csutil_cluster_setup(cluster_name, service_name, cname):
    """
    Configure (deploy) the SOS IKS tooling into an IKS cluster.
    This will retrieve and reserve an ovpn file from Vault if one is not yet reserved for the cluster.
    Args:
        cluster_name: The name of the cluster to configure
        service_name: The SOS application name that the cluster will be registered under in the SOS Inventory DB
        cname: Must be ether "bluemix" or "staging" depending on whether the cluster is produciton or non-production respectively
    """
    iks_ovpn_config_name = _reserve_iks_ovpn_config_name(cluster_name)
    iks_ovpn_config = vault.read('{vault_path}/files/{config_name}'.format(vault_path=vault_iks_ovpn_path, config_name=iks_ovpn_config_name), 'content')
    tmp_dir = tempfile.mkdtemp()
    try:
        config_path = os.path.join(tmp_dir, iks_ovpn_config_name)
        with open(config_path, 'w') as fh:
            fh.write(iks_ovpn_config)
        baseutils.exe_cmd(('/usr/local/bin/ibmcloud csutil cluster-setup --crn-service-name {service_name} --crn-cname {cname} '
                           '--sos-config-path {config_path} --skip-prometheus=true {cluster_name} --silent').format(
                               service_name=baseutils.shell_escape(service_name),
                               cname=baseutils.shell_escape(cname),
                               config_path=baseutils.shell_escape(config_path),
                               cluster_name=baseutils.shell_escape(cluster_name)), env=_get_csutil_env())
    finally:
        shutil.rmtree(tmp_dir)


def csutil_cluster_cleanup(cluster_name):
    """
    Removes the SOS IKS tooling from a cluster.
    This will unreserve the ovpn configuration from Vault also.
    Args:
        cluster_name: The name of the cluster to clean up
    """
    release_iks_ovpn_config_reservation(cluster_name)
    baseutils.exe_cmd('/usr/local/bin/ibmcloud csutil cluster-cleanup {cluster_name} --silent'.format(cluster_name=baseutils.shell_escape(cluster_name)), env=_get_csutil_env())


def _reserve_iks_ovpn_config_name(cluster_name):
    """
    Get the name of the ovpn config associated to an IKS cluster.
    If one is not already associated with the cluster, a new one will be reserved.
    An exception is raised if a config cannot be reserved for the cluster.
    Args:
        cluster_name: The name of the cluster to retrieve the ovpn name for
    Returns: The name of the ovpn config that has been reserved for this cluster
    """
    iks_ovpn_config_name = _get_current_iks_ovpn_config_name(cluster_name)
    if not iks_ovpn_config_name:
        available_ovpn_configs = vault.list_keys('{vault_path}/files'.format(vault_path=vault_iks_ovpn_path))
        vault_reservation_path = '{vault_path}/reservations'.format(vault_path=vault_iks_ovpn_path)
        with baseutils.local_lock(lock_name=iks_ovpn_reservation_lock_name):
            reserved_ovpn_configs = vault.list_keys(vault_reservation_path)
            for config_name in available_ovpn_configs:
                if config_name not in reserved_ovpn_configs:
                    iks_ovpn_config_name = config_name
                    vault.write('{vault_path}/{config_name}'.format(vault_path=vault_reservation_path, config_name=iks_ovpn_config_name), {'cluster': cluster_name})
                    break
    if not iks_ovpn_config_name:
        raise Exception('Unable to reservice ovpn config file for cluster "{name}". No configs available to select'.format(name=cluster_name))
    return iks_ovpn_config_name


def _get_current_iks_ovpn_config_name(cluster_name):
    """
    Retrieves the name of the currently associated ovpn config associated to an IKS cluster
    Args:
        cluster_name: The name of the cluster to retrieve the ovpn name for
    Returns: The name of config if there exists a reserved config, otherwise None is returned
    """
    iks_ovpn_config_name = None
    if k8s.exists('secret', 'ibm-services-system', 'sos-vpn-secret'):
        vpn_secret = k8s.get('secret', 'ibm-services-system', 'sos-vpn-secret')
        for key in vpn_secret['data']:
            if key.endswith('.ovpn'):
                iks_ovpn_config_name = key
                with baseutils.local_lock(lock_name=iks_ovpn_reservation_lock_name):
                    # Ensure the reservation system is in-sync with the current state of the IKS cluster
                    vault_reservation_path = '{parent}/reservations/{config_name}'.format(parent=vault_iks_ovpn_path, config_name=iks_ovpn_config_name)
                    current_reservation_owner = vault.read(vault_reservation_path, property='cluster')
                    if current_reservation_owner:
                        if current_reservation_owner != cluster_name:
                            raise Exception('Cluster is using and ovpn config reserved by a different cluster')
                    else:
                        vault.write(vault_reservation_path, {'cluster': cluster_name})
                break
    return iks_ovpn_config_name


def _get_csutil_env():
    """
    The csutil plugin makes a number of assumptions regards the system it runs on.
    This function creates a modified environment for use by the csutil plugin.
    Returns: A dictionary that represents a modified version of the current environment for use by the csutil plugin
    """
    sos_env = os.environ.copy()
    if '/usr/local/bin' not in sos_env['PATH']:  # For the ibmcloud and kubectl binaries
        sos_env['PATH'] = '{path}:/usr/local/bin'.format(path=sos_env['PATH'])
    if 'P2PAAS_ORCH_DIR' in sos_env and sos_env['P2PAAS_ORCH_DIR'] not in sos_env['PATH']:  # For the helm binary
        sos_env['PATH'] = '{path}:{custom_dir}'.format(path=sos_env['PATH'], custom_dir=sos_env['P2PAAS_ORCH_DIR'])
    if 'IBMCLOUD_HOME' in sos_env and 'BLUEMIX_HOME' not in sos_env:  # It doesn't support the IBMCLOUD_HOME param for the path to config and plugins
        sos_env['BLUEMIX_HOME'] = sos_env['IBMCLOUD_HOME']
    if 'IKS_BETA_VERSION' in sos_env:  # It doesn't seem to to support the new ks syntax yet
        del sos_env['IKS_BETA_VERSION']  # Soon this behaviour will be unsupported. The csutil plugin needs to be updated to support this.
    sos_env['HELM_HOME'] = os.path.join(sos_env['P2PAAS_ORCH_DIR'], 'csutil', 'helm')  # It manages its own tiller instance
    if not os.path.exists(sos_env['HELM_HOME']):
        os.makedirs(sos_env['HELM_HOME'])
    return sos_env


def release_iks_ovpn_config_reservation(cluster_name):
    """
    Releases an ovpn configuration associated to a cluster.
    If the cluster has no such reservation, nothing will happen.
    Args:
        cluster_name: The name of the cluster to release the reservation for
    """
    try:
        iks_ovpn_config_name = _get_current_iks_ovpn_config_name(cluster_name)
        if iks_ovpn_config_name:
            vault.delete('{vault_path}/reservations/{config_name}'.format(vault_path=vault_iks_ovpn_path, config_name=iks_ovpn_config_name))
    except Exception as e:
        # This is not a problem if the exception was raised because a different cluster now owns the config. Nothing to do in that case
        exc_message = str(e)
        if 'Cluster is using and ovpn config reserved by a different cluster' != exc_message:
            raise
