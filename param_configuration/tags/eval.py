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
import math
import os
from typing import Any

# ROS
from ament_index_python.packages import get_package_share_directory

# Thirdparty
import numpy
import simpleeval
from ruamel.yaml import BaseConstructor, MappingNode

# Parameter Configuration
from param_configuration.configuration import ConfigConstructor, Configuration, get_resolved_yaml


class Dotdict(dict):
    """Dot.notation access to dictionary attributes."""

    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __getattr__(self, item, *args, **kwargs) -> Any:
        return dict.get(item, *args, **kwargs)


def additional_names(var: dict[str, Any]) -> dict[str, Any]:
    """Function providing additional variables for simple eval."""
    return {"env": os.environ, "m": math, "np": numpy, "var": Dotdict(var)}


def additional_functions() -> dict[str, Any]:
    """Function providing additional function for simple eval."""
    return {
        "path_to": get_package_share_directory,
        "join": os.path.join,
        "round": round,
        "get_resolved_yaml": get_resolved_yaml,
        "to_string": str,
    }


# pylint: disable=too-few-public-methods
# Fine for inheritance


class EvalConfigConstructor(ConfigConstructor, tag="!eval"):
    """Provides the directive to add an !eval function to yaml."""

    def __init__(self):
        super().__init__()
        self._vars = {}

    def constructor(self, tag_value: str, file: str, loader: BaseConstructor) -> Any:
        """Constructs the !eval tag."""
        # Resolve variables in the file
        self._vars = self.extract_variables(loader)

        default_functions = simpleeval.DEFAULT_FUNCTIONS
        default_functions.update(additional_functions())
        res = self.eval_with_compound_types(
            tag_value, functions=default_functions, names=additional_names(var=self._vars)
        )
        return res

    @staticmethod
    def extract_variables(loader) -> dict:
        """Extracts variables from a YAML loader. Variable loading works slightly differently for !overlay tagged files
        and for regular files.

        :param loader: The YAML loader containing the data.
        :type loader: Loader
        :return: The extracted variables.
        """
        variables = {}
        new_node = list(loader.recursive_objects.keys())[0]
        nodes = [new_node] + list(loader.constructed_objects.keys())
        for node in nodes:
            if not isinstance(node, MappingNode):
                continue

            for key_node, value_node in node.value:
                key = loader.construct_object(key_node, deep=True)
                if key != ".variables":
                    continue

                yaml_seq = list(loader.construct_yaml_seq(node=value_node))[0]
                if yaml_seq:
                    for var in yaml_seq:
                        if var:
                            variables |= var
        return variables

    @staticmethod
    def eval_with_compound_types(tag_value: str, functions: dict[str, Any], names: dict[str, Any]) -> Any:
        """Evaluates the tag value with compound types."""
        obj = simpleeval.EvalWithCompoundTypes(functions=functions, names=names)
        return obj.eval(tag_value)


# Add the constructor.
Configuration().add_config_constructor(const=EvalConfigConstructor)
