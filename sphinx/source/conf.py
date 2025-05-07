import sys
import os

sys.path.insert(0, os.path.abspath('../..'))

project = 'sat_download'
copyright = '2025, Sergio Heredia'
author = 'Sergio Heredia'
release = '1.0.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.autosummary',
    'sphinx.ext.githubpages',
    "nbsphinx",
    'IPython.sphinxext.ipython_console_highlighting',
]

nbsphinx_allow_errors = True
nbsphinx_execute = 'never'

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'sphinx_book_theme'
html_static_path = ['_static']
html_extra_path = ['.nojekyll']
html_baseurl = "https://github.com/Aouei/remote-sensing-satellite-downloader"