#!/usr/bin/env python
import os
import re

try:
    from setuptools import setup, Extension
except ImportError:
    from distutils.core import setup, Extension


if os.path.isfile("MANIFEST"):
    os.unlink("MANIFEST")


version = re.search('__version__ = "([^"]+)"',
                    open("commandant/__init__.py").read()).group(1)


def find_packages():
    # implement a simple find_packages so we don't have to depend on
    # setuptools
    packages = []
    for directory, subdirectories, files in os.walk("commandant"):
        if "__init__.py" in files:
            packages.append(directory.replace(os.sep, "."))
    return [package for package in packages
            if not package.startswith("commandant.tests")]


setup(
    name="commandant",
    version=version,
    description=(
        "Commandant is a framework for building command-oriented tools."),
    author="Jamshed Kakar",
    author_email="jkakar@kakar.ca",
    maintainer="Jamshed Kakar",
    maintainer_email="jkakar@kakar.ca",
    license="GPL",
    url="https://launchpad.net/commandant",
    download_url="https://launchpad.net/commandant/+download",
    packages=find_packages(),
    scripts=["bin/commandant"],
    zip_safe=False,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
        "Topic :: Utilities",
        "Topic :: Software Development :: User Interfaces",
    ])
