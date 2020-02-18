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
import base64
import os
from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase

DOCUMENTATION = """
  lookup: random_string
  version_added: "2.4"
  short_description: "Generates a random alphanumeric string of a specified length"
  description:
  - "This plugin generates a random string of variable lengths"
  - "urandom is the source of randomness, which is then urlsafe base64 encoded"
  options:
    length:
      description:
      - "The length of the string to generate"
      required: True
"""

EXAMPLES = """
- debug:
    msg: "{{ lookup('random_string', 'length=10')}}"
"""

RETURN = """
_raw:
  description:
  - "The random string that was generated"
"""


class LookupModule(LookupBase):
    def run(self, terms, variables, **kwargs):
        try:
            length = int(terms[0].split('=', 2)[1])
        except ValueError:
            raise AnsibleError('random_string takes parameters of the form length=xxx, received: {params}'.format(params=terms))

        result = base64.urlsafe_b64encode(os.urandom(length)).decode('utf8')
        return [result[0:length]]
