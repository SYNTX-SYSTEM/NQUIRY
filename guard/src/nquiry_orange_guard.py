"""ORANGE import-origin guard (proof-infrastructure field, PX-1).

Binds this hermetic Python 3.13 environment exclusively to the frozen ORANGE
worktree (checkpoint-PFC-PCPG-5 @ e0a6b3b). It fails closed: a run is refused,
never silently continued, when

- user site-packages are enabled (PYTHONNOUSERSITE must hold);
- the interpreter is not this environment's;
- a first-party distribution (`nquiry`) or an `__editable__` finder is present
  (the master-bound editable install must never be reused);
- any first-party top-level name (derived from the ORANGE tree's own
  pyproject `[tool.setuptools] packages` plus its `scripts/` modules, never a
  hand-kept list) resolves outside the ORANGE root, or not at all;
- after collection, any loaded first-party module has a file outside it.

Loaded automatically by pytest through the `pytest11` entry point of this
distribution, so every pytest process in this environment (including xdist
workers) runs it. Also usable without pytest: `python -m nquiry_orange_guard`.
"""

from __future__ import annotations

import importlib.metadata
import importlib.util
import site
import sys
import tomllib
from pathlib import Path

ORANGE_ROOT = Path("/home/codi/Entwicklung/nquiry/worktrees/orange-proof-infra").resolve()
ENV_PREFIX = Path("/home/codi/Entwicklung/nquiry/.venv-proof313-orange").resolve()
FORBIDDEN_DISTRIBUTIONS = ("nquiry",)


class ImportOriginViolation(Exception):
    pass


def first_party_names() -> tuple[str, ...]:
    with (ORANGE_ROOT / "pyproject.toml").open("rb") as handle:
        packages = tomllib.load(handle)["tool"]["setuptools"]["packages"]
    names = {p.split(".")[0] for p in packages}
    names |= {p.stem for p in (ORANGE_ROOT / "scripts").glob("*.py")}
    return tuple(sorted(names))


def _inside(path: str | None) -> bool:
    if not path:
        return False
    try:
        Path(path).resolve().relative_to(ORANGE_ROOT)
    except ValueError:
        return False
    return True


def environment_violations() -> list[str]:
    problems: list[str] = []
    if site.ENABLE_USER_SITE or not sys.flags.no_user_site:
        problems.append("user site-packages enabled (PYTHONNOUSERSITE=1 must hold)")
    if Path(sys.prefix).resolve() != ENV_PREFIX:
        problems.append(f"interpreter prefix {sys.prefix} is not {ENV_PREFIX}")
    for name in FORBIDDEN_DISTRIBUTIONS:
        try:
            dist = importlib.metadata.distribution(name)
        except importlib.metadata.PackageNotFoundError:
            continue
        problems.append(f"first-party distribution {name!r} is installed ({dist.version})")
    for finder in sys.meta_path:
        label = getattr(finder, "__module__", "") + "." + getattr(finder, "__name__", "")
        if "__editable__" in label:
            problems.append(f"editable finder on sys.meta_path: {label}")
    return problems


def spec_violations() -> list[str]:
    problems: list[str] = []
    for name in first_party_names():
        spec = importlib.util.find_spec(name)
        if spec is None:
            problems.append(f"{name}: not resolvable")
            continue
        locations = list(spec.submodule_search_locations or []) or [spec.origin]
        outside = [loc for loc in locations if not _inside(loc)]
        if outside:
            problems.append(f"{name}: resolves outside ORANGE -> {outside}")
    return problems


def loaded_violations() -> list[str]:
    names = set(first_party_names())
    problems: list[str] = []
    for module_name, module in list(sys.modules.items()):
        if module_name.split(".")[0] not in names or module is None:
            continue
        where = getattr(module, "__file__", None)
        if where is None:
            paths = list(getattr(module, "__path__", []) or [])
            where = paths[0] if paths else None
        if not _inside(where):
            problems.append(f"loaded {module_name} from {where}")
    return problems


def verify(*, loaded: bool = False) -> None:
    problems = environment_violations() + spec_violations()
    if loaded:
        problems += loaded_violations()
    if problems:
        raise ImportOriginViolation(
            "ORANGE import-origin guard REFUSED:\n  " + "\n  ".join(problems)
        )


# --------------------------------------------------------------- pytest plugin


_WORKER_REFUSAL: list[str] = []


def pytest_configure(config):  # type: ignore[no-untyped-def]
    import pytest

    try:
        verify()
    except ImportOriginViolation as exc:
        if hasattr(config, "workerinput"):
            # An xdist worker that dies in configure is aggregated by the
            # controller as exit 5 ("no tests collected"), which is
            # indistinguishable from an empty selection. Refuse inside the
            # worker's collection instead, so the refusal is a reported
            # collection ERROR (exit != 0 and != 5).
            _WORKER_REFUSAL.append(str(exc))
            return
        raise pytest.UsageError(str(exc)) from None


def pytest_collect_file(file_path, parent):  # type: ignore[no-untyped-def]
    if _WORKER_REFUSAL:
        raise ImportOriginViolation(_WORKER_REFUSAL[0])
    return None


def pytest_collection_finish(session):  # type: ignore[no-untyped-def]
    import pytest

    try:
        verify(loaded=True)
    except ImportOriginViolation as exc:
        pytest.exit(str(exc), returncode=4)


def pytest_report_header(config):  # type: ignore[no-untyped-def]
    return [f"ORANGE import-origin guard: bound to {ORANGE_ROOT} (env {ENV_PREFIX})"]


def main() -> int:
    try:
        verify(loaded=True)
    except ImportOriginViolation as exc:
        print(exc)
        return 1
    print(
        f"ORANGE_IMPORT_ORIGIN::PASS ({len(first_party_names())} first-party names under "
        f"{ORANGE_ROOT})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
