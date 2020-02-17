import json
import logging
from datetime import datetime

from orchutils import helm
from orchutils import ibmcloud
from orchutils import k8s

logger = logging.getLogger(__name__)


def run_release_tests(release_name):
    """
    Runs post-deployment Helm tests if the chart contains Helm tests.
    Nothing will be done if the release does not contain tests.
    Pre-existing test pods will be cleaned up prior to executing the tests.
    An exception is raised if the tests fail. Logs of the test containers are captured.
    Args:
        release: The name of the release to test
    """
    release_tests = helm.get_hooks(release_name, resource_types=['Pod'], hook_types=['test-success', 'test-failure'])
    if release_tests:
        for release_test in release_tests:
            test_kind = release_test['kind']
            test_namespace = release_test['metadata'].get('namespace', 'default')
            test_name = release_test['metadata']['name']
            if k8s.exists(test_kind, test_namespace, test_name):
                k8s.delete(test_kind, test_namespace, test_name)
        try:
            helm.test(release_name)
        finally:
            # Grab the logs of any (failed) tests
            for release_test in release_tests:
                test_kind = release_test['kind']
                test_namespace = release_test['metadata'].get('namespace', 'default')
                test_name = release_test['metadata']['name']
                if k8s.exists(test_kind, test_namespace, test_name):
                    test_pod = k8s.get(test_kind, namespace=test_namespace, name=test_name)
                    for test_container in test_pod['spec']['containers']:
                        test_container_name = test_container['name']
                        logger.info('Logs for test pod "{pod}" container "{container}":'.format(pod=test_name, container=test_container_name))
                        k8s.logs(test_name, namespace=test_namespace, container=test_container_name)


def conditional_release_rollback(release_name, start_time):
    """
    Roll a release back to the previous stable version.
    The rollback will only be performed if a revision is found that occurred after a specified start time.
    This allows the user to call this function without certainty that the upgrade was even successfully submitted to Kubernetes.
    Args:
        release: The name of the release to rollback
        start_time: The start time (cut-off time) for which an upgrade must have occurred after for a rollback to happen as a Python datetime
    """
    revision_history = helm.history(release_name)
    latest_revision = revision_history[-1]
    if latest_revision.updated >= start_time:
        for revision in reversed(revision_history[0:-1]):
            if ('SUPERSEDED' in revision.status or 'DEPLOYED' in revision.status) and (
                    'Rollback' in revision.description or 'Upgrade complete' in revision.description or 'Install complete' in revision.description):
                helm.rollback(release_name, revision.revision)
                helm.wait_for_release_resources(release_name)
                break
        else:
            logger.info('Healthy superseded version could not be found to roll back to')
    else:
        logger.info('An upgrade of the release never occurred. Rollback not needed')


def import_certificates(release_name):
    """
    Triggers the import of certificates from Certificate Manager into the Kubernetes cluster if the correct annotations are found on ingress resources.
    Specifically, ingress resources may have an ingress with key "p2paas-certificate" and the value equal to the CRN in Certificate Manager.
    The secret created in Kubernetes will be named as "{namespace-of-ingress}-{name-of-ingress}".
    Args:
        release_name: The name of the release to check for certificate annotations
    """
    cluster_info = None
    manifest = helm.get_manifest(release_name)
    for resource in manifest:
        kind = resource['kind'].lower()
        if kind == 'ingress':
            annotations = resource['metadata'].get('annotations', {})
            certificate_crn = annotations.get('p2paas-certificate')
            if certificate_crn:
                if not cluster_info:
                    cluster_info = json.loads(k8s.get('configmap', 'kube-system', 'cluster-info')['data']['cluster-config.json'])
                certificate_secret_name = '{namespace}.{name}'.format(namespace=resource['metadata'].get('namespace', 'default'), name=resource['metadata']['name'])
                logger.info('Importing certificate "{crn}" as secret "{secret}"'.format(crn=certificate_crn, secret=certificate_secret_name))
                ibmcloud.ks_alb_cert_deploy(cluster_info['cluster_id'], certificate_secret_name, certificate_crn)


def process_chart_deployment(full_chart_reference, chart_version, release_name, namespace, env_settings, enforce_chart_requirements):
    """
    Triggers the deployment of a helm chart into Kubernetes, either an upgrade or clean install.
    It will wait for the install/upgrade to complete and then run run functional tests if applicable.
    The deployment will be rolled back if anything fails.
    Args:
        full_chart_reference: The full reference to the chart to install, including repository, eg. p2paas/p2paas-console-ui
        chart_version: The version of the chart to install
        release_name: The name of the release to install
        namespace: The namespace to install the chart to
        env_settings: Settings to be passed to Helm as substitutions
        enforce_chart_requirements: Whether certain chart requirements should be enforced
    """
    start_time = datetime.now()
    new_install = not helm.list_releases('^{release}$'.format(release=release_name))
    try:
        if new_install:
            logger.info('Installing chart "{chart}-{version}" as release "{release}"'.format(chart=full_chart_reference, version=chart_version, release=release_name))
            helm.install_chart(full_chart_reference, chart_version, env_settings, release_name, namespace, validate_manifest=enforce_chart_requirements)
        else:
            logger.info('Upgrading chart "{chart}-{version}" as release "{release}"'.format(chart=full_chart_reference, version=chart_version, release=release_name))
            helm.upgrade_chart(full_chart_reference, chart_version, env_settings, release_name, namespace)
        helm.wait_for_release_resources(release_name)
        import_certificates(release_name)
        run_release_tests(release_name)
    except Exception as e:
        logger.error(str(e), exc_info=True)
        conditional_release_rollback(release_name, start_time)
        raise
