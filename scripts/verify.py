"""Deterministically verify the public Market v1 distribution tree."""

from __future__ import annotations

import ast
import compileall
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
MARKET_REPOSITORY_URL = "https://github.com/Sweetteabittersugar/market.git"
MARKET_REF = "master"
MARKET_VERSION = "1.0.0"
LEGACY_PACKAGE = "agency-v2"
LEGACY_VERSION = "2.0.0"
EXPECTED_PLUGINS = {
    "agent-personas",
    "full-arsenal",
    "research-kit",
    "story-dev",
    "workflow-core",
}

MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\(([^)\n]*)\)")
EXTERNAL_SCHEMES = ("http://", "https://", "mailto:", "tel:", "data:")
FORBIDDEN_PUBLIC_PATTERNS = (
    (
        "machine-specific private workspace path",
        re.compile(r"(?i)\b[A-Z]:[/\\]" + "ai" + r"(?:[/\\]|$)"),
    ),
    (
        "personal Windows home path",
        re.compile(r"(?i)\b[A-Z]:[/\\]Users[/\\][^/\\\s]+"),
    ),
    (
        "personal macOS home path",
        re.compile(r"(?i)(?:^|[\s(`'\"])\/Users\/[^/\s]+\/"),
    ),
    (
        "private root repository URL",
        re.compile(
            r"(?i)github\.com/Sweetteabittersugar/"
            + "ai"
            + r"(?:\.git)?(?:[/#)\s]|$)"
        ),
    ),
    (
        "private governance evidence path",
        re.compile(r"(?i)\.context[/\\](?:evidence|handoffs|upstream-projects)[/\\]"),
    ),
    ("retired private control-plane command", re.compile(r"(?i)\b" + "task" + "ctl\b")),
    ("obsolete marketplace name", re.compile("sweettea-" + "ai-marketplace", re.I)),
)
SECRET_PATTERNS = (
    ("private key", re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----")),
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{30,}\b")),
    ("OpenAI key", re.compile(r"\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{20,}\b")),
    ("AWS access key", re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")),
)


class VerificationError(RuntimeError):
    """Raised when the public distribution tree is inconsistent."""


def run(*argv: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(argv),
        cwd=ROOT,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        shell=False,
    )


def load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise VerificationError(f"missing JSON file: {path.relative_to(ROOT)}") from exc
    except (OSError, json.JSONDecodeError) as exc:
        raise VerificationError(
            f"invalid JSON file {path.relative_to(ROOT)}: {exc}"
        ) from exc
    if not isinstance(payload, dict):
        raise VerificationError(f"JSON root must be an object: {path.relative_to(ROOT)}")
    return payload


def require_string(payload: dict[str, Any], field: str, label: str) -> str:
    value = payload.get(field)
    if not isinstance(value, str) or not value.strip():
        raise VerificationError(f"{label} field {field} must be a non-empty string")
    return value


def tracked_paths() -> list[Path]:
    completed = run("git", "ls-files", "-z")
    if completed.returncode != 0:
        raise VerificationError("git ls-files failed")
    return [ROOT / item for item in completed.stdout.split("\0") if item]


def verify_marketplace() -> None:
    marketplace = load_json(ROOT / ".claude-plugin" / "marketplace.json")
    if require_string(marketplace, "name", "marketplace") != "market":
        raise VerificationError("marketplace name must be market")
    plugins = marketplace.get("plugins")
    if not isinstance(plugins, list):
        raise VerificationError("marketplace plugins must be an array")

    declared: set[str] = set()
    for index, item in enumerate(plugins, start=1):
        if not isinstance(item, dict):
            raise VerificationError(f"marketplace plugin {index} must be an object")
        name = require_string(item, "name", f"marketplace plugin {index}")
        version = require_string(item, "version", f"marketplace plugin {name}")
        if name in declared:
            raise VerificationError(f"duplicate marketplace plugin: {name}")
        declared.add(name)
        if version != MARKET_VERSION:
            raise VerificationError(f"marketplace plugin {name} must be {MARKET_VERSION}")

        source = item.get("source")
        if not isinstance(source, dict):
            raise VerificationError(f"marketplace plugin {name} source must be an object")
        if require_string(source, "source", f"plugin {name} source") != "url":
            raise VerificationError(f"marketplace plugin {name} source type must be url")
        if require_string(source, "url", f"plugin {name} source") != MARKET_REPOSITORY_URL:
            raise VerificationError(f"plugin {name} must use the canonical Market repository")
        if require_string(source, "ref", f"plugin {name} source") != MARKET_REF:
            raise VerificationError(f"plugin {name} source ref must be {MARKET_REF}")
        subdir = require_string(source, "subdir", f"plugin {name} source")
        if subdir != f"plugins/{name}":
            raise VerificationError(f"plugin {name} source subdir must be plugins/{name}")

        plugin_root = ROOT / subdir
        manifest = load_json(plugin_root / ".claude-plugin" / "plugin.json")
        if require_string(manifest, "name", f"plugin {name}") != name:
            raise VerificationError(f"plugin manifest name mismatch: {name}")
        if require_string(manifest, "version", f"plugin {name}") != MARKET_VERSION:
            raise VerificationError(f"plugin manifest version mismatch: {name}")

    actual = {path.name for path in (ROOT / "plugins").iterdir() if path.is_dir()}
    if declared != EXPECTED_PLUGINS or actual != EXPECTED_PLUGINS:
        raise VerificationError(
            "plugin set must be exactly: " + ", ".join(sorted(EXPECTED_PLUGINS))
        )


def markdown_targets(markdown: Path) -> Iterable[str]:
    text = markdown.read_text(encoding="utf-8")
    for match in MARKDOWN_LINK.finditer(text):
        raw = match.group(1).strip()
        if raw.startswith("<") and ">" in raw:
            raw = raw[1 : raw.index(">")]
        else:
            raw = raw.split(maxsplit=1)[0] if raw else ""
        yield raw.strip()


def verify_markdown_links(paths: list[Path]) -> None:
    failures: list[str] = []
    for markdown in (path for path in paths if path.suffix.lower() == ".md"):
        for target in markdown_targets(markdown):
            lowered = target.lower()
            if (
                not target
                or target.startswith("#")
                or lowered.startswith(EXTERNAL_SCHEMES)
                or "{" in target
                or "}" in target
                or target == "URL"
            ):
                continue
            local = unquote(target.split("#", 1)[0].split("?", 1)[0])
            if not local:
                continue
            if local.startswith(("/", "\\")) or re.match(r"^[A-Za-z]:[/\\]", local):
                failures.append(f"{markdown.relative_to(ROOT)} -> absolute path {target}")
                continue
            candidate = markdown.parent.joinpath(*local.replace("\\", "/").split("/"))
            try:
                candidate.resolve().relative_to(ROOT.resolve())
            except ValueError:
                failures.append(f"{markdown.relative_to(ROOT)} -> outside tree {target}")
                continue
            if not candidate.exists():
                failures.append(f"{markdown.relative_to(ROOT)} -> {target}")
    if failures:
        raise VerificationError("broken local Markdown links:\n- " + "\n- ".join(failures))


def read_text(path: Path) -> str | None:
    try:
        if path.stat().st_size > 1_000_000:
            return None
        data = path.read_bytes()
    except OSError:
        return None
    if b"\0" in data[:4096]:
        return None
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError:
        return None


def verify_public_boundary(paths: list[Path]) -> None:
    relative_paths = [path.relative_to(ROOT).as_posix() for path in paths]
    if any(item == ".context" or item.startswith(".context/") for item in relative_paths):
        raise VerificationError("repository .context must not be tracked in the release tree")

    findings: list[str] = []
    for path in paths:
        text = read_text(path)
        if text is None:
            continue
        for label, pattern in (*FORBIDDEN_PUBLIC_PATTERNS, *SECRET_PATTERNS):
            if pattern.search(text):
                findings.append(f"{path.relative_to(ROOT)}: {label}")
    if findings:
        raise VerificationError("public boundary violations:\n- " + "\n- ".join(findings))


def verify_python_helper() -> None:
    setup_path = ROOT / "setup.py"
    tree = ast.parse(setup_path.read_text(encoding="utf-8"), filename=str(setup_path))
    metadata: dict[str, str] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name):
            continue
        if node.func.id != "setup":
            continue
        for keyword in node.keywords:
            if keyword.arg in {"name", "version"}:
                value = ast.literal_eval(keyword.value)
                if isinstance(value, str):
                    metadata[keyword.arg] = value
    if metadata.get("name") != LEGACY_PACKAGE:
        raise VerificationError(f"setup.py name must remain {LEGACY_PACKAGE}")
    if metadata.get("version") != LEGACY_VERSION:
        raise VerificationError(f"setup.py version must remain {LEGACY_VERSION}")
    if not compileall.compile_dir(ROOT / "agency", quiet=1):
        raise VerificationError("Python compilation failed under agency")
    if not compileall.compile_dir(ROOT / "scripts", quiet=1):
        raise VerificationError("Python compilation failed under scripts")


def verify_git_diff() -> None:
    completed = run("git", "diff", "--check", "HEAD", "--")
    if completed.returncode != 0:
        raise VerificationError("git diff --check failed:\n" + completed.stdout)


def main() -> int:
    try:
        paths = tracked_paths()
        verify_marketplace()
        verify_markdown_links(paths)
        verify_public_boundary(paths)
        verify_python_helper()
        verify_git_diff()
    except (OSError, VerificationError) as exc:
        print(f"market verify: {exc}", file=sys.stderr)
        return 1
    print(
        f"market verify: PASS ({len(EXPECTED_PLUGINS)} plugins, "
        f"Marketplace {MARKET_VERSION}, legacy helper {LEGACY_VERSION})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
