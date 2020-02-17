import re

from orchutils.ibmcloudmodels.pluginversion import PluginVersion


class Plugin(object):
    def __init__(self, plugin_text):
        self.name = re.search(r'Looking up \'([^\']+)\' from repository', plugin_text).group(1)
        self.alt_names = re.search(r'\nName:\s+(\S+)', plugin_text).group(1).split('/')
        self.versions = PluginVersion.parse_plugin_versions(re.search(r'\nVersions:[\s\w]+\n(.+)\nTags:', plugin_text, re.DOTALL).group(1))

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def alt_names(self):
        return self._alt_names

    @alt_names.setter
    def alt_names(self, alt_names):
        self._alt_names = alt_names

    @property
    def versions(self):
        return self._versions

    @versions.setter
    def versions(self, versions):
        self._versions = versions
