#!/usr/bin/env python3
"""
Generate API documentation for InsolvencyBot using Sphinx.

This script sets up and builds Sphinx documentation for the project.
"""

import os
import sys
import subprocess
import shutil

def setup_sphinx_docs():
    """Set up Sphinx documentation directory and configuration."""
    docs_dir = "docs"
    
    # Create docs directory if it doesn't exist
    if not os.path.exists(docs_dir):
        os.makedirs(docs_dir)
    
    # Create source directory for docs
    source_dir = os.path.join(docs_dir, "source")
    if not os.path.exists(source_dir):
        os.makedirs(source_dir)
    
    # Create conf.py with Sphinx configuration
    conf_py = """
# Configuration file for the Sphinx documentation builder.

import os
import sys
sys.path.insert(0, os.path.abspath('../..'))

# -- Project information -----------------------------------------------------
project = 'InsolvencyBot'
copyright = '2023, Fast Data Science'
author = 'Fast Data Science'

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
]

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True

# Intersphinx settings
intersphinx_mapping = {'python': ('https://docs.python.org/3', None)}
"""
    
    with open(os.path.join(source_dir, "conf.py"), "w") as f:
        f.write(conf_py)
    
    # Create index.rst
    index_rst = """
Welcome to InsolvencyBot's documentation!
========================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   modules

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
"""
    
    with open(os.path.join(source_dir, "index.rst"), "w") as f:
        f.write(index_rst)
    
    # Create Makefile for docs
    makefile = """
# Minimal makefile for Sphinx documentation

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
SPHINXPROJ    = InsolvencyBot
SOURCEDIR     = source
BUILDDIR      = build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(SPHINXPROJ)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(SPHINXPROJ)
"""
    
    with open(os.path.join(docs_dir, "Makefile"), "w") as f:
        f.write(makefile)

def generate_api_docs():
    """Generate API documentation using sphinx-apidoc."""
    docs_dir = "docs"
    source_dir = os.path.join(docs_dir, "source")
    
    # Generate API documentation
    subprocess.run([
        "sphinx-apidoc", 
        "-o", source_dir, 
        "src/hoi_insolvencybot",
        "-f",  # Force overwrite existing files
        "--implicit-namespaces",  # Handle implicit namespace packages
    ])
    
    # Build HTML documentation
    subprocess.run([
        "sphinx-build",
        "-b", "html",
        source_dir,
        os.path.join(docs_dir, "build", "html")
    ])
    
    print(f"Documentation built successfully. Open {os.path.join(docs_dir, 'build', 'html', 'index.html')} to view.")

if __name__ == "__main__":
    # Install required packages
    print("Installing Sphinx and related packages...")
    subprocess.run([sys.executable, "-m", "pip", "install", "sphinx", "sphinx_rtd_theme"])
    
    print("Setting up Sphinx documentation...")
    setup_sphinx_docs()
    
    print("Generating API documentation...")
    generate_api_docs()
