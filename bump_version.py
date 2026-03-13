#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024-2026 Tonic

"""Bump version across all canonical files.

Usage:
    python bump_version.py 0.1.0
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def bump(new_version: str) -> None:
	files = {
		ROOT / "VERSION": replace_whole_file,
		ROOT / "home" / "__init__.py": replace_dunder_version,
		ROOT / "pyproject.toml": None,  # dynamic — reads from __init__.py
	}

	# Optional: frontend/package.json
	pkg = ROOT / "frontend" / "package.json"
	if pkg.exists():
		files[pkg] = replace_package_json_version

	for path, replacer in files.items():
		if replacer is None:
			continue
		if not path.exists():
			print(f"  SKIP {path} (not found)")
			continue
		replacer(path, new_version)
		print(f"  OK   {path}")

	print(f"\nVersion bumped to {new_version}")


def replace_whole_file(path: Path, version: str) -> None:
	path.write_text(version + "\n")


def replace_dunder_version(path: Path, version: str) -> None:
	text = path.read_text()
	text = re.sub(r'__version__\s*=\s*"[^"]*"', f'__version__ = "{version}"', text)
	path.write_text(text)


def replace_package_json_version(path: Path, version: str) -> None:
	text = path.read_text()
	text = re.sub(r'"version"\s*:\s*"[^"]*"', f'"version": "{version}"', text)
	path.write_text(text)


if __name__ == "__main__":
	if len(sys.argv) != 2:
		print("Usage: python bump_version.py <new-version>")
		sys.exit(1)
	bump(sys.argv[1])
