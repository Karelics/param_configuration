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
from abc import abstractmethod
from pathlib import Path
from typing import Dict, List, Union


class ConfigLayer:
    """Abstract layer for YAML file overlaying."""

    @abstractmethod
    def load(self, path: Union[str, Path]) -> Union[str, Path, None]:
        """Resolve path and return path or yaml string."""

    @abstractmethod
    def get_files(self) -> Dict[str, Union[List[Path], str]]:
        """Returns a list of files that match this layer."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of the layer."""
