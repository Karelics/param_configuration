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
from typing import Dict, List, Optional, Union

# Parameter Configuration
from param_configuration.config_layer import ConfigLayer
from param_configuration.utils import walk_directory


class FileLocationLayer(ConfigLayer):
    """Overlay configuration layer for a normal folder in config directory."""

    def __init__(self, layer_folder: str, config_directory: Optional[str] = None):
        self._layer_folder = layer_folder
        self._config_directory = config_directory

    @property
    def name(self) -> str:
        return self._layer_folder

    def get_config_directory(self) -> Union[Path, str]:
        """Returns the config directory.

        :raises RuntimeError: If PARAM_CONFIG_DIR env variable is not set.
        """
        if self._config_directory:
            return self._config_directory

        default_path = os.environ.get("PARAM_CONFIG_DIR")
        if default_path:
            return Path(default_path)

        raise RuntimeError("Set PARAM_CONFIG_DIR environmental variable that points to configuration directory")

    def load(self, path: Path) -> Union[str, Path, None]:
        """Try to load the file from the layer."""
        directory = self.get_config_directory() / self._layer_folder
        converted_path = Path(str(path).replace("config:", str(directory)))
        if converted_path.exists():
            return converted_path
        return None

    def get_files(self) -> Dict[str, Union[List[Path], str]]:
        """Return all possible files."""
        return walk_directory(directory=self.get_config_directory() / self._layer_folder)
