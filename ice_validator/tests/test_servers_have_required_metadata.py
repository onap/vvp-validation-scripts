# -*- coding: utf8 -*-
# ============LICENSE_START=======================================================
# org.onap.vvp/validation-scripts
# ===================================================================
# Copyright © 2019 AT&T Intellectual Property. All rights reserved.
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

import pytest
from tests import cached_yaml as yaml

from .helpers import validates


@validates("R-37437", "R-71493", "R-72483")
def test_servers_have_required_metadata(yaml_file):
    """
    Check all defined nova server instances have the required metadata:
    vnf_id, vf_module_id, and vnf_name
    """
    with open(yaml_file) as fh:
        yml = yaml.load(fh)

    if "resources" not in yml:
        pytest.skip("No resources specified in the heat template")

    required_metadata = {"vnf_id", "vf_module_id", "vnf_name"}

    errors = []
    for k, v in yml["resources"].items():
        if v.get("type") != "OS::Nova::Server":
            continue
        if "properties" not in v:
            continue
        if "metadata" not in v["properties"]:
            continue

        metadata = set(v.get("properties", {}).get("metadata", {}).keys())
        missing_metadata = required_metadata.difference(metadata)
        if missing_metadata:
            msg_template = (
                "OS::Nova::Server {} is missing the following "
                + "metadata properties: {}"
            )
            errors.append(msg_template.format(k, missing_metadata))

    assert not errors, "\n".join(errors)
