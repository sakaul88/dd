import os
import unittest
from mock import patch

from orchutils import sos


class TestSOS(unittest.TestCase):
    @patch('baseutils.local_lock')
    @patch('orchutils.vault.client')
    @patch('baseutils.exe_cmd')
    def test_csutil_cluster_setup(self, mock_exe_cmd, mock_vault, mock_local_lock):
        mock_exe_cmd.side_effect = [
            (0, '{"kind": "List", "items": [{"metadata": {"name": "sos-vpn-secret"}}]}'),
            (0, '{"data": {"name0001.ovpn": ""}}'),
            (0, '')
        ]
        mock_vault.read.side_effect = [
            None,
            {
                'lease_id': '',
                'warnings': None,
                'wrap_info': None,
                'auth': None,
                'lease_duration': 2764800,
                'request_id': '277cd38b-cd5b-32aa-8ad2-7587afd8f175',
                'data': {'content': 'content'},
                'renewable': False
            }
        ]
        os.environ['P2PAAS_ORCH_DIR'] = '/tmp'
        self.assertIsNone(sos.csutil_cluster_setup('cluster_name', 'p2paas', 'staging'))
        self.assertEqual(3, mock_exe_cmd.call_count)
        self.assertEqual(2, mock_vault.read.call_count)
        self.assertIn('--crn-service-name \'p2paas\'', mock_exe_cmd.call_args_list[2][0][0])
        self.assertIn('--crn-cname \'staging\'', mock_exe_cmd.call_args_list[2][0][0])
        self.assertIn('name0001.ovpn', mock_exe_cmd.call_args_list[2][0][0])
        self.assertIn('cluster_name', mock_exe_cmd.call_args_list[2][0][0])
        del os.environ['P2PAAS_ORCH_DIR']

    @patch('baseutils.local_lock')
    @patch('orchutils.vault.client')
    @patch('baseutils.exe_cmd')
    def test_csutil_cluster_cleanup(self, mock_exe_cmd, mock_vault, mock_local_lock):
        mock_exe_cmd.side_effect = [
            (0, '{"kind": "List", "items": [{"metadata": {"name": "sos-vpn-secret"}}]}'),
            (0, '{"data": {"name0001.ovpn": ""}}'),
            (0, '')
        ]
        os.environ['P2PAAS_ORCH_DIR'] = '/tmp'
        self.assertIsNone(sos.csutil_cluster_cleanup('cluster_name'))
        self.assertEqual(3, mock_exe_cmd.call_count)
        self.assertIn('cluster_name', mock_exe_cmd.call_args_list[2][0][0])
        del os.environ['P2PAAS_ORCH_DIR']

    @patch('baseutils.local_lock')
    @patch('orchutils.vault.client')
    @patch('baseutils.exe_cmd')
    def test_reserve_iks_ovpn_config_name(self, mock_exe_cmd, mock_vault, mock_local_lock):
        mock_exe_cmd.side_effect = [
            (0, '{"kind": "List", "items": [{"metadata": {"name": "sos-vpn-secret"}}]}'),
            (0, '{"data": {"config0001.ovpn": ""}}')
        ]
        mock_vault.read.return_value = None
        self.assertEqual('config0001.ovpn', sos._reserve_iks_ovpn_config_name('cluster_name'))
        self.assertEqual(2, mock_exe_cmd.call_count)
        self.assertEqual(1, mock_vault.write.call_count)
        mock_exe_cmd.side_effect = [
            (0, '{"kind": "List", "items": [{"metadata": {"name": "name"}}]}'),
        ]
        mock_vault.list.side_effect = [
            {
                'lease_id': '',
                'warnings': None,
                'wrap_info': None,
                'auth': None,
                'lease_duration': 2764800,
                'request_id': '277cd38b-cd5b-32aa-8ad2-7587afd8f175',
                'data': {'keys': ['config0001.ovpn', 'config0002.ovpn']},
                'renewable': False
            },
            {
                'lease_id': '',
                'warnings': None,
                'wrap_info': None,
                'auth': None,
                'lease_duration': 2764800,
                'request_id': '277cd38b-cd5b-32aa-8ad2-7587afd8f175',
                'data': {'keys': ['config0001.ovpn']},
                'renewable': False
            },
            {}
        ]
        self.assertEqual('config0002.ovpn', sos._reserve_iks_ovpn_config_name('cluster_name'))
        self.assertEqual(3, mock_exe_cmd.call_count)
        self.assertEqual(2, mock_vault.list.call_count)
        self.assertEqual(2, mock_vault.write.call_count)
        mock_exe_cmd.side_effect = [
            (0, '{"kind": "List", "items": [{"metadata": {"name": "false"}}]}'),
        ]
        mock_vault.list.side_effect = [
            {
                'lease_id': '',
                'warnings': None,
                'wrap_info': None,
                'auth': None,
                'lease_duration': 2764800,
                'request_id': '277cd38b-cd5b-32aa-8ad2-7587afd8f175',
                'data': {'keys': ['config0001.ovpn', 'config0002.ovpn']},
                'renewable': False
            },
            {
                'lease_id': '',
                'warnings': None,
                'wrap_info': None,
                'auth': None,
                'lease_duration': 2764800,
                'request_id': '277cd38b-cd5b-32aa-8ad2-7587afd8f175',
                'data': {'keys': ['config0001.ovpn', 'config0002.ovpn']},
                'renewable': False
            }
        ]
        with self.assertRaises(Exception) as context:
            sos._reserve_iks_ovpn_config_name('cluster_name')
        self.assertIn('No configs available to select', str(context.exception))
        self.assertEqual(4, mock_exe_cmd.call_count)
        self.assertEqual(4, mock_vault.list.call_count)
        self.assertEqual(2, mock_vault.write.call_count)

    @patch('baseutils.local_lock')
    @patch('orchutils.vault.client')
    @patch('baseutils.exe_cmd')
    def test_get_current_iks_ovpn_config_name(self, mock_exe_cmd, mock_vault, mock_local_lock):
        mock_exe_cmd.side_effect = [
            (0, '{"kind": "List", "items": [{"metadata": {"name": "sos-vpn-secret"}}]}'),
            (0, '{"data": {"name0001.ovpn": ""}}')
        ]
        mock_vault.read.return_value = None
        self.assertEqual('name0001.ovpn', sos._get_current_iks_ovpn_config_name('cluster_name'))
        self.assertEqual(2, mock_exe_cmd.call_count)
        self.assertEqual(1, mock_vault.read.call_count)
        self.assertEqual(1, mock_vault.write.call_count)
        mock_exe_cmd.side_effect = [
            (0, '{"kind": "List", "items": [{"metadata": {"name": "false"}}]}'),
        ]
        self.assertIsNone(sos._get_current_iks_ovpn_config_name('cluster_name'))
        self.assertEqual(3, mock_exe_cmd.call_count)
        self.assertEqual(1, mock_vault.write.call_count)
        mock_exe_cmd.side_effect = [
            (0, '{"kind": "List", "items": [{"metadata": {"name": "sos-vpn-secret"}}]}'),
            (0, '{"data": {"name0001.ovpn": ""}}')
        ]
        mock_vault.read.return_value = {
            'lease_id': '',
            'warnings': None,
            'wrap_info': None,
            'auth': None,
            'lease_duration': 2764800,
            'request_id': '277cd38b-cd5b-32aa-8ad2-7587afd8f175',
            'data': {'cluster': 'different_cluster'},
            'renewable': False
        }
        with self.assertRaises(Exception) as context:
            sos._reserve_iks_ovpn_config_name('cluster_name')
        self.assertIn('Cluster is using and ovpn config reserved by a different cluster', str(context.exception))
        self.assertEqual(5, mock_exe_cmd.call_count)
        self.assertEqual(2, mock_vault.read.call_count)
        self.assertEqual(1, mock_vault.write.call_count)

    def test_get_csutil_env(self):
        os.environ['P2PAAS_ORCH_DIR'] = '/tmp'
        self.assertNotIn('HELM_HOME', os.environ)
        sos_env = sos._get_csutil_env()
        self.assertNotIn('HELM_HOME', os.environ)
        self.assertIn('HELM_HOME', sos_env)
        self.assertNotIn('BLUEMIX_HOME', sos_env)
        os.environ['IBMCLOUD_HOME'] = '/tmp'
        sos_env = sos._get_csutil_env()
        self.assertIn('BLUEMIX_HOME', sos_env)
        del os.environ['IBMCLOUD_HOME']
        del os.environ['P2PAAS_ORCH_DIR']

    @patch('baseutils.local_lock')
    @patch('orchutils.vault.client')
    @patch('baseutils.exe_cmd')
    def test_release_iks_ovpn_config_reservation(self, mock_exe_cmd, mock_vault, mock_local_lock):
        mock_exe_cmd.side_effect = [
            (0, '{"kind": "List", "items": [{"metadata": {"name": "sos-vpn-secret"}}]}'),
            (0, '{"data": {"name0001.ovpn": ""}}')
        ]
        mock_vault.read.return_value = None
        self.assertIsNone(sos.release_iks_ovpn_config_reservation('cluster_name'))
        self.assertEqual(2, mock_exe_cmd.call_count)
        self.assertEqual(1, mock_vault.read.call_count)
        self.assertEqual(1, mock_vault.write.call_count)
        self.assertEqual(1, mock_vault.delete.call_count)
        mock_exe_cmd.side_effect = [
            (0, '{"kind": "List", "items": []}')
        ]
        self.assertIsNone(sos.release_iks_ovpn_config_reservation('cluster_name'))
        self.assertEqual(3, mock_exe_cmd.call_count)
        self.assertEqual(1, mock_vault.read.call_count)
        self.assertEqual(1, mock_vault.write.call_count)
        self.assertEqual(1, mock_vault.delete.call_count)
        mock_vault.read.return_value = {
            'lease_id': '',
            'warnings': None,
            'wrap_info': None,
            'auth': None,
            'lease_duration': 2764800,
            'request_id': '277cd38b-cd5b-32aa-8ad2-7587afd8f175',
            'data': {'cluster': 'different_cluster'},
            'renewable': False
        }
        mock_exe_cmd.side_effect = [
            (0, '{"kind": "List", "items": [{"metadata": {"name": "sos-vpn-secret"}}]}'),
            (0, '{"data": {"name0001.ovpn": ""}}')
        ]
        self.assertIsNone(sos.release_iks_ovpn_config_reservation('cluster_name'))
        self.assertEqual(5, mock_exe_cmd.call_count)
        self.assertEqual(2, mock_vault.read.call_count)
        self.assertEqual(1, mock_vault.write.call_count)
        self.assertEqual(1, mock_vault.delete.call_count)


if __name__ == '__main__':
    unittest.main()
