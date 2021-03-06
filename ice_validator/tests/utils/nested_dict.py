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

"""nested_dict.get
"""

VERSION = "1.1.1"


def get(dic, *keys, **kwargs):
    """Return the value of the last key given a (nested) dict and
    list of keys.  If any key is missing, or if the value of any key
    except the last is not a dict, then the default value is returned.
    The default value may be passed in using the keyword 'default=',
    otherwise the default value is None.
    """
    d = dic
    default = kwargs.get("default", None)
    for key in keys:
        if hasattr(d, "get"):
            d = d.get(key, default)
        else:
            return default
    return d


def is_dict_has_key(obj, key):
    """return True/False `obj` is a dict and has `key`
    """
    return isinstance(obj, dict) and key in obj
