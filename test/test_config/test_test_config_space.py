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

"""Tests for validating the behavior in test_config space."""
import os
from pathlib import Path
from pprint import pprint
from unittest import mock

# Thirdparty
import pytest

# Current package
from param_configuration.configuration import Configuration
from param_configuration.temp_config_env import TempConfigEnv
from param_configuration.utils import walk_directory


@pytest.fixture(name="test_config_path")
def fixture_test_config_path() -> Path:
    """Fixture to return the configuration path."""
    return Path(__file__).parent


@mock.patch.dict(os.environ, {"PARAM_DEVICE_DIR": "device"})
def test_getting_yaml_from_config(test_config_path: Path) -> None:
    """Test loading from the test config space."""
    with TempConfigEnv(path=test_config_path):
        config = Configuration()
        data = config.load("config://navigation_params.yaml")
        assert data == {"nested_param": {"model_param": 2, "device_param": 1}}


def test_walk_dir(test_config_path: Path) -> None:
    """Test loading from the test config space."""
    print(test_config_path)
    with TempConfigEnv(path=test_config_path) as path:
        tree = walk_directory(directory=path)
        pprint(tree)
        # TODO This test doesn't yet assert anything. To be fixed with fixing the ROS directory listing


def test_ruamel_types(test_config_path: Path) -> None:
    """Tests that we load the expected types from the configuration file.

    We expect to have: str, int, float, bool, CommentedSeq (instance of list) and CommentedMap (instance of dict).
    Otherwise, we might experience issues when trying to pass these values for ROS Nodes
    """
    with TempConfigEnv(path=test_config_path):
        config = Configuration()
        data = config.load("config://ruamel_types.yaml")
        for key, val in data.items():
            # pylint: disable=eval-used
            # Trusted source in this case
            assert isinstance(val, eval(key))  # Make sure that the value has the data type of the key
