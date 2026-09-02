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
import pytest

# Parameter Configuration
from param_configuration.utils import AppendList, merge_left, unwrap_append_lists


def test_merge_left_append_list() -> None:
    """Test that an AppendList value concatenates onto the lower dict's existing list."""
    result = merge_left({"x": [1]}, {"x": AppendList([2])})
    assert result == {"x": [1, 2]}
    assert type(result["x"]) is list  # pylint: disable=unidiomatic-typecheck


def test_merge_left_append_list_missing_lower_key() -> None:
    """Test that an AppendList value with no lower-level key just becomes its own list."""
    result = merge_left({}, {"x": AppendList([2])})
    assert result == {"x": [2]}


def test_merge_left_append_list_type_mismatch() -> None:
    """Test that appending onto a non-list lower-level value raises."""
    with pytest.raises(TypeError):
        merge_left({"x": "not_a_list"}, {"x": AppendList([2])})


def test_unwrap_append_lists() -> None:
    """Test that leftover AppendList markers are replaced with plain lists, in place, at any nesting depth."""
    data = {"x": AppendList([1]), "nested": {"y": [AppendList([2])]}, "z": "unaffected"}
    unwrap_append_lists(data)
    assert data == {"x": [1], "nested": {"y": [[2]]}, "z": "unaffected"}
    assert type(data["x"]) is list  # pylint: disable=unidiomatic-typecheck
    assert type(data["nested"]["y"][0]) is list  # pylint: disable=unidiomatic-typecheck
