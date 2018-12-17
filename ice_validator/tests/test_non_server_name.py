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

"""
resource property name
"""

import pytest

from .structures import Heat
from .helpers import validates

VERSION = "1.1.0"


def get_non_servers(heat):
    """
    Return a dict of non servers.  key is rid, value is resource
    """
    non_servers = {
        rid: resource
        for rid, resource in heat.resources.items()
        if heat.nested_get(resource, "type") != "OS::Nova::Server"
    }
    return non_servers


@validates("R-85734")
def test_non_server_name(heat_template):
    """
    If a VNF's Heat Orchestration Template contains the property ``name``
    for a non ``OS::Nova::Server`` resource, the intrinsic function
    ``str_replace`` **MUST** be used in conjunction with the ECOMP
    supplied metadata parameter ``vnf_name`` to generate a unique value.

    """
    h = Heat(filepath=heat_template)
    if not h.resources:
        pytest.skip("No resources in this template")

    non_servers = get_non_servers(h)
    if not non_servers:
        pytest.skip("No non-server resources in this template")

    bad = []
    for rid, resource in non_servers.items():
        name = h.nested_get(resource, "properties", "name")
        if not name:
            continue

        # Make sure it uses str_replace
        str_replace = name.get("str_replace") if hasattr(name, "get") else None
        if not str_replace:
            bad.append("{}'s name property does not use str_replace".format(rid))
            continue

        # Make sure str_replace is properly formatted
        if not all(key in str_replace for key in ("template", "params")):
            bad.append(
                (
                    "{}'s name property use of str_replace is "
                    + "missing template, params, or both"
                ).format(rid)
            )
            continue
        params = str_replace["params"]
        if not isinstance(params, dict):
            bad.append(
                (
                    "{}'s name property's use of str_replace.params is "
                    + "missing or invalid"
                ).format(rid)
            )
            continue

        # Find the param that uses vnf_name
        vnf_name_param = None
        for key, value in params.items():
            if not isinstance(value, dict):
                continue
            if value.get("get_param", "") == "vnf_name":
                vnf_name_param = key
                break
        if not vnf_name_param:
            bad.append(
                (
                    "{}'s name property's use str_replace does not "
                    + "use have a params that maps to the parameter "
                    "via {{get_param: vnf_name}}"
                ).format(rid)
            )
            continue

        # make sure the VNF name is used in the template string
        template = str_replace.get("template") or ""
        if vnf_name_param not in template:
            bad.append(
                (
                    "{}'s name property's str_replace template does "
                    + "not incorporate vnf_name; expected {} in "
                    + "template ({})"
                ).format(rid, vnf_name_param, template)
            )
    msg = "Improper name property for non-OS::Nova::Server resources. " + ". ".join(bad)

    assert not bad, msg
