# -*- coding: utf-8 -*-
# Name: atmospherics.py
# Authors: Stephan Meighen-Berger
# Builds the high-energy atmospheric flux tables

import logging
from MCEq.core import MCEqRun
import crflux.models as pm
import pkgutil
import pickle as pkl
from .config import config


_log = logging.getLogger(__name__)


class Atmos(object):
    """Deals with the atmospheric particle fluxes produced in the
    atmosphere

    Parameters
    ----------
    None

    Raises
    ------
    Unknown atmospheric model
    """
    def __init__(self):
        if not config["general"]["enable logging"]:
            _log.disabled = True
        if config["atmospherics"]["name"] == "mceq":
            self._mceq_setup = config["atmospherics"]["mceq model"]
            try:
                self._load_str = (
                        self._mceq_setup["atmospheric storage"]
                    )
                _log.info("Trying to load pre-calculated tables")
                _log.debug("Searching for " + self._load_str)
                _log.info("Loading pre-computed data")
                param_file = pkgutil.get_data(
                        __name__,
                        self._load_str
                )
                self._cascade = pkl.loads(param_file)
            except FileNotFoundError:
                _log.warning('Shower file not found')
                _log.info("Generating new atmospherics tables")
                # MCEq setup
                _log.info("Setting up MCEq")
                # Setting up MCEq
                self._int_model = self._mceq_setup["interaction model"]
                _log.debug("Using the " + self._int_model + " model.")
                self._primary_model = self._mceq_setup["primary model"]
                _log.debug(
                    "Using the " + self._primary_model[0] +
                    "model with subset " + self._primary_model[1])
                self._atmosphere = self._mceq_setup["atmosphere"]
                _log.debug(
                    "Using the " + self._atmosphere[0] +
                    "model at " + self._atmosphere[1][0] +
                    "and month" + self._atmosphere[1][1]
                )
                if self._primary_model[0] == "HillasGaisser2012":
                    _log.debug("Setting the primary model")
                    self.__pm = pm.HillasGaisser2012
                else:
                    raise ValueError("Unknown primary model!")
                self._zeniths = self._mceq_setup["zeniths"]
                _log.info("Starting zenith loop")
                self._cascade = {}
                for zen in self._zeniths:
                    _log.debug("Using zenith set to %.f" % zen)
                    self._mceq_run = MCEqRun(
                        interaction_model=self._int_model,
                        primary_model=(self.__pm, self._primary_model[1]),
                        theta_deg=zen
                    )
                    # Setting the atmosphere
                    self._mceq_run.set_density_model(self._atmosphere)
                    # Running the simulation
                    _log.info("Running the simulation")
                    self._cascade[zen] = self._run()
                _log.debug("Dumping results for later use")
                pkl.dump(
                    self._cascade,
                    open("%s" % self._load_str, "wb")
                )
        else:
            raise ValueError("Unknown atmospherics simulation approach! Please check the config file")

    @property
    def cascade(self):
        """ Load the modelled atmospheric fluxes and grids
        """
        return self._cascade

    def _run(self):
        """ Runs the atmospheric shower simulation

        Parameters
        ----------
        None

        Returns
        -------
        dict:
            Dictionary containing the energy grid(s)
            and the nue and numu fluxes.
        """
        self._mceq_run.solve()
        # Fetching nu_mu
        mceq_numu_flux = (
            self._mceq_run.get_solution('total_numu', 0) +
            self._mceq_run.get_solution('total_antinumu', 0)
        )
        # Fetching nu_e
        mceq_nue_flux = (
            self._mceq_run.get_solution('total_nue', 0) +
            self._mceq_run.get_solution('total_antinue', 0)
        )

        return {
            "e grid": self._mceq_run.e_grid,
            "e width": self._mceq_run.e_widths,
            "e bin": self._mceq_run.e_bins,
            "numu": mceq_numu_flux,
            "nue": mceq_nue_flux,
        }
