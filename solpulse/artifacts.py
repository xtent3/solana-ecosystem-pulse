"""Persist one snapshot as consistent, atomically replaced artifacts."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from solpulse.render import render_html, render_json, render_markdown


def _atomic_write(path: Path, content: str) -> None:
    """Write UTF-8 content beside the destination, then replace it atomically."""
    temporary = path.with_name(f".{path.name}.tmp")
    try:
        temporary.write_text(content, encoding="utf-8", newline="\n")
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def write_artifacts(
    snapshot: dict[str, Any], output_directory: str | Path
) -> dict[str, Path]:
    """Render and persist JSON, Markdown, and HTML from the same snapshot."""
    output = Path(output_directory)
    output.mkdir(parents=True, exist_ok=True)
    paths = {
        "json": output / "snapshot.json",
        "markdown": output / "report.md",
        "html": output / "dashboard.html",
    }
    rendered = {
        "json": render_json(snapshot),
        "markdown": render_markdown(snapshot),
        "html": render_html(snapshot),
    }
    for name, path in paths.items():
        _atomic_write(path, rendered[name])
    return paths
