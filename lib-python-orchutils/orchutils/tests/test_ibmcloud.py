import json
import os
import signal
import sys
import unittest
from mock import Mock
from mock import patch

import baseutils
from orchutils import ibmcloud
from orchutils.ibmcloudmodels.servicepolicy import ServicePolicy
from orchutils.ibmcloudmodels.target import Target
from helpers.test_k8shelpers import namespace_pods_partial
from ibmcloudmodels.test_albcertificate import alb_certificates_json
from ibmcloudmodels.test_clusteralbs import clusteralbs_json
from ibmcloudmodels.test_ikscluster import clusters_json
from ibmcloudmodels.test_iksworker import workers_json
from ibmcloudmodels.test_iksworkerpool import worker_pools_json
from ibmcloudmodels.test_kpkey import kp_keys_json
from ibmcloudmodels.test_serviceinstance import service_instances_json
from ibmcloudmodels.test_servicekey import service_keys_json
from ibmcloudmodels.test_servicepolicy import service_policies_json
from ibmcloudmodels.test_subnet import subnets_json
from ibmcloudmodels.test_target import target_json
from ibmcloudmodels.test_volume import file_volume_output_long


class TestIBMCloud(unittest.TestCase):
    def test_set_config_dir(self):
        self.assertFalse('IBMCLOUD_HOME' in os.environ)
        home_dir = '/tmp'
        self.assertIsNone(ibmcloud.set_config_dir(home_dir))
        self.assertEqual(home_dir, os.environ['IBMCLOUD_HOME'])
        del os.environ['IBMCLOUD_HOME']

    @patch('baseutils.exe_cmd')
    def test_apply_pull_secret(self, mock_exe_cmd):
        self.assertIsNone(ibmcloud.apply_pull_secret('cluster-name'))
        self.assertEqual(1, mock_exe_cmd.call_count)

    @patch('baseutils.exe_cmd')
    def test_configure_kubecfg(self, mock_exe_cmd):
        mock_exe_cmd.return_value = (0, '')
        self.assertIsNone(ibmcloud.configure_kubecfg('cluster'))
        self.assertEqual(1, mock_exe_cmd.call_count)

    @patch('baseutils.exe_cmd')
    def test_configure_alb(self, mock_exe_cmd):
        self.assertIsNone(ibmcloud.configure_alb('id'))
        self.assertEqual(1, mock_exe_cmd.call_count)
        self.assertIsNone(ibmcloud.configure_alb('id', False))
        self.assertEqual(2, mock_exe_cmd.call_count)

    @patch('baseutils.exe_cmd')
    def test_get_albs(self, mock_exe_cmd):
        mock_exe_cmd.return_value = (0, json.dumps(clusteralbs_json))
        clusteralbs = ibmcloud.get_albs('cluster_name')
        self.assertEqual(clusteralbs_json['id'], clusteralbs.id)
        self.assertEqual(1, mock_exe_cmd.call_count)

    @patch('baseutils.exe_cmd')
    def test_get_iks_clusters(self, mock_exe_cmd):
        mock_exe_cmd.return_value = (0, '[]')
        self.assertEqual([], ibmcloud.get_iks_clusters())
        self.assertEqual(1, mock_exe_cmd.call_count)
        mock_exe_cmd.return_value = (1, 'The specified cluster could not be found. (A0006)')
        self.assertEqual(None, ibmcloud.get_iks_clusters('name'))
        self.assertEqual(2, mock_exe_cmd.call_count)
        mock_exe_cmd.return_value = (1, '')
        self.assertRaises(Exception, ibmcloud.get_iks_clusters, 'cluster')
        mock_exe_cmd.return_value = (0, json.dumps(clusters_json))
        self.assertEqual(3, len(ibmcloud.get_iks_clusters()))
        mock_exe_cmd.return_value = (0, json.dumps(clusters_json[0]))
        cluster = ibmcloud.get_iks_clusters('test-priv-nosub')
        self.assertEqual('test-priv-nosub', cluster.name)

    @patch('time.sleep')
    @patch('baseutils.exe_cmd')
    def test_replace_iks_workers(self, mock_exe_cmd, mock_sleep):
        if os.name == 'nt':
            signal.SIGALRM = signal.SIGTERM
            signal.alarm = Mock()
        mock_exe_cmd.return_value = (0, json.dumps(workers_json))
        workers = ibmcloud.ks_worker_ls('cluster')
        upgraded_worker_json = workers_json[0].copy()
        upgraded_worker_json['kubeVersion'] = upgraded_worker_json['targetVersion']
        mock_exe_cmd.side_effect = [
            (0, json.dumps(workers_json[0])),
            (0, ''),
            (0, ''),
            (0, json.dumps(upgraded_worker_json)),
            (0, ''),
            (0, namespace_pods_partial),
            (0, json.dumps(workers_json[1])),
            (0, ''),
            (0, ''),
            (0, json.dumps(upgraded_worker_json)),
            (0, ''),
            (0, namespace_pods_partial)
        ]
        self.assertIsNone(ibmcloud.replace_iks_workers('cluster', workers))
        self.assertEqual(13, mock_exe_cmd.call_count)
        if os.name == 'nt':
            del signal.SIGALRM
            del signal.alarm

    @patch('time.sleep')
    @patch('baseutils.exe_cmd')
    def test_wait_for_worker(self, mock_exe_cmd, mock_sleep):
        if os.name == 'nt':
            signal.SIGALRM = signal.SIGTERM
            signal.alarm = Mock()
        mock_exe_cmd.return_value = (0, json.dumps(workers_json))
        workers = ibmcloud.ks_worker_ls('cluster')
        workers_json[0]['kubeVersion'] = workers_json[0]['targetVersion']
        mock_exe_cmd.side_effect = [
            (0, json.dumps(workers_json[0])),
            (0, ''),
            (0, namespace_pods_partial)
        ]
        self.assertIsNone(ibmcloud.wait_for_worker('cluster', workers[0]))
        self.assertEqual(4, mock_exe_cmd.call_count)
        if os.name == 'nt':
            del signal.SIGALRM
            del signal.alarm

    @patch('baseutils.exe_cmd')
    def test_update_iks_cluster(self, mock_exe_cmd):
        mock_exe_cmd.return_value = (0, json.dumps(clusters_json[0]))
        self.assertIsNone(ibmcloud.update_iks_cluster('cluster', clusters_json[0]['masterKubeVersion'].split('_')[0]))
        self.assertEqual(1, mock_exe_cmd.call_count)
        mock_exe_cmd.side_effect = [
            (0, json.dumps(clusters_json[0])),
            (0, ''),
            (0, json.dumps(clusters_json[0]))
        ]
        self.assertIsNone(ibmcloud.update_iks_cluster('cluster', '1.0.0'))
        self.assertEqual(2, mock_exe_cmd.call_count)

    @patch('baseutils.exe_cmd')
    def test_ks_cluster_get(self, mock_exe_cmd):
        mock_exe_cmd.return_value = (1, 'The specified cluster could not be found. (A0006)')
        self.assertEqual(None, ibmcloud.ks_cluster_get('name'))
        self.assertEqual(1, mock_exe_cmd.call_count)
        mock_exe_cmd.return_value = (1, '')
        self.assertRaises(Exception, ibmcloud.ks_cluster_get, 'cluster')
        mock_exe_cmd.return_value = (0, json.dumps(clusters_json[0]))
        cluster = ibmcloud.ks_cluster_get('test-priv-nosub')
        self.assertEqual('test-priv-nosub', cluster.name)
        self.assertIn('get --cluster \'test-priv-nosub\'', mock_exe_cmd.call_args[0][0])

    @patch('baseutils.exe_cmd')
    def test_ks_cluster_ls(self, mock_exe_cmd):
        mock_exe_cmd.return_value = (0, '[]')
        self.assertEqual([], ibmcloud.ks_cluster_ls())
        self.assertEqual(1, mock_exe_cmd.call_count)
        self.assertIn('ks cluster ls', mock_exe_cmd.call_args[0][0])
        mock_exe_cmd.return_value = (0, json.dumps(clusters_json))
        clusters = ibmcloud.ks_cluster_ls()
        self.assertEqual(3, len(clusters))
        self.assertEqual('test-priv-nosub', clusters[0].name)

    @patch('baseutils.exe_cmd')
    def test_ks_worker_get(self, mock_exe_cmd):
        mock_exe_cmd.return_value = (1, 'The specified worker node could not be found. (E0011)')
        self.assertEqual(None, ibmcloud.ks_worker_get('cluster', 'w1_id'))
        self.assertEqual(1, mock_exe_cmd.call_count)
        mock_exe_cmd.return_value = (1, '')
        with self.assertRaises(Exception) as context:
            ibmcloud.ks_worker_get('cluster', 'w1_id')
        self.assertIn('Error during call to ibmcloud cli', str(context.exception))
        self.assertEqual(2, mock_exe_cmd.call_count)
        mock_exe_cmd.return_value = (0, json.dumps(workers_json[0]))
        self.assertEqual('kube-sjc03-cra8efa36505be48d0a382aa2fa7081082-w1', ibmcloud.ks_worker_get('cluster', 'kube-sjc03-cra8efa36505be48d0a382aa2fa7081082-w1').id)
        self.assertEqual(3, mock_exe_cmd.call_count)

    @patch('baseutils.exe_cmd')
    def test_ks_worker_ls(self, mock_exe_cmd):
        mock_exe_cmd.return_value = (0, '[]')
        self.assertEqual([], ibmcloud.ks_worker_ls('cluster'))
        self.assertEqual(1, mock_exe_cmd.call_count)
        mock_exe_cmd.return_value = (0, json.dumps(workers_json))
        self.assertEqual('kube-sjc03-cra8efa36505be48d0a382aa2fa7081082-w1', ibmcloud.ks_worker_ls('cluster')[0].id)
        self.assertEqual(2, mock_exe_cmd.call_count)
        self.assertNotIn('--worker-pool', mock_exe_cmd.call_args[0][0])
        self.assertEqual('kube-sjc03-cra8efa36505be48d0a382aa2fa7081082-w1', ibmcloud.ks_worker_ls('cluster', worker_pool_name='pool')[0].id)
        self.assertEqual(3, mock_exe_cmd.call_count)
        self.assertIn('--worker-pool \'pool\'', mock_exe_cmd.call_args[0][0])

    @patch('baseutils.exe_cmd')
    def test_ks_worker_pool_create_classic(self, mock_exe_cmd):
        mock_exe_cmd.return_value = (0, '')
        self.assertIsNone(ibmcloud.ks_worker_pool_create_classic('cluster', 'pool', 'machine', 2, 'shared'))
        self.assertEqual(1, mock_exe_cmd.call_count)
        self.assertIn('--cluster \'cluster\'', mock_exe_cmd.call_args[0][0])
        self.assertIn('--name \'pool\'', mock_exe_cmd.call_args[0][0])
        self.assertIn('--machine-type \'machine\'', mock_exe_cmd.call_args[0][0])
        self.assertIn('--size-per-zone 2', mock_exe_cmd.call_args[0][0])
        self.assertIn('--hardware \'shared\'', mock_exe_cmd.call_args[0][0])
        self.assertNotIn('--label', mock_exe_cmd.call_args[0][0])
        self.assertIsNone(ibmcloud.ks_worker_pool_create_classic('cluster', 'pool', 'machine', 2, 'shared', {'key1': 'value1'}))
        self.assertEqual(2, mock_exe_cmd.call_count)
        self.assertIn('--label \'key1=value1\'', mock_exe_cmd.call_args[0][0])

    @patch('baseutils.exe_cmd')
    def test_ks_worker_pool_get(self, mock_exe_cmd):
        mock_exe_cmd.return_value = (0, json.dumps(worker_pools_json[0]))
        self.assertEqual('bm12clsw08k9uctrq8cg-d423e5a', ibmcloud.ks_worker_pool_get('cluster', 'pool').id)
        self.assertEqual(1, mock_exe_cmd.call_count)
        self.assertIn('--cluster \'cluster\'', mock_exe_cmd.call_args[0][0])
        self.assertIn('--worker-pool \'pool\'', mock_exe_cmd.call_args[0][0])

    @patch('baseutils.exe_cmd')
    def test_ks_worker_pool_ls(self, mock_exe_cmd):
        mock_exe_cmd.return_value = (0, '[]')
        self.assertEqual([], ibmcloud.ks_worker_pool_ls('cluster'))
        self.assertEqual(1, mock_exe_cmd.call_count)
        mock_exe_cmd.return_value = (0, json.dumps(worker_pools_json))
        self.assertEqual('bm12clsw08k9uctrq8cg-d423e5a', ibmcloud.ks_worker_pool_ls('cluster')[0].id)
        self.assertEqual(2, mock_exe_cmd.call_count)

    @patch('requests.patch')
    @patch('baseutils.exe_cmd')
    def test_ks_worker_pool_labels(self, mock_exe_cmd, mock_patch):
        mock_exe_cmd.return_value = (0, '{"iam_token": "Bearer token"}')
        self.assertIsNone(ibmcloud.ks_worker_pool_labels('cluster', 'pool', {'key': 'value'}))
        self.assertEqual(1, mock_exe_cmd.call_count)
        self.assertEqual(1, mock_patch.call_count)
        self.assertIn('/cluster/workerpools/pool', mock_patch.call_args[0][0])
        self.assertEqual({'state': 'labels', 'labels': {'key': 'value'}}, mock_patch.call_args[1]['json'])

    @patch('baseutils.exe_cmd')
    def test_ks_worker_pool_rm(self, mock_exe_cmd):
        mock_exe_cmd.return_value = (0, '')
        self.assertIsNone(ibmcloud.ks_worker_pool_rm('cluster', 'pool'))
        self.assertEqual(1, mock_exe_cmd.call_count)
        self.assertIn(' --cluster \'cluster\'', mock_exe_cmd.call_args[0][0])
        self.assertIn(' --worker-pool \'pool\' -f', mock_exe_cmd.call_args[0][0])

    @patch('baseutils.exe_cmd')
    def test_ks_zone_add_classic(self, mock_exe_cmd):
        mock_exe_cmd.return_value = (0, '')
        self.assertIsNone(ibmcloud.ks_zone_add_classic('cluster', 'zone', 'pool', 'private_vlan_id', public_vlan_id='public_vlan_id'))
        self.assertIn('public-vlan', mock_exe_cmd.call_args[0][0])
        self.assertNotIn('private-only', mock_exe_cmd.call_args[0][0])
        self.assertIsNone(ibmcloud.ks_zone_add_classic('cluster', 'zone', 'pool', 'private_vlan_id',))
        self.assertNotIn('public-vlan', mock_exe_cmd.call_args[0][0])
        self.assertIn('private-only', mock_exe_cmd.call_args[0][0])

    @patch('baseutils.exe_cmd')
    def test_ks_cluster_remove(self, mock_exe_cmd):
        mock_exe_cmd.return_value = (0, '')
        self.assertIsNone(ibmcloud.ks_cluster_remove('cluster'))

    @patch('time.sleep')
    @patch('baseutils.exe_cmd')
    def test_ks_enable_key_protect(self, mock_exe_cmd, mock_sleep):
        cluster_json = json.dumps(clusters_json[0])
        cluster_modified = json.loads(cluster_json)
        cluster_modified['keyProtectEnabled'] = True
        cluster_modified = json.dumps(cluster_modified)
        mock_exe_cmd.side_effect = [
            (0, cluster_json),
            (0, ''),
            (0, cluster_json),
            (0, cluster_modified)
        ]
        self.assertIsNone(ibmcloud.ks_enable_key_protect('cluster', 'us-east', 'guid', 'id'))

    @patch('baseutils.exe_cmd')
    def test_get_resource_service_instances(self, mock_exe_cmd):
        mock_exe_cmd.return_value = (0, '[]')
        self.assertEqual([], ibmcloud.get_resource_service_instances())
        self.assertEqual(1, mock_exe_cmd.call_count)
        mock_exe_cmd.return_value = (0, json.dumps(service_instances_json))
        self.assertEqual(2, len(ibmcloud.get_resource_service_instances()))
        instances = ibmcloud.get_resource_service_instances(name='P2PaaS-Platform-NonProd-COS')
        self.assertEqual(1, len(instances))
        self.assertEqual('P2PaaS-Platform-NonProd-COS', instances[0].name)
        instances = ibmcloud.get_resource_service_instances(name='alan-test', location='global')
        self.assertEqual(1, len(instances))
        self.assertEqual('alan-test', instances[0].name)
        instances = ibmcloud.get_resource_service_instances(name='alan-test', service='cloud-object-storage')
        self.assertEqual(1, len(instances))
        self.assertEqual('alan-test', instances[0].name)
        instances = ibmcloud.get_resource_service_instances(name='alan-test', service='cloud-object-storage', location='global')
        self.assertEqual(1, len(instances))
        self.assertEqual('alan-test', instances[0].name)

    @patch('baseutils.exe_cmd')
    def test_create_resource_service_instance(self, mock_exe_cmd):
        mock_exe_cmd.return_value = (0, '')
        self.assertIsNone(ibmcloud.create_resource_service_instance('name', 'service', 'plan', 'location'))
        self.assertEqual(1, mock_exe_cmd.call_count)
        self.assertIsNone(ibmcloud.create_resource_service_instance('name', 'service', 'plan', 'location', parameters={'key': 'value'}))
        self.assertEqual(2, mock_exe_cmd.call_count)

    @patch('baseutils.exe_cmd')
    def test_get_user_access_groups(self, mock_exe_cmd):
        mock_output = '''OK
Name                                       ID                                                   Description
Add cases and view orders                  AccessGroupId-kztcwlwp-pjdx-rxdn-7oz0-bi02ujgdguw6   DO NOT DELETE.  This Access Group is used for classic infrastructure permission migration.
adhoc-query-np-editor                      AccessGroupId-jfxljaeo-1vi1-wzyb-ven2-cdpebl3bcf8z
common-ui-np-auditor                       AccessGroupId-ghnhwodv-sjow-smmp-53ze-apux8g0tjqgg
common-ui-np-editor                        AccessGroupId-kpvcqehd-lx5c-mm3l-koib-c2wqgm8qwvcv
Edit cases                                 AccessGroupId-8oaylqjo-4vbz-gqfx-p0bh-es0adtdbdm8g   DO NOT DELETE.  This Access Group is used for classic infrastructure permission migration.
Edit company profile                       AccessGroupId-kwprgr8p-fdqm-ty43-zifz-z0jcsmsttbzp   DO NOT DELETE.  This Access Group is used for classic infrastructure permission migration.
Get compliance report                      AccessGroupId-mdocuajp-kxta-qowd-fuih-etywhcuivpiv   DO NOT DELETE.  This Access Group is used for classic infrastructure permission migration.
One-time payments                          AccessGroupId-cvshtqvp-gqsc-iezw-fdpm-t06rg9v6mhod   DO NOT DELETE.  This Access Group is used for classic infrastructure permission migration.
oss-data-science-pr-auditor                AccessGroupId-itif1vtg-32op-timv-jrz3-i1ajgkjfodzy
wce-faas-pr-viewer                         AccessGroupId-kdphtsms-atjc-v5hk-d8mg-bjdzuisqezke
''' # noqa
        mock_exe_cmd.return_value = (0, mock_output)
        expected_result = [
            'Add cases and view orders',
            'adhoc-query-np-editor',
            'common-ui-np-auditor',
            'common-ui-np-editor',
            'Edit cases',
            'Edit company profile',
            'Get compliance report',
            'One-time payments',
            'oss-data-science-pr-auditor',
            'wce-faas-pr-viewer']
        result = ibmcloud.get_user_access_groups('johndoe@ibm.com')
        self.assertEqual(result, expected_result)

    @patch('baseutils.exe_cmd')
    def test_get_resource_service_keys(self, mock_exe_cmd):
        mock_exe_cmd.return_value = (0, '[]')
        self.assertEqual([], ibmcloud.get_resource_service_keys())
        self.assertEqual(1, mock_exe_cmd.call_count)
        mock_exe_cmd.return_value = (0, json.dumps(service_keys_json))
        self.assertEqual(1, len(ibmcloud.get_resource_service_keys()))
        keys = ibmcloud.get_resource_service_keys(instance_id='myid')
        self.assertEqual(1, len(keys))
        self.assertEqual('P2PaaS-Platform-NonProd-COS', keys[0].name)
        keys = ibmcloud.get_resource_service_keys(name='P2PaaS-Platform-NonProd-COS', instance_id='myid')
        self.assertEqual(1, len(keys))
        self.assertEqual('P2PaaS-Platform-NonProd-COS', keys[0].name)
        keys = ibmcloud.get_resource_service_keys(name='myname')
        self.assertEqual(0, len(keys))

    @patch('baseutils.exe_cmd')
    def test_create_resource_service_key(self, mock_exe_cmd):
        mock_exe_cmd.return_value = (0, '')
        self.assertIsNone(ibmcloud.create_resource_service_key('name', 'role', 'instance-id'))
        self.assertEqual(1, mock_exe_cmd.call_count)
        self.assertIsNone(ibmcloud.create_resource_service_key('name', 'role', 'instance-id', service_endpoint='private'))
        self.assertEqual(2, mock_exe_cmd.call_count)
        self.assertIsNone(ibmcloud.create_resource_service_key('name', 'role', 'instance-id', parameters={'key': 'value'}))
        self.assertEqual(3, mock_exe_cmd.call_count)
        self.assertIsNone(ibmcloud.create_resource_service_key('name', 'role', 'instance-id', service_endpoint='public', parameters={'key': 'value'}))
        self.assertEqual(4, mock_exe_cmd.call_count)

    @patch('baseutils.exe_cmd')
    def test_get_subnets(self, mock_exe_cmd):
        mock_exe_cmd.return_value = (0, '[]')
        self.assertEqual([], ibmcloud.get_subnets())
        self.assertEqual(1, mock_exe_cmd.call_count)
        self.assertEqual([], ibmcloud.get_subnets(ids='1111'))
        self.assertEqual(2, mock_exe_cmd.call_count)
        self.assertEqual([], ibmcloud.get_subnets(note='note'))
        self.assertEqual(3, mock_exe_cmd.call_count)
        mock_exe_cmd.return_value = (0, json.dumps(subnets_json))
        subnets = ibmcloud.get_subnets(ids=['1970265'])
        self.assertEqual(1, len(subnets))
        self.assertEqual('1970265', subnets[0].id)
        subnets = ibmcloud.get_subnets(note='iks-platform-hub-pr-dal')
        self.assertEqual(1, len(subnets))
        self.assertEqual('1922973', subnets[0].id)
        subnets = ibmcloud.get_subnets(ids=['1922973'], note='iks-platform-hub-pr-dal')
        self.assertEqual(1, len(subnets))
        self.assertEqual('1922973', subnets[0].id)

    @patch('baseutils.exe_cmd')
    def test_add_cluster_subnet(self, mock_exe_cmd):
        self.assertIsNone(ibmcloud.add_cluster_subnet('cluster_id', 'subnet_id'))
        self.assertEqual(1, mock_exe_cmd.call_count)

    @patch('baseutils.exe_cmd')
    def test_get_kube_versions(self, mock_exe_cmd):
        mock_exe_cmd.return_value = (0, '''
{
    "kubernetes": [
        {
            "major": 1,
            "minor": 12,
            "patch": 10,
            "default": false,
            "end_of_service": ""
        },
        {
            "major": 1,
            "minor": 13,
            "patch": 10,
            "default": false,
            "end_of_service": ""
        },
        {
            "major": 1,
            "minor": 14,
            "patch": 6,
            "default": true,
            "end_of_service": ""
        },
        {
            "major": 1,
            "minor": 15,
            "patch": 3,
            "default": false,
            "end_of_service": ""
        }
    ],
    "openshift": [
        {
            "major": 3,
            "minor": 11,
            "patch": 135,
            "default": false,
            "end_of_service": ""
        }
    ]
}''')
        self.assertEqual(['1.12.10', '1.13.10', '1.14.6', '1.15.3'], ibmcloud.get_kube_versions())
        self.assertEqual('1.13.10', ibmcloud.get_kube_versions('1.13'))
        self.assertEqual('1.13.10', ibmcloud.get_kube_versions('1.13.3'))
        self.assertEqual(None, ibmcloud.get_kube_versions('1.10'))

    @patch('baseutils.exe_cmd')
    def test_login(self, mock_exe_cmd):
        self.assertIsNone(ibmcloud.login('key', 'us-south', 'r-group'))
        self.assertEqual(1, mock_exe_cmd.call_count)
        self.assertIn('-r \'us-south\'', mock_exe_cmd.call_args_list[0][0][0])
        self.assertIn('-g \'r-group\'', mock_exe_cmd.call_args_list[0][0][0])
        self.assertIn('--apikey \'key\'', mock_exe_cmd.call_args_list[0][0][0])
        self.assertIsNone(ibmcloud.login('key', region='us-south', resource_group='r-group'))
        self.assertEqual(2, mock_exe_cmd.call_count)
        self.assertIn('-r \'us-south\'', mock_exe_cmd.call_args_list[1][0][0])
        self.assertIn('-g \'r-group\'', mock_exe_cmd.call_args_list[1][0][0])
        self.assertIn('--apikey \'key\'', mock_exe_cmd.call_args_list[1][0][0])
        self.assertIsNone(ibmcloud.login('key'))
        self.assertEqual(3, mock_exe_cmd.call_count)
        self.assertNotIn('-r ', mock_exe_cmd.call_args_list[2][0][0])
        self.assertIn('--no-region', mock_exe_cmd.call_args_list[2][0][0])
        self.assertNotIn('-g', mock_exe_cmd.call_args_list[2][0][0])
        self.assertIn('--apikey \'key\'', mock_exe_cmd.call_args_list[2][0][0])

    @patch('baseutils.exe_cmd')
    def test_target(self, mock_exe_cmd):
        mock_exe_cmd.return_value = (0, '')
        self.assertIsNone(ibmcloud.target(region='us-south', resource_group='r-group', org='org', space='space'))
        self.assertEqual(1, mock_exe_cmd.call_count)
        self.assertIsNone(ibmcloud.target(region='us-south'))
        self.assertEqual(2, mock_exe_cmd.call_count)
        self.assertIsNone(ibmcloud.target(resource_group='r-group'))
        self.assertEqual(3, mock_exe_cmd.call_count)
        self.assertIsNone(ibmcloud.target(org='org', space='space'))
        self.assertEqual(4, mock_exe_cmd.call_count)
        mock_exe_cmd.return_value = (0, json.dumps(target_json))
        target = ibmcloud.target()
        self.assertIsInstance(target, Target)
        self.assertEqual(5, mock_exe_cmd.call_count)
        self.assertEqual(target.account.guid, target_json['account']['guid'])
        self.assertEqual(target.api_endpoint, target_json['api_endpoint'])
        self.assertEqual(target.region.mccp_id, target_json['region']['mccp_id'])
        self.assertEqual(target.user.display_name, target_json['user']['display_name'])

    @patch('baseutils.exe_cmd')
    def test_ks_alb_cert_ls(self, mock_exe_cmd):
        mock_exe_cmd.return_value = (0, json.dumps(alb_certificates_json))
        alb_certificates = ibmcloud.ks_alb_cert_ls(alb_certificates_json[0]['clusterID'])
        self.assertEqual(len(alb_certificates_json), len(alb_certificates))
        self.assertEqual(alb_certificates_json[0]['clusterID'], alb_certificates[0].cluster_id)
        self.assertEqual(1, mock_exe_cmd.call_count)
        mock_exe_cmd.return_value = (0, 'null')
        self.assertEqual([], ibmcloud.ks_alb_cert_ls('cluster'))
        self.assertEqual(2, mock_exe_cmd.call_count)

    @patch('baseutils.exe_cmd')
    def test_ks_alb_cert_deploy(self, mock_exe_cmd):
        side_effect = [
            (0, json.dumps(alb_certificates_json)),
            (0, '')
        ]
        mock_exe_cmd.side_effect = side_effect
        self.assertIsNone(ibmcloud.ks_alb_cert_deploy(alb_certificates_json[0]['clusterID'], 'secret_name', 'cert_crn'))
        self.assertEqual(2, mock_exe_cmd.call_count)
        self.assertNotIn('--update', mock_exe_cmd.call_args_list[1][0][0])
        mock_exe_cmd.side_effect = side_effect
        self.assertIsNone(ibmcloud.ks_alb_cert_deploy(alb_certificates_json[0]['clusterID'], alb_certificates_json[0]['secretName'], 'cert_crn'))
        self.assertEqual(4, mock_exe_cmd.call_count)
        self.assertIn('--update', mock_exe_cmd.call_args_list[3][0][0])

    @patch('baseutils.exe_cmd')
    def test_ks_infra_credentials(self, mock_exe_cmd):
        self.assertIsNone(ibmcloud.ks_infra_credentials('sl_user', 'sl_key'))
        self.assertEqual(1, mock_exe_cmd.call_count)
        self.assertIn('ks credential set classic', mock_exe_cmd.call_args_list[0][0][0])
        self.assertIn('--infrastructure-username \'sl_user\'', mock_exe_cmd.call_args_list[0][0][0])
        self.assertIn('--infrastructure-api-key \'sl_key\'', mock_exe_cmd.call_args_list[0][0][0])

    @patch('baseutils.exe_cmd')
    def test_ks_cluster_master_auditwebhook_set(self, mock_exe_cmd):
        self.assertIsNone(ibmcloud.ks_cluster_master_auditwebhook_set('cluster', 'http://url'))
        self.assertEqual(1, mock_exe_cmd.call_count)

    @patch('baseutils.exe_cmd')
    def test_ks_cluster_master_refresh(self, mock_exe_cmd):
        self.assertIsNone(ibmcloud.ks_cluster_master_refresh('cluster'))
        self.assertEqual(1, mock_exe_cmd.call_count)

    @patch('baseutils.exe_cmd')
    def test_iam_oauth_tokens(self, mock_exe_cmd):
        expected_result = {
             'iam_token': 'Bearer 123'
        }
        mock_exe_cmd.return_value = (0, json.dumps(expected_result))
        self.assertEqual(expected_result, ibmcloud.iam_oauth_tokens())

    @patch('baseutils.exe_cmd')
    def test_iam_service_policies(self, mock_exe_cmd):
        mock_exe_cmd.return_value = (0, json.dumps(service_policies_json))
        policies = ibmcloud.iam_service_policies('service-id')
        self.assertEqual(1, len(policies))
        self.assertEqual('11ec84df-8ef0-4186-8dce-76023432a338', policies[0].id)

    @patch('baseutils.exe_cmd')
    def test_iam_service_policy_update(self, mock_exe_cmd):
        mock_exe_cmd.return_value = (0, '')
        policy = ServicePolicy(service_policies_json[0])
        self.assertIsNone(ibmcloud.iam_service_policy_update('service-id', policy))

    @patch('baseutils.exe_cmd')
    def test_kp_create(self, mock_exe_cmd):
        mock_exe_cmd.return_value = (0, json.dumps(kp_keys_json[0]))
        self.assertEqual('387c4fb0-4ca7-4075-8bc8-51a9ec51ad8a', ibmcloud.kp_create('2ea53eef-a93b-4c58-a654-d0f2b4effd27', 'name').id)
        self.assertEqual('387c4fb0-4ca7-4075-8bc8-51a9ec51ad8a', ibmcloud.kp_create('2ea53eef-a93b-4c58-a654-d0f2b4effd27', 'name', key_material='b64=').id)
        self.assertEqual('387c4fb0-4ca7-4075-8bc8-51a9ec51ad8a', ibmcloud.kp_create('2ea53eef-a93b-4c58-a654-d0f2b4effd27', 'name', standard_key=True).id)

    @patch('baseutils.exe_cmd')
    def test_kp_list(self, mock_exe_cmd):
        mock_exe_cmd.return_value = (0, 'null')
        self.assertEqual([], ibmcloud.kp_list('2ea53eef-a93b-4c58-a654-d0f2b4effd27'))
        mock_exe_cmd.return_value = (0, json.dumps(kp_keys_json))
        keys = ibmcloud.kp_list('2ea53eef-a93b-4c58-a654-d0f2b4effd27')
        self.assertEqual(2, len(keys))
        self.assertEqual('387c4fb0-4ca7-4075-8bc8-51a9ec51ad8a', keys[0].id)
        self.assertEqual('47f623ff-f2a5-45ff-9258-31c75f0253cf', keys[1].id)
        keys = ibmcloud.kp_list('2ea53eef-a93b-4c58-a654-d0f2b4effd27', name='mykey')
        self.assertEqual(1, len(keys))
        self.assertEqual('47f623ff-f2a5-45ff-9258-31c75f0253cf', keys[0].id)

    @patch('baseutils.exe_cmd')
    def test_file_volume_parse_volumes(self, mock_exe_cmd):
        mock_exe_cmd.return_value = (0, file_volume_output_long)
        file_volume_list = ibmcloud.file_volume_list()
        self.assertEqual(5, len(file_volume_list), "Pass if returned object number count is equal to 3")
        self.assertEqual('21873481', file_volume_list[0].id, "Pass if [0].id value from element object in position 0 is equal to 21873481")
        self.assertEqual('wdc04', file_volume_list[1].datacenter, "Pass if [1].datacenter value from element object in position 1 is equal to wdc04")
        self.assertEqual('28299608000', file_volume_list[2].bytes_used, "Pass if [2].bytes_used value from element object in position 2 is equal to 72812452000")

    @patch('baseutils.exe_cmd')
    def test_block_volume_parse_volumes(self, mock_exe_cmd):
        mock_exe_cmd.return_value = (0, file_volume_output_long)
        block_volume_list = ibmcloud.block_volume_list()
        self.assertEqual(5, len(block_volume_list), "Pass if returned object number count is equal to 3")
        self.assertEqual('21873481', block_volume_list[0].id, "Pass if [0].id value from element object in position 0 is equal to 21873481")
        self.assertEqual('wdc04', block_volume_list[1].datacenter, "Pass if [1].datacenter value from element object in position 1 is equal to wdc04")
        self.assertEqual('28299608000', block_volume_list[2].bytes_used, "Pass if [2].bytes_used value from element object in position 2 is equal to 72812452000")

    @patch('baseutils.exe_cmd')
    def test_sl_volume_detail(self, mock_exe_cmd):
        mock_volume_details = '''Name                       Value
ID                         107091018
User name                  IBM02SEL299783-112
Type                       endurance_block_storage
Capacity (GB)              80
LUN Id                     4
Endurance Tier             10_IOPS_PER_GB
Endurance Tier Per IOPS    10
Datacenter                 wdc04
Target IP                  10.201.14.79
# of Active Transactions   1
Ongoing Transactions       This is a buffer time in which the customer may cancel the server
Replicant Count            0
'''
        mock_exe_cmd.return_value = (0, mock_volume_details)
        volume = ibmcloud.sl_volume_detail('107091018', 'block')
        self.assertEqual(volume.volume_type, 'block')
        self.assertEqual(volume.id, '107091018')
        self.assertEqual(volume.name, 'IBM02SEL299783-112')
        self.assertEqual(volume.datacenter, 'wdc04')
        self.assertEqual(volume.capacity_gb, '80')
        self.assertEqual(volume.ip_addr, '10.201.14.79')
        self.assertEqual(volume.storage_type, 'endurance_block_storage')
        self.assertEqual(volume.active_transactions, 1)
        self.assertEqual(volume.replicant_count, '0')
        self.assertIsNone(volume.bytes_used)
        self.assertIsNone(volume.notes)

    @patch('baseutils.exe_cmd')
    def test_sl_file_volume_cancel(self, mock_exe_cmd):
        ibmcloud.sl_file_volume_cancel("12345")
        mock_exe_cmd.assert_called_with('/usr/local/bin/ibmcloud sl file volume-cancel \'12345\' --immediate -f')

    @patch('baseutils.exe_cmd')
    def test_sl_block_volume_cancel(self, mock_exe_cmd):
        ibmcloud.sl_block_volume_cancel("54321")
        mock_exe_cmd.assert_called_with('/usr/local/bin/ibmcloud sl block volume-cancel \'54321\' --immediate -f')

    @patch('baseutils.exe_cmd')
    def test_sl_call_api(self, mock_exe_cmd):
        mock_exe_cmd.return_value = (0, '{"key": "value"}')
        result = ibmcloud.sl_call_api('SoftLayer_Network_Storage', 'getBillingItem', '12345', mask='invoiceItem[totalOneTimeAmount,totalRecurringAmount]',
                                      parameters='', limit='0', offset='0')
        mock_exe_cmd.assert_called_with('/usr/local/bin/ibmcloud sl call-api SoftLayer_Network_Storage getBillingItem \
--init \'12345\' --mask \'invoiceItem[totalOneTimeAmount,totalRecurringAmount]\'  --limit \'0\' --offset \'0\'')
        self.assertEqual(type(result), type({}))

    def test_setup_cli(self):
        # This is linux-specific and will not work on windows or mac
        if sys.platform not in ('win32', 'darwin'):
            self.assertIsNone(ibmcloud.setup_cli())
            self.assertIsNone(ibmcloud.setup_cli(False))
            self.assertIsNone(ibmcloud.setup_cli(True))
            plugins_dir = os.listdir(os.path.join(os.environ.get('IBMCLOUD_HOME', os.environ['HOME']), '.bluemix', 'plugins'))
            self.assertIn('container-service', plugins_dir)
            self.assertIn('container-registry', plugins_dir)
            self.assertIn('key-protect', plugins_dir)

    def test_plugin_install(self):
        # This is linux-specific and will not work on windows or mac
        if sys.platform not in ('win32', 'darwin'):
            ibmcloud.setup_cli()
            self.assertIsNone(ibmcloud.plugin_install('container-service', version='0.3'))
            (rc, output) = baseutils.exe_cmd('/usr/local/bin/ibmcloud plugin show container-service | grep "Plugin Version"')
            self.assertTrue(output.split()[-1].startswith('0.3.'))
            self.assertIsNone(ibmcloud.plugin_install('container-service', repository='IBM Cloud', version='0.4'))
            (rc, output) = baseutils.exe_cmd('/usr/local/bin/ibmcloud plugin show container-service | grep "Plugin Version"')
            self.assertTrue(output.split()[-1].startswith('0.4.'))


if __name__ == '__main__':
    unittest.main()
