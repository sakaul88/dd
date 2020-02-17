import unittest

from orchutils.ibmcloudmodels.pluginversion import PluginVersion

plugin_versions_text = '''
                0.4.64    Yes          1244821125d383c33f160346f8eb33fe976d0640   N/A
                0.4.61    Yes          a29c8a57beb4c4be485895f2e42e8b64b8533c8a   0.18.2
                0.4.51    Yes          855155308ae4296a7c7d03760c347e030d2c4fdc   0.18.2
                0.2.21    Yes          d4c1e3c71aa3ba211791849bcc39ebf49ffc10bc   0.18.2
                0.2.1    Yes          6de09e00dd3bc0cf6f0d6a8e98dc6acdd19e3f01   0.18.2
                0.1.9    Yes          f33688ac61ea2d530ed3ee3a42fe32432a08c317   0.18.2
                0.1.0    Yes          8b2c4d66f8558dcb278b602f0985ab56cc7eeaba   0.18.2
'''


class TestPluginVersion(unittest.TestCase):
    def test_constructor(self):
        plugin_version = PluginVersion('0.4.38    Yes          6de09e00dd3bc0cf6f0d6a8e98dc6acdd19e3f01   0.18.2')
        self.assertEqual('0.4.38', plugin_version.version)
        self.assertEqual(True, plugin_version.compatible)
        self.assertEqual('6de09e00dd3bc0cf6f0d6a8e98dc6acdd19e3f01', plugin_version.sha1)
        self.assertEqual('0.18.2', plugin_version.min_cli_version)

    def test_properties(self):
        plugin_version = PluginVersion('0.4.38    Yes          6de09e00dd3bc0cf6f0d6a8e98dc6acdd19e3f01   0.18.2')
        self.assertEqual('0.4.38', plugin_version.version)
        plugin_version.version = '2.1.0'
        self.assertEqual('2.1.0', plugin_version.version)
        plugin_version.compatible = False
        self.assertEqual(False, plugin_version.compatible)
        plugin_version.sha1 = 'fake'
        self.assertEqual('fake', plugin_version.sha1)
        plugin_version.min_cli_version = '2.1.1'
        self.assertEqual('2.1.1', plugin_version.min_cli_version)

    def test_parse_plugin_versions(self):
        plugin_versions = PluginVersion.parse_plugin_versions(plugin_versions_text)
        self.assertEqual(7, len(plugin_versions))
        self.assertEqual('0.4.64', plugin_versions[0].version)


if __name__ == '__main__':
    unittest.main()
