import datetime
import unittest

from orchutils.ibmcloudmodels.ikscluster import IKSCluster

clusters_json = [
    {
        'location': 'sjc03',
        'dataCenter': 'sjc03',
        'multiAzCapable': False,
        'vlans': None,
        'worker_vlans': None,
        'workerZones': [
            'sjc03'
        ],
        'id': '2fc5c4f6fd9540999d95e3a2d833e710',
        'name': 'test-priv-nosub',
        'region': 'us-south',
        'resourceGroup': '5f91fc3fba594e959af7ceabfb0a7278',
        'resourceGroupName': 'P2PaaS-Platform-Arch',
        'serverURL': 'https://c9.sjc03.containers.cloud.ibm.com:24175',
        'state': 'normal',
        'createdDate': '2019-02-25T16:44:56+0000',
        'modifiedDate': '2019-02-25T16:44:56+0000',
        'workerCount': 4,
        'isPaid': True,
        'masterKubeVersion': '1.11.8_1547',
        'targetVersion': '1.11.8_1547',
        'ingressHostname': '',
        'ingressSecretName': '',
        'ownerEmail': 'DNEMEC@US.IBM.COM',
        'logOrg': '',
        'logOrgName': '',
        'logSpace': '',
        'logSpaceName': '',
        'apiUser': '',
        'monitoringURL': 'https://metrics.ng.bluemix.net/app/#/grafana4/dashboard/db/a-69a92444d0c448d',
        'addons': None,
        'isTrusted': False,
        'versionEOS': '',
        'disableAutoUpdate': False,
        'etcdPort': '25629',
        'masterStatus': 'Ready',
        'masterStatusModifiedDate': '2019-03-05T11:09:06+0000',
        'keyProtectEnabled': False,
        'pullSecretApplied': True,
        'crn': 'crn:v1:bluemix:public:containers-kubernetes:us-south:a/69a92444d0c448d994ceb2f517b2fd39:2fc5c4f6fd9540999d95e3a2d833e710::'
    },
    {
        'location': 'sjc03',
        'dataCenter': 'sjc03',
        'multiAzCapable': False,
        'vlans': None,
        'worker_vlans': None,
        'workerZones': [
            'sjc03'
        ],
        'id': '00b0b711b4894f2da241e33b76a62c08',
        'name': 'test-refarch_54a01b6d',
        'region': 'us-south',
        'resourceGroup': '5f91fc3fba594e959af7ceabfb0a7278',
        'resourceGroupName': 'P2PaaS-Platform-Arch',
        'serverURL': 'https://c9.sjc03.containers.cloud.ibm.com:20677',
        'state': 'normal',
        'createdDate': '2019-01-29T13:41:27+0000',
        'modifiedDate': '2019-01-29T13:41:27+0000',
        'workerCount': 6,
        'isPaid': True,
        'masterKubeVersion': '1.12.6_1541',
        'targetVersion': '1.12.6_1541',
        'ingressHostname': 'test-refarch54a01b6d.sjc03.containers.appdomain.cloud',
        'ingressSecretName': 'test-refarch54a01b6d',
        'ownerEmail': 'DNEMEC@US.IBM.COM',
        'logOrg': '',
        'logOrgName': '',
        'logSpace': '',
        'logSpaceName': '',
        'apiUser': '',
        'monitoringURL': 'https://metrics.ng.bluemix.net/app/#/grafana4/dashboard/db/a-69a92444d0c448d994ceb2f517b2fd3',
        'addons': None,
        'isTrusted': False,
        'versionEOS': '',
        'disableAutoUpdate': False,
        'etcdPort': '26279',
        'masterStatus': 'Ready',
        'masterStatusModifiedDate': '2019-03-05T10:09:15+0000',
        'keyProtectEnabled': False,
        'pullSecretApplied': True,
        'crn': 'crn:v1:bluemix:public:containers-kubernetes:us-south:a/69a92444d0c448d994ceb2f517b2fd39:00b0b711b4894f2da241e33b76a62c08::'
    },
    {
        'location': 'fra04',
        'dataCenter': 'fra04',
        'multiAzCapable': False,
        'vlans': None,
        'worker_vlans': None,
        'workerZones': [
            'fra04'
        ],
        'id': '008uc248r498u324tv893un48934753v',
        'name': 'test-monaco',
        'region': 'us-east',
        'resourceGroup': '748vny78nyt23578ty2378tvy378ty23',
        'resourceGroupName': 'test-monaco-ny3874yt',
        'serverURL': 'https://c9.fra04.containers.cloud.ibm.com:20677',
        'state': 'normal',
        'createdDate': '2019-01-29T19:11:48+0000',
        'modifiedDate': '2019-01-29T19:11:48+0000',
        'workerCount': 6,
        'isPaid': True,
        'masterKubeVersion': '1.12.6_1541',
        'targetVersion': '1.12.6_1541',
        'ingressHostname': 'test-monaco-ny3874yt.fra04.containers.appdomain.cloud',
        'ingressSecretName': 'test-monaco-ny3874yt',
        'ownerEmail': 'DNEMEC@US.IBM.COM',
        'logOrg': '',
        'logOrgName': '',
        'logSpace': '',
        'logSpaceName': '',
        'apiUser': '',
        'monitoringURL': 'https://metrics.ng.bluemix.net/app/#/grafana4/dashboard/db/a-69a92444d0c448d994ceb2f517b2fd3',
        'addons': None,
        'isTrusted': False,
        'versionEOS': '',
        'disableAutoUpdate': False,
        'etcdPort': '26279',
        'masterStatus': 'Ready',
        'masterStatusModifiedDate': '2019-03-05T10:09:15+0000',
        'keyProtectEnabled': False,
        'pullSecretApplied': True,
        'crn': 'crn:v1:bluemix:public:containers-kubernetes:us-south:a/69a92444d0c448d994ceb2f517b2fd39:00b0b711b4894f2da241e33b76a62c08::'
    }
]


class TestIKSCluster(unittest.TestCase):
    def test_constructor(self):
        cluster = IKSCluster(clusters_json[0])
        self.assertEqual('2fc5c4f6fd9540999d95e3a2d833e710', cluster.id)
        self.assertEqual('test-priv-nosub', cluster.name)
        self.assertEqual('us-south', cluster.region)
        self.assertEqual(['sjc03'], cluster.zones)
        self.assertEqual('P2PaaS-Platform-Arch', cluster.resource_group_name)
        self.assertEqual('5f91fc3fba594e959af7ceabfb0a7278', cluster.resource_group_id)
        self.assertEqual('1.11.8_1547', cluster.master_kube_version)
        self.assertEqual('1.11.8_1547', cluster.target_version)
        self.assertEqual('Ready', cluster.master_status)
        self.assertEqual(False, cluster.key_protect_enabled)
        self.assertEqual(True, cluster.pull_secret_applied)
        self.assertEqual(datetime.datetime.strptime(clusters_json[0]['createdDate'], '%Y-%m-%dT%H:%M:%S+0000'), cluster.created_date)

    def test_properties(self):
        cluster = IKSCluster(clusters_json[0])
        self.assertEqual('2fc5c4f6fd9540999d95e3a2d833e710', cluster.id)
        cluster.id = 'newid'
        self.assertEqual('newid', cluster.id)
        cluster.name = 'cluster_name'
        self.assertEqual('cluster_name', cluster.name)
        cluster.region = 'region'
        self.assertEqual('region', cluster.region)
        cluster.zones = ['dal10']
        self.assertEqual(['dal10'], cluster.zones)
        cluster.zones.append('dal13')
        self.assertEqual(['dal10', 'dal13'], cluster.zones)
        cluster.resource_group_name = 'resource_group_name'
        self.assertEqual('resource_group_name', cluster.resource_group_name)
        cluster.resource_group_id = 'resource_group_id'
        self.assertEqual('resource_group_id', cluster.resource_group_id)
        cluster.master_kube_version = '1.0.1_123'
        self.assertEqual('1.0.1_123', cluster.master_kube_version)
        cluster.target_version = '1.0.2_123'
        self.assertEqual('1.0.2_123', cluster.target_version)
        cluster.master_status = 'status'
        self.assertEqual('status', cluster.master_status)
        cluster.key_protect_enabled = True
        self.assertEqual(True, cluster.key_protect_enabled)
        cluster.pull_secret_applied = False
        self.assertEqual(False, cluster.pull_secret_applied)
        now = datetime.datetime.utcnow().replace(microsecond=0)
        cluster.created_date = now
        self.assertEqual(now, cluster.created_date)
        cluster.created_date = now.strftime('%Y-%m-%dT%H:%M:%S+0000')
        self.assertEqual(now, cluster.created_date)

    def test_parse_ikscluster(self):
        clusters = IKSCluster.parse_iks_clusters(clusters_json)
        self.assertEqual(3, len(clusters))
        self.assertEqual('2fc5c4f6fd9540999d95e3a2d833e710', clusters[0].id)
        self.assertEqual('00b0b711b4894f2da241e33b76a62c08', clusters[1].id)
        self.assertEqual('008uc248r498u324tv893un48934753v', clusters[2].id)


if __name__ == '__main__':
    unittest.main()
