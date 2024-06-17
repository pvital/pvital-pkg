# (c) Copyright Paulo Vital 2024

import click

from pvital_pkg.commands import hello
from pvital_pkg.version import __version__ as VERSION

PROG_NAME = "pvital-pkg"


@click.version_option(VERSION, prog_name=PROG_NAME)
@click.group(invoke_without_command=True)
def cli():
    hello()


cli.add_command(hello)
