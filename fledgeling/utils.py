# -*- coding: utf-8 -*-
# Name: utils.py
# Authors: Stephan Meighen-Berger
# Utility functions

# imports
import csv
from typing import Dict
import numpy as np
import pandas as pd

def ice_parser(filename: str) -> np.array:
    """ loads IceCube data and parses it in a useful fashion.
    Note depending on the type of data the output shape may be different.
    For Aeff:
        log10(E_nu/GeV)_min, log10(E_nu/GeV)_max, Dec_nu_min[deg], Dec_nu_max[deg], A_Eff[cm^2]
    For Events:
        MJD, log10(E/GeV), AngErr[deg], RA[deg], Dec[deg], Azimuth[deg], Zenith[deg]
    For the smearing matrix:
        log10(E_nu/GeV)_min, log10(E_nu/GeV)_max, Dec_nu_min[deg], Dec_nu_max[deg], log10(E/GeV), PSF_min[deg], PSF_max[deg],
        AngErr_min[deg], AngErr_max[deg], Fractional_Counts
    Parameters
    ----------
    filename: str
        Path to the icecube data file to load
    """
    store = []
    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row_num, row in enumerate(reader):
            if row_num == 0:
                continue
            store.append(row[0].split())
    store = np.array(store, dtype=float)
    return store

def dataframe_from2d(dic: Dict, column_names: list, new_col_name: str) -> pd.DataFrame:
    """ Converts a 2d dictionary to a combined dataframe

    Parameters
    ----------
    dic: Dict
        A dictionary whose elements are 2d numpy arrays
    column_names: list
        Names of the columns of the 2d arrays
    new_col_name: str
        Name of the new column containing the original dictionary key
    Returns
    -------
    df: pd.DataFrame
        Dataframe object containing the data with an addional column for the original
        dictionary index
    """
    dfs = []
    for key in dic.keys():
        tmp = pd.DataFrame(
            dic[key],
            columns=column_names
        )
        tmp[new_col_name] = key
        dfs.append(tmp)
    return pd.concat(dfs)
        