"""Deterministically verify the public marketplace package structure."""

from __future__ import annotations

import compileall
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


class VerificationError(RuntimeError):
    """Raised when marketplace source truth is inconsistent."""


def load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise VerificationError(f"missing JSON file: {path.relative_to(ROOT)}") from exc
    except (OSError, json.JSONDecodeError) as exc:
        raise VerificationError(f"invalid JSON file {path.relative_to(ROOT)}: {exc}") from exc
    if not isinstance(payload, dict):
        raise VerificationError(f"JSON root must be an object: {path.relative_to(ROOT)}")
    return payload


def require_string(payload: dict[str, Any], field: str, label: str) -> str:
    value = payload.get(field)
    if not isinstance(value, str) or not value.strip():
        raise VerificationError(f"{label} field {field} must be a non-empty string")
    return value


def verify_marketplace() -> None:
    marketplace = load_json(ROOT / ".claude-plugin" / "marketplace.json")
    if require_string(marketplace, "name", "marketplace") != "market":
        raise VerificationError("marketplace name must be market")
    plugins = marketplace.get("plugins")
    if not isinstance(plugins, list) or not plugins:
        raise VerificationError("marketplace plugins must be a non-empty list")
    declared: set[str] = set()
    for index, item in enumerate(plugins, start=1):
        if not isinstance(item, dict):
            raise VerificationError(f"marketplace plugin {index} must be an object")
        name = require_string(item, "name", f"marketplace plugin {index}")
        version = require_string(item, "version", f"marketplace plugin {name}")
        if name in declared:
            raise VerificationError(f"duplicate marketplace plugin: {name}")
        declared.add(name)
        source = item.get("source")
        if not isinstance(source, dict):
            raise VerificationError(f"marketplace plugin {name} source must be an object")
        subdir = require_string(source, "subdir", f"marketplace plugin {name} source")
        if subdir != f"plugins/{name}":
            raise VerificationError(
                f"marketplace plugin {name} source subdir must be plugins/{name}"
            )
        manifest = load_json(ROOT / subdir / ".claude-plugin" / "plugin.json")
        if require_string(manifest, "name", f"plugin {name}") != name:
            raise VerificationError(f"plugin manifest name mismatch: {name}")
        if require_string(manifest, "version", f"plugin {name}") != version:
            raise VerificationError(f"plugin manifest version mismatch: {name}")
    actual = {path.name for path in (ROOT / "plugins").iterdir() if path.is_dir()}
    if actual != declared:
        raise VerificationError(
            f"plugin directory set differs from marketplace: missing={sorted(declared - actual)}, "
            f"extra={sorted(actual - declared)}"
        )


def verify_python_package() -> None:
    completed = subprocess.run(
        [sys.executable, "setup.py", "--name"],
        cwd=ROOT,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        shell=False,
    )
    if completed.returncode != 0:
        raise VerificationError(
            f"setup.py --name failed with exit code {completed.returncode}"
        )
    if completed.stdout.strip().splitlines()[-1:] != ["agency-v2"]:
        raise VerificationError("setup.py package name must remain agency-v2")
    for relative in ("agency", "scripts"):
        if not compileall.compile_dir(ROOT / relative, quiet=1):
            raise VerificationError(f"Python compilation failed under {relative}")


def main() -> int:
    try:
        verify_marketplace()
        verify_python_package()
    except (OSError, VerificationError) as exc:
        print(f"market verify: {exc}", file=sys.stderr)
        return 1
    print("market verify: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
