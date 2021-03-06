# -*- coding: utf8 -*-
# ============LICENSE_START=======================================================
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
#
from collections import defaultdict

import pytest
from tests import cached_yaml as yaml

from .helpers import validates


@validates("R-36772", "R-44001")
def test_heat_template_parameters_contain_required_fields(yaml_file):
    """
    Check that all parameters in the environment
    file have the required fields
    """
    required_keys = {"type", "description"}

    with open(yaml_file) as fh:
        yml = yaml.load(fh)

    # skip if parameters are not defined
    if "parameters" not in yml:
        pytest.skip("No parameters specified in the heat template")

    invalid_params = defaultdict(list)
    for param, param_attrs in yml["parameters"].items():
        if not isinstance(param_attrs, dict):
            continue
        for key in required_keys:
            if key not in param_attrs:
                invalid_params[param].append(key)

    msg = [
        "Parameter {} is missing required attribute(s): {}".format(k, ", ".join(v))
        for k, v in invalid_params.items()
    ]
    msg = ". ".join(msg)
    assert not invalid_params, msg
