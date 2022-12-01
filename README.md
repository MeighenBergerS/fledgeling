# Fennel

Authors:

1. Stephan Meighen-Berger, developed the Nyx Code

## Table of contents

1. [Introduction](#introduction)

2. [Citation](#citation)

3. [Installation](#installation)

4. [Usage](#usage)

## Introduction <a name="introduction"></a>

![Logo](/images/logo.png "Fledgeling")

Welcome to Fledgeling!

This is a light-weight python package to give you a brief introduction how to handle IceCube data and atmospherics.

## Citation <a name="citation"></a>

Please cite this [software](https://github.com/MeighenBergerS/fledgeling) using
```
@software{sloth2022@github,
  author = {Stephan Meighen-Berger},
  title = {{Fledgeling}: Introduction to IceCube Atmospheric Comparisons,
  url = {https://github.com/MeighenBergerS/fledgeling},
  version = {0.0.1},
  year = {2022},
}
```

## Installation <a name="installation"></a>

Install using pip:
```python
pip install fledgeling
```
[The PyPi webpage](https://pypi.org/project/fledgeling/)

## Usage <a name="usage"></a>

A very basic example of how to use this code is given in examples.
There a quick tutorial is given how to generate an image like

![Example](/images/model_vs_data.png "Simulation")

is given. Note that you will the 10 years of IceCube dataset and either the pre-calculated
icecube_standard.pkl and shower.pkl files or calculate them yourself using standard_generator.py
