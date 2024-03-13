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

# pylint: disable=too-few-public-methods
# Fine for inheritance


class IncludeConfigConstructor(ConfigConstructor, tag="!include"):
    """This directive can be used to include another yaml file.

    It will start at the top config layer and then go down to find the file that is being included.
    """

    def constructor(self, tag_value: str, file: str, loader: BaseConstructor):
        return Configuration().load(tag_value)


Configuration().add_config_constructor(const=IncludeConfigConstructor)
