#!/usr/bin/env python
# -*- coding: utf-8 -*-

# setup.py based on https://github.com/kennethreitz/setup.py/blob/master/setup.py

import io
import os

from setuptools import setup

# Package meta-data.
NAME = 'tcf_to_ometiff'
DESCRIPTION = 'Parser that transforms a Tomocube TCF file into a standardized OME-TIFF.'
URL = 'https://github.com/hzwirnmann/tcf_to_ometiff'
EMAIL = 'henning.zwirnmann@tum.de'
AUTHOR = 'Henning Zwirnmann'
REQUIRES_PYTHON = '>=3.8.0'
VERSION = '0.4.4'

# What packages are required for this module to be executed?
REQUIRED = [
    "numpy", "ome_types", "h5py", "aicsimageio", "typer"
]

EXTRAS = {}

here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in your MANIFEST.in file!
try:
    with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

# Load the package's __version__.py module as a dictionary.
about = {}
if not VERSION:
    project_slug = NAME.lower().replace("-", "_").replace(" ", "_")
    with open(os.path.join(here, project_slug, '__version__.py')) as f:
        exec(f.read(), about)
else:
    about['__version__'] = VERSION


# Where the magic happens:
setup(
    name=NAME,
    version=about['__version__'],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    # packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    # If your package is a single module, use this instead of 'packages':
    packages=['tcf_to_ometiff'],
    # entry_points={
    #     'console_scripts': ['mycli=mymodule:cli'],
    # },
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    include_package_data=True,
    license='GPLv3',
)
