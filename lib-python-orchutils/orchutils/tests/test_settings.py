import base64
import os
import unittest
import yaml
from mock import patch

from orchutils import settings


class TestSettings(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        settings.settings_dir = os.path.abspath(os.path.join(os.getcwd(), 'orchutils', 'tests', 'mock_settings'))

    @patch('orchutils.vault.client')
    def test_get_settings(self, mock_client):
        # Test with default settings
        mock_client.secrets.transit.decrypt_data.return_value = {
            'data': {
                'batch_results': [{
                    'plaintext': base64.b64encode('reveal1'.encode('utf-8'))
                }, {
                    'plaintext': base64.b64encode('reveal2'.encode('utf-8'))
                }]
            },
        }
        expected = {
            'category_var1': 'category1',
            'category_var2': 'category2',
            'category_var3': {
                'category_var4': 'category4',
                'category_var5': 'category5'
            },
            'metro_var1': 'metro1',
            'metro_var2': 'metro2',
            'global_var1': 'global1',
            'global_var2': 'global2',
            'offering': {
                'alias': ['tof'],
                'id': 't',
                'name': 'test_offering'
            },
            'offering_var1': 'offering1',
            'offering_var2': 'offering2',
            'secret_var1': 'reveal1',
            'secret_var2': 'reveal2'
        }
        result = settings.get_settings(
            category='test_category',
            metro='test_metro',
            offering='test_offering')
        self.assertDictEqual(result, expected)

        # Test with custom settings
        mock_client.secrets.transit.decrypt_data.return_value = {
            'data': {
                'batch_results': [{
                    'plaintext': base64.b64encode('reveal1'.encode('utf-8'))
                }, {
                    'plaintext': base64.b64encode('reveal2'.encode('utf-8'))
                }]
            },
        }
        expected = {
            'c_category_var1': 'c_category1',
            'c_category_var2': 'c_category2',
            'c_category_var3': {
                'c_category_var4': 'c_category4',
                'c_category_var5': 'c_category5'
            },
            'c_metro_var1': 'c_metro1',
            'c_metro_var2': 'c_metro2',
            'offering': {
                'alias': ['on'],
                'id': 'q',
                'name': 'offering_name'
            },
            'c_offering_var1': 'c_offering1',
            'c_offering_var2': 'c_offering2',
            'secret_var1': 'reveal1',
            'secret_var2': 'reveal2'
        }
        result = settings.get_settings(
            category='custom_category',
            metro='custom_metro',
            offering='offering_name',
            global_settings='custom',
            category_settings='custom_category',
            metro_settings='custom_metro')
        self.assertDictEqual(result, expected)

        # Test not providing environment-specific values
        expected = {
            'global_var1': 'global1',
            'global_var2': 'global2'
        }
        result = settings.get_settings()
        self.assertDictEqual(result, expected)

    @patch('orchutils.vault.client')
    def test_merge_settings_type(self, mock_client):
        master_settings = {}
        expected = {
            'category_var1': 'category1',
            'category_var2': 'category2',
            'category_var3': {
                'category_var4': 'category4',
                'category_var5': 'category5'
            }
        }
        settings._merge_settings_type('category', os.path.join(settings.settings_dir, 'test_category'), master_settings, '')
        self.assertDictEqual(expected, master_settings)

        master_settings = {}
        mock_client.secrets.transit.decrypt_data.return_value = {
            'data': {
                'batch_results': [{
                    'plaintext': base64.b64encode('reveal1'.encode('utf-8'))
                }]
            },
        }
        enc_category_file = os.path.join(settings.settings_dir, 'test_category', 'category-secret.yaml')
        with open(enc_category_file, 'w') as fh:
            fh.write('cat6: enc1')
        expected = {
            'category_var1': 'category1',
            'category_var2': 'category2',
            'category_var3': {
                'category_var4': 'category4',
                'category_var5': 'category5'
            },
            'cat6': 'reveal1'
        }
        settings._merge_settings_type('category', os.path.join(settings.settings_dir, 'test_category'), master_settings, 'dec-key-name')
        self.assertDictEqual(expected, master_settings)
        os.remove(enc_category_file)

    @patch('orchutils.vault.client')
    def test_read_settings_file(self, mock_client):
        mock_client.secrets.transit.decrypt_data.return_value = {
            'data': {
                'batch_results': [{
                    'plaintext': base64.b64encode('reveal1'.encode('utf-8'))
                }, {
                    'plaintext': base64.b64encode('reveal2'.encode('utf-8'))
                }]
            },
        }
        expected = {
            'global_var1': 'global1',
            'global_var2': 'global2'
        }

        result = settings.read_settings_file(os.path.join(settings.settings_dir, 'global.yaml'))
        self.assertDictEqual(result, expected)
        secret_expected = {
            'secret_var1': 'reveal1',
            'secret_var2': 'reveal2'
        }
        secret_result = settings.read_settings_file(
            os.path.join(settings.settings_dir, 'test_category', 'test_metro', 'test_offering', 'secret.yaml'),
            encryption_key='fake-key')
        self.assertDictEqual(secret_result, secret_expected)
        with self.assertRaises(IOError):
            settings.read_settings_file(os.path.join(settings.settings_dir, 'non-existing-file.yaml'))
        with self.assertRaises(IOError):
            settings.read_settings_file(os.path.join(settings.settings_dir, 'fake_settings', 'common.yaml'))
        with self.assertRaises(IOError):
            settings.read_settings_file(os.path.join(settings.settings_dir, '..', 'mock_settings', 'common.yaml'))  # Directory traversal flow

    def test_merge_settings(self):
        master = {
            'k1': 'v1m',
            'k2': {'k2.1': 'v2.1', 'k2.2': 'v2.2m'},
            'k3': 'v3',
            'k4': 'v4'
        }
        partial = {
            'k1': 'v1p',
            'k2': {'k2.2': 'v2.2p', 'k2.3': 'v2.3'},
            'k3': 'v3',
            'k5': 'v5'
        }
        result = {
            'k1': 'v1p',
            'k2': {'k2.1': 'v2.1', 'k2.2': 'v2.2p', 'k2.3': 'v2.3'},
            'k3': 'v3',
            'k4': 'v4',
            'k5': 'v5'
        }
        output = settings.merge_settings(master, partial)
        self.assertEqual(result, output)
        # Verify the original master was mutated
        self.assertEqual(result, master)

    def test_write_settings(self):
        category = 'test_category'
        metro = 'test_metro'
        offering = 'test_offering'
        type = 'app'
        output_file = os.path.join(settings.settings_dir, category, metro, offering, '{type}.yaml'.format(type=type))
        initial = {
            'k1': 'v1',
            'k2': {'k2.1': 'v2.1', 'k2.2': 'v2.2'},
            'k3': 'v3'
        }
        update = {
            'k2': {'k2.2': 'v2.2new', 'k2.3': 'v2.3new'},
            'k3': 'v3new'
        }
        expected_result = {
            'k1': 'v1',
            'k2': {'k2.1': 'v2.1', 'k2.2': 'v2.2new', 'k2.3': 'v2.3new'},
            'k3': 'v3new'
        }
        self.assertFalse(os.path.exists(output_file))
        settings.write_settings(category, metro, offering, initial, type)
        self.assertTrue(os.path.exists(output_file))
        settings.write_settings(category, metro, offering, update, type)
        with open(output_file) as fh:
            actual_result = yaml.safe_load(fh)
        self.assertEqual(expected_result, actual_result)
        # Test the operation with overwrite set to False
        expected_result = {
            'k1': 'v1',
            'k2': {'k2.1': 'v2.1', 'k2.2': 'v2.2', 'k2.3': 'v2.3new'},
            'k3': 'v3'
        }
        with open(output_file, 'w') as fh:
            yaml.safe_dump(initial, fh, default_flow_style=False, explicit_start=True, width=1000)
        settings.write_settings(category, metro, offering, update, type, overwrite_conflicts=False)
        with open(output_file) as fh:
            actual_result = yaml.safe_load(fh)
        self.assertEqual(expected_result, actual_result)
        # Passing a bad type raises an exception
        self.assertRaises(Exception, settings.write_settings, category, metro, offering, initial, 'badtype')
        # Directory traversal raises an exception
        self.assertRaises(Exception, settings.write_settings, category, '../traversal', offering, initial, type)
        os.remove(output_file)


if __name__ == '__main__':
    unittest.main()
