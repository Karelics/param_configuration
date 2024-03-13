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

    files = configuration.list_files()
    tree = Tree("Current config structure")
    build_tree(tree=tree, files=files)
    console.print(tree)


def build_tree(files: Dict, tree: Tree) -> Tree:
    """Make a nice tree to print."""
    for name, values in files.items():
        if name == "__files":
            filenames = values
            for entry in filenames:
                tree.add(Text(str(entry), "green"))

        if "__files" in values:
            branch = tree.add(f"[bold magenta]{name}:")
            filenames = values.pop("__files")
            for entry in filenames:
                branch.add(Text(str(entry), "green"))

            for folder in values:
                if folder == "__files":
                    continue
                branch = branch.add(f"[bold magenta]{folder}:")
                build_tree(values[folder], branch)

    return tree
