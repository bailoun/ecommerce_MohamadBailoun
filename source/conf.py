project = "ecommerce_MohamadBailoun"
copyright = "2024, Mohamad Bailoun"
author = "Mohamad Bailoun"
release = "v1"

import os
import sys

sys.path.insert(0, os.path.abspath("../"))
sys.path.insert(0, os.path.abspath("../app.py"))
sys.path.insert(0, os.path.abspath("../app_init.py"))

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.autosummary",
]

templates_path = ["_templates"]
exclude_patterns = []

html_theme = "alabaster"
html_static_path = ["_static"]
