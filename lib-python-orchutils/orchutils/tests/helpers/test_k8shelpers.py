import json
import os
import signal
import unittest
from mock import patch
from mock import Mock

from orchutils.helpers import k8shelpers

autoscaler_cm_output = r'''{
    "apiVersion": "v1",
    "data": {
        "workerPoolsConfig.json": "[{\"name\": \"default\", \"minSize\": 3, \"maxSize\": 12, \"enabled\": true }]\n"
    },
    "kind": "ConfigMap",
    "metadata": {
        "annotations": {
            "workerPoolsConfigStatus": "{\"3:12:default\":\"SUCCESS\"}"
        },
        "creationTimestamp": "2019-06-19T19:59:37Z",
        "name": "iks-ca-configmap",
        "namespace": "kube-system",
        "resourceVersion": "29630997",
        "selfLink": "/api/v1/namespaces/kube-system/configmaps/iks-ca-configmap",
        "uid": "c3f937c4-92cc-11e9-8701-7663a391f182"
    }
}'''

recovery_tool_cm_output = r'''{
    "kind": "ConfigMap",
    "metadata": {
        "name": "ibm-worker-recovery-checks",
        "namespace": "kube-system"
    },
    "data": {
        "checkhttp.json-c5ba8b82496662cd0b27a8450cf2324cd26b7855e505f5f1c81732937ee44831": "{\"Check\":\"HTTP\",\"CooloffSeconds\":1800,\"CorrectiveAction\":\"REBOOT\",\"Enabled\":false,\"ExpectedStatus\":200,\"FailureThreshold\":3,\"IntervalSeconds\":180,\"Port\":80,\"Route\":\"/myhealth\",\"TimeoutSeconds\":10}\n",
        "checknode.json-f8281ed773a1fbc09cac2dee4e17978b25e0a56f2519f72d79010d5c36df0699": "{\"Resource\": \"NODE\", \"TimeoutSeconds\": 30, \"Enabled\": true, \"IntervalSeconds\": 180, \"CorrectiveAction\": \"RELOAD\", \"FailureThreshold\": 3, \"Check\": \"KUBEAPI\", \"CooloffSeconds\": 1800}",
        "checkpod.json-66c811b3de5550fefaf85840f4098d18020e0776f82c839491e4f84ed56d7c40": "{\"Resource\": \"POD\", \"TimeoutSeconds\": 30, \"Enabled\": true, \"IntervalSeconds\": 180, \"PodFailureThresholdPercent\": 50, \"CorrectiveAction\": \"RELOAD\", \"FailureThreshold\": 3, \"Check\": \"KUBEAPI\", \"CooloffSeconds\": 1800}"
    }
}'''  # noqa

namespace_pods_partial = '''
{
    "items": [
        {
            "apiVersion": "v1",
            "kind": "Pod",
            "metadata": {
            },
            "spec": {
            },
            "status": {
                "conditions": [
                ],
                "containerStatuses": [
                ],
                "hostIP": "10.85.204.229",
                "phase": "Failed",
                "podIP": "172.30.53.35",
                "qosClass": "BestEffort",
                "startTime": "2019-10-29T14:15:55Z"
            }
        },
        {
            "apiVersion": "v1",
            "kind": "Pod",
            "metadata": {
            },
            "spec": {
            },
            "status": {
                "conditions": [
                ],
                "containerStatuses": [
                    {
                        "containerID": "containerd://b371d9e0e6b14dc2f2be7228c2f15b1d35951ced0429786581e40f046cb1405f",
                        "image": "registry.eu-de.bluemix.net/armada-master/vpn-client:2.4.6-r3-IKS-116",
                        "imageID": "registry.eu-de.bluemix.net/armada-master/vpn-client@sha256:98209366cd1f86a5c133afccf16876e8d94e29fd066bb55789d452ef93f61d09",
                        "lastState": {},
                        "name": "vpn",
                        "ready": true,
                        "restartCount": 0,
                        "state": {
                            "running": {
                                "startedAt": "2019-10-29T13:39:59Z"
                            }
                        }
                    }
                ],
                "hostIP": "10.168.137.22",
                "phase": "Running",
                "podIP": "172.30.53.16",
                "qosClass": "Burstable",
                "startTime": "2019-10-29T13:39:57Z"
            }
        }
    ],
    "kind": "List",
    "metadata": {
        "resourceVersion": "",
        "selfLink": ""
    }
}
'''


class TestK8sHelpers(unittest.TestCase):
    @patch('baseutils.exe_cmd')
    def test_set_cluster_autoscaler(self, mock_exe_cmd):
        cm_list = '''{{
    "apiVersion": "v1",
    "items": [
        {cm}
    ],
    "kind": "List",
    "metadata": {{
        "resourceVersion": "",
        "selfLink": ""
    }}
}}'''.format(cm=autoscaler_cm_output)
        mock_exe_cmd.side_effect = [
            (0, cm_list),
            (0, autoscaler_cm_output)
        ]
        self.assertEqual([], k8shelpers.set_cluster_autoscaler(True))
        self.assertEqual(2, mock_exe_cmd.call_count)
        mock_exe_cmd.side_effect = [
            (0, cm_list),
            (0, autoscaler_cm_output),
            (0, '')
        ]
        self.assertEqual(['default'], k8shelpers.set_cluster_autoscaler(False))
        self.assertEqual(5, mock_exe_cmd.call_count)
        self.assertIn('\\"enabled\\": false', mock_exe_cmd.call_args[1]['stdin'])
        mock_exe_cmd.side_effect = [
            (0, cm_list),
            (0, autoscaler_cm_output),
            (0, '')
        ]
        self.assertEqual(['default'], k8shelpers.set_cluster_autoscaler(False, ['default']))
        self.assertEqual(8, mock_exe_cmd.call_count)
        self.assertIn('\\"enabled\\": false', mock_exe_cmd.call_args[1]['stdin'])
        mock_exe_cmd.side_effect = [
            (0, cm_list),
            (0, autoscaler_cm_output)
        ]
        self.assertEqual([], k8shelpers.set_cluster_autoscaler(False, ['fake']))
        self.assertEqual(10, mock_exe_cmd.call_count)
        mock_exe_cmd.side_effect = [
            (0, cm_list),
            (0, autoscaler_cm_output),
            (0, '')
        ]
        self.assertEqual(['newname'], k8shelpers.set_cluster_autoscaler(False, ['default'], ['newname']))
        self.assertEqual(13, mock_exe_cmd.call_count)
        self.assertIn('\\"enabled\\": false', mock_exe_cmd.call_args[1]['stdin'])
        self.assertIn('\\"name\\": \\"newname\\"', mock_exe_cmd.call_args[1]['stdin'])
        mock_exe_cmd.side_effect = [
            (0, '''{
    "apiVersion": "v1",
    "items": [
    ],
    "kind": "List",
    "metadata": {
        "resourceVersion": "",
        "selfLink": ""
    }
}''')
        ]
        self.assertEqual([], k8shelpers.set_cluster_autoscaler(False))
        self.assertEqual(14, mock_exe_cmd.call_count)

    @patch('baseutils.exe_cmd')
    def test_set_recovery_tool(self, mock_exe_cmd):
        mock_exe_cmd.side_effect = [
            (0, r'''{{
    "apiVersion": "v1",
    "items": [
        {cm}
    ],
    "kind": "List",
    "metadata": {{
        "resourceVersion": "",
        "selfLink": ""
    }}
}}'''.format(cm=recovery_tool_cm_output)),
            (0, recovery_tool_cm_output),
            (0, '')
        ]
        self.assertIsNone(k8shelpers.set_recovery_tool(True))
        self.assertEqual(3, mock_exe_cmd.call_count)
        mock_exe_cmd.side_effect = [
            (0, '''{
    "apiVersion": "v1",
    "items": [
    ],
    "kind": "List",
    "metadata": {
        "resourceVersion": "",
        "selfLink": ""
    }
}''')
        ]
        self.assertIsNone(k8shelpers.set_recovery_tool(False))
        self.assertEqual(4, mock_exe_cmd.call_count)

    @patch('time.sleep')
    @patch('baseutils.exe_cmd')
    def test_wait_for_node_namespace_pods(self, mock_exe_cmd, mock_sleep):
        if os.name == 'nt':
            signal.SIGALRM = signal.SIGTERM
            signal.alarm = Mock()
        namespace_pods_partial_notready_json = json.loads(namespace_pods_partial)
        namespace_pods_partial_notready_json['items'][1]['status']['containerStatuses'][0]['ready'] = False
        mock_exe_cmd.side_effect = [
            (0, json.dumps(namespace_pods_partial_notready_json)),
            (0, namespace_pods_partial)
        ]
        self.assertIsNone(k8shelpers.wait_for_node_namespace_pods('10.168.137.22', 'kube-system'))
        self.assertEqual(2, mock_exe_cmd.call_count)
        self.assertEqual(2, mock_sleep.call_count)
        if os.name == 'nt':
            del signal.SIGALRM
            del signal.alarm


if __name__ == '__main__':
    unittest.main()
