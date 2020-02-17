import unittest
import json

from mock import patch

from orchutils import ibmcloud
from orchutils.helpers import volumehelpers

from ibmcloudmodels.test_volume import file_volume_output_long
from ibmcloudmodels.test_volume import block_volume_output_long

# CONSTANTS
ID = 'id'
CLUSTER = 'cluster'

cluster_json = [
        {
            "location": "Frankfurt",
            "dataCenter": "fra02",
            "multiAzCapable": True,
            "vlans": None,
            "worker_vlans": None,
            "workerZones": [
                "fra02"
            ],
            "id": "9bbcb91437be4ba89edb9594a524777b",
            "name": "biz-trans-intel-app-np-fra",
            "region": "eu-de",
            "resourceGroup": "dd5569ffc8c2454c89700301e8f42822",
            "resourceGroupName": "biz-trans-intel-app-np",
            "serverURL": "https://c2.eu-de.containers.cloud.ibm.com:32159",
            "state": "normal",
            "createdDate": "2019-04-08T20:14:45+0000",
            "modifiedDate": "2019-04-08T20:14:45+0000",
            "workerCount": 5,
            "isPaid": True,
            "masterKubeVersion": "1.13.10_1534",
            "targetVersion": "1.14.6_1531",
            "ingressHostname": "biz-trans-intel-app-np-fra.eu-de.containers.appdomain.cloud",
            "ingressSecretName": "biz-trans-intel-app-np-fra",
            "ownerEmail": "ccsp-automation@ca.ibm.com",
            "logOrg": "",
            "logOrgName": "",
            "logSpace": "",
            "logSpaceName": "",
            "apiUser": "299783_svc_csp_ccsp-automation@ca.ibm.com",
            "monitoringURL": "",
            "addons": None,
            "isTrusted": False,
            "versionEOS": "",
            "disableAutoUpdate": False,
            "etcdPort": "24354",
            "masterStatus": "Ready",
            "masterStatusModifiedDate": "2019-09-03T11:33:43+0000",
            "masterHealth": "normal",
            "masterState": "deployed",
            "keyProtectEnabled": True,
            "pullSecretApplied": True,
            "crn": "crn:v1:bluemix:public:containers-kubernetes:eu-de:a/69a92444d0c448d994ceb2f517b2fd39:1b99445aebb740b890d6d2de73728bcb::",
            "privateServiceEndpointEnabled": True,
            "privateServiceEndpointURL": "https://c2.private.eu-de.containers.cloud.ibm.com:32159",
            "publicServiceEndpointEnabled": True,
            "publicServiceEndpointURL": "https://c2.eu-de.containers.cloud.ibm.com:32159",
            "podSubnet": "",
            "serviceSubnet": "",
            "type": "kubernetes"
        },
        {
            "location": "Frankfurt",
            "dataCenter": "fra02",
            "multiAzCapable": True,
            "vlans": None,
            "worker_vlans": None,
            "workerZones": [
                "fra02"
            ],
            "id": "37f49cd781014a91b07a9d8a6e67d11c",
            "name": "platform-hub-np-fra",
            "region": "eu-de",
            "resourceGroup": "caf60fc4514c420c86d2040feb352ef2",
            "resourceGroupName": "platform-np",
            "serverURL": "https://c2.eu-de.containers.cloud.ibm.com:28973",
            "state": "normal",
            "createdDate": "2019-04-08T20:13:38+0000",
            "modifiedDate": "2019-04-08T20:13:38+0000",
            "workerCount": 5,
            "isPaid": True,
            "masterKubeVersion": "1.13.10_1534",
            "targetVersion": "1.14.6_1531",
            "ingressHostname": "platform-hub-np-fra.eu-de.containers.appdomain.cloud",
            "ingressSecretName": "platform-hub-np-fra",
            "ownerEmail": "ccsp-automation@ca.ibm.com",
            "logOrg": "",
            "logOrgName": "",
            "logSpace": "",
            "logSpaceName": "",
            "apiUser": "299783_svc_csp_ccsp-automation@ca.ibm.com",
            "monitoringURL": "",
            "addons": None,
            "isTrusted": False,
            "versionEOS": "",
            "disableAutoUpdate": False,
            "etcdPort": "28200",
            "masterStatus": "Ready",
            "masterStatusModifiedDate": "2019-09-03T10:29:05+0000",
            "masterHealth": "normal",
            "masterState": "deployed",
            "keyProtectEnabled": True,
            "pullSecretApplied": True,
            "crn": "crn:v1:bluemix:public:containers-kubernetes:eu-de:a/69a92444d0c448d994ceb2f517b2fd39:9eeffbf923774f4eb929782f4c94a682::",
            "privateServiceEndpointEnabled": True,
            "privateServiceEndpointURL": "https://c2.private.eu-de.containers.cloud.ibm.com:28973",
            "publicServiceEndpointEnabled": True,
            "publicServiceEndpointURL": "https://c2.eu-de.containers.cloud.ibm.com:28973",
            "podSubnet": "",
            "serviceSubnet": "",
            "type": "kubernetes"
        },
        {
            "location": "sjc03",
            "dataCenter": "sjc03",
            "multiAzCapable": False,
            "vlans": None,
            "worker_vlans": None,
            "workerZones": [
                "sjc03"
            ],
            "id": "ea9b73607ff04e0da79ea730f583bf0b",
            "name": "platform-orchestration-np-sjc03",
            "region": "us-south",
            "resourceGroup": "caf60fc4514c420c86d2040feb352ef2",
            "resourceGroupName": "platform-np",
            "serverURL": "https://c9.sjc03.containers.cloud.ibm.com:28155",
            "state": "normal",
            "createdDate": "2019-06-27T17:56:44+0000",
            "modifiedDate": "2019-06-27T17:56:44+0000",
            "workerCount": 5,
            "isPaid": True,
            "masterKubeVersion": "1.15.3_1515",
            "targetVersion": "1.15.3_1515",
            "ingressHostname": "platform-orchestration.sjc03.containers.appdomain.cloud",
            "ingressSecretName": "platform-orchestration",
            "ownerEmail": "ccsp-automation@ca.ibm.com",
            "logOrg": "",
            "logOrgName": "",
            "logSpace": "",
            "logSpaceName": "",
            "apiUser": "299783_svc_csp_ccsp-automation@ca.ibm.com",
            "monitoringURL": "",
            "addons": None,
            "isTrusted": False,
            "versionEOS": "",
            "disableAutoUpdate": False,
            "etcdPort": "23074",
            "masterStatus": "Ready",
            "masterStatusModifiedDate": "2019-09-02T14:33:57+0000",
            "masterHealth": "normal",
            "masterState": "deployed",
            "keyProtectEnabled": True,
            "pullSecretApplied": True,
            "crn": "crn:v1:bluemix:public:containers-kubernetes:us-south:a/69a92444d0c448d994ceb2f517b2fd39:ea9b73607ff04e0da79ea730f583bf0b::",
            "privateServiceEndpointEnabled": True,
            "privateServiceEndpointURL": "https://c9.private.sjc03.containers.cloud.ibm.com:28155",
            "publicServiceEndpointEnabled": True,
            "publicServiceEndpointURL": "https://c9.sjc03.containers.cloud.ibm.com:28155",
            "podSubnet": "",
            "serviceSubnet": "",
            "type": "kubernetes"
        }
]


def get_id(orphan_list):
    for note_col_string in orphan_list:
        load_list = json.loads(note_col_string.notes)
        cluster_id = load_list[CLUSTER]
    return cluster_id


class TestVolumeHelpers(unittest.TestCase):
    @patch('baseutils.exe_cmd')
    def test_get_volume_list(self, mock_exe_cmd):
        mock_exe_cmd.side_effect = [(0, file_volume_output_long), (0, block_volume_output_long)]
        volume_list = volumehelpers.get_volume_list()
        self.assertEqual(len(volume_list), 11)

    @patch('baseutils.exe_cmd')
    def test_get_iks_volume_list(self, mock_exe_cmd):
        mock_exe_cmd.side_effect = [(0, file_volume_output_long), (0, block_volume_output_long)]
        iks_volume_list = volumehelpers.get_iks_volume_list()
        self.assertEqual(len(iks_volume_list), 4)

    @patch('baseutils.exe_cmd')
    def test_get_volume_notes(self, mock_exe_cmd):
        mock_exe_cmd.return_value = (0, file_volume_output_long)
        file_volume_list = ibmcloud.file_volume_list()
        notes = volumehelpers.get_volume_notes(file_volume_list[0])
        self.assertFalse(notes)
        notes = volumehelpers.get_volume_notes(file_volume_list[1])
        self.assertTrue(notes)

    @patch('baseutils.exe_cmd')
    def test_separate_volumes_by_type(self, mock_exe_cmd):
        mock_exe_cmd.side_effect = [(0, file_volume_output_long), (0, block_volume_output_long)]
        volume_list = volumehelpers.get_volume_list()
        file_volumes, block_volumes = volumehelpers.separate_volumes_by_type(volume_list)
        self.assertEqual(len(file_volumes), 5)
        self.assertEqual(len(block_volumes), 6)

    @patch('baseutils.exe_cmd')
    def test_get_volume_orphan_list(self, mock_exe_cmd):
        mock_exe_cmd.return_value = (0, file_volume_output_long)
        file_volume_list = ibmcloud.file_volume_list()
        cluster_ids = [cluster[ID] for cluster in cluster_json]
        orphan_list = volumehelpers.get_volume_orphan_list(cluster_ids, file_volume_list)
        self.assertEqual(1, len(orphan_list))
        orphan_id = get_id(orphan_list)
        self.assertEqual("74588575b4844b748725fbd9b95b5092", orphan_id)
        self.assertEqual("22032565", orphan_list[0].id)


if __name__ == '__main__':
    unittest.main()
