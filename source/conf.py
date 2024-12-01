# -- Project information -----------------------------------------------------
project = "ecommerce_MohamadBailoun"
copyright = "2024, Mohamad Bailoun"
author = "Mohamad Bailoun"
release = "v1"

import os
import sys

sys.path.insert(0, os.path.abspath("../"))
sys.path.insert(0, os.path.abspath("../app.py"))
sys.path.insert(0, os.path.abspath("../app_init.py"))

# -- General configuration ---------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",  # Optional: for Google-style docstrings
    "sphinx.ext.autosummary",  # Optional: for generating summary pages
]

# Paths for static files
templates_path = ["_templates"]
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
html_theme = "alabaster"
html_static_path = ["_static"]
