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
#

"""
resources:
{vm-type}_{vm-type_index}_{network-role}_port_{port-index}:
  type: OS::Neutron::Port
  properties:
    network: { get_param: ...}
    fixed_ips: [ { "ipaddress": { get_param: ... } } ]
    binding:vnic_type: direct           #only SR-IOV ports, not OVS ports
    value_specs: {
      vlan_filter: { get_param: ... },  #all NC ports
      public_vlans: { get_param: ... }, #all NC ports
      private_vlans: { get_param: ... },#all NC ports
      guest_vlans: { get_param: ... },  #SR-IOV Trunk Port only
      vlan_mirror: { get_param: ... },  #SRIOV Trunk Port
                                        # Receiving Mirrored Traffic only
     ATT_FABRIC_CONFIGURATION_REQUIRED: true #all NC ports
    }
  metadata:
    port_type: SR-IOV_Trunk             #SR-IOV Trunk Port
    port_type: SR-IOV_Non_Trunk         #SR-IOV Non Trunk Port
    port_type: OVS                      #OVS Port
    port_type: SR-IOV_Mirrored_Trunk    #SR-IOV Trunk Port
                                        # Receiving Mirrored Traffic
"""
import re

from tests.utils.network_roles import get_network_type_from_port
from tests.parametrizers import get_nested_files

from .structures import Heat
from .helpers import validates, load_yaml, get_base_template_from_yaml_files
from .utils.ports import check_ip_format

VERSION = "1.3.0"

RE_EXTERNAL_PARAM_SUBNET = re.compile(  # match pattern
    r"(?P<network_role>.+)(?<!_v6)(_v6)?_subnet_id$"
)

RE_INTERNAL_PARAM_SUBNET = re.compile(  # match pattern
    r"int_(?P<network_role>.+)(?<!_v6)(_v6)?_subnet_id$"
)

fip_regx_dict = {
    "external": {
        "string": {
            "readable": "{network-role}_subnet_id or {network-role}_v6_subnet_id",
            "machine": RE_EXTERNAL_PARAM_SUBNET,
        }
    },
    "internal": {
        "string": {
            "readable": "int_{network-role}_subnet_id or int_{network-role}_v6_subnet_id",
            "machine": RE_INTERNAL_PARAM_SUBNET,
        }
    },
    "parameter_to_resource_comparisons": ["network_role"],
}


@validates("R-38236", "R-84123", "R-76160")
def test_internal_subnet_format(yaml_file):
    check_ip_format(yaml_file, fip_regx_dict, "internal", "fixed_ips", "subnet")


@validates("R-38236", "R-62802", "R-15287")
def test_external_subnet_format(yaml_file):
    check_ip_format(yaml_file, fip_regx_dict, "external", "fixed_ips", "subnet")


@validates("R-84123", "R-76160")
def test_neutron_port_internal_fixed_ips_subnet_in_base(yaml_files):
    """
    Only check parent incremental modules, because nested file parameter
    name may have been changed.

    When

      * the VNF's Heat Orchestration Template's
        resource ``OS::Neutron::Port`` in an Incremental Module is attaching
        to an internal network
        that is created in the Base Module, AND
      * an IPv4 address is being cloud assigned by OpenStack's DHCP Service AND
      * the internal network IPv4 subnet is to be specified
        using the property ``fixed_ips`` map property ``subnet``/``subnet_id``,

    the parameter **MUST** follow the naming convention

      * ``int_{network-role}_subnet_id``
    an IPv6 address is being cloud assigned by OpenStack's DHCP Service AND
      * ``int_{network-role}_v6_subnet_id``

    Note that the parameter MUST be defined as an output parameter in
    the base module.
    """

    base_path = get_base_template_from_yaml_files(yaml_files)
    base_heat = load_yaml(base_path)
    base_outputs = base_heat.get("outputs") or {}
    nested_template_paths = get_nested_files(yaml_files)
    errors = []

    for yaml_file in yaml_files:
        if yaml_file == base_path or yaml_file in nested_template_paths:
            continue  # Only applies to incremental modules
        heat = Heat(filepath=yaml_file)
        internal_ports = {
            r_id: p
            for r_id, p in heat.neutron_port_resources.items()
            if get_network_type_from_port(p) == "internal"
        }
        for r_id, port in internal_ports.items():
            props = port.get("properties") or {}
            fip_list = props.get("fixed_ips") or []
            if not isinstance(fip_list, list):
                continue
            for ip in fip_list:
                subnet = ip.get("subnet")
                if not subnet:
                    continue

                if "get_param" not in subnet:
                    continue
                param = subnet.get("get_param")
                if param not in base_outputs:
                    errors.append(
                        (
                            "Internal fixed_ips/subnet parameter {} is attached to port {}, but the subnet parameter "
                            "is not defined as an output in the base module ({})."
                        ).format(param, r_id, base_path)
                    )

    assert not errors, " ".join(errors)
