#!/usr/bin/env python3
"""setup.py — pip install agency-v2 (editable or normal).

Usage:
    pip install -e .          # development (editable)
    pip install .             # normal install
"""

from setuptools import setup, find_packages

setup(
    name="agency-v2",
    version="2.0.0",
    description="Claude Code enhancement pack — agents, skills, workflow, cost tracking",
    author="Agency",
    python_requires=">=3.8",
    packages=find_packages(),
    include_package_data=True,
    # Minimal dependencies — everything else is stdlib
    install_requires=[],
    # Slash commands as console scripts
    entry_points={
        "console_scripts": [
            "agency-cost = agency.cost:main",
            "agency-history = agency.history:main",
        ],
    },
)
