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

# Current package
from param_configuration.configuration import ConfigConstructor, Configuration

# pylint: disable=too-few-public-methods
# Fine for inheritance


class FromConfigConstructor(ConfigConstructor, tag="!from"):
    """Get a single key from a config file."""

    def constructor(self, tag_value: str, file: str, loader: BaseConstructor):
        file, fields = tag_value.split(" ")
        fields = fields.split(".")  # Split for nested fields
        data = Configuration().load(file)

        try:
            for field in fields:
                data = data[field]
        except KeyError as e:
            raise RuntimeError(f"Could not find {field} in {file}." f"Possible keys are {data}") from e
        return data


Configuration().add_config_constructor(const=FromConfigConstructor)
