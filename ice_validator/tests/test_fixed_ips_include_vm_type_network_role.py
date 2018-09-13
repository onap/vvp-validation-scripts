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
# ECOMP is a trademark and service mark of AT&T Intellectual Property.
#

import pytest
from tests import cached_yaml as yaml

from .helpers import validates
from .utils.ports import get_invalid_ip_addresses


@validates('R-40971',
           'R-27818',
           'R-29765',
           'R-85235',
           'R-78380',
           'R-23503',
           'R-71577',
           'R-04697',
           'R-34037')
def test_fixed_ips_include_vm_type_network_role(heat_template):
    '''
    Check that all fixed_ips ip addresses include the {vm_type} of the
    nova server it is associated to and also contains the {network_role}
    of the network it is associated with
    '''
    with open(heat_template) as fh:
        yml = yaml.load(fh)

    # skip if resources are not defined
    if "resources" not in yml:
        pytest.skip("No resources specified in the heat template")

    if "parameters" not in yml:
        pytest.skip("No parameters specified in the heat template")

    invalid_ip_addresses = get_invalid_ip_addresses(yml['resources'],
                                                    "fixed_ips",
                                                    yml["parameters"])

    assert not set(invalid_ip_addresses)
