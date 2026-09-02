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
from pathlib import Path
from typing import Any, Dict


class AppendList(list):
    """Marks a list as append-only for overlay merging.

    Produced by the !append tag. When encountered by merge_left, it is concatenated onto the lower layer's list instead
    of overwriting it.
    """


def merge_left(keys_a, keys_b, path=None):
    """Merges b into a where b overwrites a.

    A value in b wrapped in AppendList is concatenated onto a's list instead of overwriting it.

    :raises TypeError: If b's value is an AppendList but a's existing value at that key is not a list.
    """
    if path is None:
        path = []

    for key in keys_b:
        if isinstance(keys_b[key], AppendList):
            lower = keys_a.get(key, [])
            if not isinstance(lower, list):
                raise TypeError(f"Cannot !append onto non-list value at '{'.'.join(path + [str(key)])}'")
            keys_a[key] = list(lower) + list(keys_b[key])
        elif key in keys_a:
            if isinstance(keys_a[key], dict) and isinstance(keys_b[key], dict):
                merge_left(keys_a[key], keys_b[key], path + [str(key)])
            else:
                keys_a[key] = keys_b[key]
        else:
            keys_a[key] = keys_b[key]
    return keys_a


def unwrap_append_lists(data: Any) -> None:
    """Recursively replaces any leftover AppendList markers in data with plain lists, in place.

    Needed for the case where !append is used without a lower layer to merge into (e.g. the bottom-most layer, or a file
    loaded standalone without !overlay), since AppendList itself isn't representable when dumping to YAML.
    """
    if isinstance(data, dict):
        items = data.items()
    elif isinstance(data, list):
        items = enumerate(data)
    else:
        return

    for key, value in items:
        if isinstance(value, AppendList):
            data[key] = list(value)
            unwrap_append_lists(data[key])
        else:
            unwrap_append_lists(value)


def walk_directory(directory: Path, tree=None) -> Dict:
    """Recursively build a Tree with directory contents.

    Lists only YAML files
    """
    # Sort dirs first then by filename
    if tree is None:
        tree = {"__files": []}
    paths = sorted(
        Path(directory).iterdir(),
        key=lambda path: (path.is_file(), path.name.lower()),
    )
    for path in paths:
        # Remove hidden files
        if path.name.startswith("."):
            continue

        if path.name.startswith("__"):
            continue

        if path.is_dir():
            tree[path.name] = walk_directory(path)
        else:
            if not path.name.endswith(".yaml") and not path.name.endswith(".yml"):
                continue
            tree["__files"] += [path.name]

    return tree
