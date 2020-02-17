import base64
import os
import unittest
from mock import Mock
from mock import patch

from orchutils import vault


class TestVault(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        vault.client = 'client'  # Set the client to non-None to avoid the ensure_client decorator. This decorator has its own unit test.

    def test_get_vault_ca(self):
        ca = os.path.join(vault.certs_dir, 'cacerts.pem')
        self.assertEqual(ca, vault.get_vault_ca())

    @patch('hvac.Client')
    def test_login(self, mock_client):
        vault.client = None
        self.assertIsNone(vault.login('url', 'token'))
        self.assertIsNotNone(vault.client)
        vault.client = 'client'

    @patch('hvac.Client')
    def test_ensure_client(self, mock_client):
        # Test flow pulling creds from file
        vault.client = None
        orig_credentials_file = vault.credentials_file
        if os.name == 'nt':
            vault.credentials_file = os.path.join(os.environ['TEMP'], 'creds.yaml')
        else:
            vault.credentials_file = '/tmp/creds.yaml'
        with open(vault.credentials_file, 'w') as fh:
            fh.write('vault_url: "url"\nvault_access_token: "token"')
        func = Mock()
        func.__name__ = ''
        vault.ensure_client(func)()
        self.assertIsNotNone(vault.client)
        self.assertEqual(func.called, True)
        os.remove(vault.credentials_file)
        vault.credentials_file = orig_credentials_file

        # Test flow pulling creds from environment variables
        vault.client = None
        os.environ['VAULT_URL'] = 'url'
        os.environ['VAULT_ACCESS_TOKEN'] = 'token'
        func = Mock()
        func.__name__ = ''
        vault.ensure_client(func)()
        self.assertIsNotNone(vault.client)
        self.assertEqual(func.called, True)
        del os.environ['VAULT_URL']
        del os.environ['VAULT_ACCESS_TOKEN']

        # Test flow without credentials
        vault.client = None
        self.assertRaises(Exception, vault.ensure_client(func))
        vault.client = 'client'

    @patch('orchutils.vault.client')
    def test_create_transit_key(self, mock_client):
        self.assertIsNone(vault.create_transit_key('keyname'))

    @patch('orchutils.vault.client')
    def test_decrypt_dict(self, mock_client):
        mock_client.secrets.transit.decrypt_data.return_value = {
            'lease_id': '',
            'warnings': None,
            'wrap_info': None,
            'auth': None,
            'lease_duration': 0,
            'request_id': '882923cd-8b3c-e5e3-4d08-6e8ade5a6f00',
            'data': {'batch_results': [{'plaintext': base64.b64encode('dec1'.encode('utf-8'))}, {'plaintext': base64.b64encode('dec2'.encode('utf-8'))}]},
            'renewable': False
        }
        data = {'k1': 'enc1', 'k2': {'k3': 'enc2'}}
        expected_result = {'k1': 'dec1', 'k2': {'k3': 'dec2'}}
        vault.decrypt_dict('key', data)
        self.assertEqual(expected_result, data)

    @patch('orchutils.vault.client')
    def test_encrypt_dict(self, mock_client):
        mock_client.secrets.transit.encrypt_data.return_value = {
            'lease_id': '',
            'warnings': None,
            'wrap_info': None,
            'auth': None,
            'lease_duration': 0,
            'request_id': '1af5038c-2a33-cf51-65ea-8915dafca4e4',
            'data': {'batch_results': [{'ciphertext': 'vault:v1:OYQLZnYO5E'}, {'ciphertext': 'vault:v1:JbKUWTOZMW8KY'}]},
            'renewable': False
        }
        data = {'k1': 'dec1', 'k2': {'k3': 'dec2'}}
        expected_result = {'k1': 'vault:v1:OYQLZnYO5E', 'k2': {'k3': 'vault:v1:JbKUWTOZMW8KY'}}
        vault.encrypt_dict('key', data)
        self.assertEqual(expected_result, data)

    def test_aggregate_dict_for_vault(self):
        # Test ciphertext mode
        data = {'k1': 'enc1', 'k2': {'k3': 'enc2'}}
        expected_result = [{'ciphertext': 'enc1'}, {'ciphertext': 'enc2'}]
        self.assertEqual(expected_result, vault._aggregate_dict_for_vault(data, 'ciphertext'))

        # Test plaintext mode
        data = {'k1': 'dec1', 'k2': {'k3': 'dec2'}}
        expected_result = [{'plaintext': base64.b64encode('dec1'.encode('utf-8'))}, {'plaintext': base64.b64encode('dec2'.encode('utf-8'))}]
        self.assertEqual(expected_result, vault._aggregate_dict_for_vault(data, 'plaintext'))

    def test_restore_dict_from_vault(self):
        # Test ciphertext mode
        data = {'k1': 'dec1', 'k2': {'k3': 'dec2'}}
        aggregated_data = [{'ciphertext': 'enc1'}, {'ciphertext': 'enc2'}]
        expected_result = {'k1': 'enc1', 'k2': {'k3': 'enc2'}}
        vault._restore_dict_from_vault(data, 'ciphertext', aggregated_data)
        self.assertEqual(expected_result, data)

        # Test plaintext mode
        data = {'k1': 'enc1', 'k2': {'k3': 'enc2'}}
        aggregated_data = [{'plaintext': base64.b64encode('dec1'.encode('utf-8'))}, {'plaintext': base64.b64encode('dec2'.encode('utf-8'))}]
        expected_result = {'k1': 'dec1', 'k2': {'k3': 'dec2'}}
        vault._restore_dict_from_vault(data, 'plaintext', aggregated_data)
        self.assertEqual(expected_result, data)

    @patch('orchutils.vault.client')
    def test_decrypt_value(self, mock_client):
        mock_client.secrets.transit.decrypt_data.return_value = {
            'lease_id': '',
            'warnings': None,
            'wrap_info': None,
            'auth': None,
            'lease_duration': 0,
            'request_id': 'c20653c0-63e6-438f-ce27-da74ecf0aafe',
            'data': {'plaintext': 'ZGVjMQ=='},
            'renewable': False
        }
        self.assertEqual('dec1', vault.decrypt_value('key', 'enc1'))

    @patch('orchutils.vault.client')
    def test_encrypt_value(self, mock_client):
        mock_client.secrets.transit.encrypt_data.return_value = {
            'lease_id': '',
            'warnings': None,
            'wrap_info': None,
            'auth': None,
            'lease_duration': 0,
            'request_id': '882923cd-8b3c-e5e3-4d08-6e8ade5a6f00',
            'data': {'ciphertext': 'enc1'},
            'renewable': False
        }
        self.assertEqual('enc1', vault.encrypt_value('key', 'dec1'))

    @patch('requests.post')
    @patch('orchutils.vault.client')
    def test_issue_certificate(self, mock_client, mock_post):
        mock_client.url = 'http://url'
        mock_client.token = 'token'
        expected_result = {'certificate': 'cert', 'private_key': 'key', 'ca_chain': [], 'serial_number': '1:2'}
        mock_post.return_value.json.return_value = {
            'lease_id': '',
            'warnings': None,
            'wrap_info': None,
            'auth': None,
            'lease_duration': 2764800,
            'request_id': '277c128b-cd5b-32aa-8ad2-7587a348f175',
            'data': expected_result,
            'renewable': False
        }
        self.assertEqual(expected_result, vault.issue_certificate('hostname'))
        mock_post.return_value.json.side_effect = [
            {
                'lease_id': '',
                'warnings': None,
                'wrap_info': None,
                'auth': None,
                'lease_duration': 2764800,
                'request_id': '277c128b-cd5b-32aa-8ad2-7587a348f175',
                'data': expected_result,
                'renewable': False
            },
            {}
        ]
        self.assertEqual(expected_result, vault.issue_certificate('hostname', ca_mount='pki', role='role', ttl='2160h', revoke_cert=True))

    @patch('orchutils.vault.client')
    def test_delete(self, mock_client):
        self.assertIsNone(vault.delete('secret/my/path'))

    @patch('orchutils.vault.client')
    def test_list(self, mock_client):
        keys = ['key1', 'key2']
        mock_client.list.return_value = {
            'lease_id': '',
            'warnings': None,
            'wrap_info': None,
            'auth': None,
            'lease_duration': 2764800,
            'request_id': '277cd38b-cd5b-32aa-8ad2-7587afd8f175',
            'data': {'keys': keys},
            'renewable': False
        }
        self.assertEqual(keys, vault.list_keys('secret/my/path'))
        mock_client.list.return_value = None
        self.assertEqual([], vault.list_keys('secret/fake/path'))

    @patch('orchutils.vault.client')
    def test_read(self, mock_client):
        data = {'password': 'pass', 'user': 'user'}
        mock_client.read.return_value = {
            'lease_id': '',
            'warnings': None,
            'wrap_info': None,
            'auth': None,
            'lease_duration': 2764800,
            'request_id': '277cd38b-cd5b-32aa-8ad2-7587afd8f175',
            'data': data,
            'renewable': False
        }
        self.assertEqual(data, vault.read('secret/my/path'))
        self.assertEqual('pass', vault.read('secret/my/path', property='password'))
        self.assertEqual(None, vault.read('secret/my/path', property='fake'))

    @patch('orchutils.vault.client')
    def test_write(self, mock_client):
        self.assertIsNone(vault.write('secret/my/path', {'k1': 'v1', 'k2': 'v2'}))


if __name__ == '__main__':
    unittest.main()
