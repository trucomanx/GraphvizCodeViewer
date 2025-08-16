#!/usr/bin/python3

#!/usr/bin/env python3
import pathlib
import sys

here = pathlib.Path(__file__).parent.resolve()
sys.path.insert(0, str(here))

from graphviz_code_viewer.about import (
    __version__,
    __package__,
    __program_name__,
    __author__,
    __email__,
    __description__,
    __url_source__,
    __url_doc__,
    __url_funding__,
    __url_bugs__,
)

# Lê o conteúdo do README.md
readme_path = here / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

pyproject_content = f"""
[build-system]
requires = ["setuptools>=61", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{__package__}"
version = "{__version__}"
description = "{__description__}"
readme = "README.md"
authors = [{{name = "{__author__}", email = "{__email__}"}}]
maintainers = [{{name = "{__author__}", email = "{__email__}"}}]
requires-python = ">=3.8"
classifiers = [
    "Programming Language :: Python :: 3",
    "Operating System :: OS Independent",
]
license = "GPL-3.0-only WITH Classpath-Exception-2.0 OR BSD-3-Clause"
license-files = ["LICENSE"]
keywords = ["writing", "translate"]
dependencies = [
    "PyQt5",
    "deep-consultation"
]

[project.urls]
"Bug Reports" = "{__url_bugs__}"
"Funding" = "{__url_funding__}"
"Documentation" = "{__url_doc__}"
"Source" = "{__url_source__}"

[project.scripts]
"{__program_name__}" = "{__package__}.program:main"

[tool.setuptools]
packages = ["{__package__}", "{__package__}.modules"]

[tool.setuptools.package-data]
"{__package__}" = ["icons/logo.png"]
"""

# Escreve o pyproject.toml
path_pyproject = here / "pyproject.toml"
path_pyproject.write_text(pyproject_content.strip() + "\n", encoding="utf-8")

print(f"Arquivo 'pyproject.toml' gerado com sucesso em {path_pyproject}")

