# -*- coding: utf8 -*-
# ============LICENSE_START====================================================
# org.onap.vvp/validation-scripts
# ===================================================================
# Copyright © 2017 AT&T Intellectual Property. All rights reserved.
# ===================================================================
#
# Unless otherwise specified, all software contained herein is licensed
# under the Apache License, Version 2.0 (the "License");
# you may not use this software except in compliance with the License.
# You may obtain a copy of the License at
#
#             http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
#
# Unless otherwise specified, all documentation contained herein is licensed
# under the Creative Commons License, Attribution 4.0 Intl. (the "License");
# you may not use this documentation except in compliance with the License.
# You may obtain a copy of the License at
#
#             https://creativecommons.org/licenses/by/4.0/
#
# Unless required by applicable law or agreed to in writing, documentation
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# ============LICENSE_END============================================
#
# ECOMP is a trademark and service mark of AT&T Intellectual Property.
#

"""nested files
"""

from os import path
import re
from tests import cached_yaml as yaml

VERSION = '1.0.2'


def get_list_of_nested_files(yml, dirpath):
    '''
    return a list of all nested files
    '''

    if not hasattr(yml, 'items'):
        return []

    nested_files = []

    for v in yml.values():
        if isinstance(v, dict) and "type" in v:
            t = v["type"]
            if t.endswith(".yml") or t.endswith(".yaml"):
                filepath = path.join(dirpath, t)
                if path.exists(filepath):
                    with open(filepath) as fh:
                        t_yml = yaml.load(fh)
                    nested_files.append(filepath)
                    nested_files.extend(get_list_of_nested_files(t_yml, dirpath))
            elif t == "OS::Heat::ResourceGroup":
                rdt = (v.get("properties", {})
                        .get("resource_def", {})
                        .get("type", None))
                if rdt and (rdt.endswith(".yml") or rdt.endswith(".yaml")):
                    filepath = path.join(dirpath, rdt)
                    if path.exists(filepath):
                        with open(filepath) as fh:
                            rdt_yml = yaml.load(fh)
                        nested_files.append(filepath)
                        nested_files.extend(
                            get_list_of_nested_files(rdt_yml, dirpath))
        if isinstance(v, dict):
            nested_files.extend(
                get_list_of_nested_files(v, dirpath))
        elif isinstance(v, list):
            for d in v:
                nested_files.extend(
                    get_list_of_nested_files(d, dirpath))
    return nested_files


def check_for_invalid_nesting(yml, yaml_file, dirpath):
    '''
    return a list of all nested files
    '''
    if not hasattr(yml, 'items'):
        return []
    invalid_nesting = []
    p = re.compile('^[A-z]*::[A-z]*::[A-z]*$')

    for v in yml.values():
        if isinstance(v, dict) and "type" in v:
            t = v["type"]
            if t.endswith(".yml") or t.endswith(".yaml"):
                filepath = path.join(dirpath, t)
            elif t == "OS::Heat::ResourceGroup":
                rd = v["properties"]["resource_def"]
                if not isinstance(rd, dict) or "type" not in rd:
                    invalid_nesting.append(yaml_file)
                    continue
                elif not p.match(rd["type"]):
                    filepath = path.join(dirpath, rd["type"])
                else:
                    continue
            else:
                continue
            try:
                with open(filepath) as fh:
                    yml = yaml.load(fh)
            except yaml.YAMLError as e:
                invalid_nesting.append(filepath)
                print(e)    # pylint: disable=superfluous-parens
            invalid_nesting.extend(check_for_invalid_nesting(
                yml,
                filepath,
                dirpath))
        if isinstance(v, dict):
            invalid_nesting.extend(check_for_invalid_nesting(
                v,
                yaml_file,
                dirpath))
        elif isinstance(v, list):
            for d in v:
                invalid_nesting.extend(check_for_invalid_nesting(
                    d,
                    yaml_file,
                    dirpath))
    return invalid_nesting

