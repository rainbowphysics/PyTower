import pytower
from datetime import datetime
import os
import sys

# Ensure Sphinx can include package/module
sys.path.insert(0, os.path.abspath('../../'))

# Configuration file for the Sphinx documentation builder.

# -- Project information

project = 'PyTower'
copyright = f'{datetime.now().year}, Rainbow Physics'
author = 'Rainbow Physics'

release = f'{pytower.__version__}'
version = f'{pytower.__version__}'

# -- General configuration

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
    'sphinx.ext.napoleon',
    'sphinx_autodoc_typehints'
]

autosummary_generate = True
autosummary_generate_overwrite = True
autosummary_imported_members = False

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
}
intersphinx_disabled_domains = ['std']

templates_path = ['_templates']

# -- Options for HTML output
html_theme = 'sphinx_rtd_theme'
