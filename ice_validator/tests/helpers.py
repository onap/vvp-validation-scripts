# -*- coding: utf8 -*-
# ============LICENSE_START=======================================================
# org.onap.vvp/validation-scripts
# ===================================================================
# Copyright © 2017 AT&T Intellectual Property. All rights reserved.
# ===================================================================
#
# Unless otherwise specified, all software contained herein is licensed
# under the Apache License, Version 2.0 (the “License”);
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
# under the Creative Commons License, Attribution 4.0 Intl. (the “License”);
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

import yaml
from boltons import funcutils


def check_basename_ending(template_type, basename):
    '''
    return True/False if the template type is matching
    the filename
    '''
    if not template_type:
        return True
    elif template_type == 'volume':
        return basename.endswith('_volume')
    else:
        return not basename.endswith('_volume')


def get_parsed_yml_for_yaml_files(yaml_files, sections=[]):
    '''
    get the parsed yaml for a list of yaml files
    '''
    parsed_yml_list = []
    for yaml_file in yaml_files:
        yml = ''

        try:
            with open(yaml_file) as fh:
                yml = yaml.load(fh)
        except Exception as e:
            print(e)

        if yml:
            if sections:
                for k in yml.keys():
                    if k not in sections:
                        del yml[k]
            parsed_yml_list.append(yml)

    return parsed_yml_list

def validates(*requirement_ids):
    """Decorator that tags the test function with one or more requirement IDs.

    Example:
        >>> @validates('R-12345', 'R-12346')
        ... def test_something():
        ...     pass
        >>> assert test_something.requirement_ids == ['R-12345', 'R-12346']
    """
    def decorator(func):
        # NOTE: We use a utility here to ensure that function signatures are
        # maintained because pytest inspects function signatures to inject
        # fixtures.  I experimented with a few options, but this is the only
        # library that worked. Other libraries dynamically generated a
        # function at run-time, and then lost the requirement_ids attribute
        @funcutils.wraps(func)
        def wrapper(*args, **kw):
            return func(*args, **kw)
        wrapper.requirement_ids = requirement_ids
        return wrapper
    decorator.requirement_ids = requirement_ids
    return decorator
