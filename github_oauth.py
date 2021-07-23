#!/usr/bin/python
#Generate JWT Token for GitHub Apps

DOCUMENTATION = '''
---
module: github_token
description: Generate token using Private key
short_description: Generate token using Private key
options:
  private_key:
    description:
    - GitHub App private key
    required: true
  issuer_claim:
    description:
    - GitHub App issuer claim
    required: true
author: Sukesh Sama
'''

EXAMPLES = '''
- name: Generate JWT token
    github_token:
      issuer_claim: "{{ issuer_claim_from_github }}"
      private_key: "{{ githubsshkey_in_base64_format }}"
    register: _jwttoken
'''

from ansible.module_utils.basic import *
from ansible.executor.playbook_executor import PlaybookExecutor

import jwt
import base64

def main():
    fields = {
        "issuer_claim": {"default": True, "type": "str"},
        "private_key": {"default": True, "type": "str"}
    }
    module = AnsibleModule(argument_spec=fields)
    secret = module.params['private_key']
    
    utc_time = datetime.datetime.utcnow()
    expiry_time = utc_time + datetime.timedelta(seconds=600) #token expiry time is 10minutes

    jwt_payload = {"iat": utc_time,  "exp": expiry_time,  "iss":  module.params['issuer_claim']}

    encoded = jwt.encode(jwt_payload, base64.b64decode(secret), algorithm="RS256")
    
    result = {
        'token': encoded,
    }
    
    module.exit_json(changed=True, metadata=result)
    
if __name__ == '__main__':
    main()
