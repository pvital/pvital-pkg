# (c) Copyright Paulo Vital 2024

import sys


def get_py_version() -> str:
    py_version = sys.version.split()[0]
    return py_version
