"""Packaging completeness (WU-PFC-AC1.1): every Python package that the
distribution maps must be listed in `pyproject.toml`'s explicit `packages`.

`pyproject.toml` says why the list is explicit ("a missing entry here is a
packaging bug, not something to paper over with `find`"). The images install
the distribution (`pip install .`), so an unlisted subpackage exists in the
repository and in every test run, but not in the deployed container. WU-PFC-AC1's
production candidate proved exactly that: `nquiry_api.operator` was missing from
the api image.
"""

from __future__ import annotations

import pathlib

try:
    import tomllib
except ModuleNotFoundError:  # the local toolchain runs 3.10; the images run 3.13
    import tomli as tomllib  # type: ignore[no-redef]

ROOT = pathlib.Path(__file__).resolve().parents[2]


def _listed() -> set[str]:
    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    return set(data["tool"]["setuptools"]["packages"])


def _mapped() -> set[str]:
    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    found: set[str] = set()
    for prefix, rel in data["tool"]["setuptools"]["package-dir"].items():
        base = ROOT / rel
        for init in base.rglob("__init__.py"):
            if "__pycache__" in init.parts:
                continue
            parts = init.parent.relative_to(base).parts
            name = ".".join((prefix, *parts)) if prefix else ".".join(parts)
            if name:
                found.add(name)
    return found


def test_every_mapped_package_is_listed_for_the_distribution() -> None:
    assert sorted(_mapped() - _listed()) == []


def test_every_listed_package_exists() -> None:
    assert sorted(_listed() - _mapped()) == []
