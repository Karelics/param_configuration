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


class TempConfigEnv:
    """Creates a temporary config space for easier testing by replacing the PARAM_CONFIG_DIR env variable with the given
    path."""

    def __init__(self, path: Path) -> None:
        self._path = path
        self._old_value = None

    def __enter__(self) -> str:
        self._old_value = os.environ.get("PARAM_CONFIG_DIR", None)
        os.environ["PARAM_CONFIG_DIR"] = str(self._path)
        return os.environ["PARAM_CONFIG_DIR"]

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._old_value:
            os.environ["PARAM_CONFIG_DIR"] = str(self._old_value)
