import os
import shutil
import tempfile
import unittest
import yaml

from orchutils import icpsettings


class TestSettings(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        icpsettings.settings_dir = tempfile.mkdtemp()

    @classmethod
    def tearDownClass(self):
        shutil.rmtree(icpsettings.settings_dir)

    def tearDown(self):  # Reset the settings dir after every unit test function
        shutil.rmtree(icpsettings.settings_dir)
        os.mkdir(icpsettings.settings_dir)

    def test_get_settings(self):
        with open(os.path.join(icpsettings.settings_dir, icpsettings.common_settings_file), 'w') as fh:
            fh.write('common_setting1: "cv1"\ncommon_setting2: "cv2"')
        with open(os.path.join(icpsettings.settings_dir, icpsettings.offering_settings_file), 'w') as fh:
            fh.write('hub:\n  common_setting2: "ov2"\n  offering_setting_global1: "ovg1"\n  offering_setting_global2: "ovg2"')
        datacenter = 'dc1'
        offering = 'hub'
        os.makedirs(os.path.join(icpsettings.settings_dir, datacenter, offering, 'group_vars'))
        os.makedirs(os.path.join(icpsettings.settings_dir, datacenter, offering, 'vars'))
        with open(os.path.join(icpsettings.settings_dir, datacenter, icpsettings.common_settings_file), 'w') as fh:
            fh.write('common_setting1: "dv1"\ndc_setting: "dv2"')
        with open(os.path.join(icpsettings.settings_dir, datacenter, offering, 'group_vars', icpsettings.common_settings_file), 'w') as fh:
            fh.write('common_setting1: "dov1"')
        with open(os.path.join(icpsettings.settings_dir, datacenter, offering, 'vars', 'off.yaml'), 'w') as fh:
            fh.write('offering_setting_global2: "dov2"\ndc_offering_setting: "dov3"')
        # Validate settings retrieval when no values are passed
        config = icpsettings.get_settings()
        self.assertEqual('cv1', config.get('common_setting1'))
        self.assertEqual('cv2', config.get('common_setting2'))
        self.assertEqual(None, config.get('offering_setting_global1'))
        self.assertEqual(None, config.get('dc_setting'))
        self.assertEqual(None, config.get('dc_offering_setting'))
        # Passing only the datacenter
        config = icpsettings.get_settings(datacenter)
        self.assertEqual('dv1', config.get('common_setting1'))
        self.assertEqual('cv2', config.get('common_setting2'))
        self.assertEqual('dv2', config.get('dc_setting'))
        self.assertEqual(None, config.get('dc_offering_setting'))
        # Passing a valid datacenter and an offering with no offering-specific config
        config = icpsettings.get_settings(datacenter, 'fake_off')
        self.assertEqual('dv1', config.get('common_setting1'))
        self.assertEqual('cv2', config.get('common_setting2'))
        self.assertEqual(None, config.get('offering_setting_global1'))
        self.assertEqual('dv2', config.get('dc_setting'))
        self.assertEqual(None, config.get('dc_offering_setting'))
        # Passing a datacenter and a valid offering
        config = icpsettings.get_settings(datacenter, offering)
        self.assertEqual('dov1', config.get('common_setting1'))
        self.assertEqual('ov2', config.get('common_setting2'))
        self.assertEqual('ovg1', config.get('offering_setting_global1'))
        self.assertEqual('dov2', config.get('offering_setting_global2'))
        self.assertEqual('dv2', config.get('dc_setting'))
        self.assertEqual('dov3', config.get('dc_offering_setting'))
        # Passing an offering but no datacenter
        config = icpsettings.get_settings(offering=offering)
        self.assertEqual('cv1', config.get('common_setting1'))
        self.assertEqual('ov2', config.get('common_setting2'))
        self.assertEqual('ovg1', config.get('offering_setting_global1'))
        self.assertEqual('ovg2', config.get('offering_setting_global2'))
        self.assertEqual(None, config.get('dc_setting'))
        self.assertEqual(None, config.get('dc_offering_setting'))
        # Passing an incorrect datacenter
        self.assertRaises(Exception, icpsettings.get_settings, 'fake_dc')
        # Test the use of common_settings_only
        config = icpsettings.get_settings(datacenter, offering, common_settings_only=True)
        self.assertEqual('dov1', config.get('common_setting1'))
        self.assertEqual('ov2', config.get('common_setting2'))
        self.assertEqual('ovg1', config.get('offering_setting_global1'))
        self.assertEqual('ovg2', config.get('offering_setting_global2'))
        self.assertEqual('dv2', config.get('dc_setting'))
        self.assertEqual(None, config.get('dc_offering_setting'))

    def test_list_datacenters(self):
        dc_dirs = ['scj01', 'wdc04']
        for dc in dc_dirs:
            os.mkdir(os.path.join(icpsettings.settings_dir, dc))
        dcs = icpsettings.list_datacenters()
        dcs.sort()
        self.assertEqual(dc_dirs, dcs)

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
        output = icpsettings.merge_settings(master, partial)
        self.assertEqual(result, output)
        # Verify the original master was mutated
        self.assertEqual(result, master)

    def test_write_settings(self):
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
        relative_path = 'wdc04/hub/vars/environment.yaml'
        full_path = os.path.join(icpsettings.settings_dir, relative_path)
        self.assertFalse(os.path.exists(full_path))
        icpsettings.write_settings(initial, relative_path)
        self.assertTrue(os.path.exists(full_path))
        icpsettings.write_settings(update, relative_path)
        with open(full_path) as fh:
            actual_result = yaml.safe_load(fh)
        self.assertEqual(expected_result, actual_result)
        # Test the operation with overwrite set to False
        expected_result = {
            'k1': 'v1',
            'k2': {'k2.1': 'v2.1', 'k2.2': 'v2.2', 'k2.3': 'v2.3new'},
            'k3': 'v3'
        }
        with open(full_path, 'w') as fh:
            yaml.safe_dump(initial, fh, default_flow_style=False, explicit_start=True, width=1000)
        icpsettings.write_settings(update, relative_path, overwrite_conflicts=False)
        with open(full_path) as fh:
            actual_result = yaml.safe_load(fh)
        self.assertEqual(expected_result, actual_result)
        # Passing no path raises an exception
        self.assertRaises(Exception, icpsettings.write_settings, {})
        # Passing full_path
        full_path = os.path.join(icpsettings.settings_dir, 'testfile.yaml')
        self.assertFalse(os.path.exists(full_path))
        icpsettings.write_settings(initial, full_path)
        self.assertTrue(os.path.exists(full_path))
        with open(full_path) as fh:
            actual_result = yaml.safe_load(fh)
        self.assertEqual(initial, actual_result)

    def test_prep_environment_settings(self):
        with open(os.path.join(icpsettings.settings_dir, 'excluded_file'), 'w') as fh:
            fh.write('setting: "value"')
        with open(os.path.join(icpsettings.settings_dir, icpsettings.common_settings_file), 'w') as fh:
            fh.write('common_setting1: "cv1"')
        with open(os.path.join(icpsettings.settings_dir, icpsettings.offering_settings_file), 'w') as fh:
            fh.write('hub:\n  common_setting2: "ov2"')
        datacenter = 'dc1'
        offering = 'hub'
        os.makedirs(os.path.join(icpsettings.settings_dir, datacenter, offering, 'group_vars'))
        os.makedirs(os.path.join(icpsettings.settings_dir, datacenter, offering, 'vars'))
        with open(os.path.join(icpsettings.settings_dir, datacenter, icpsettings.common_settings_file), 'w') as fh:
            fh.write('common_setting3: "dv3"')
        with open(os.path.join(icpsettings.settings_dir, datacenter, offering, 'group_vars', icpsettings.common_settings_file), 'w') as fh:
            fh.write('key: "value"')
        with open(os.path.join(icpsettings.settings_dir, datacenter, offering, 'vars', 'environment.yaml'), 'w') as fh:
            fh.write('env_setting: "env_value"')
        settings_dir = icpsettings.prep_environment_settings(datacenter, offering)
        try:
            self.assertTrue(os.path.isdir(settings_dir))
            self.assertFalse(os.path.exists(os.path.join(settings_dir, 'excluded_file')))
            merged_settings_file = os.path.join(settings_dir, 'group_vars', icpsettings.common_settings_file)
            self.assertTrue(os.path.isfile(merged_settings_file))
            with open(merged_settings_file) as fh:
                actual_result = yaml.safe_load(fh)
            expected_result = {
                'common_setting1': 'cv1',
                'common_setting2': 'ov2',
                'common_setting3': 'dv3',
                'key': 'value'
            }
            self.assertEqual(expected_result, actual_result)
            self.assertTrue(os.path.isfile(os.path.join(settings_dir, 'vars', 'environment.yaml')))
        finally:
            shutil.rmtree(settings_dir)  # Always clean the temporary directory created

    def test_seed_environment_settings(self):
        datacenter = 'wdc04'
        offering = 'hub'
        env_dir = os.path.join(icpsettings.settings_dir, datacenter, offering)
        os.makedirs(os.path.join(env_dir, 'vars'))
        with open(os.path.join(icpsettings.settings_dir, icpsettings.common_settings_file), 'w') as fh:
            fh.write('hostname_suffix: ".fs.local"')
        with open(os.path.join(icpsettings.settings_dir, icpsettings.offering_settings_file), 'w') as fh:
            fh.write(
                'hub:\n'
                '  offering_id: "u"'
            )
        with open(os.path.join(icpsettings.settings_dir, datacenter, icpsettings.common_settings_file), 'w') as fh:
            fh.write(
                'platform_id_suffix: "-pp"\n'
                'subnets:\n'
                '- id: 1745229\n'
                '  gateway: "10.183.228.1"\n'
                '  network_prefix: "23"\n'
                '  vmware_network: "DPG-FS1-WCH-C1_APP-NP-1469"\n'
                'icp:\n'
                '  zones:\n'
                '  - zone_name: "zone1"\n'
                '    datastore: "FS1-PLATFORM-C1-SIOC1-disk02"\n'
                '    infra_zone: "1"\n'
                '  - zone_name: "zone2"\n'
                '    datastore: "FS1-PLATFORM-C2-SIOC2-disk02"\n'
                '    infra_zone: "2"\n'
            )
        with open(os.path.join(env_dir, 'vars', 'environment.yaml'), 'w') as fh:
            fh.write(
                'icp:\n'
                '  nodes:\n'
                '    vmware:\n'
                '      mgt:\n'
                '        current:\n'
                '        - address: 10.183.229.211\n'
                '          hostname: p2pppocupwdc04uk8mgt001.fs.local\n'
                '          id: 114235381\n'
                '          subnet_id: 1745229\n'
                '        - address: 10.183.229.212\n'
                '          hostname: p2pppocupwdc04uk8mgt002.fs.local\n'
                '          id: 114235383\n'
                '          subnet_id: 1745229\n'
                '        desired: 2\n'
                '      mst:\n'
                '        current:\n'
                '        - address: 10.183.229.200\n'
                '          hostname: p2pppocupwdc04uk8mst001.fs.local\n'
                '          id: 114235359\n'
                '          subnet_id: 1745229\n'
                '        - address: 10.183.229.201\n'
                '          hostname: p2pppocupwdc04uk8mst002.fs.local\n'
                '          id: 114235361\n'
                '          subnet_id: 1745229\n'
                '        desired: 2\n'
                '      pxy:\n'
                '        current:\n'
                '        - address: 10.183.229.203\n'
                '          hostname: p2pppocupwdc04uk8pxy001.fs.local\n'
                '          id: 114235365\n'
                '          subnet_id: 1745229\n'
                '        desired: 1\n'
                '      wrk:\n'
                '        current:\n'
                '        - address: 10.183.229.205\n'
                '          hostname: p2pppocupwdc04uk8wrk001.fs.local\n'
                '          id: 114235369\n'
                '          subnet_id: 1745229\n'
                '        desired: 1\n'
                '  vips:\n'
                '    mst:\n'
                '      address: 10.183.229.198\n'
                '      hostname: p2pppocupwdc04uk8mstvip.fs.local\n'
                '      id: 114235355\n'
                '      subnet_id: 1745229\n'
                '    pxy:\n'
                '      address: 10.183.229.199\n'
                '      hostname: p2pppocupwdc04uk8pxyvip.fs.local\n'
                '      id: 114235357\n'
                '      subnet_id: 1745229\n'
            )
        rendered = icpsettings.seed_environment_settings(datacenter, offering)
        self.assertTrue(rendered)
        hosts_file = os.path.join(env_dir, 'hosts')
        self.assertTrue(os.path.isfile(hosts_file))
        config = icpsettings.get_settings(datacenter, offering)
        self.assertEqual('10.183.229.200 10.183.229.201', config['icp_role_master'])
        self.assertEqual('u-pp', config['platform_id'])
        self.assertEqual('p2pppocupwdc04uk8mgt002.fs.local', config['icp']['nodes']['vmware']['mgt']['current'][1]['hostname'])
        with open(os.path.join(env_dir, 'group_vars', 'master.yaml')) as fh:
            config = yaml.safe_load(fh)
        self.assertEqual('ldaps://ldap.{datacenter}.dc.local:636'.format(datacenter=datacenter), config['icp_ldap_url'])
        with open(os.path.join(env_dir, 'host_vars', 'p2pppocupwdc04uk8mst001.yaml')) as fh:
            config = yaml.safe_load(fh)
        self.assertEqual('10.183.229.200', config['ansible_host'])
        self.assertEqual('DPG-FS1-WCH-C1_APP-NP-1469', config['network'])
        # Confirm that re-running the function does not re-run the templating
        hosts_file_mtime = os.path.getmtime(hosts_file)
        rendered = icpsettings.seed_environment_settings(datacenter, offering)
        self.assertFalse(rendered)
        self.assertEqual(hosts_file_mtime, os.path.getmtime(hosts_file))


if __name__ == '__main__':
    unittest.main()
