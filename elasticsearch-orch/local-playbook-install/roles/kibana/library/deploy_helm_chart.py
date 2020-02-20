#!/usr/bin/python
##############################################################################################
#
# IBM Confidential
#
# OCO Source Materials
#
# (c) Copyright IBM Corp. 2018
# The source code for this program is not published or other-
# wise divested of its trade secrets, irrespective of what has
# been deposited with the U.S. Copyright Office.
##############################################################################################
import json
import logging
import traceback
from orchutils import helm3
import baseutils
from ansible.module_utils.basic import AnsibleModule


logger = logging.getLogger()

ANSIBLE_METADATA = {

    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

RETURN = '''
'''

def run_helm():
    modulename = "elasticsearch"
    baseutils.configure_logger(logger, file_path='/tmp/'+modulename+'.log', level=logging.INFO)
    module_args = {
        'environments': {'type': 'list', 'required': True},
        'charts': {'type': 'list', 'required': True},
        'helm_repository_url': {'type': 'str', 'required': True},
        'enforce_chart_requirements': {'type': 'bool', 'required': True}
    }

    result = {
        'changed': False,
    }

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    try:
        environments = module.params['environments']
        charts = module.params['charts']
        enforce_chart_requirements = module.params['enforce_chart_requirements']
        helm_repository_url = module.params['helm_repository_url']

        for element in charts:
            name = element['name']
            release = element['release']
            logger.info("release = " + release)
            namespace = element['namespace']
            logger.info("namespace = " + namespace)
            chartVersion = element['chartVersion']
            valuesFile = element['valuesFile']
            helm3.install_chart(name,
                          chartVersion,
                          valuesFile,
                          release,
                          namespace)


    except Exception as e:
        print(e)
        logger.error(str(e), exc_info=True)
    module.exit_json(**result)


if __name__ == '__main__':
    run_helm()
