# -*- coding: utf-8 -*-
# Name: config.py
# Authors: Stephan Meighen-Berger
# Config file for the fledgeling package.

import logging
from typing import Dict, Any
import yaml

_baseconfig: Dict[str, Any]

_baseconfig = {
    ###########################################################################
    # General inputs
    ###########################################################################
    "general": {
        # Random state seed
        "random state seed": 1337,
        # Enable logger and config dump
        "enable logging": False,
        # Output level
        'debug level': logging.ERROR,
        # Note the paths need to be set appropiately for your system
        # Location of logging file handler
        "log file handler": "fledgeling.log",
        # Dump experiment config to this location
        "config location": "fledgeling.txt",
        "detector": "icecube",
    },
    ###########################################################################
    # Atmospherics
    ###########################################################################
    "atmospherics": {
        "name": "mceq",  # Options: mceq, FLUKA/HKKM
        "mceq model": {
            "interaction model": 'SIBYLL2.3c',
            "primary model": ("HillasGaisser2012", "H3a"),
            "atmosphere": ('MSIS00', ('SouthPole', 'January')),
            "zeniths": [0, 10, 20, 30, 40, 50, 60, 70, 80],
            "atmospheric storage": "data/shower.pkl"
        }
    },
    ###########################################################################
    # Experimental data
    ###########################################################################
    "experimental data": {
        "pre-computed": True,
        "standard": True,
        "tables": "data/icecube_standard.pkl",
        "filepath": "/home/unimelb.edu.au/smeighenberg/snap/firefox/common/Downloads/icecube_10year_ps"
    },
    ###########################################################################
    # IceCube 10 year point source data (standard used here)
    ###########################################################################
    "icecube data": {
        "effective areas": [
            '/irfs/IC40_effectiveArea.csv',
            '/irfs/IC59_effectiveArea.csv',
            '/irfs/IC79_effectiveArea.csv',
            '/irfs/IC86_I_effectiveArea.csv',
            '/irfs/IC86_II_effectiveArea.csv'
        ],
        "event data": [
            '/events/IC40_exp.csv',
            '/events/IC59_exp.csv',
            '/events/IC79_exp.csv',
            '/events/IC86_I_exp.csv',
            '/events/IC86_II_exp.csv',
            '/events/IC86_III_exp.csv',
            '/events/IC86_IV_exp.csv',
            '/events/IC86_V_exp.csv',
            '/events/IC86_VI_exp.csv',
            '/events/IC86_VII_exp.csv',
        ],
        "uptime": [
            '/uptime/IC40_exp.csv',
            '/uptime/IC59_exp.csv',
            '/uptime/IC79_exp.csv',
            '/uptime/IC86_I_exp.csv',
            '/uptime/IC86_II_exp.csv',
            '/uptime/IC86_III_exp.csv',
            '/uptime/IC86_IV_exp.csv',
            '/uptime/IC86_V_exp.csv',
            '/uptime/IC86_VI_exp.csv',
            '/uptime/IC86_VII_exp.csv'
        ],
        "smearing matrix": [
            '/irfs/IC40_smearing.csv',
            '/irfs/IC59_smearing.csv',
            '/irfs/IC79_smearing.csv',
            '/irfs/IC86_I_smearing.csv',
            '/irfs/IC86_II_smearing.csv',
            '/irfs/IC86_II_smearing.csv',
            '/irfs/IC86_II_smearing.csv',
            '/irfs/IC86_II_smearing.csv',
            '/irfs/IC86_II_smearing.csv',
            '/irfs/IC86_II_smearing.csv',
        ]
    },
    ###########################################################################
    # PDG ID Lib
    ###########################################################################
    "pdg id": {
        11: "e-",
        -11: "e+",
        12: "nue",
        -12: "anti_nue",
        13: "mu-",
        -13: "mu+",
        14: "numu",
        -14: "anti_numu",
        15: "tau-",
        -15: "tau+",
        16: "nutau",
        -16: "anti_nutau",
        22: "gamma",
        211: "pi+",
        -211: "pi-",
        130: "KL0",
        2212: "p+",
        -2212: "p-",
        2112: "n",
    },
    ###########################################################################
    # Advanced
    ###########################################################################
    "advanced": {
        "ebins": [2, 9, 71],  # In log10(E/GeV)
        "thetas": [0., 180., 1],  # Defining the theta grid
        "years": 10,
        # Storing loaded conversion tables, this is for advanced users
        "store conversion tables": False,
        # Relative path to the data folder (used for storing)
        "conversion dump": "/home/unimelb.edu.au/smeighenberg/Projects/fledgeling/fledgeling/"
    },
}


class ConfigClass(dict):
    """ The configuration class. This is used
    by the package for all parameter settings. If something goes wrong
    its usually here.

    Parameters
    ----------
    config : dic
        The config dictionary

    Returns
    -------
    None
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # TODO: Update this
    def from_yaml(self, yaml_file: str) -> None:
        """ Update config with yaml file

        Parameters
        ----------
        yaml_file : str
            path to yaml file

        Returns
        -------
        None
        """
        yaml_config = yaml.load(open(yaml_file), Loader=yaml.SafeLoader)
        self.update(yaml_config)

    # TODO: Update this
    def from_dict(self, user_dict: Dict[Any, Any]) -> None:
        """ Creates a config from dictionary

        Parameters
        ----------
        user_dict : dic
            The user dictionary

        Returns
        -------
        None
        """
        self.update(user_dict)


config = ConfigClass(_baseconfig)
