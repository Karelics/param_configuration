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
import os
from pathlib import Path
from typing import Dict, Optional, Union

# Parameter Configuration
from param_configuration.config_layer import ConfigLayer
from param_configuration.config_layers.file_location_layer import FileLocationLayer
from param_configuration.config_layers.ros_package import RosParamPackageLayer


class PathResolver:
    """The path resolver goes through all defined layers to find the correct files."""

    def __init__(self):
        self._layers: list[ConfigLayer] = []

        # Add the default config layers, order matters!
        if os.getenv("PARAM_CONFIG_DIR"):  # Add model and device layers only if ENV variable exists
            self.add_layer(layer=FileLocationLayer(layer_folder=os.getenv("PARAM_DEVICE_DIR", "device")))
            self.add_layer(layer=FileLocationLayer(layer_folder="model"))
        self.add_layer(layer=RosParamPackageLayer())

    def resolve_path(
        self, path: Union[str, Path], config_layers: Optional[list[ConfigLayer]] = None
    ) -> Union[str, Path]:
        """Resolves the configuration path by overlaying different YAML files based on the provided configuration
        layers.

        :param path: YAML in string format, or path to the YAML file
        :param config_layers: List of configuration layers that describe the order of overlaying different
            YAML files. If None, uses the default layers
        :return: Resolved configuration data as a string or Path object.
        :raises ValueError: If the path cannot be resolved
        """
        path = str(path)

        if not path.startswith("config:"):
            return path

        layers = self._layers if config_layers is None else config_layers

        for layer in layers:
            data = layer.load(path)
            if data is not None:
                return data

        raise ValueError(f"Could not resolve {path}")

    def add_layer(self, layer: ConfigLayer) -> None:
        """Add layer to the config resolver."""
        self._layers.append(layer)

    def get_layers(self) -> list[ConfigLayer]:
        """Returns the list of overlay layers."""
        return self._layers

    def get_files(self) -> Dict:
        """Return possible files for all layers."""
        result = {}
        for layer in self._layers:
            result[layer.name] = layer.get_files()
        return result
