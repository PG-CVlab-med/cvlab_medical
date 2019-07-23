#!/usr/bin/env python3

import sys
import os
from distutils.core import setup

from setuptools import find_packages
from glob import glob


def add_package(package_data, package_name, extensions):
    files = glob(package_name + "/**", recursive=True)
    files = list(map(lambda x:x[len(package_name)+1:].replace("\\","/"), files))
    files = [f for f in files if any(f.endswith(e) for e in extensions)]
    package_data[package_name] = files


def find_package_data():
    package_data = {}

    packages = glob("cvlab_*/__init__.py")
    extensions = [".cvlab", ".jpg", ".png", ".dcm", ".json", ".bmp"]

    for package_name in packages:
        package_name = package_name.replace("\\","/").split("/")[0]
        add_package(package_data, package_name, extensions)

    return package_data


if sys.version_info.major <= 2:
    raise Exception("Only python 3+ is supported!")


requirements = [
    "cvlab>=1.2",
]


__version__ = "0.1"

this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

description = long_description.splitlines()[0].strip()

setup(
    name="cvlab_medical",
    version=__version__,
    description=description,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Adam Brzeski, Jan Cychnerski',
    author_email='adam.m.brzeski@gmail.com, jan.cychnerski@gmail.com',
    url='https://github.com/cvlab-ai/cvlab_medical',
    packages=find_packages(exclude=["temp"]),
    package_data=find_package_data(),
    license="AGPL-3.0+",
    python_requires='>=3.3',
    install_requires=requirements,
)
