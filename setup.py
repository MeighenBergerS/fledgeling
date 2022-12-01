#!/usr/bin/env python

import pathlib
from setuptools import setup

# Parent directory
HERE = pathlib.Path(__file__).parent

# The readme file
README = (HERE / "README.md").read_text()

setup(
    name="fledgeling",
    version="0.0.1",
    description="Introduction to IceCube data and atmospherics",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Stephan Meighen-Berger",
    author_email="stephan.meighenberger@gmail.com",
    url='https://github.com/MeighenBergerS/fledgeling',
    license="GNU",
    install_requires=[
        "PyYAML",
        "numpy",
        "scipy",
        "pandas",
        "mceq",
        "tqdm",
        "pyarrow"
    ],
    extras_require={
        "interactive": ["nbstripout", "matplotlib", "jupyter"],
        "custom": ["mceq"]
    },
    packages=["fledgeling"],
    package_data={'fledgeling': ["data/*.pkl"]},
    include_package_data=True
)
