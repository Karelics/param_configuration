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
from typing import Dict


def merge_left(keys_a, keys_b, path=None):
    """Merges b into a where b overwrites a."""
    if path is None:
        path = []

    for key in keys_b:
        if key in keys_a:
            if isinstance(keys_a[key], dict) and isinstance(keys_b[key], dict):
                merge_left(keys_a[key], keys_b[key], path + [str(key)])
            else:
                keys_a[key] = keys_b[key]
        else:
            keys_a[key] = keys_b[key]
    return keys_a


def walk_directory(directory: Path, tree=None) -> Dict:
    """Recursively build a Tree with directory contents."""
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
            tree["__files"] += [path.name]

    return tree
