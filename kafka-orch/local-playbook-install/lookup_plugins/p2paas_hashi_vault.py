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
import time
from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase
from ansible.plugins.lookup.hashi_vault import HashiVault

DOCUMENTATION = """
  lookup: p2paas_hashi_vault
  version_added: "2.4"
  short_description: "Retrieve secrets from Vault, retrying up to 10 times on lookup failure"
  requirements:
    - "hvac (python library)"
  description:
    - "This plugin calls into the hashi_corp plugin to retrieve secrets from Vault. It will retry up to 10 times if a failure occurs"
    - "VAULT_TOKEN and VAULT_ADDR must be passed as environment variables where they will be read by the hashi_corp plugin. See that plugin for details"
  options:
    secret:
      description:
      - "Path to the secret to retrieve"
      required: True
"""

EXAMPLES = """
- debug:
    msg: "{{ lookup('p2paas_hashi_vault', 'secret=secret/path/to/secret:password')}}"
"""

RETURN = """
_raw:
  description:
  - "The data retrieved from the call to the downstream hashi_vault plugin"
"""


class LookupModule(LookupBase):
    def run(self, terms, variables, **kwargs):
        try:
            secret = terms[0].split('=', 2)[1]
        except ValueError:
            raise AnsibleError('p2paas_hashi_vault takes parameters of the form secret=xxx, received: {params}'.format(params=terms))
        ret = []

        attempt = 1
        while not ret:
            try:
                vault_conn = HashiVault(secret=secret, validate_certs=False)
                ret.append(vault_conn.get())
            except Exception:
                if attempt < 10:
                    attempt += 1
                    time.sleep(20)
                else:
                    raise

        return ret
