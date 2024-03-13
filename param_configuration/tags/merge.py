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
from pathlib import Path

# Parameter Configuration
from param_configuration.configuration import ConfigMultiConstructor, Configuration
from param_configuration.utils import merge_left

# pylint: disable=too-few-public-methods
# Fine for inheritance


class MergeMultiConfigConstructor(ConfigMultiConstructor, tag="!merge"):
    """The !merge directive makes it possible to include a file and then change a value in what is included."""

    def constructor(self, items: str, file: Path):
        # We assume that the fist entry is the main one.
        config = items[0]
        for i in items[1:]:
            merge_left(items[0], i)

        return config


Configuration().add_config_multi_constructor(multi_const=MergeMultiConfigConstructor)
