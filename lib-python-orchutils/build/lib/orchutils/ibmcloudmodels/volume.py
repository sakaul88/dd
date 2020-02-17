ID = 'id'
USERNAME = 'username'
DATACENTER = 'datacenter'
STORAGE_TYPE = 'storage_type'
CAPACITY_GB = 'capacity_gb'
BYTES_USED = 'bytes_used'
IP_ADDR = 'ip_addr'
MOUNT_ADDR = 'mount_addr'
NOTES = 'notes'
FILE = 'file'


class Volume(object):
    def __init__(self, cli_result_string='', header_indexes=[], volume_type='file'):
        self.volume_type = volume_type
        self.id = None
        self.name = None
        self.datacenter = None
        self.storage_type = None
        self.capacity_gb = None
        self.bytes_used = None
        self.ip_addr = None
        self.mount_addr = None
        self.notes = None
        if cli_result_string:
            self.id = cli_result_string[header_indexes[ID]:].split()[0]
            self.name = cli_result_string[header_indexes[USERNAME]:].split()[0]
            self.datacenter = cli_result_string[header_indexes[DATACENTER]:].split()[0]
            self.storage_type = cli_result_string[header_indexes[STORAGE_TYPE]:].split()[0]
            self.capacity_gb = cli_result_string[header_indexes[CAPACITY_GB]:].split()[0]
            self.bytes_used = cli_result_string[header_indexes[BYTES_USED]:].split()[0]
            self.ip_addr = cli_result_string[header_indexes[IP_ADDR]:].split()[0]
            if self.volume_type == FILE:
                self.mount_addr = cli_result_string[header_indexes[MOUNT_ADDR]:].split()[0]
            self.notes = cli_result_string[header_indexes[NOTES]:]

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id):
        self._id = id

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, username):
        self._name = username

    @property
    def datacenter(self):
        return self._datacenter

    @datacenter.setter
    def datacenter(self, datacenter):
        self._datacenter = datacenter

    @property
    def storage_type(self):
        return self._extractable_storage_type

    @storage_type.setter
    def storage_type(self, storage_type):
        self._extractable_storage_type = storage_type

    @property
    def capacity_gb(self):
        return self._capacity_gb

    @capacity_gb.setter
    def capacity_gb(self, capacity_gb):
        self._capacity_gb = capacity_gb

    @property
    def bytes_used(self):
        return self._bytes_used

    @bytes_used.setter
    def bytes_used(self, bytes_used):
        self._bytes_used = bytes_used

    @property
    def ip_addr(self):
        return self._ip_addr

    @ip_addr.setter
    def ip_addr(self, ip_addr):
        self._ip_addr = ip_addr

    @property
    def mount_addr(self):
        return self._mount_addr

    @mount_addr.setter
    def mount_addr(self, mount_addr):
        self._mount_addr = mount_addr

    @property
    def notes(self):
        return self._notes

    @notes.setter
    def notes(self, notes):
        self._notes = notes

    @property
    def volume_type(self):
        return self._volume_type

    @volume_type.setter
    def volume_type(self, volume_type):
        self._volume_type = volume_type

    @classmethod
    def parse_volumes(cls, cli_return_results_string, volume_type):
        """
        Helper method to parse a list of IKS storage volumes.
        This function iterates over returned IBMCLOUD CLI result, instantiating a Volume object for each line in the list.
        Args:
            cli_return_results: A string of file storage volumes from the ibmcloud cli
        Returns: A list of file storage volumes model objects
        """
        cli_results_split = cli_return_results_string.splitlines()
        cli_return_results_list = list(cli_results_split)

        header_list_indexes = Volume.get_index_list(cli_return_results_list[0], volume_type)
        del cli_return_results_list[0]

        file_volume_model_list = []
        for each_line_in_cli_results in cli_return_results_list:
            file_volume_model_list.append(Volume(each_line_in_cli_results.strip(), header_list_indexes, volume_type))
        return file_volume_model_list

    @classmethod
    def get_index_list(cls, column_header_string, volume_type):
        """Find and add to list the index of each column title from the header fetched from the 'ibmcloud sl file/block volume-list' query.
         Args:
            Str: column_header_string -> First line from the query result return.
            'id, username, datacenter, storage_type, capacity_gb, bytes_used, ip_addr, mount_addr, notes'
        Returns:
            List of indexes of column headers
         """
        header_column_index_list = {}
        header_column_index_list[ID] = column_header_string.index(ID)
        header_column_index_list[USERNAME] = column_header_string.index(USERNAME)
        header_column_index_list[DATACENTER] = column_header_string.index(DATACENTER)
        header_column_index_list[STORAGE_TYPE] = column_header_string.index(STORAGE_TYPE)
        header_column_index_list[CAPACITY_GB] = column_header_string.index(CAPACITY_GB)
        header_column_index_list[BYTES_USED] = column_header_string.index(BYTES_USED)
        header_column_index_list[IP_ADDR] = column_header_string.index(IP_ADDR)
        if volume_type == FILE:
            header_column_index_list[MOUNT_ADDR] = column_header_string.index(MOUNT_ADDR)
        header_column_index_list[NOTES] = column_header_string.index(NOTES)
        return header_column_index_list
