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
from unittest import mock

# Thirdparty
import pytest
import yaml
from simpleeval import AttributeDoesNotExist

# Parameter Configuration
from param_configuration.configuration import Configuration
from param_configuration.temp_config_env import TempConfigEnv


@pytest.fixture(name="yaml_string")
def fixture_yaml_string() -> str:
    """Fixture to test all the possible eval statements, including numpy int and float types."""
    yaml_str = """
.variables:
 - var1: 1
env_var: !eval env.TEST_VAR
math_exp: !eval m.pi
numpy_int: !eval np.int64(42)
numpy_float: !eval np.sin(1)
math: !eval (m.pi*2/4)
path_to_package: !eval path_to('path_to_example_pkg')
use_var: !eval var.var1*100
"""
    return yaml_str


def test_eval_tag_from_string(yaml_string: str) -> None:
    """Test the loading and dumping !eval directive from a string."""
    configuration = Configuration()
    with mock.patch(
        "param_configuration.tags.eval.get_package_share_directory",
        return_value="path_to_example_pkg",
    ):
        os.environ["TEST_VAR"] = "TEST_VALUE"
        data = configuration.load(yaml_string)

        assert data == {
            "env_var": "TEST_VALUE",
            "math_exp": 3.141592653589793,
            "numpy_int": 42,
            "numpy_float": 0.8414709848078965,
            "math": 1.5707963267948966,
            "path_to_package": "path_to_example_pkg",
            "use_var": 100,
        }

        data_str = configuration.dump(data)
        expected_str = (
            "env_var: TEST_VALUE\n"
            "math_exp: 3.141592653589793\n"
            "numpy_int: 42\n"
            "numpy_float: 0.8414709848078965\n"
            "math: 1.5707963267948966\n"
            "path_to_package: path_to_example_pkg\n"
            "use_var: 100"
        )

        assert data_str == expected_str


def test_eval_round() -> None:
    """Test the !eval directive with the round function."""
    yaml_string = """
    round: !eval round(3.141592653589793, 2)
    """
    expected_string = "round: 3.14"

    configuration = Configuration()
    data = configuration.load(yaml_string)
    data_str = configuration.dump(data)
    assert data_str == expected_string


def test_eval_to_string() -> None:
    """Test the !eval directive with the to_string function."""
    yaml_string = """
    float_to_string: !eval to_string(3.141592653589793)
    array_to_string: !eval to_string([[1.0, 1.0], [2.0, 2.0]])
    """
    # fmt: off
    expected_string = (
        "float_to_string: '3.141592653589793'\n"
        "array_to_string: '[[1.0, 1.0], [2.0, 2.0]]'"
    )
    # fmt: on

    configuration = Configuration()
    data = configuration.load(yaml_string)
    data_str = configuration.dump(data)
    assert data_str == expected_string


def test_eval_small_numbers() -> None:
    """Test the loading and dumping !eval directive from a string."""
    configuration = Configuration()

    data = configuration.load("small_value: 1.0e-08")

    assert data == {
        "small_value": 1.0e-8,
    }

    assert isinstance(data["small_value"], float)

    data_str = configuration.dump(data)
    expected_str = "small_value: 1e-08"
    assert data_str == expected_str


def test_eval_tag_from_file(tmp_path: Path, yaml_string: str) -> None:
    """Test the !eval directive from a file."""
    test_file = tmp_path / "test_file.yaml"
    test_file.write_text(yaml_string)
    configuration = Configuration()

    with mock.patch(
        "param_configuration.tags.eval.get_package_share_directory",
        return_value="path_to_example_pkg",
    ):
        os.environ["TEST_VAR"] = "TEST_VALUE"

        data = configuration.load(test_file)

        assert data == {
            "env_var": "TEST_VALUE",
            "math_exp": 3.141592653589793,
            "numpy_int": 42,
            "numpy_float": 0.8414709848078965,
            "math": 1.5707963267948966,
            "path_to_package": "path_to_example_pkg",
            "use_var": 100,
        }


def test_eval_variables() -> None:
    """Tests the !eval tag for variables."""
    yaml_data = """
    .variables:
    - var_1: 1
    - var_2: 2
    - var_3: 37
    - var_4: !eval var.var_1 + 2
    other_vars:  # Checks that other main-level variables do not affect to the logic
    - var_3: abc
    eval_1: !eval var.var_1 + 1
    eval_2:  [!eval (var.var_1 + var.var_2), !eval (var.var_2), !eval (var.var_3)]
    eval_3: !eval var.var_4
    """
    data = Configuration().load(yaml_data)
    assert data == {"other_vars": [{"var_3": "abc"}], "eval_1": 2, "eval_2": [3, 2, 37], "eval_3": 3}


# TODO Multiple nested variables are not yet supported
@pytest.mark.skip(reason="Known issue")
def test_eval_variables_multiple_levels() -> None:
    """Test loading multiple-levelled nested variables."""
    yaml_data = """
    .variables:
    - var_1: 1
    - var_2: !eval var.var_1 + 1
    - var_3: !eval var.var_2 + 1
    eval_1: !eval var.var_2
    """
    data = Configuration().load(yaml_data)
    assert data == {"eval_1": 3}


def test_eval_non_existing_var() -> None:
    """If the !eval tag is used with a parameter that does not exist, should raise an error."""
    yaml_data = """
    .variables:
    - var_2: 1
    eval_1: !eval var.var_1
    """
    with pytest.raises(AttributeDoesNotExist):
        Configuration().load(yaml_data)


def test_eval_with_overlay(tmp_path: Path, yaml_string: str) -> None:
    """Test that all the !eval commands work as expected with the !overlay tag."""
    test_file = "test_file1.yaml"
    test_pkg = "test_package"
    yaml_string = "!overlay\n" + yaml_string

    package_data = """
    env_var: 0
    math_exp: 0
    numpy_int: 0
    numpy_float: 0
    math: 0
    path_to_package: 0
    use_var: 0
    not_in_model_data: 0  # Makes sure the file was truly overlaid
    """

    # Create a model directory and add file
    write_to_file_config_layer(
        yaml_string, level="model", package_name=test_pkg, file_name=test_file, config_base_dir=tmp_path
    )

    pkg_param_file = write_to_ros_pkg_layer(
        package_data, package_name=test_pkg, file_name=test_file, config_base_dir=tmp_path
    )

    with mock.patch(
        "param_configuration.tags.eval.get_package_share_directory",
        return_value="path_to_example_pkg",
    ):
        with mock.patch(
            "param_configuration.config_layers.ros_package.get_package_share_directory",
            return_value=str(pkg_param_file),
        ):
            # Set the params config directory to a tmp directory
            with TempConfigEnv(path=tmp_path):
                os.environ["TEST_VAR"] = "TEST_VALUE"
                configuration = Configuration()
                data = configuration.load(f"config://{test_pkg}/{test_file}")
                assert data == {
                    "env_var": "TEST_VALUE",
                    "math_exp": 3.141592653589793,
                    "numpy_int": 42,
                    "numpy_float": 0.8414709848078965,
                    "math": 1.5707963267948966,
                    "path_to_package": "path_to_example_pkg",
                    "use_var": 100,
                    "not_in_model_data": 0,
                }


def test_eval_get_resolved_yaml(tmp_path: Path):
    """Tests the !eval get_resolved_yaml function."""
    yaml_1 = """
    var_1: !eval 1 + 1
    var_2: 1.0e-08
    """

    yaml_1_path = tmp_path / "yaml_1.yaml"
    yaml_1_path.write_text(yaml_1)

    yaml_2 = f"""
    yaml_path: !eval get_resolved_yaml("{yaml_1_path}")
    """

    data = Configuration().load(yaml_2)
    with open(data["yaml_path"], encoding="utf-8") as file:
        yaml_1_resolved = yaml.safe_load(file)
        assert yaml_1_resolved["var_1"] == 2
        assert isinstance(yaml_1_resolved["var_2"], float)
        assert yaml_1_resolved["var_2"] == 1e-08


@mock.patch.dict(os.environ, {"PARAM_DEVICE_DIR": "device"})
def test_include_tag(tmp_path: Path) -> None:
    """Test cases for loading included files."""
    (tmp_path / "model").mkdir(parents=True, exist_ok=True)
    (tmp_path / "device").mkdir(parents=True, exist_ok=True)

    test_file1 = tmp_path / "model" / "test_file1.yaml"
    test_file2 = tmp_path / "model" / "test_file2.yaml"
    test_file3 = tmp_path / "device" / "test_file2.yaml"

    file_1_contents = f"""
    include_file: !include {test_file2}                     # Normal include with absolute path
    include_file_2: !include config://test_file2.yaml       # Include using overlays
    #include_file_3: !include /(!eval env.PARAM_CONFIG_DIR)/device/test_file2.yaml
    """
    # TODO include_file_3 is not evaluated correctly

    file_2_contents = """
    nested:
        var_1: 1
    """

    file_3_contents = """
    nested:
        var_1: 2
    """

    test_file1.write_text(file_1_contents)
    test_file2.write_text(file_2_contents)
    test_file3.write_text(file_3_contents)

    with TempConfigEnv(path=tmp_path):
        data = Configuration().load(test_file1)
        assert data == {"include_file": {"nested": {"var_1": 1}}, "include_file_2": {"nested": {"var_1": 2}}}


def test_from_tag(tmp_path: Path) -> None:
    """Test getting values from config file using !from-tag."""

    test_file1 = tmp_path / "test_file1.yaml"
    test_file2 = tmp_path / "test_file2.yaml"

    file_1_contents = f"""
    from_other_file: !from {test_file2} var_1
    from_other_file_2: !from {test_file2} nested.nested2.var_2
    """

    file_2_contents = """
    var_1: 1
    nested:
        nested2:
            var_2: 2
    """

    test_file1.write_text(file_1_contents)
    test_file2.write_text(file_2_contents)

    configuration = Configuration()
    data = configuration.load(test_file1)
    assert data == {"from_other_file": 1, "from_other_file_2": 2}


def test_merge_tag_from_string(tmp_path: Path) -> None:
    """Test merge from a string."""
    yaml_data = """
    var_1: 1
    """
    test_file1 = tmp_path / "test_file1.yaml"
    test_file1.write_text(yaml_data)

    yaml_str = f"""
    test: !merge
        - !include  "{str(test_file1)}"
        - var_2: 2
    """
    configuration = Configuration()
    data = configuration.load(yaml_str)

    assert data == {
        "test": {
            "var_1": 1,
            "var_2": 2,
        }
    }


@mock.patch.dict(os.environ, {"PARAM_DEVICE_DIR": "device"})
def test_overlay(tmp_path: Path) -> None:
    """Test overlaying with different layers.

    Tests also that different tags work correctly with the overlay
    """
    package_name = "test_package"

    # This file exist on device / model and package level
    test_file_1 = "test_file1.yaml"

    # This file exist only on model level
    test_file_2 = "test_file2.yaml"

    device_data = f"""
!overlay
var1: "device_level_1"
var2: "device_level_2"
test_include: !include config://{package_name}/{test_file_2}
test_from: !from config://{package_name}/{test_file_2} var1a
"""

    model_data_1 = """
!overlay
var2: "model_level_var2"
var3: "model_level_var3"
"""

    model_data_2 = """
var1a: "model_level_var1a"
var2b: "model_level_var2b"
"""

    package_data_1 = """
var3: "package_level_var3"
var4: "package_level_var4"
var5: "package_level_var5"
"""

    # Create a device directory and add file
    write_to_file_config_layer(device_data, "device", package_name, test_file_1, tmp_path)

    # Create a model directory and add files
    write_to_file_config_layer(model_data_1, "model", package_name, test_file_1, tmp_path)
    write_to_file_config_layer(model_data_2, "model", package_name, test_file_2, tmp_path)
    # Create a package directory and add file

    package_dir = tmp_path / "test_install_space/"
    (package_dir / package_name / "params/").mkdir(parents=True, exist_ok=True)
    package_param_file = package_dir / package_name
    (package_param_file / "params/test_file1.yaml").write_text(package_data_1)

    with mock.patch(
        "param_configuration.config_layers.ros_package.get_package_share_directory",
        return_value=str(package_param_file),
    ):
        # Set the param config directory to a tmp directory
        with TempConfigEnv(path=tmp_path):
            configuration = Configuration()
            data = configuration.load(f"config://{package_name}/{test_file_1}")
            assert data == {
                "var3": "model_level_var3",
                "var4": "package_level_var4",
                "var5": "package_level_var5",
                "var2": "device_level_2",
                "var1": "device_level_1",
                "test_include": {"var1a": "model_level_var1a", "var2b": "model_level_var2b"},
                "test_from": "model_level_var1a",
            }


def write_to_file_config_layer(data, level, package_name, file_name, config_base_dir):
    """Creates necessary folders and writes the file."""
    device_dir = config_base_dir / f"{level}/"
    (device_dir / package_name).mkdir(parents=True, exist_ok=True)
    (device_dir / package_name / file_name).write_text(data)


def write_to_ros_pkg_layer(data, package_name, file_name, config_base_dir) -> str:
    """Creates necessary folders and writes the file."""
    package_dir = config_base_dir / "test_install_space/"
    (package_dir / f"{package_name}/params/").mkdir(parents=True, exist_ok=True)
    package_param_file = package_dir / package_name
    (package_param_file / f"params/{file_name}").write_text(data)
    return package_param_file


@mock.patch.dict(os.environ, {"PARAM_DEVICE_DIR": "device"})
def test_overlay_skip_layer(tmp_path):
    """Test overlaying when the Model layer is not present."""
    test_file = "test_package/test_file1.yaml"
    device_data = """
!overlay
var1: "device_level_1"
var2: "device_level_2"
var3: "device_level_3"
"""

    package_data = """
var3: "package_level_var3"
var4: "package_level_var4"
var5: "package_level_var5"
"""

    # Create a device directory and add file
    device_dir = tmp_path / "device/"
    (device_dir / "test_package").mkdir(parents=True, exist_ok=True)
    (device_dir / test_file).write_text(device_data)

    # Create a package directory
    package_dir = tmp_path / "test_install_space/"

    (package_dir / "test_package/params/").mkdir(parents=True, exist_ok=True)
    package_param_file = package_dir / "test_package"
    (package_param_file / "params/test_file1.yaml").write_text(package_data)

    with mock.patch(
        "param_configuration.config_layers.ros_package.get_package_share_directory",
        return_value=str(package_param_file),
    ):
        # Set the param config directory to a tmp directory
        with TempConfigEnv(path=tmp_path):
            configuration = Configuration()
            data = configuration.load(f"config://{test_file}")

            assert data == {
                "var1": "device_level_1",
                "var2": "device_level_2",
                "var3": "device_level_3",
                "var4": "package_level_var4",
                "var5": "package_level_var5",
            }


def test_overlay_only_ros_layer(tmp_path):
    """Test overlaying when only the ROS layer is present."""
    test_file = "test_package/test_file1.yaml"

    package_data = """
var3: "package_level_var3"
"""

    # Create a package directory
    package_dir = tmp_path / "test_install_space/"

    (package_dir / "test_package/params/").mkdir(parents=True, exist_ok=True)
    package_param_file = package_dir / "test_package"
    (package_param_file / "params/test_file1.yaml").write_text(package_data)

    with mock.patch(
        "param_configuration.config_layers.ros_package.get_package_share_directory",
        return_value=str(package_param_file),
    ):
        with TempConfigEnv(path=tmp_path):
            configuration = Configuration()
            data = configuration.load(f"config://{test_file}")

            assert data == {
                "var3": "package_level_var3",
            }


@mock.patch.dict(os.environ, {"PARAM_DEVICE_DIR": "device"})
def test_nested_tags(tmp_path: Path) -> None:
    """Test nested tags."""
    package_name = "test_package"

    # This file exist on device and package level
    test_file_1 = "test_file1.yaml"

    yaml_data = f"""
from: !from '!eval path_to("test_package") + "/params/{test_file_1} var3"'
include: !include '!eval path_to("test_package") + "/params/{test_file_1}"'
"""

    package_data_1 = """
var3: "package_level_var3"
"""

    # Create a device directory and add file
    write_to_file_config_layer(yaml_data, "device", package_name, test_file_1, tmp_path)

    # Create a package directory and add file
    package_dir = tmp_path / "test_install_space/"
    (package_dir / package_name / "params/").mkdir(parents=True, exist_ok=True)
    package_param_file = package_dir / package_name
    (package_param_file / "params/test_file1.yaml").write_text(package_data_1)

    with mock.patch(
        "param_configuration.tags.eval.get_package_share_directory",
        return_value=str(package_param_file),
    ):
        with TempConfigEnv(path=tmp_path):
            configuration = Configuration()
            data = configuration.load(f"config://{package_name}/{test_file_1}")
            assert data == {"from": "package_level_var3", "include": {"var3": "package_level_var3"}}
