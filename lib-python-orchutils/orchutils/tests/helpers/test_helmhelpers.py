import json
import os
import signal
import unittest
import yaml
from datetime import datetime
from mock import Mock
from mock import patch

from orchutils.helpers import helmhelpers
from test_helm import valid_manifest
from test_helm import release_hooks
from helmmodels.test_releaserevision import revisions_json
from ibmcloudmodels.test_albcertificate import alb_certificates_json

ingress_manifest = '''
# Source: p2paas-console-ui/templates/ingress.yaml
apiVersion: "networking.k8s.io/v1beta1"
kind: "Ingress"
metadata:
  name: "p2paas-console-ui"
  namespace: "console"
  labels:
    app.kubernetes.io/name: "p2paas-console-ui"
    helm.sh/chart: "p2paas-console-ui-1.20191008.138"
    app.kubernetes.io/instance: "p2paas-console-ui"
    app.kubernetes.io/managed-by: "Tiller"
  annotations:
    ingress.bluemix.net/ALB-ID: "private-cr082c22b41bae42e2bca33e0e08b50617-alb1"
    ingress.bluemix.net/redirect-to-https: "True"
    ingress.bluemix.net/ssl-services: "ssl-service=p2paas-console-ui"
    p2paas-certificate: "crn:v1:bluemix:public:cloudcerts:us-south:a/69a92444d0c448d994ceb2f517b2fd39:21f25d57-2d21-46bf-ba3c-e73e37ffd6da:certificate:873784046e45eef7491c45d830"
spec:
  rules:
  - host: "console.platform-hub-sjc03.np.wce.ibm.com"
    http:
      paths:
      - path: "/"
        backend:
          serviceName: "p2paas-console-ui"
          servicePort: 443
  tls:
  - hosts:
    - console.platform-hub-sjc03.np.wce.ibm.com
    secretName: "console-p2paas-console-ui"
'''

cluster_info = r'''{
  "apiVersion": "v1",
  "data": {
    "cluster-config.json": "{\n  \"cluster_id\": \"082c22b41bae42e2bca33e0e08b50617\",\n  \"cluster_name\": \"prod-sjc03-082c22b41bae42e2bca33e0e08b50617\",\n  \"cluster_type\": \"cruiser\",\n  \"cluster_pay_tier\": \"paid\",\n  \"datacenter\": \"sjc03\",\n  \"account_id\": \"69a92444d0c448d994ceb2f517b2fd39\",\n  \"created\": \"2019-03-13T17:08:00+0000\",\n  \"name\": \"platform-hub-np-sjc03\",\n  \"master_public_url\": \"https://:20245\",\n  \"master_url\": \"https://c9.sjc03.containers.cloud.ibm.com:20245\",\n  \"crn\":  \"crn:v1:bluemix:public:containers-kubernetes:us-south:69a92444d0c448d994ceb2f517b2fd39:082c22b41bae42e2bca33e0e08b50617\"\n}\n",
    "etcd_host": "c9.sjc03.containers.cloud.ibm.com",
    "etcd_port": "31940"
  },
  "kind": "ConfigMap",
  "metadata": {
    "creationTimestamp": "2019-03-13T17:20:20Z",
    "name": "cluster-info",
    "namespace": "kube-system",
    "resourceVersion": "33143745",
    "selfLink": "/api/v1/namespaces/kube-system/configmaps/cluster-info",
    "uid": "476d20d5-45b4-11e9-97fe-d2eb8712f324"
  }
}'''  # noqa


class TestHelmHelpers(unittest.TestCase):
    @patch('baseutils.exe_cmd')
    def test_run_release_tests(self, mock_exe_cmd):
        release_hooks_podlist = {
            'items': list(yaml.safe_load_all(release_hooks)),
            'kind': 'List'
        }
        mock_exe_cmd.side_effect = [
            (0, release_hooks),
            (0, json.dumps(release_hooks_podlist)),
            (0, ''),
            (0, ''),
            (0, json.dumps(release_hooks_podlist)),
            (0, json.dumps(release_hooks_podlist['items'][0])),
            (0, '')
        ]
        self.assertIsNone(helmhelpers.run_release_tests('release'))
        self.assertEqual(7, mock_exe_cmd.call_count)

    @patch('baseutils.exe_cmd')
    def test_rconditional_release_rollback(self, mock_exe_cmd):
        if os.name == 'nt':
            signal.SIGALRM = signal.SIGTERM
            signal.alarm = Mock()
        mock_exe_cmd.side_effect = [
            (0, json.dumps(revisions_json)),
            (0, ''),
            (0, valid_manifest),
            (0, 'deployment "p2paas-console-ui" successfully rolled out'),
            (0, '{"spec": {"selector": {"matchLabels": {"my-label": "myvalue"}}}, "metadata": {"annotations": {"deployment.kubernetes.io/revision": "2"}}}'),
            (0, '{"items": [{"kind": "ReplicaSet", "spec": {"selector": {"matchLabels": {"my-label": "myvalue"}}}, ' +
                '"metadata": {"annotations": {"deployment.kubernetes.io/revision": "2"}}}],"kind": "List"}'),
            (0, '{"items": [], "kind": "List"}')
        ]
        self.assertIsNone(helmhelpers.conditional_release_rollback('release', datetime.strptime(revisions_json[-1]['updated'], '%a %b %d %H:%M:%S %Y')))
        self.assertEqual(7, mock_exe_cmd.call_count)
        if os.name == 'nt':
            del signal.SIGALRM
            del signal.alarm

    @patch('baseutils.exe_cmd')
    def test_import_certificates(self, mock_exe_cmd):
        mock_exe_cmd.side_effect = [
            (0, valid_manifest)
        ]
        self.assertIsNone(helmhelpers.import_certificates('release'))
        self.assertEqual(1, mock_exe_cmd.call_count)
        mock_exe_cmd.side_effect = [
            (0, ingress_manifest),
            (0, cluster_info),
            (0, json.dumps(alb_certificates_json)),
            (0, '')
        ]
        self.assertIsNone(helmhelpers.import_certificates('release'))
        self.assertEqual(5, mock_exe_cmd.call_count)
        self.assertIn('--cluster \'082c22b41bae42e2bca33e0e08b50617\'', mock_exe_cmd.call_args_list[4][0][0])
        self.assertIn('873784046e45eef7491c45d830', mock_exe_cmd.call_args_list[4][0][0])
        self.assertIn('--secret-name \'console.p2paas-console-ui\'', mock_exe_cmd.call_args_list[4][0][0])

    @patch('baseutils.exe_cmd')
    def test_process_chart_deployment(self, mock_exe_cmd):
        if os.name == 'nt':
            signal.SIGALRM = signal.SIGTERM
            signal.alarm = Mock()
        side_effect = [
            (0, ''),
            (0, valid_manifest),
            (0, valid_manifest),
            (0, valid_manifest),
            (0, 'deployment "p2paas-console-ui" successfully rolled out'),
            (0, '{"spec": {"selector": {"matchLabels": {"my-label": "myvalue"}}}, "metadata": {"annotations": {"deployment.kubernetes.io/revision": "2"}}}'),
            (0, '{"items": [{"kind": "ReplicaSet", "spec": {"selector": {"matchLabels": {"my-label": "myvalue"}}}, ' +
                '"metadata": {"annotations": {"deployment.kubernetes.io/revision": "2"}}}],"kind": "List"}'),
            (0, '{"items": [], "kind": "List"}'),
            (0, valid_manifest),
            (0, '')
        ]
        mock_exe_cmd.side_effect = side_effect
        self.assertIsNone(helmhelpers.process_chart_deployment('p2paas/chart', '1.0.0', 'release', 'pltfrm', {'k1': 'v1'}, False))
        self.assertEqual(10, mock_exe_cmd.call_count)
        mock_exe_cmd.side_effect = side_effect
        self.assertIsNone(helmhelpers.process_chart_deployment('p2paas/chart', '1.0.0', 'release', 'pltfrm', {'k1': 'v1'}, True))
        self.assertEqual(20, mock_exe_cmd.call_count)
        side_effect[0] = (0, '''NAME            REVISION        UPDATED                         STATUS          CHART                           NAMESPACE
release         56              Tue Oct  3 13:01:33 2017        DEPLOYED        governor-www-1.20171003.54      default''')
        side_effect.pop(1)
        mock_exe_cmd.side_effect = side_effect
        self.assertIsNone(helmhelpers.process_chart_deployment('p2paas/chart', '1.0.0', 'release', 'pltfrm', {'k1': 'v1'}, False))
        self.assertEqual(29, mock_exe_cmd.call_count)
        mock_exe_cmd.side_effect = [
            (0, ''),
            (0, valid_manifest),
            (0, valid_manifest),
            (0, valid_manifest),
            (1, 'deployment failed'),
            (0, json.dumps(revisions_json))
        ]
        with self.assertRaises(Exception) as context:
            with patch('orchutils.helpers.helmhelpers.logger.error'):  # The client code logs the stack trace before raising. This can cause confusing as it appears like an error
                helmhelpers.process_chart_deployment('p2paas/chart', '1.0.0', 'release', 'pltfrm', {'k1': 'v1'}, False)
        self.assertEqual('deployment failed', str(context.exception))
        self.assertEqual(35, mock_exe_cmd.call_count)
        if os.name == 'nt':
            del signal.SIGALRM
            del signal.alarm


if __name__ == '__main__':
    unittest.main()
