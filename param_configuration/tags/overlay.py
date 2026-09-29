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
from ruamel.yaml.comments import CommentedMap

# Parameter Configuration
from param_configuration.configuration import ConfigConstructor, Configuration
from param_configuration.path_resolver import PathResolver
from param_configuration.utils import merge_left

# pylint: disable=too-few-public-methods
# Fine for inheritance


class OverlayConfigConstructor(ConfigConstructor, tag="!overlay"):
    """The !overlay directive makes it possible to overlay files from different layers."""

    def constructor(self, tag_value: str, file: str, loader: BaseConstructor):
        # Overlay on the layers below the one this file was resolved from, if any
        _, underlay_layers = PathResolver().resolve_path_with_underlay(self.file, config_layers=self.config_layers)
        underlay = Configuration().load(self.file, config_layers=underlay_layers) if underlay_layers else CommentedMap()
        for i in tag_value:
            merge_left(underlay, i)
        return underlay

    def __call__(self, loader, node):
        items = list(loader.construct_yaml_map(node=node))
        return self.constructor(tag_value=items, file=node.end_mark.name, loader=loader)


Configuration().add_config_constructor(const=OverlayConfigConstructor)
