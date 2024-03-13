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
import pathlib
import tempfile
from abc import abstractmethod
from pathlib import Path
from typing import Any, Optional, Type, Union

# Thirdparty
import numpy
import ruamel.yaml
from ruamel.yaml import BaseConstructor, Node, ScalarNode
from ruamel.yaml.comments import CommentedMap
from ruamel.yaml.constructor import Constructor

# Parameter Configuration
from param_configuration.config_layer import ConfigLayer
from param_configuration.path_resolver import PathResolver


class ConfigConstructor:
    """Constructor to build a single value from YAML file in runtime.

    Inherit to implement functionality for custom tags.
    """

    tag: str

    def __init__(self):
        self.config_layers = []
        self.file = None

    def __init_subclass__(cls, *, tag: str, **kwargs):
        cls.tag = tag

    @abstractmethod
    def constructor(self, tag_value: str, file: str, loader: BaseConstructor) -> Any:
        """Constructs the final value from tag's value.

        :param loader: BaseLoader instance to use for constructing the tags
        :param tag_value: Value after the given tag. For example, for eval tag, the value could be "env.HOME"
        :param file: Path of the YAML file
        :return: The constructed value, for example "/home/user/"
        """

    def __call__(self, loader: BaseConstructor, node: ScalarNode):
        tag_value = loader.construct_scalar(node)

        # Support for nested tags
        if "!" in tag_value:
            raw = f"value: {tag_value}"
            tag_value = Configuration().load(raw)["value"]

        return self.constructor(tag_value=tag_value, file=node.end_mark.name, loader=loader)


class ConfigMultiConstructor:
    """Constructor to change multiple values at once in YAML file.

    Inherit to implement functionality for custom tags.
    """

    tag: str

    def __init__(self):
        self.config_layers = []
        self.file = None

    def __init_subclass__(cls, *, tag: str, **kwargs):
        cls.tag = tag

    @abstractmethod
    def constructor(self, items: list[CommentedMap], file: Path):
        """Constructs the final values from tag's values.

        :param items: List of the values after given tag.
        :param file: Path of the YAML file
        :return: The constructed value
        """

    def __call__(self, constructor: Constructor, _tag: str, node: Node):
        items = constructor.construct_sequence(node, deep=True)
        return self.constructor(items=items, file=node.end_mark.name)


class Configuration:
    """Builds the final configuration from a given YAML file."""

    _constructors: dict[str, Type[ConfigConstructor]] = {}
    _multi_constructor: dict[str, Type[ConfigMultiConstructor]] = {}

    def load(self, file: Union[Path, str], config_layers: list[ConfigLayer] = None) -> Any:
        """Loads a given YAML file into a ruamel format dictionary.

        :param file: Yaml file in string format or path to YAML file
        :param config_layers: List of configuration layers that describe the order of overlaying different
            YAML files. If None, uses the default layers
        :return: Loaded yaml file in Ruamel format. Mainly CommentedMap which corresponds dictionary.
        """
        path = None

        if str(file).startswith("/"):  # Absolute YAML path was given
            file = Path(file)
        else:  # YAML string or "config://" was given
            path = PathResolver().resolve_path(file, config_layers=config_layers)

        if config_layers is None:
            config_layers = PathResolver().get_layers()

        yaml_loader = ruamel.yaml.YAML()

        # In some cases, ruamel loads floats as ScalarFloat, which is ruamel-specific type. If this is passed
        # to ROS Nodes, the Node doesn't read the parameter nor print any errors or warnings about it, and just
        # uses the default values for it. To fix this issue, we register a float constructor as suggested in
        # https://stackoverflow.com/questions/71552717/could-ruamel-yaml-support-type-descriptor-like-num-float-4
        yaml_loader.constructor.add_constructor(
            "tag:yaml.org,2002:float", ruamel.yaml.constructor.SafeConstructor.construct_yaml_float
        )

        # numpy floats and ints couldn't be represented, so add the representers as suggested here:
        # https://stackoverflow.com/questions/76430001
        yaml_loader.Representer.add_representer(numpy.float64, represent_numpy_float64)
        yaml_loader.Representer.add_representer(numpy.int64, represent_numpy_int64)

        for const in self._constructors.values():
            new_const = const()
            new_const.config_layers = config_layers
            new_const.file = file
            yaml_loader.constructor.add_constructor(tag=new_const.tag, constructor=new_const)

        for multi_const in self._multi_constructor.values():
            new_const = multi_const()
            new_const.config_layers = config_layers
            new_const.file = file
            yaml_loader.constructor.add_multi_constructor(tag_prefix=new_const.tag, multi_constructor=new_const)

        resolved_yaml = yaml_loader.load(path if path else file)
        resolved_yaml.pop(".variables", None)  # Remove the variables that are used for eval purposes
        return resolved_yaml

    def add_config_constructor(self, const: Type[ConfigConstructor]):
        """Add a new config constructor to be used.

        :raises RuntimeError: If the tag already exists.
        """
        if const.tag in self._constructors:
            raise RuntimeError("Tag already registered")
        self._constructors[const.tag] = const

    def add_config_multi_constructor(self, multi_const: Type[ConfigMultiConstructor]):
        """Add a new config multi-constructor to be used.

        :raises RuntimeError: If the tag already exists.
        """
        if multi_const.tag in self._multi_constructor:
            raise RuntimeError("Tag already registered")
        self._multi_constructor[multi_const.tag] = multi_const

    @staticmethod
    def dump(data: dict) -> str:
        """Dump the YAML dictionary into string format."""
        yaml = ruamel.yaml.YAML(typ=["rt", "string"])
        # pylint: disable=no-member
        # Pylint thinks dump_to_string doesn't exist, but seems to work correctly.
        return yaml.dump_to_string(data)

    @staticmethod
    def dump_to_file(data: dict, path: str, yaml_version: Optional[str] = None) -> str:
        """Dump the YAML dictionary into a file."""
        yaml = ruamel.yaml.YAML(typ=["rt", "string"])
        if yaml_version:
            yaml.version = yaml_version
        return yaml.dump(data, pathlib.Path(path))

    @staticmethod
    def list_files() -> dict:
        """Return the list of YAML files across all the layers."""
        return PathResolver().get_files()


def get_resolved_yaml(path: str):
    """Evaluates YAML file and dumps it into a temporary file. When passing parameters for ROS Nodes, passing a file is
    desired, as that way we can maintain Node names that exist in the parameter file. Otherwise, passing two parameter
    dictionaries to a single Node might lead into a parameter name conflicts.

    :param path: path to YAML file
    :return: path to evaluated YAML file
    """
    config = Configuration()
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as file:
        config.dump_to_file(config.load(path), file.name, yaml_version="1.1")
    return file.name


def represent_numpy_float64(self, value):
    """Represents numpy float64 format as normal Python float."""
    return self.represent_float(value)


def represent_numpy_int64(self, value):
    """Represents numpy int64 format as normal Python int."""
    return self.represent_int(value)
