#!/usr/bin/env python3
"""
Configuración de instalación para el SDK de Agent Tool Description Format (ATDF).
"""

import os
from setuptools import setup, find_packages

# Leer README.md para descripción larga
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Definir dependencias
install_requires = ["pydantic>=2.0.0", "jsonschema>=4.0.0", "PyYAML>=6.0"]

extras_require = {
    "vector": ["chromadb>=0.4.0", "sentence-transformers>=2.0.0"],
    "dev": ["black", "isort", "mypy", "pytest", "pytest-cov"],
}

setup(
    name="atdf-sdk",
    version="0.3.0",
    author="ATDF Contributors",
    author_email="info@atdf.dev",
    description="SDK para Agent Tool Description Format (ATDF)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MauricioPerera/agent-tool-description-format",
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    extras_require=extras_require,
    entry_points={
        "console_scripts": [
            "atdf-search=sdk.vector_search.search_cli:main_entry",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
)
