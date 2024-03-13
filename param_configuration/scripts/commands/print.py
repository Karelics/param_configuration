import os
from pathlib import Path
from typing import Annotated, Optional

# Thirdparty
import typer
from rich.console import Console
from rich.syntax import Syntax

# Parameter Configuration
from param_configuration.configuration import Configuration
from param_configuration.temp_config_env import TempConfigEnv

console = Console()


def print_config(
    config_file: str, config_directory: Annotated[Optional[str], typer.Option(help="path to the config dir")] = None
):
    """Prints the evaluated configuration."""
    # If we don't have config:// in the beginning, or do not have an absolute path, resolve the absolute path.
    if not config_file.startswith("/") and not config_file.startswith("config://"):  #
        config_file = os.path.abspath(config_file)

    if config_directory is not None:
        console.print(f"[bold][red] Got custom config directory: {config_directory}")

        with TempConfigEnv(path=Path(config_directory)):
            configuration = Configuration()
            data = configuration.load(config_file)

    else:
        configuration = Configuration()
        data = configuration.load(config_file)

    console.print(f"[bold][white] Contents of: {config_file}")
    yaml_string = configuration.dump(data)
    syntax = Syntax(yaml_string, "yaml")
    console.print(syntax)
