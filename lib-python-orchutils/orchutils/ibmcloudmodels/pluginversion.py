class PluginVersion(object):
    def __init__(self, version_text):
        version_properties = version_text.split()
        if len(version_properties) != 4:
            raise Exception('Invalid version_text passed to Plugin constructor')
        self.version = version_properties[0]
        self.compatible = version_properties[1]
        self.sha1 = version_properties[2]
        self.min_cli_version = version_properties[3]

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, version):
        self._version = version

    @property
    def compatible(self):
        return self._compatible

    @compatible.setter
    def compatible(self, compatible):
        if isinstance(compatible, str):
            compatible = compatible == 'Yes'
        self._compatible = compatible

    @property
    def sha1(self):
        return self._sha1

    @sha1.setter
    def sha1(self, sha1):
        self._sha1 = sha1

    @property
    def min_cli_version(self):
        return self._min_cli_version

    @min_cli_version.setter
    def min_cli_version(self, min_cli_version):
        self._min_cli_version = min_cli_version

    @classmethod
    def parse_plugin_versions(self, versions_text):
        """
        Helper method to parse a list of plugin versions from the ibmcloud cli output.
        This method simply iterates over the text, instantiating a version object for each valid entry.
        Args:
            version_text: The plugin version text from the ibmcloud cli
        Returns: A list of PluginVersion objects
        """
        plugin_versions = []
        for version_text in versions_text.strip().splitlines():
            version_text = version_text.strip()
            if version_text:
                plugin_versions.append(PluginVersion(version_text))
        return plugin_versions
