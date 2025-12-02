#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Setup configuration for Crypto Portfolio Tracker v3
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    with open(requirements_file) as f:
        requirements = [
            line.strip() 
            for line in f 
            if line.strip() and not line.startswith("#")
        ]

setup(
    name="crypto-portfolio-tracker",
    version="3.0.0",
    description="Multi-wallet, multi-blockchain cryptocurrency portfolio tracker with DeFi support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Crypto Portfolio Tracker Team",
    author_email="info@cryptotracker.dev",
    url="https://github.com/yourusername/crypto-portfolio-tracker",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/crypto-portfolio-tracker/issues",
        "Documentation": "https://crypto-portfolio-tracker.readthedocs.io",
        "Source Code": "https://github.com/yourusername/crypto-portfolio-tracker",
    },
    license="MIT",
    packages=find_packages(where=".", include=["src*"]),
    python_requires=">=3.9",
    install_requires=requirements,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: Spanish",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Financial",
        "Topic :: Software :: Libraries :: Python Modules",
    ],
    keywords=[
        "cryptocurrency",
        "portfolio",
        "tracker",
        "defi",
        "uniswap",
        "aave",
        "ethereum",
        "blockchain",
    ],
    entry_points={
        "console_scripts": [
            "crypto-tracker=scripts.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
