import json
import os
import unittest
from mock import patch

from orchutils import k8s

pod_output = '''{
    "apiVersion": "v1",
    "kind": "Pod",
    "metadata": {
        "annotations": {
            "kubernetes.io/psp": "ibm-privileged-psp"
        },
        "creationTimestamp": "2019-03-12T14:01:37Z",
        "generateName": "tiller-deploy-5c477df6bf-",
        "labels": {
            "app": "helm",
            "name": "tiller",
            "pod-template-hash": "5c477df6bf"
        },
        "name": "tiller-deploy-5c477df6bf-rsjhp",
        "namespace": "kube-system",
        "ownerReferences": [
            {
                "apiVersion": "apps/v1",
                "blockOwnerDeletion": true,
                "controller": true,
                "kind": "ReplicaSet",
                "name": "tiller-deploy-5c477df6bf",
                "uid": "5a2d3c83-44cf-11e9-adc4-f2af0847707a"
            }
        ],
        "resourceVersion": "71090",
        "selfLink": "/api/v1/namespaces/kube-system/pods/tiller-deploy-5c477df6bf-rsjhp",
        "uid": "5a32ad09-44cf-11e9-adc4-f2af0847707a"
    },
    "spec": {
        "automountServiceAccountToken": true,
        "containers": [
            {
                "command": [
                    "/tiller",
                    "--storage=secret"
                ],
                "env": [
                    {
                        "name": "TILLER_NAMESPACE",
                        "value": "kube-system"
                    },
                    {
                        "name": "TILLER_HISTORY_MAX",
                        "value": "20"
                    }
                ],
                "image": "gcr.io/kubernetes-helm/tiller:v2.13.0",
                "imagePullPolicy": "IfNotPresent",
                "livenessProbe": {
                    "failureThreshold": 3,
                    "httpGet": {
                        "path": "/liveness",
                        "port": 44135,
                        "scheme": "HTTP"
                    },
                    "initialDelaySeconds": 1,
                    "periodSeconds": 10,
                    "successThreshold": 1,
                    "timeoutSeconds": 1
                },
                "name": "tiller",
                "ports": [
                    {
                        "containerPort": 44134,
                        "name": "tiller",
                        "protocol": "TCP"
                    },
                    {
                        "containerPort": 44135,
                        "name": "http",
                        "protocol": "TCP"
                    }
                ],
                "readinessProbe": {
                    "failureThreshold": 3,
                    "httpGet": {
                        "path": "/readiness",
                        "port": 44135,
                        "scheme": "HTTP"
                    },
                    "initialDelaySeconds": 1,
                    "periodSeconds": 10,
                    "successThreshold": 1,
                    "timeoutSeconds": 1
                },
                "resources": {},
                "terminationMessagePath": "/dev/termination-log",
                "terminationMessagePolicy": "File",
                "volumeMounts": [
                    {
                        "mountPath": "/var/run/secrets/kubernetes.io/serviceaccount",
                        "name": "tiller-token-wtkgc",
                        "readOnly": true
                    }
                ]
            }
        ],
        "dnsPolicy": "ClusterFirst",
        "enableServiceLinks": true,
        "nodeName": "10.168.137.60",
        "priority": 0,
        "restartPolicy": "Always",
        "schedulerName": "default-scheduler",
        "securityContext": {},
        "serviceAccount": "tiller",
        "serviceAccountName": "tiller",
        "terminationGracePeriodSeconds": 30,
        "tolerations": [
            {
                "effect": "NoExecute",
                "key": "node.kubernetes.io/not-ready",
                "operator": "Exists",
                "tolerationSeconds": 300
            },
            {
                "effect": "NoExecute",
                "key": "node.kubernetes.io/unreachable",
                "operator": "Exists",
                "tolerationSeconds": 300
            }
        ],
        "volumes": [
            {
                "name": "tiller-token-wtkgc",
                "secret": {
                    "defaultMode": 420,
                    "secretName": "tiller-token-wtkgc"
                }
            }
        ]
    },
    "status": {
        "conditions": [
            {
                "lastProbeTime": null,
                "lastTransitionTime": "2019-03-12T14:01:37Z",
                "status": "True",
                "type": "Initialized"
            },
            {
                "lastProbeTime": null,
                "lastTransitionTime": "2019-03-12T14:01:47Z",
                "status": "True",
                "type": "Ready"
            },
            {
                "lastProbeTime": null,
                "lastTransitionTime": "2019-03-12T14:01:47Z",
                "status": "True",
                "type": "ContainersReady"
            },
            {
                "lastProbeTime": null,
                "lastTransitionTime": "2019-03-12T14:01:37Z",
                "status": "True",
                "type": "PodScheduled"
            }
        ],
        "containerStatuses": [
            {
                "containerID": "containerd://f783f2cf95da36e6daf952ce80568296385b5706fec17085991ce8710ad0db87",
                "image": "gcr.io/kubernetes-helm/tiller:v2.13.0",
                "imageID": "gcr.io/kubernetes-helm/tiller@sha256:c4bf03bb67b3ae07e38e834f29dc7fd43f472f67cad3c078279ff1bbbb463aa6",
                "lastState": {},
                "name": "tiller",
                "ready": true,
                "restartCount": 0,
                "state": {
                    "running": {
                        "startedAt": "2019-03-12T14:01:41Z"
                    }
                }
            }
        ],
        "hostIP": "10.168.137.60",
        "phase": "Running",
        "podIP": "172.30.68.129",
        "qosClass": "BestEffort",
        "startTime": "2019-03-12T14:01:37Z"
    }
}'''


class TestK8s(unittest.TestCase):
    @patch('baseutils.exe_cmd')
    def test_apply(self, mock_exe_cmd):
        mock_exe_cmd.return_value = (0, '')
        self.assertIsNone(k8s.apply({}))

    @patch('baseutils.exe_cmd')
    def test_cordon(self, mock_exe_cmd):
        mock_exe_cmd.return_value = (0, '')
        self.assertIsNone(k8s.cordon(node='node'))
        self.assertEqual(1, mock_exe_cmd.call_count)
        self.assertIn(' cordon \'node\'', mock_exe_cmd.call_args[0][0])
        self.assertNotIn('-l', mock_exe_cmd.call_args[0][0])
        self.assertIsNone(k8s.cordon(labels={'dedicated': 'edge'}))
        self.assertEqual(2, mock_exe_cmd.call_count)
        self.assertIn(' -l \'dedicated=edge\'', mock_exe_cmd.call_args[0][0])
        self.assertNotIn('\'node\'', mock_exe_cmd.call_args[0][0])
        self.assertIsNone(k8s.cordon(labels='key=value'))
        self.assertEqual(3, mock_exe_cmd.call_count)
        self.assertIn(' cordon  -l \'key=value\'', mock_exe_cmd.call_args[0][0])

    @patch('baseutils.exe_cmd')
    def test_delete(self, mock_exe_cmd):
        mock_exe_cmd.return_value = (0, '')
        self.assertIsNone(k8s.delete('clusterrolebinding'))
        self.assertIsNone(k8s.delete('deployment', namespace='ns'))
        self.assertIsNone(k8s.delete('serviceaccount', name='name'))
        self.assertIsNone(k8s.delete('pod', name='name', wait=False))
        self.assertIsNone(k8s.delete('pod', name='name', grace_period='5'))
        self.assertIsNone(k8s.delete('pod', namespace='ns', name='name', wait=True, grace_period='-1'))

    @patch('baseutils.exe_cmd')
    def test_describe(self, mock_exe_cmd):
        expected_result = 'human readable output'
        mock_exe_cmd.return_value = (0, expected_result)
        self.assertEqual(expected_result, k8s.describe('clusterrolebinding'))
        self.assertEqual(expected_result, k8s.describe('deployment', namespace='kube-config'))
        self.assertEqual(expected_result, k8s.describe('pod', namespace='all'))
        self.assertEqual(expected_result, k8s.describe('serviceaccount', name='name'))
        self.assertEqual(expected_result, k8s.describe('pod', name='name', namespace='kube-config'))
        self.assertEqual(expected_result, k8s.describe('node', name='name', labels='dedicated=edge'))
        self.assertEqual(expected_result, k8s.describe('node', name='name', labels={'dedicated': 'edge', 'key2': 'label2'}))

    @patch('baseutils.exe_cmd')
    def test_drain(self, mock_exe_cmd):
        mock_exe_cmd.return_value = (0, '')
        self.assertIsNone(k8s.drain('10.1.5.1'))
        self.assertIsNone(k8s.drain('10.1.5.1', force=False))
        self.assertIsNone(k8s.drain('10.1.5.1', delete_local_data=False))
        self.assertIsNone(k8s.drain('10.1.5.1', force=True, delete_local_data=False))
        self.assertIsNone(k8s.drain('10.1.5.1', ignore_daemonsets=False))
        self.assertIsNone(k8s.drain('10.1.5.1', force=False, ignore_daemonsets=False))
        self.assertIsNone(k8s.drain('10.1.5.1', force=False, delete_local_data=False, ignore_daemonsets=False))

    @patch('baseutils.exe_cmd')
    def test_exists(self, mock_exe_cmd):
        mock_exe_cmd.return_value = (0, '{"items": [], "kind": "List"}')
        self.assertEqual(False, k8s.exists('Pod', 'name', 'ns'))
        mock_exe_cmd.return_value = (0, '{{"items": [{pod}], "kind": "List"}}'.format(pod=pod_output))
        self.assertEqual(False, k8s.exists('Pod', 'name', 'kube-system'))
        self.assertEqual(True, k8s.exists('Pod', 'kube-system', 'tiller-deploy-5c477df6bf-rsjhp'))

    @patch('baseutils.exe_cmd')
    def test_get(self, mock_exe_cmd):
        mock_exe_cmd.return_value = (0, '{"items": [], "kind": "List"}')
        self.assertEqual([], k8s.get('clusterrolebinding'))
        self.assertEqual([], k8s.get('deployment', namespace='kube-config'))
        self.assertEqual([], k8s.get('pod', namespace='all'))
        mock_exe_cmd.return_value = (0, '{}')
        self.assertEqual({}, k8s.get('serviceaccount', name='name'))
        self.assertEqual({}, k8s.get('pod', name='name', namespace='kube-config'))
        self.assertEqual({}, k8s.get('node', name='name', labels='dedicated=edge'))
        self.assertEqual({}, k8s.get('node', name='name', labels={'dedicated': 'edge', 'key2': 'label2'}))
        mock_exe_cmd.return_value = (0, pod_output)
        self.assertEqual(json.loads(pod_output), k8s.get('Pod', name='tiller-deploy-5c477df6bf-rsjhp'))

    @patch('baseutils.exe_cmd')
    def test_label(self, mock_exe_cmd):
        mock_exe_cmd.return_value = (0, '')
        self.assertIsNone(k8s.label('kubernetes.io/label=mylabel', 'node'))
        self.assertIsNone(k8s.label('kubernetes.io/label=mylabel', 'node', name='mynode'))
        self.assertIsNone(k8s.label('kubernetes.io/label=mylabel', 'pod', namespace='ns', name='mynode'))

    @patch('baseutils.exe_cmd')
    def test_logs(self, mock_exe_cmd):
        expected_result = 'human readable logs'
        mock_exe_cmd.return_value = (0, expected_result)
        self.assertEqual(expected_result, k8s.logs('pod-name'))
        self.assertEqual(expected_result, k8s.logs('pod-name', namespace='kube-config'))
        self.assertEqual(expected_result, k8s.logs('pod-name', container='container'))
        self.assertEqual(expected_result, k8s.logs('pod-name', container='container', namespace='kube-config'))

    @patch('baseutils.exe_cmd')
    def test_rollout_status(self, mock_exe_cmd):
        successful_output = 'statefulset rolling update complete 4 pods at revision governor-cassandra-74897547b...'
        mock_exe_cmd.return_value = (0, successful_output)
        self.assertEqual(successful_output, k8s.rollout_status('statefulset', 'my-sts'))
        failed_output = 'error: Status is available only for RollingUpdate strategy type'
        mock_exe_cmd.return_value = (1, failed_output)
        with self.assertRaises(Exception) as raises_cm:
            k8s.rollout_status('statefulset', 'my-sts')
        self.assertEqual(failed_output, str(raises_cm.exception))

    @patch('baseutils.exe_cmd')
    def test_taint(self, mock_exe_cmd):
        mock_exe_cmd.return_value = (0, '')
        self.assertIsNone(k8s.taint(['key1=v1:taint1'], node='node'))
        self.assertEqual(1, mock_exe_cmd.call_count)
        self.assertIn(' taint node \'node\' ', mock_exe_cmd.call_args[0][0])
        self.assertNotIn('-l', mock_exe_cmd.call_args[0][0])
        self.assertIsNone(k8s.taint(['key1=v1:taint1', 'key2=v2:taint2'], node='node'))
        self.assertEqual(2, mock_exe_cmd.call_count)
        self.assertIn(' \'key1=v1:taint1\' \'key2=v2:taint2\'', mock_exe_cmd.call_args[0][0])
        self.assertIsNone(k8s.taint(['key1=v1:taint1'], labels={'dedicated': 'edge'}))
        self.assertEqual(3, mock_exe_cmd.call_count)
        self.assertIn(' -l \'dedicated=edge\' ', mock_exe_cmd.call_args[0][0])
        self.assertNotIn('\'node\'', mock_exe_cmd.call_args[0][0])
        self.assertIsNone(k8s.taint(['key1=v1:taint1'], labels='key=value'))
        self.assertEqual(4, mock_exe_cmd.call_count)
        self.assertIn('taint node  -l \'key=value\' ', mock_exe_cmd.call_args[0][0])

    @patch('baseutils.exe_cmd')
    def test_uncordon(self, mock_exe_cmd):
        mock_exe_cmd.return_value = (0, '')
        self.assertIsNone(k8s.uncordon(node='node'))
        self.assertEqual(1, mock_exe_cmd.call_count)
        self.assertIn(' uncordon \'node\'', mock_exe_cmd.call_args[0][0])
        self.assertNotIn('-l', mock_exe_cmd.call_args[0][0])
        self.assertIsNone(k8s.uncordon(labels={'dedicated': 'edge'}))
        self.assertEqual(2, mock_exe_cmd.call_count)
        self.assertIn(' -l \'dedicated=edge\'', mock_exe_cmd.call_args[0][0])
        self.assertNotIn('\'node\'', mock_exe_cmd.call_args[0][0])
        self.assertIsNone(k8s.uncordon(labels='key=value'))
        self.assertEqual(3, mock_exe_cmd.call_count)
        self.assertIn(' uncordon  -l \'key=value\'', mock_exe_cmd.call_args[0][0])

    def test_install_kubectl(self):
        if os.name != 'nt':  # This is windows-specific and will not work on linux. No point attempting the test on windows
            original_kubectl_binary = k8s.kubectl_binary
            k8s.kubectl_binary = '/tmp/kubectl'
            self.assertIsNone(k8s.install_kubectl('v1.12.6'))  # Download new
            self.assertIsNone(k8s.install_kubectl('v1.12.6'))  # Second call should be a no-op
            os.remove(k8s.kubectl_binary)
            k8s.kubectl_binary = original_kubectl_binary


if __name__ == '__main__':
    unittest.main()
