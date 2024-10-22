# (c) Copyright Paulo Vital 2024

from click.testing import CliRunner

from pvital_pkg.commands import hello


def test_hello() -> None:
    runner = CliRunner()
    result = runner.invoke(hello)

    msg = "Hello, World! You are using Python 3"
    assert result.exit_code == 0
    assert result.output.startswith(msg)
