import json
import os
import signal
import unittest
import yaml
from mock import Mock
from mock import patch

from orchutils import helm
from helmmodels.test_releaserevision import revisions_json

valid_manifest = '''
# Source: p2paas-console-ui/templates/service.yaml
apiVersion: "v1"
kind: "Service"
metadata:
  name: "p2paas-console-ui"
  namespace: "console"
spec:
  ports:
    - name: "p2paas-console-ui"
      protocol: "TCP"
      port: 443
      targetPort: 4443
  type: "ClusterIP"
  selector:
    name: "p2paas-console-ui"
---
# Source: p2paas-console-ui/templates/deployment.yaml
apiVersion: "apps/v1"
kind: "Deployment"
metadata:
  name: "p2paas-console-ui"
  namespace: "console"
spec:
  replicas: 3
  template:
    metadata:
      name: "p2paas-console-ui"
      labels:
        name: "p2paas-console-ui"
    spec:
      containers:
      - name: "p2paas-console-ui"
        image: "registry.ng.bluemix.net/p2paas-platform-arch/p2paas-console-ui:1.20190213.81"
        imagePullPolicy: "Always"
        ports:
        - containerPort: 4443
        resources:
          requests:
            memory: "400Mi"
            cpu: "600m"
          limits:
            memory: "600Mi"
            cpu: "800m"
        env:
        - name: "ENVIRONMENT_NAME"
          value: "sbx-orch"
        - name: "FLASK_APP_SECRET"
          valueFrom:
            secretKeyRef:
              name: "p2paas-console-ui"
              key: "flaskAppSecret"
        - name: "OAUTH2_CLIENT_ID"
          value: "NzU1MmI5ODUtY2Q3Zi00"
        - name: "OAUTH2_CLIENT_SECRET"
          valueFrom:
            secretKeyRef:
              name: "p2paas-console-ui"
              key: "oauth2ClientSecret"
        livenessProbe:
          httpGet:
            path: "/healthz-saBzb58uiXKhaqw"
            port: 4443
            scheme: "HTTPS"
          initialDelaySeconds: 60
          timeoutSeconds: 3
          periodSeconds: 15
        readinessProbe:
          httpGet:
            path: "/healthz-saBzb58uiXKhaqw"
            port: 4443
            scheme: "HTTPS"
          initialDelaySeconds: 60
          timeoutSeconds: 3
          periodSeconds: 15
        lifecycle:
          preStop:
            exec:
              command: ["sleep", "15"]'''

release_hooks = '''
---
# ibmcloud-object-storage-driver-test
apiVersion: v1
kind: Pod
metadata:
  name: ibmcloud-object-storage-driver-test
  namespace: kube-system
  labels:
    #app: ibmcloud-object-storage-driver-test
    app: ibmcloud-object-storage-driver-test
    chart: ibmcloud-object-storage-plugin-1.0.3-beta
    release: ibmcloud-object-storage-plugin
    heritage: Tiller
  annotations:
    "helm.sh/hook": test-success
spec:
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
        - matchExpressions:
          - key: beta.kubernetes.io/arch
            operator: In
            values:
            - amd64
  tolerations:
  - operator: "Exists"
  serviceAccountName: ibmcloud-object-storage-driver
  containers:
    - name: ibmcloud-object-storage-driver-test
      image: "nkkashyap/ibmcloud-object-storage-driver:1.8.3beta"
      imagePullPolicy: Always
      command: ["sh", "-c", 'version1=$(cat /home/s3-dep/version.txt | head -n 2 | tail -n 1);
        version2=$(/host/kubernetes/kubelet-plugins/volume/exec/ibm~ibmc-s3fs/ibmc-s3fs version);
        if [[ "$version1" == "$version2" ]]; then exit 0; else exit 1; fi']
      volumeMounts:
         - mountPath: /host/kubernetes
           name: kube-driver
  restartPolicy: Never
  volumes:
    - name: kube-driver
      hostPath:
         path: /usr/libexec/kubernetes
'''


class TestHelm(unittest.TestCase):
    def test_set_helm_home(self):
        helm_home = '/helm/home'
        self.assertFalse('HELM_HOME' in os.environ)
        self.assertIsNone(helm.set_helm_home(helm_home))
        self.assertEqual(helm_home, os.environ['HELM_HOME'])
        del os.environ['HELM_HOME']

    @patch('baseutils.exe_cmd')
    def test_add_repo(self, mock_exe_cmd):
        self.assertIsNone(helm.add_repo('name', 'user', 'pass'))
        self.assertEqual(2, mock_exe_cmd.call_count)
        self.assertIsNone(helm.add_repo('name', 'user', 'pass', 'url'))
        self.assertEqual(4, mock_exe_cmd.call_count)

    @patch('baseutils.exe_cmd')
    def test_delete(self, mock_exe_cmd):
        self.assertIsNone(helm.delete('release_name'))
        self.assertEqual(1, mock_exe_cmd.call_count)
        self.assertEqual('{helm} delete \'release_name\' --purge'.format(helm=helm.helm_binary), mock_exe_cmd.call_args_list[0][0][0])
        self.assertIsNone(helm.delete('release_name', purge=True))
        self.assertEqual(2, mock_exe_cmd.call_count)
        self.assertEqual('{helm} delete \'release_name\' --purge'.format(helm=helm.helm_binary), mock_exe_cmd.call_args_list[1][0][0])
        self.assertIsNone(helm.delete('release_name', purge=False))
        self.assertEqual(3, mock_exe_cmd.call_count)
        self.assertEqual('{helm} delete \'release_name\' '.format(helm=helm.helm_binary), mock_exe_cmd.call_args_list[2][0][0])

    @patch('baseutils.exe_cmd')
    def test_update_repos(self, mock_exe_cmd):
        self.assertIsNone(helm.update_repos())
        self.assertEqual(1, mock_exe_cmd.call_count)

    @patch('baseutils.exe_cmd')
    def test_install_chart(self, mock_exe_cmd):
        mock_exe_cmd.return_value = (0, valid_manifest)
        self.assertIsNone(helm.install_chart('chart', 'version', {'v1': 'k1'}, 'release', 'namespace'))
        self.assertEqual(2, mock_exe_cmd.call_count)
        self.assertIsNone(helm.install_chart('chart', 'version', {'v1': 'k1'}, 'release', 'namespace', False, True, True))
        self.assertEqual(4, mock_exe_cmd.call_count)
        mock_exe_cmd.return_value = (1, 'parsing error message')
        with self.assertRaises(Exception) as context:
            with patch('orchutils.helm.logger.error'):  # The client code logs the error before raising. This can cause confusion as it appears like an error
                helm.install_chart('chart', 'version', {'v1': 'k1'}, 'release', 'namespace', False, True, True)
        self.assertEqual('Failed to parse Helm template. parsing error message', str(context.exception))

    @patch('baseutils.exe_cmd')
    def test_upgrade_chart(self, mock_exe_cmd):
        self.assertIsNone(helm.upgrade_chart('chart', 'version', {'v1': 'k1'}, 'release', 'namespace'))
        self.assertEqual(1, mock_exe_cmd.call_count)
        self.assertIsNone(helm.upgrade_chart('chart', 'version', {'v1': 'k1'}, 'release', 'namespace', True, True))
        self.assertEqual(2, mock_exe_cmd.call_count)

    @patch('baseutils.exe_cmd')
    def test_attempt_chart_deploy(self, mock_exe_cmd):
        self.assertIsNone(helm._attempt_chart_deploy('cmd'))
        self.assertEqual(1, mock_exe_cmd.call_count)
        mock_exe_cmd.side_effect = [Exception('')]
        self.assertRaises(Exception, helm._attempt_chart_deploy, 'cmd')
        with patch('time.sleep') as mock_sleep:
            mock_exe_cmd.side_effect = [
                Exception('Could not get apiVersions from Kubernetes: unable to retrieve the complete list of server APIs'),
                (0, '')
            ]
            self.assertIsNone(helm._attempt_chart_deploy('cmd'))
            self.assertEqual(4, mock_exe_cmd.call_count)
            self.assertEqual(1, mock_sleep.call_count)

    def test_create_values_file(self):
        expected_result = {'k1': 'v1', 'k2': ['v2']}
        path_to_file = helm.create_values_file(expected_result)
        with open(path_to_file, 'r') as fh:
            actual_result = yaml.safe_load(fh)
        self.assertEqual(expected_result, actual_result)
        os.remove(path_to_file)

    @patch('baseutils.exe_cmd')
    def test_list_releases(self, mock_exe_cmd):
        expected_result = '''NAME            REVISION        UPDATED                         STATUS          CHART                           NAMESPACE
governor-www    56              Tue Oct  3 13:01:33 2017        DEPLOYED        governor-www-1.20171003.54      default'''
        mock_exe_cmd.return_value = (0, expected_result)
        self.assertEqual(expected_result, helm.list_releases())

    @patch('baseutils.exe_cmd')
    def test_search_charts(self, mock_exe_cmd):
        expected_result = '''NAME                           CHART VERSION   APP VERSION     DESCRIPTION
p2paas/p2paas-console-ui       1.20190222.13                   The p2paas-console-ui service exposes self-service capabi...'''
        mock_exe_cmd.return_value = (0, expected_result)
        self.assertEqual(expected_result, helm.search_charts('p2paas/p2paas-console-ui'))

    @patch('baseutils.exe_cmd')
    def test_get_latest_chart_version(self, mock_exe_cmd):
        expected_result = '1.20190222.13'
        mock_exe_cmd.return_value = (0, '''NAME                           CHART VERSION   APP VERSION     DESCRIPTION
p2paas/p2paas-console-ui       {version}                   The p2paas-console-ui service exposes self-service capabi...'''.format(version=expected_result))
        self.assertEqual(expected_result, helm.get_latest_chart_version('p2paas/p2paas-console-ui'))
        mock_exe_cmd.return_value = (0, '')
        self.assertRaises(Exception, helm.get_latest_chart_version, 'p2paas/p2paas-console-ui')

    def test_validate_manifest_requirements(self):
        self.assertEqual(0, len(helm.validate_manifest_requirements(valid_manifest)))
        bad_manifest = valid_manifest.replace('ENVIRONMENT_NAME', 'ENVIRONMENT_SECRET').replace('livenessProbe', 'livenessDisabledProbe')
        self.assertEqual(2, len(helm.validate_manifest_requirements(bad_manifest)))
        bad_manifest = valid_manifest.replace('resources', 'resourcesDisabled').replace('replicas: 3', 'replicas: 2')
        self.assertEqual(2, len(helm.validate_manifest_requirements(bad_manifest)))
        bad_manifest = valid_manifest.replace('targetPort: 4443', 'nodePort: 32001')
        self.assertEqual(1, len(helm.validate_manifest_requirements(bad_manifest)))

    def test_validate_manifest_resources(self):
        manifests = yaml.safe_load_all(valid_manifest)
        for manifest in manifests:
            if manifest['kind'] == 'Deployment':
                break
        container = manifest['spec']['template']['spec']['containers'][0]
        errors = []
        helm._validate_manifest_resources('kind', 'name', container, errors)
        self.assertEqual(0, len(errors))
        del container['resources']['requests']['memory']
        errors = []
        helm._validate_manifest_resources('kind', 'name', container, errors)
        self.assertEqual(1, len(errors))

    def test_validate_manifest_envvars(self):
        manifests = yaml.safe_load_all(valid_manifest)
        for manifest in manifests:
            if manifest['kind'] == 'Deployment':
                break
        envvars = manifest['spec']['template']['spec']['containers'][0]['env']
        errors = []
        helm._validate_manifest_envvars('kind', 'name', envvars, errors)
        self.assertEqual(0, len(errors))
        envvars[0]['name'] = 'ENV_SECRET'
        errors = []
        helm._validate_manifest_envvars('kind', 'name', envvars, errors)
        self.assertEqual(1, len(errors))
        envvars[0]['name'] = 'ENV_PASS'
        errors = []
        helm._validate_manifest_envvars('kind', 'name', envvars, errors)
        self.assertEqual(1, len(errors))
        envvars[0]['name'] = 'ENV_PW'
        errors = []
        helm._validate_manifest_envvars('kind', 'name', envvars, errors)
        self.assertEqual(1, len(errors))

    @patch('baseutils.exe_cmd')
    def test_get_max_replicas_count_in_manifest(self, mock_exe_cmd):
        manifest = list(yaml.safe_load_all(valid_manifest))
        self.assertEqual(3, helm.get_max_replicas_count_in_manifest(manifest))

    @patch('baseutils.exe_cmd')
    def test_get_manifest(self, mock_exe_cmd):
        mock_exe_cmd.return_value = (0, valid_manifest)
        expected_result = list(yaml.safe_load_all(valid_manifest))
        self.assertEqual(expected_result, helm.get_manifest('release_name'))

    @patch('baseutils.exe_cmd')
    def test_get_hooks(self, mock_exe_cmd):
        mock_exe_cmd.return_value = (0, release_hooks)
        hooks = list(yaml.safe_load_all(release_hooks))
        self.assertEqual(hooks, helm.get_hooks('release_name'))
        self.assertEqual(1, mock_exe_cmd.call_count)
        self.assertEqual(hooks, helm.get_hooks('release_name', resource_types=['Pod']))
        self.assertEqual([], helm.get_hooks('release_name', resource_types=['resource_type']))
        self.assertEqual(hooks, helm.get_hooks('release_name', hook_types=['test-success']))
        self.assertEqual(hooks, helm.get_hooks('release_name', resource_types=['Pod'], hook_types=['test-success']))

    @patch('baseutils.exe_cmd')
    def test_history(self, mock_exe_cmd):
        mock_exe_cmd.return_value = (0, json.dumps(revisions_json))
        revisions = helm.history('release_name')
        self.assertEqual(len(revisions_json), len(revisions))
        self.assertEqual(revisions_json[0]['chart'], revisions[0].chart)
        self.assertEqual(revisions_json[1]['revision'], revisions[1].revision)

    @patch('baseutils.exe_cmd')
    def test_rollback(self, mock_exe_cmd):
        mock_exe_cmd.return_value = (0, '')
        self.assertIsNone(helm.rollback('release', 10))
        self.assertIsNone(helm.rollback('release', '10'))

    @patch('baseutils.exe_cmd')
    def test_test(self, mock_exe_cmd):
        mock_exe_cmd.return_value = (0, '')
        self.assertIsNone(helm.test('release_name'))
        self.assertIsNone(helm.test('release_name', seconds=10))

    @patch('baseutils.exe_cmd')
    def test_get_tiller_version(self, mock_exe_cmd):
        expected_value = 'v2.12.3'
        cmd_return = {
            'spec': {
                'template': {
                    'spec': {
                        'containers': [{'image': 'gcr.io/kubernetes-helm/tiller:{version}'.format(version=expected_value)}]
                    }
                }
            }
        }
        mock_exe_cmd.return_value = (0, json.dumps(cmd_return))
        self.assertEqual(expected_value, helm.get_tiller_version())

    @patch('baseutils.exe_cmd')
    def test_wait_for_release_resources(self, mock_exe_cmd):
        if os.name == 'nt':
            signal.SIGALRM = signal.SIGTERM
            signal.alarm = Mock()
        mock_exe_cmd.side_effect = [
            (0, valid_manifest),
            (0, 'deployment "p2paas-console-ui" successfully rolled out'),
            (0, '{"spec": {"selector": {"matchLabels": {"my-label": "myvalue"}}}, "metadata": {"annotations": {"deployment.kubernetes.io/revision": "2"}}}'),
            (0, '{"items": [{"kind": "ReplicaSet", "spec": {"selector": {"matchLabels": {"my-label": "myvalue"}}}, ' +
                '"metadata": {"annotations": {"deployment.kubernetes.io/revision": "2"}}}],"kind": "List"}'),
            (0, '{"items": [], "kind": "List"}')
        ]
        self.assertIsNone(helm.wait_for_release_resources('release_name'))
        self.assertEqual(5, mock_exe_cmd.call_count)
        mock_exe_cmd.side_effect = [
            (0, valid_manifest),
            (1, 'Status is available only for RollingUpdate strategy type')
        ]
        self.assertIsNone(helm.wait_for_release_resources('release_name'))
        if os.name == 'nt':
            del signal.SIGALRM
            del signal.alarm

    @patch('baseutils.exe_cmd')
    def test_check_for_resource_pod_errors(self, mock_exe_cmd):
        mock_exe_cmd.side_effect = [
            (0, '{"spec": {"selector": {"matchLabels": {"my-label": "myvalue"}}}, "metadata": {"generation": "12"}}'),
            (0, '{"items": [{"metadata": {"name": "myname"}, "status": {}}], "kind": "List"}')
        ]
        self.assertIsNone(helm._check_for_resource_pod_errors('daemonset', 'namespace', 'name'))
        mock_exe_cmd.side_effect = [
            (0, '{"spec": {"selector": {"matchLabels": {"my-label": "myvalue"}}}, "metadata": {"generation": "12"}}'),
            (0, '{"items": [{"metadata": {"name": "myname"}, "status": {"containerStatuses": [{"state": {"waiting": {"reason": "waiting"}}}]}}], "kind": "List"}')
        ]
        self.assertIsNone(helm._check_for_resource_pod_errors('daemonset', 'namespace', 'name'))
        mock_exe_cmd.side_effect = [
            (0, '{"spec": {"selector": {"matchLabels": {"my-label": "myvalue"}}}, "metadata": {"generation": "12"}}'),
            (0, '{"items": [{"metadata": {"name": "n"}, "status": {"containerStatuses": [{"name": "c", "state": {"waiting": {"reason": "ErrImagePull"}}}]}}], "kind": "List"}')
        ]
        self.assertRaises(Exception, helm._check_for_resource_pod_errors, 'daemonset', 'namespace', 'name')
        mock_exe_cmd.side_effect = [
            (0, '{"spec": {"selector": {"matchLabels": {"my-label": "myvalue"}}}, "status": {"updateRevision": "rev"}}'),
            (0, '{"items": [{"metadata": {"name": "myname"}, "status": {"containerStatuses": [{"state": {"terminated": {"reason": "waiting"}}}]}}], "kind": "List"}'),
            (0, 'describe'),
            (0, 'log')
        ]
        self.assertIsNone(helm._check_for_resource_pod_errors('statefulset', 'namespace', 'name'))
        mock_exe_cmd.side_effect = [
            (0, '{"spec": {"selector": {"matchLabels": {"my-label": "myvalue"}}}, "status": {"updateRevision": "rev"}}'),
            (0, '{"items": [{"metadata": {"name": "n"}, "status": {"containerStatuses": [{"name": "c", "restartCount": 1, "state": {}}]}}], "kind": "List"}'),
            (0, 'describe'),
            (0, 'log')
        ]
        self.assertRaises(Exception, helm._check_for_resource_pod_errors, 'statefulset', 'namespace', 'name')
        mock_exe_cmd.side_effect = [
            (0, '{"spec": {"selector": {"matchLabels": {"my-label": "myvalue"}}}, "metadata": {"annotations": {"deployment.kubernetes.io/revision": "2"}}}'),
            (0, '{"items": [{"kind": "ReplicaSet", "spec": {"selector": {"matchLabels": {"my-label": "myvalue"}}}, ' +
                '"metadata": {"annotations": {"deployment.kubernetes.io/revision": "2"}}}], "kind": "List"}'),
            (0, '{"items": [{"metadata": {"name": "myname", "annotations": {"deployment.kubernetes.io/revision": "1.0.0"}}, ' +
                '"status": {"containerStatuses": [{"state": {}}]}}], "kind": "List"}')
        ]
        self.assertIsNone(helm._check_for_resource_pod_errors('deployment', 'namespace', 'name'))

    @patch('baseutils.exe_cmd')
    @patch('os.rename')
    @patch('os.chmod')
    def test_install_helm(self, mock_chmod, mock_rename, mock_exe_cmd):
        mock_exe_cmd.side_effect = [(0, 'v2.1.2'), (0, 'v2.1.2,v2.1.2'), (0, '')]
        self.assertIsNone(helm.install_helm('v2.1.2'))
        self.assertEqual(3, mock_exe_cmd.call_count)
        helm.helm_binary = '/tmp/helm'
        mock_exe_cmd.side_effect = [(0, 'v2.1.2'), (0, ''), (0, ''), (1, 'v2.1.1'),
                                    (0, '{"items": [{"metadata": {"name": "tiller"}}], "kind": "List"}'),
                                    (0, '{"items": [{"metadata": {"name": "tiller"}}], "kind": "List"}'), (0, '')]
        self.assertIsNone(helm.install_helm('v2.1.1'))
        self.assertEqual(10, mock_exe_cmd.call_count)
        mock_exe_cmd.side_effect = [(0, 'v2.1.2'), (0, ''), (0, ''), (1, 'v2.1.1'),
                                    (0, '{"items": [{"metadata": {"name": "nontiller"}}], "kind": "List"}'), (0, ''),
                                    (1, '{"items": [{"metadata": {"name": "nontiller"}}], "kind": "List"}'), (0, ''), (0, '')]
        self.assertIsNone(helm.install_helm('v2.1.1'))
        self.assertEqual(19, mock_exe_cmd.call_count)
        mock_exe_cmd.side_effect = [(0, 'v2.1.2'), (0, ''), (0, ''), (0, 'v2.1.1,v2.1.2'), (0, '')]
        self.assertIsNone(helm.install_helm('v2.1.1'))
        self.assertEqual(24, mock_exe_cmd.call_count)

    @patch('baseutils.exe_cmd')
    def test_upgrade_tiller(self, mock_exe_cmd):
        mock_exe_cmd.side_effect = [(0, '''
Client: v2.15.1+gcf1de4f
Server: v2.15.1+gcf1de4f''')]
        self.assertIsNone(helm.upgrade_tiller('kube-system'))
        self.assertEqual(1, mock_exe_cmd.call_count)
        self.assertIn('-tiller-namespace \'kube-system\'', mock_exe_cmd.call_args_list[0][0][0])
        mock_exe_cmd.side_effect = [(0, '''
Client: v2.15.1+gcf1de4f
Server: v2.15.0'''), (0, '''
{
    "apiVersion": "extensions/v1beta1",
    "kind": "Deployment",
    "metadata": {
        "name": "tiller-deploy",
        "namespace": "namespace"
    },
    "spec": {
        "template": {
            "spec": {
                "containers": [
                    {
                        "command": [
                            "/tiller",
                            "--storage=secret"
                        ]
                    }
                ],
                "serviceAccount": "tiller",
                "serviceAccountName": "tiller"
            }
        }
    }
}'''), (0, '')]
        self.assertIsNone(helm.upgrade_tiller('namespace'))
        self.assertEqual(4, mock_exe_cmd.call_count)
        self.assertIn('-n \'namespace\'', mock_exe_cmd.call_args_list[2][0][0])
        self.assertIn('--tiller-namespace \'namespace\'', mock_exe_cmd.call_args_list[3][0][0])
        self.assertIn('--service-account \'tiller\'', mock_exe_cmd.call_args_list[3][0][0])
        self.assertIn('--override \'"spec.template.spec.containers[0].command"="{{/tiller,--storage=secret}}"\'', mock_exe_cmd.call_args_list[3][0][0])
        mock_exe_cmd.side_effect = [(0, '''
Client: v2.15.1+gcf1de4f
Server: v2.15.0'''), (0, '''
{
    "apiVersion": "extensions/v1beta1",
    "kind": "Deployment",
    "metadata": {
        "name": "tiller-deploy",
        "namespace": "ns"
    },
    "spec": {
        "template": {
            "spec": {
                "containers": [
                    {
                    }
                ],
                "serviceAccount": "tiller-ac",
                "serviceAccountName": "tiller-ac"
            }
        }
    }
}'''), (0, '')]
        self.assertIsNone(helm.upgrade_tiller('ns'))
        self.assertEqual(7, mock_exe_cmd.call_count)
        self.assertIn('--tiller-namespace \'ns\'', mock_exe_cmd.call_args_list[6][0][0])
        self.assertIn('--service-account \'tiller-ac\'', mock_exe_cmd.call_args_list[6][0][0])
        self.assertNotIn('--override', mock_exe_cmd.call_args_list[6][0][0])


if __name__ == '__main__':
    unittest.main()
