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

from os import path

from .helpers import validates


@validates(
    "R-86285",
    "R-38474",
    "R-81725",
    "R-53433",
    "R-56438",
    "R-74304",
    "R-91342",
    "R-94509",
    "R-31141",
)
def test_heat_pairs_provided(heat_templates, env_files, volume_templates):
    """
    Check that every yaml file is submitted with
    an associated env file, and every env has an
    associated yaml file.
    """

    env_files_missing_template = []
    for filename in env_files:
        basename = path.splitext(filename)[0]
        if not (
            basename + ".yaml" in heat_templates
            or basename + ".yml" in heat_templates
            or basename + ".yml" in volume_templates
            or basename + ".yaml" in volume_templates
        ):
            env_files_missing_template.append(filename)

    heat_template_missing_env = []
    for filename in heat_templates:
        basename = path.splitext(filename)[0]
        if not basename + ".env" in env_files:
            heat_template_missing_env.append(filename)

    for filename in volume_templates:
        basename = path.splitext(filename)[0]
        if not basename + ".env" in env_files:
            heat_template_missing_env.append(filename)

    msg = (
        "Mismatched template and environment file pairs detected. "
        + "Environment files with no matching template: {} ".format(
            env_files_missing_template
        )
        + "Heat templates with no matching environment file: {}".format(
            heat_template_missing_env
        )
    )

    assert not (env_files_missing_template or heat_template_missing_env), msg
