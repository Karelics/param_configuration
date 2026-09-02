#  ------------------------------------------------------------------
#   Copyright 2024 Karelics Oy
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#  ------------------------------------------------------------------
# Thirdparty
from ruamel.yaml import BaseConstructor

# Parameter Configuration
from param_configuration.configuration import ConfigConstructor, Configuration
from param_configuration.utils import AppendList

# pylint: disable=too-few-public-methods
# Fine for inheritance


class AppendConfigConstructor(ConfigConstructor, tag="!append"):
    """The !append directive marks a list to be concatenated onto the lower overlay layer's list for the same key,
    instead of overwriting it."""

    def constructor(self, tag_value: list, file: str, loader: BaseConstructor):
        return AppendList(tag_value)

    def __call__(self, loader, node):
        # construct_yaml_seq is a two-stage generator: exhausting it via list() populates and returns the single
        # CommentedSeq it yields, so the actual list of items is the first (only) element.
        items = list(loader.construct_yaml_seq(node=node))[0]
        return self.constructor(tag_value=items, file=node.end_mark.name, loader=loader)


Configuration().add_config_constructor(const=AppendConfigConstructor)
