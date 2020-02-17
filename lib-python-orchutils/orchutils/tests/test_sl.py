import os
import unittest
from mock import Mock
from mock import patch

from orchutils import sl
from orchutils.slmodels.ip import IP


class TestSL(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sl.client = 'client'  # Set the client to non-None to avoid the ensure_clients decorator. This decorator has its own unit test.
        sl.dns_manager = 'client'
        sl.network_manager = 'client'

    @patch('SoftLayer.managers.network.NetworkManager')
    @patch('SoftLayer.managers.dns.DNSManager')
    @patch('SoftLayer.create_client_from_env')
    def test_login(self, mock_create_from_env, mock_dns_manager, mock_network_manager):
        sl.client = None
        sl.dns_manager = None
        sl.network_manager = None
        self.assertIsNone(sl.login('user', 'key'))
        self.assertIsNotNone(sl.client)
        self.assertIsNotNone(sl.dns_manager)
        self.assertIsNotNone(sl.network_manager)
        sl.client = 'client'
        sl.dns_manager = 'client'
        sl.network_manager = 'client'

    @patch('SoftLayer.managers.network.NetworkManager')
    @patch('SoftLayer.managers.dns.DNSManager')
    @patch('SoftLayer.create_client_from_env')
    def test_ensure_clients(self, mock_create_from_env, mock_dns_manager, mock_network_manager):
        # Test flow pulling creds from file
        sl.client = None
        sl.dns_manager = None
        sl.network_manager = None
        orig_credentials_file = sl.credentials_file
        if os.name == 'nt':
            sl.credentials_file = os.path.join(os.environ['TEMP'], 'creds.yaml')
        else:
            sl.credentials_file = '/tmp/creds.yaml'
        with open(sl.credentials_file, 'w') as fh:
            fh.write('sl_username: "user"\nsl_api_key: "key"')
        func = Mock()
        func.__name__ = ''
        sl.ensure_clients(func)()
        self.assertIsNotNone(sl.client)
        self.assertIsNotNone(sl.dns_manager)
        self.assertIsNotNone(sl.network_manager)
        self.assertEqual(func.called, True)
        os.remove(sl.credentials_file)
        sl.credentials_file = orig_credentials_file

        # Test flow pulling creds from environment variables
        sl.client = None
        sl.dns_manager = None
        sl.network_manager = None
        os.environ['SL_USERNAME'] = 'user'
        os.environ['SL_API_KEY'] = 'key'
        func = Mock()
        func.__name__ = ''
        sl.ensure_clients(func)()
        self.assertIsNotNone(sl.client)
        self.assertEqual(func.called, True)
        del os.environ['SL_USERNAME']
        del os.environ['SL_API_KEY']

        # Test flow without credentials
        sl.client = None
        sl.dns_manager = None
        sl.network_manager = None
        self.assertRaises(Exception, sl.ensure_clients(func))
        sl.client = 'client'
        sl.dns_manager = 'client'
        sl.network_manager = 'client'

    @patch('orchutils.sl.dns_manager')
    def test_create_dns_record(self, mock_dns_manager):
        mock_dns_manager.get_records.return_value = [
            {'host': 'grafana-test.i1', 'data': 'nginx.i1-armada.armadainteg.com', 'id': 94121007},
            {'host': 'grafana-test.i1-armada', 'data': 'nginx.i1-armada.armadainteg.com', 'id': 94267089},
            {'host': 'test456', 'data': '109.42.43.1', 'id': 92879747}
        ]
        mock_dns_manager.create_record.return_value = {'id': 92874827}
        self.assertEqual(92874827, sl.create_dns_record(2431041, 'test456', '109.42.43.2'))
        mock_dns_manager.get_records.return_value = [
            {'host': 'grafana-test.i1', 'data': 'nginx.i1-armada.armadainteg.com', 'id': 94121007},
            {'host': 'grafana-test.i1-armada', 'data': 'nginx.i1-armada.armadainteg.com', 'id': 94267089}
        ]
        mock_dns_manager.create_record.return_value = {'id': 92879395}
        self.assertEqual(92879395, sl.create_dns_record(2431041, 'test456', '109.42.43.1'))
        mock_dns_manager.get_records.return_value = [
            {'host': 'grafana-test.i1', 'data': 'nginx.i1-armada.armadainteg.com', 'id': 94121007},
            {'host': 'grafana-test.i1-armada', 'data': 'nginx.i1-armada.armadainteg.com', 'id': 94267089},
            {'host': 'test456', 'data': '109.42.43.2', 'id': 92879747}
        ]
        self.assertEqual(92879747, sl.create_dns_record(2431041, 'test456', '109.42.43.2'))

    @patch('orchutils.sl.dns_manager')
    def test_delete_dns_record(self, mock_dns_manager):
        mock_dns_manager.get_records.return_value = [
            {'host': 'grafana-test.i1', 'data': 'nginx.i1-armada.armadainteg.com', 'id': 94121007},
            {'host': 'grafana-test.i1-armada', 'data': 'nginx.i1-armada.armadainteg.com', 'id': 94267089},
            {'host': 'test456', 'data': '109.42.43.2', 'id': 92879747}
        ]
        self.assertIsNone(sl.delete_dns_record(2431041, 'grafana-test.i1', 'CNAME'))
        self.assertEqual(1, mock_dns_manager.delete_record.call_count)
        self.assertFalse(sl.delete_dns_record(2431041, 'non-existing', 'CNAME'))
        self.assertEqual(1, mock_dns_manager.delete_record.call_count)

    @patch('orchutils.sl.dns_manager')
    def test_get_hosted_zone_id(self, mock_dns_manager):
        mock_dns_manager.list_zones.return_value = [
           {'updateDate': '2018-04-25T15:39:00+00:00', 'serial': 2018042505, 'id': 2398389, 'name': 'armadatestpoc.com'},
           {'updateDate': '', 'serial': 2018022300, 'id': 2268453, 'name': 'artifactorypoc.com'},
        ]
        self.assertEqual(2398389, sl.get_hosted_zone_id('armadatestpoc.com'))
        self.assertIsNone(sl.get_hosted_zone_id('fakedomain.com'))

    @patch('orchutils.sl.network_manager')
    def test_get_subnet(self, mock_network_manager):
        mock_network_manager.get_subnet.return_value = {
            'id': 23,
            'cidr': 24,
            'networkIdentifier': '10.183.228.0',
            'networkVlanId': 1234,
            'ipAddresses': [
                {'id': 114234643, 'subnetId': 23, 'ipAddress': '10.183.228.98'},
                {'id': 114234645, 'subnetId': 23, 'ipAddress': '10.183.228.99'},
                {'id': 114234647, 'subnetId': 23, 'ipAddress': '10.183.228.100', 'note': 'fsrv1inupwdc040trans001.fs.local'},
                {'id': 114234633, 'subnetId': 23, 'ipAddress': '10.183.228.109', 'note': 'fsrv1inupwdc040test2.fs.local'},
                {'id': 114234543, 'subnetId': 23, 'ipAddress': '10.183.228.110', 'isReserved': True}
            ]
        }
        subnet = sl.get_subnet(23)
        self.assertEqual(5, len(subnet.ips))
        self.assertEqual(2, len(subnet.ips_available))
        self.assertEqual(2, len(subnet.ips_inuse))
        inuse_keys = list(subnet.ips_inuse.keys())
        inuse_keys.sort()
        self.assertEqual(['fsrv1inupwdc040test2.fs.local', 'fsrv1inupwdc040trans001.fs.local'], inuse_keys)

    @patch('orchutils.sl.client')
    def test_update_note(self, mock_client):
        ip_json = {'id': 1, 'subnetId': 1, 'ipAddress': '1.1.1.1', 'note': 'host'}
        ip = IP(1, ip_json)
        mock_client.call.side_effect = [{'id': 1, 'subnetId': 1, 'ipAddress': '1.1.1.1'}, True]
        self.assertIsNone(sl.update_note(ip))
        mock_client.call.return_value = {'id': 1, 'subnetId': 1, 'ipAddress': '1.1.1.1', 'isGateway': True}
        self.assertRaises(Exception, sl.update_note, ip)
        mock_client.call.return_value = {'id': 1, 'subnetId': 1, 'ipAddress': '1.1.1.1', 'note': 'host2'}
        self.assertRaises(Exception, sl.update_note, ip)
        mock_client.call.side_effect = [{'id': 1, 'subnetId': 1, 'ipAddress': '1.1.1.1', 'note': 'host2'}, True]
        self.assertIsNone(sl.update_note(ip, False))


if __name__ == '__main__':
    unittest.main()
