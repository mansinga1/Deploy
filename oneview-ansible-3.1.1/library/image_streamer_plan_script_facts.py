#!/usr/bin/python
# -*- coding: utf-8 -*-
###
# Copyright (2016) Hewlett Packard Enterprise Development LP
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
###
from ansible.module_utils.basic import *

try:
    from hpOneView.oneview_client import OneViewClient
    from hpOneView.exceptions import HPOneViewException

    HAS_HPE_ONEVIEW = True
except ImportError:
    HAS_HPE_ONEVIEW = False

DOCUMENTATION = '''
---
module: image_streamer_plan_script_facts
short_description: Retrieve facts about the Image Streamer Plan Scripts.
description:
    - Retrieve facts about one or more of the Image Streamer Plan Script.
requirements:
    - "python >= 2.7.9"
    - "hpOneView >= 3.0.1"
author:
    - "Gustavo Hennig (@GustavoHennig)"
options:
    config:
      description:
        - Path to a .json configuration file containing the OneView client configuration.
          The configuration file is optional. If the file path is not provided, the configuration will be loaded from
          environment variables.
      required: false
    name:
      description:
        - Plan Script name.
      required: false
    params:
      description:
        - List of params to delimit, filter and sort the list of resources.
        - "params allowed:
           'start': The first item to return, using 0-based indexing.
           'count': The number of resources to return.
           'filter': A general filter/query string to narrow the list of items returned.
           'sort': The sort order of the returned data set."
      required: false
notes:
    - "A sample configuration file for the config parameter can be found at:
       https://github.com/HewlettPackard/oneview-ansible/blob/master/examples/oneview_config-rename.json"
    - "Check how to use environment variables for configuration at:
       https://github.com/HewlettPackard/oneview-ansible#environment-variables"
'''

EXAMPLES = '''
- name: Gather facts about all Plan Scripts
  image_streamer_plan_script_facts:
    config: "{{ config }}"
  delegate_to: localhost
- debug: var=plan_scripts

- name: Gather paginated, filtered and sorted facts about Plan Scripts
  image_streamer_plan_script_facts:
    config: "{{ config }}"
    params:
      start: 0
      count: 3
      sort: name:ascending
      filter: planType=capture
  delegate_to: localhost
- debug: var=plan_scripts

- name: Gather facts about a Plan Script by name
  image_streamer_plan_script_facts:
    config: "{{ config }}"
    name: "Demo Plan Script"
  delegate_to: localhost
- debug: var=plan_scripts
'''

RETURN = '''
plan_scripts:
    description: The list of Plan Scripts.
    returned: Always, but can be null.
    type: list
'''

HPE_ONEVIEW_SDK_REQUIRED = 'HPE OneView Python SDK is required for this module.'


class PlanScriptFactsModule(object):
    argument_spec = dict(
        config=dict(required=False, type='str'),
        name=dict(required=False, type='str'),
        options=dict(required=False, type='list'),
        params=dict(required=False, type='dict')
    )

    def __init__(self):
        self.module = AnsibleModule(argument_spec=self.argument_spec, supports_check_mode=False)
        if not HAS_HPE_ONEVIEW:
            self.module.fail_json(msg=HPE_ONEVIEW_SDK_REQUIRED)

        if not self.module.params['config']:
            oneview_client = OneViewClient.from_environment_variables()
        else:
            oneview_client = OneViewClient.from_json_file(self.module.params['config'])

        self.i3s_client = oneview_client.create_image_streamer_client()

    def run(self):
        try:
            name = self.module.params.get("name")

            ansible_facts = {}

            if name:
                plan_scripts = self.i3s_client.plan_scripts.get_by("name", name)
            else:
                params = self.module.params.get('params') or {}
                plan_scripts = self.i3s_client.plan_scripts.get_all(**params)

            ansible_facts['plan_scripts'] = plan_scripts

            self.module.exit_json(changed=False, ansible_facts=ansible_facts)

        except HPOneViewException as exception:
            self.module.fail_json(msg='; '.join(str(e) for e in exception.args))


def main():
    PlanScriptFactsModule().run()


if __name__ == '__main__':
    main()
