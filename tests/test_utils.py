# (c) Copyright Paulo Vital 2024

from pvital_pkg.utils import get_py_version


def test_get_py_version() -> None:
    py_version = get_py_version()
    py_version_list = py_version.split(".")

    assert py_version.startswith("3.")
    assert len(py_version_list) == 3
    assert int(py_version_list[1]) >= 9
    assert int(py_version_list[1]) <= 13
