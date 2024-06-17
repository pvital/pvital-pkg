# (c) Copyright Paulo Vital 2024


import click

from pvital_pkg.utils import get_py_version


@click.command(hidden=True)
def hello() -> None:
    py_version = get_py_version()
    msg = f"Hello, World! You are using Python {py_version}!"
    click.echo(msg)


if __name__ == "__main__":
    hello()
