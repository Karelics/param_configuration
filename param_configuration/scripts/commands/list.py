from pathlib import Path
from typing import Annotated, Dict, Optional

# Thirdparty
import typer
from rich.console import Console
from rich.text import Text
from rich.tree import Tree

# Parameter Configuration
from param_configuration.configuration import Configuration
from param_configuration.temp_config_env import TempConfigEnv

console = Console()


def list_config_files(config_directory: Annotated[Optional[str], typer.Option(help="path to the config dir")] = None):
    """Prints the tree of the current config structure."""

    if config_directory is not None:
        console.print(f"[bold][red] Got custom config directory: {config_directory}")

        with TempConfigEnv(path=Path(config_directory)):
            configuration = Configuration()
    else:
        configuration = Configuration()

    files_and_folders = configuration.list_files()
    tree = Tree("Current config structure")
    build_tree(tree=tree, files_and_folders=files_and_folders)
    console.print(tree)


def build_tree(files_and_folders: Dict, tree: Tree, directory_name="Layers") -> Tree:
    """Make a nice tree to print."""
    files = files_and_folders.pop("__files", [])

    if not files and not files_and_folders:  # Return if there are no files or any more subdirectories
        return tree

    branch = tree.add(f"[bold magenta]{directory_name}:")

    for file_name in files:
        branch.add(Text(str(file_name), "green"))

    for sub_dir_name, sub_dirs_and_files in files_and_folders.items():
        build_tree(sub_dirs_and_files, branch, sub_dir_name)
    return tree
