import unittest

from orchutils.ibmcloudmodels.plugin import Plugin
from orchutils.ibmcloudmodels.pluginversion import PluginVersion

plugin_text = '''
Looking up 'container-service' from repository 'IBM Cloud'...

Name:           container-service/kubernetes-service
Description:    IBM Cloud Kubernetes Service for management of Kubernetes clusters
Company:        IBM
Homepage:       https://cloud.ibm.com/docs/containers?topic=containers-cli-plugin-kubernetes-service-cli
Authors:
Versions:       Version   Compatible   SHA1                                       Minimal CLI version required
                0.4.64    Yes          1244821125d383c33f160346f8eb33fe976d0640   N/A
                0.4.61    Yes          a29c8a57beb4c4be485895f2e42e8b64b8533c8a   0.18.2
                0.4.3     Yes          6b4d0d58312f1d2deaa942c304060eca79e2c94e   0.9.0
                0.2.99    Yes          7ff7ccbeda6382d003fe66fb485d780d680ff717   0.9.0
                0.2.95    Yes          b63701c85117f220be489d79c1ca5d396ea6caee   0.9.0
Tags:

'''


class TestPlugin(unittest.TestCase):
    def test_constructor(self):
        plugin = Plugin(plugin_text)
        self.assertEqual('container-service', plugin.name)
        self.assertEqual(['container-service', 'kubernetes-service'], plugin.alt_names)
        self.assertEqual(5, len(plugin.versions))
        self.assertEqual('0.4.64', plugin.versions[0].version)

    def test_properties(self):
        plugin = Plugin(plugin_text)
        self.assertEqual('container-service', plugin.name)
        plugin.name = 'name'
        self.assertEqual('name', plugin.name)
        plugin.alt_names = ['name']
        self.assertEqual(['name'], plugin.alt_names)
        plugin.alt_names.append('name2')
        self.assertEqual(['name', 'name2'], plugin.alt_names)
        plugin_version = PluginVersion('0.4.38    Yes          6de09e00dd3bc0cf6f0d6a8e98dc6acdd19e3f01   0.18.2')
        plugin.versions = [plugin_version]
        self.assertEqual([plugin_version], plugin.versions)
        plugin.versions.append(plugin_version)
        self.assertEqual(2, len(plugin.versions))


if __name__ == '__main__':
    unittest.main()
