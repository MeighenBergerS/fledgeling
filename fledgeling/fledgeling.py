# -*- coding: utf-8 -*-
# Name: fledgeling.py
# Authors: Stephan Meighen-Berger
# Main interface to the fledgeling module. This is a very basic package to analyze and work
# with IceCube data

# Imports
# Native modules
import logging
import sys
import numpy as np
import yaml
# -----------------------------------------
# Package modules
from .config import config
from .data_reader import DR
from .atmospherics import Atmos

# unless we put this class in __init__, __name__ will be contagion.contagion
_log = logging.getLogger("fledgeling")


class Fledgeling(object):
    """
    class: Fledgeling
    Interface to the fledgeling package. This class
    stores all methods required to run the simulation
    and analysis of IceCube data
    ----------
    config : dic
        Configuration dictionary for the simulation

    Returns
    -------
    None
    """
    def __init__(self, userconfig=None):
        """
        function: __init__
        Initializes the class fledgeling.
        Here all run parameters are set.
        Parameters
        ----------
        config : dic
            Configuration dictionary for the simulation

        Returns
        -------
        None
        """
        # Inputs
        if userconfig is not None:
            if isinstance(userconfig, dict):
                config.from_dict(userconfig)
            else:
                config.from_yaml(userconfig)

        # Create RandomState
        if config["general"]["random state seed"] is None:
            _log.warning("No random state seed given, constructing new state")
            rstate = np.random.RandomState()
        else:
            rstate = np.random.RandomState(
                config["general"]["random state seed"]
            )
        config["runtime"] = {"random state": rstate}

        # Logger
        # Logging formatter
        fmt = "%(levelname)s: %(message)s"
        fmt_with_name = "[%(name)s] " + fmt
        formatter_with_name = logging.Formatter(fmt=fmt_with_name)
        # creating file handler with debug messages
        if config["general"]["enable logging"]:
            fh = logging.FileHandler(
                config["general"]["log file handler"], mode="w"
            )
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(formatter_with_name)
            _log.addHandler(fh)
        else:
            _log.disabled = True
        # console logger with a higher log level
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(config["general"]["debug level"])
        # add class name to ch only when debugging
        if config["general"]["debug level"] == logging.DEBUG:
            ch.setFormatter(formatter_with_name)
        else:
            formatter = logging.Formatter(fmt=fmt)
            ch.setFormatter(formatter)
        _log.addHandler(ch)
        _log.setLevel(logging.DEBUG)
        _log.info('---------------------------------------------------')
        _log.info('---------------------------------------------------')
        _log.info('Welcome to Fledgeling!')
        _log.info(
            'This package will help you model atmospheric fluxes for IceCube'
        )
        _log.info('---------------------------------------------------')
        _log.info('---------------------------------------------------')
        _log.info('Doing some prelim setup')
        self._ebins = np.logspace(
            config["advanced"]["ebins"][0],
            config["advanced"]["ebins"][1],
            config["advanced"]["ebins"][2]
        )
        self._ewidths = self._ebins[1:] - self._ebins[:-1]
        self._egrid = np.sqrt(self._ebins[1:] * self._ebins[:-1])
        self._thetas = np.arange(
            config["advanced"]["thetas"][0],
            config["advanced"]["thetas"][1],
            config["advanced"]["thetas"][2]
        )
        self._years = range(0, config["advanced"]["years"])
        _log.info('---------------------------------------------------')
        _log.info('---------------------------------------------------')
        _log.info('Loading the flux to event conversion function')
        self._dr = DR(self._egrid, self._thetas, self._years)
        _log.info('---------------------------------------------------')
        _log.info('---------------------------------------------------')
        _log.info('Launching or loading the atmospheric shower simulation')
        self._atmos = Atmos()
        _log.info('---------------------------------------------------')
        _log.info('---------------------------------------------------')


    def close(self):
        """ Wraps up the program

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        _log.info('---------------------------------------------------')
        _log.info('---------------------------------------------------')
        # A new simulation
        if config["general"]["enable logging"]:
            _log.debug(
                "Dumping run settings into %s",
                config["general"]["config location"],
            )
            with open(config["general"]["config location"], "w") as f:
                yaml.dump(config, f)
        # Closing log
        logging.shutdown()
