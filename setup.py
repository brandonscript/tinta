#!/usr/bin/env python

# Tinta — Copyright (c) 2026 github.com/brandonscript
# Licensed under the MIT License. See LICENSE.

from pathlib import Path

from setuptools import setup

with Path("README.md").open(encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="tinta",
    version="1.0.0",
    description="Tinta, a magical console output tool.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://github.com/brandonscript/tinta",
    author="Brandon Shelley",
    author_email="brandon@pacificaviator.co",
    install_requires=[],
    include_package_data=True,
    license="MIT",
    packages=["tinta"],
    keywords="console colors ansi print terminal development",
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Environment :: Console",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
    ],
    zip_safe=False,
)
