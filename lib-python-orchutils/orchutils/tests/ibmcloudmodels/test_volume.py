import unittest

from orchutils.ibmcloudmodels.volume import Volume

FILE = 'file'
BLOCK = 'block'

header_list_indexes = {'id': 0, 'username': 11, 'datacenter': 37, 'storage_type': 50, 'capacity_gb': 85, 'bytes_used': 99, 'ip_addr': 115, 'mount_addr': 155, 'notes': 227}

file_volume_output_short = '''21873481   IBM02SEV299783_1          sjc03        endurance_file_storage             100           16275072000     fsf-sjc0301d-fz.service.softlayer.com   \
fsf-sjc0301d-fz.service.softlayer.com:/IBM02SEV299783_1/data01          Offering 0 - Nexus - platform'''

file_volume_output_long = '''id         username                  datacenter   storage_type                       capacity_gb   bytes_used      \
ip_addr                                 mount_addr                                                              notes
21873481   IBM02SEV299783_1          sjc03        endurance_file_storage             100           16297476000     \
fsf-sjc0301d-fz.service.softlayer.com   fsf-sjc0301d-fz.service.softlayer.com:/IBM02SEV299783_1/data01          Offering 0 - Nexus - platform
21879125   IBM02SEV299783_2          wdc04        endurance_file_storage             100           555536000       \
fsf-wdc0401b-fz.service.softlayer.com   fsf-wdc0401b-fz.service.softlayer.com:/IBM02SEV299783_2/data01          \
{"plugin":"ibm-file-plugin-798549b8b9-p6p7c","region":"us-south","type":"Endurance","ns":"uss", \
"pvc":"sq60296cp1roo4ncxa8voasi0zyoasb4j107jou5","pv":"pvc-2f2f0152-3531-11e9-8156-86ae1fa837d8","storageclass":"ibmc-file-retain-bronze","reclaim":"Retain"}
21986559   IBM02SEV299783_3          wdc04        endurance_file_storage             250           28299608000     \
fsf-wdc0401b-fz.service.softlayer.com   fsf-wdc0401b-fz.service.softlayer.com:/IBM02SEV299783_3/data01          Offering 1 - Nexus - Digital Commerce
22030747   IBM02SEV299783_4          sjc03        endurance_file_storage             250           22348016000     \
fsf-sjc0301b-fz.service.softlayer.com   fsf-sjc0301b-fz.service.softlayer.com:/IBM02SEV299783_4/data01          NEW Nexus Prod Hub repo WDC04 (replica is in DAL10) \
Snapshot at 46 minutes after the hour, to coordinate with Nexus database export
22032565   IBM02SEV299783_5          wdc04        endurance_file_storage             250           72812452000     \
fsf-wdc0401a-fz.service.softlayer.com   fsf-wdc0401a-fz.service.softlayer.com:/IBM02SEV299783_5/data01          \
{"plugin":"ibm-file-plugin-6fc85ff676-4rqxb","region":"us-south","cluster":"74588575b4844b748725fbd9b95b5092","type":"Endurance","ns":"pltfrm", \
"pvc":"pvc-for-graylog-platform-slave-graylog-slave-0","pv":"pvc-5cd656a6-b211-11e9-882e-06536791a0dc","storageclass":"ibmc-file-bronze","reclaim":"Delete"}   '''

block_volume_output_long = '''id          username            datacenter   storage_type                capacity_gb   bytes_used   \
    ip_addr     notes
44918759    IBM02SEL299783-1    sjc03        endurance_block_storage     4000          -            \
10.3.190.104    Offering 0 - Log Storage test block  #1 (Jon Mc)
88600864    IBM02SEL299783-12   fra02        endurance_block_storage     20            -            \
10.3.94.181     {"plugin":"ibmcloud-block-storage-plugin-79f94979c8-mj8tp","region":"eu-de","cluster":"f7a83ed987114e8093c7405b516301d1","type":"Endurance","ns":"default","pvc":"esblockstorage","pv":"pvc-5fefa855-b9b2-11e9-91da-f26a3561dc95","storageclass":"ibmc-block-retain-gold","reclaim":"Retain"}
47136843    IBM02SEL299783-4    dal10        endurance_block_storage     1000          -            \
161.26.98.120   Offering 2cupdal102dbcas007 /data3600a098038304750615d4c6c33635056
100574496   IBM02SEL299783-15   wdc04        endurance_block_storage     100           -            \
10.201.14.96    {"plugin":"ibmcloud-block-storage-plugin-78f596bf5-6lbx7","cluster":"bm8vok2w06lcuo6n7a2g","type":"Endurance","ns":"oms-fvt01-dev1","pvc":"oms-fvt01-dev1-volume","pv":"pvc-f8bbe0f0-6b63-4169-8f14-6da983a68b64","storageclass":"ibmc-block-gold","reclaim":"Delete"}
100574512   IBM02SEL299783-16   wdc04        endurance_block_storage     20            -            \
10.201.14.94    {"plugin":"ibmcloud-block-storage-plugin-78f596bf5-6lbx7","cluster":"bm8vok2w06lcuo6n7a2g","type":"Endurance","ns":"oms-fvt01-dev1","pvc":"oms-fvt01-dev1-mq-volume","pv":"pvc-0b5fcfd3-bd36-46f4-9cbc-c8f567f020bd","storageclass":"ibmc-block-bronze","reclaim":"Delete"}
51241799    IBM02SEL299783-5    fra02        endurance_block_storage     600           -            \
10.3.94.194     cspv1icupfra022dbcas007.dc.local'''  # noqa


class TestVolumeModelClass(unittest.TestCase):
    def test_constructor(self):
        file_volume_list = Volume(file_volume_output_short, header_list_indexes, FILE)
        self.assertEqual('21873481', file_volume_list.id, "Pass test if ID column value is equal to 21873481")
        self.assertEqual('IBM02SEV299783_1', file_volume_list.name, "Pass test if username column value is equal to IBM02SEV299783_1")
        self.assertEqual('sjc03', file_volume_list.datacenter, "Pass test if datacenter column value is equal to sjc03")
        self.assertEqual('endurance_file_storage', file_volume_list.storage_type, "Pass test if storage_type column value is equal to endurance_file_storage")
        self.assertEqual('100', file_volume_list.capacity_gb, "Pass test if capacity_gb column value is equal to 100")
        self.assertEqual('16275072000', file_volume_list.bytes_used, "Pass test if bytes_used column value is equal to 16275072000")
        self.assertEqual('fsf-sjc0301d-fz.service.softlayer.com', file_volume_list.ip_addr, "Pass test if ip_addr column value is equal to fsf-sjc0301d-fz.service.softlayer.com")
        self.assertEqual('fsf-sjc0301d-fz.service.softlayer.com:/IBM02SEV299783_1/data01', file_volume_list.mount_addr, "Pass test if mount_addr column value is equal \
                        + to fsf-sjc0301d-fz.service.softlayer.com:/IBM02SEV299783_1/data01")
        self.assertEqual('Offering 0 - Nexus - platform', file_volume_list.notes, "Pass test if notes column value is equal to Offering 0 - Nexus - platform")

    def test_file_volume_parse_Volume(self):
        file_volume_list = Volume.parse_volumes(file_volume_output_long, FILE)
        self.assertEqual(5, len(file_volume_list), "Pass if count is equal to 3")
        self.assertEqual('IBM02SEV299783_1', file_volume_list[0].name, "Pass if [0].name value is equal to IBM02SEV299783_1")
        self.assertEqual('fsf-sjc0301d-fz.service.softlayer.com', file_volume_list[0].ip_addr, "Pass if [0].ip_addr value is equal to fsf-sjc0301d-fz.service.softlayer.com")
        self.assertEqual('wdc04', file_volume_list[1].datacenter, "Pass if [1].datacenter value is equal to wdc04")
        self.assertEqual('555536000', file_volume_list[1].bytes_used, "Pass if [1].bytes_used value is equal to 555536000")
        self.assertEqual('Offering 1 - Nexus - Digital Commerce', file_volume_list[2].notes, "Pass if [2].notes value is equal to Offering 1 - Nexus - DC customizations")
        self.assertEqual('NEW Nexus Prod Hub repo WDC04 (replica is in DAL10) Snapshot at 46 minutes after the hour, to coordinate with Nexus database export',
                         file_volume_list[3].notes, "Pass if file_volume_list[3].notes NEW Nexus Prod Hub repo WDC04 (replica is in DAL10) Snapshot at 46.....+")

    def test_block_volume_parse_volumes(self):
        file_volume_list = Volume.parse_volumes(file_volume_output_long, BLOCK)
        self.assertEqual(5, len(file_volume_list), "Pass if count is equal to 3")
        self.assertEqual('IBM02SEV299783_1', file_volume_list[0].name, "Pass if [0].name value is equal to IBM02SEV299783_1")
        self.assertEqual('fsf-sjc0301d-fz.service.softlayer.com', file_volume_list[0].ip_addr, "Pass if [0].ip_addr value is equal to fsf-sjc0301d-fz.service.softlayer.com")
        self.assertEqual('wdc04', file_volume_list[1].datacenter, "Pass if [1].datacenter value is equal to wdc04")
        self.assertEqual('555536000', file_volume_list[1].bytes_used, "Pass if [1].bytes_used value is equal to 555536000")
        self.assertEqual('Offering 1 - Nexus - Digital Commerce', file_volume_list[2].notes, "Pass if [2].notes value is equal to Offering 1 - Nexus - DC customizations")
        self.assertEqual('NEW Nexus Prod Hub repo WDC04 (replica is in DAL10) Snapshot at 46 minutes after the hour, to coordinate with Nexus database export',
                         file_volume_list[3].notes, "Pass if file_volume_list[3].notes NEW Nexus Prod Hub repo WDC04 (replica is in DAL10) Snapshot at 46.....+")

    def test_get_file_index_list(self):
        column_header_string = "id, username, datacenter, storage_type, capacity_gb, bytes_used, ip_addr, mount_addr, notes"
        return_list_expected = {'id': 0, 'username': 4, 'datacenter': 14, 'storage_type': 26, 'capacity_gb': 40, 'bytes_used': 53, 'ip_addr': 65, 'mount_addr': 74, 'notes': 86}
        full_index_list = Volume.get_index_list(column_header_string, FILE)
        self.assertEqual(full_index_list, return_list_expected, "Pass test if return_list_expected is equal to expected column_header_string")

    def test_get_block_index_list(self):
        column_header_string = "id, username, datacenter, storage_type, capacity_gb, bytes_used, ip_addr, notes"
        return_list_expected = {'id': 0, 'username': 4, 'datacenter': 14, 'storage_type': 26, 'capacity_gb': 40, 'bytes_used': 53, 'ip_addr': 65, 'notes': 74}
        full_index_list = Volume.get_index_list(column_header_string, BLOCK)
        self.assertEqual(full_index_list, return_list_expected, "Pass test if return_list_expected is equal to expected column_header_string")

    def test_file_getter_setter(self):
        file_volume_list = Volume(file_volume_output_short, header_list_indexes, FILE)
        self.assertEqual('21873481', file_volume_list.id)
        file_volume_list.id = 1
        self.assertEqual(1, file_volume_list.id)
        file_volume_list.name = 'Foo_1'
        self.assertEqual('Foo_1', file_volume_list.name)
        file_volume_list.datacenter = 'Bar_01'
        self.assertEqual('Bar_01', file_volume_list.datacenter)
        file_volume_list.storage_type = 'test_storage'
        self.assertEqual('test_storage', file_volume_list.storage_type)
        file_volume_list.capacity_gb = 2
        self.assertEqual(2, file_volume_list.capacity_gb)
        file_volume_list.bytes_used = 3
        self.assertEqual(3, file_volume_list.bytes_used)
        file_volume_list.ip_addr = 'test_softlayer.com'
        self.assertEqual('test_softlayer.com', file_volume_list.ip_addr)
        self.assertEqual('fsf-sjc0301d-fz.service.softlayer.com:/IBM02SEV299783_1/data01', file_volume_list.mount_addr)
        file_volume_list.mount_addr = 'test_mount_address'
        self.assertEqual('test_mount_address', file_volume_list.mount_addr)
        file_volume_list.notes = 'test_offering'
        self.assertEqual('test_offering', file_volume_list.notes)
        self.assertEqual('file', file_volume_list.volume_type)
        file_volume_list.volume_type = 'not-file'
        self.assertEqual('not-file', file_volume_list.volume_type)

    def test_block_getter_setter(self):
        file_volume_list = Volume(file_volume_output_short, header_list_indexes, BLOCK)
        self.assertEqual('21873481', file_volume_list.id)
        file_volume_list.id = 1
        self.assertEqual(1, file_volume_list.id)
        file_volume_list.name = 'Foo_1'
        self.assertEqual('Foo_1', file_volume_list.name)
        file_volume_list.datacenter = 'Bar_01'
        self.assertEqual('Bar_01', file_volume_list.datacenter)
        file_volume_list.storage_type = 'test_storage'
        self.assertEqual('test_storage', file_volume_list.storage_type)
        file_volume_list.capacity_gb = 2
        self.assertEqual(2, file_volume_list.capacity_gb)
        file_volume_list.bytes_used = 3
        self.assertEqual(3, file_volume_list.bytes_used)
        file_volume_list.ip_addr = 'test_softlayer.com'
        self.assertEqual('test_softlayer.com', file_volume_list.ip_addr)
        file_volume_list.notes = 'test_offering'
        self.assertEqual('test_offering', file_volume_list.notes)
        self.assertEqual('block', file_volume_list.volume_type)
        file_volume_list.volume_type = 'not-block'
        self.assertEqual('not-block', file_volume_list.volume_type)


if __name__ == '__main__':
    unittest.main()
