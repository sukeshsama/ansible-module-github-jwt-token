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
      issuer_claim: "{{ github_issuer_claim }}"
      private_key: "{{ githubsshkey }}" #provide private in base64 format
    register: _jwttoken         
- name: Generate Oauth token
    uri:
      url:  "https://api.github.com/app/installations/{{ github_installation_id }}/access_tokens"
      method: POST
      headers:
        Authorization: "Bearer {{ _jwttoken.metadata.token }}"
        Accept: "application/vnd.github.v3+json"
      status_code: [201]
    register: _oauth
- set_fact:
    github_token: "{{ _oauth.json.token }}"
  no_log: true
  
- name: Create GitHub Project 
  shell: >
    curl -v -sS \
    -X POST \
    -H "Accept: application/vnd.github.nebula-preview+json" \
    -H "Authorization: Bearer {{ github_token }}" \
    https://api.github.com/orgs/{{ github_group }}/repos \
    -d '{"name":"{{ repo_name }}","visibility":"{{ scope }}"}'
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
