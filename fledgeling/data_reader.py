# -*- coding: utf-8 -*-
# Name: atmospherics.py
# Authors: Stephan Meighen-Berger
# Data reader for neutrino telescope data

import logging
import pkgutil
import numpy as np
import pickle as pkl
from tqdm import tqdm
from .utils import ice_parser, dataframe_from2d
from .config import config
from scipy.interpolate import UnivariateSpline


_log = logging.getLogger(__name__)

class DR(object):
    """ data reader class. This handles the loading parsing and setup of external or pre-calculated data

    Parameters
    ----------
    egrid: np.array
        The energy grid to evaluate on. Should have units GeV
    thetas: np.array
        The thetas to evaluate for
    """
    def __init__(self, egrid: np.array, thetas: np.array, years: list):
        if not config["general"]["enable logging"]:
            _log.disabled = True
        if config["general"]["detector"] == "icecube":
            _log.info("Running for icecube")
            self.sim_to_dec = self._sim_to_dec_icecube
            self._icecube_reader()
        else:
            _log.error("Unknown detector! Check the config file")
        if config["experimental data"]["pre-computed"]:
            _log.info("Loading pre-computed experimental data")
            param_file = pkgutil.get_data(
                    __name__,
                    config["experimental data"]["tables"]
            )
            self._conversion_tables = pkl.loads(param_file)
        else:
            _log.info("Loading experimental data")
            _log.info("Generating conversion tables")
            self._conversion_tables = {}
            for year in years:
                _log.info("Currently generating tables for year %d" % year)
                self._conversion_tables[year] = self.sim_to_dec(np.log10(egrid), egrid, thetas, year)
            if config["advanced"]["store conversion tables"]:
                _log.info("Dumping conversion tables")
                with open(config["advanced"]["conversion dump"] + config["experimental data"]["tables"], "wb") as f:
                    pkl.dump(self._conversion_tables, f)

    @property
    def conversion_tables(self):
        """ Conversion tables to go from injected neutrino (surface)
        to reconstructed
        """
        return self._conversion_tables

    def _icecube_reader(self):
        """ parses icecube data

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        seconds = 60.
        minutes = 60.
        days = seconds * minutes * 24.
        self._aeff_dic = {}
        self._smearing_dic = {}
        self._event_dic = {}
        uptime_dic = {}
        self._uptime_tot_dic = {}
        storage_location = config["experimental data"]["filepath"]
        _log.info("Loading effective area data")
        for i, datafile in enumerate(config["icecube data"]["effective areas"]):
            self._aeff_dic[i] = ice_parser(storage_location + datafile)
        # IceCube effective areas in the last few years is the same
        self._aeff_dic[5] = self._aeff_dic[4]
        self._aeff_dic[6] = self._aeff_dic[4]
        self._aeff_dic[7] = self._aeff_dic[4]
        self._aeff_dic[8] = self._aeff_dic[4]
        self._aeff_dic[9] = self._aeff_dic[4]
        _log.info("Loading event data")
        for i, datafile in enumerate(config["icecube data"]["event data"]):
            self._event_dic[i] = ice_parser(storage_location + datafile)
        _log.info("Loading the smearing matrix")
        for i, datafile in enumerate(config["icecube data"]["smearing matrix"]):
            self._smearing_dic[i] = ice_parser(storage_location + datafile)
        _log.info("Loading the uptimes")
        for i, datafile in enumerate(config["icecube data"]["uptime"]):
            uptime_dic[i] = ice_parser(storage_location + datafile)
        for year in range(10):
           self._uptime_tot_dic[year] = np.sum(np.diff(uptime_dic[year])) * days
        _log.info("Converting to pandas dataframe objects")
        
        self._aeff_dic = dataframe_from2d(
            self._aeff_dic,
            column_names=["E_min", "E_max", "dec_min", "dec_max", "aeff"],
            new_col_name="year"
        )
        self._event_dic = dataframe_from2d(
            self._event_dic,
            column_names=["MJD", "E", "angerr", "ra", "dec", "azimuth", "zenith"],
            new_col_name="year"
        )
        self._smearing_dic = dataframe_from2d(
            self._smearing_dic,
            column_names=[
                "E_min", "E_max", "dec_min", "dec_max", "E_rec_min", "E_rec_max", "PSF_min", "PSF_max",
                "angerr_min", "angerr_max", "fractional_counts"
            ],
            new_col_name="year"
        )

    def effective_area_func(
            self,
            e_grid: np.array,
            thetas: np.array,
            year: int) -> np.array:
        """ Creates a numpy array of effective areas for the energy grid, thetas, and years

        Parameters
        ----------
        e_grid: np.array
            The energies to evaluate for
        thetas: np.array
            The theta angles to evaluate for
        year: int
            The year of interest

        Returns
        -------
        aeff_val: np.array
            2d numpy array with all values of aeff for the e_grid and thetas.
            The shape will be (len(thetas), len(e_grid)), with the rows corresponding
            to the angles while the columns to the energies
        """
        # Filtering the year
        y_aeff = self._aeff_dic[self._aeff_dic["year"] == year]
        # Converting to declination
        tmp_thetas = np.array([
            -(90. - theta) if theta < 90
            else (theta - 90)
            for theta in thetas
        ])
        _log.debug("Creating mask arrays")
        # creating mask arrays
        # Energy
        emasks = np.array([
            (y_aeff['E_min'] <= elog) & (y_aeff['E_max'] > elog)
            for elog in np.log10(e_grid)
        ])
        # Angles
        amasks = np.array([
            (y_aeff['dec_min'] <= theta) & (y_aeff["dec_max"] > theta)
            for theta in tmp_thetas
        ])
        # All masks
        eamasks = np.array([[
            np.logical_and(emask, amask) for emask in emasks
        ] for amask in amasks])
        _log.debug("Finished masks")
        _log.debug("Fetching the values")
        # Fetching values
        aeff_val = np.array([[
            y_aeff[mask]["aeff"].values for mask in esub
        ] for esub in eamasks], dtype=object)
        _log.debug("Finished")
        return aeff_val

    def smearing_function(
            self,
            e_grid: np.array,
            thetas: np.array,
            year: int):
        """ Smearing function used to go from true energies to reconstructed ones.

        Parameters
        ----------
        e_grid: np.array
            The energies to evaluate for
        thetas: np.array
            The theta angles to evaluate for
        year: int
            The year of interest

        Returns
        -------
        smearing_val: np.array
            3d numpy array with all values of aeff for the e_grid and thetas.
            The shape will be (len(thetas), len(e_grid), len(reco_grid)), with the rows corresponding
            to the angles while the columns to the energies. Note the reco grid is defined by the next
            output
        smearing_egrid: np.array
            3d numpy array with all reco grids for the smearing_values.
            The shape will be (len(thetas), len(e_grid), len(reco_grid)), with the rows corresponding
            to the angles while the columns to the energies
        """
        # Filtering the year
        y_smear = self._smearing_dic[self._smearing_dic["year"] == year]
        # Converting to declination
        tmp_thetas = np.array([
            -(90. - theta) if theta < 90
            else (theta - 90)
            for theta in thetas
        ])
        _log.debug("Generating mask arrays for smearing")
        # creating mask arrays
        # Energy
        emasks = np.array([
            (y_smear['E_min'] <= elog) & (y_smear['E_max'] > elog)
            for elog in np.log10(e_grid)
        ])
        # Angles
        amasks = np.array([
            (y_smear['dec_min'] <= theta) & (y_smear["dec_max"] > theta)
            for theta in tmp_thetas
        ])
        _log.debug("Finished energy and angle masks")
        _log.debug("Combining masks...")
        # # All masks
        # TODO: make this memory efficient. Probably through pre-allocation
        # eamasks = np.array([[
        #     np.logical_and(emask, amask) for emask in emasks
        # ] for amask in amasks])
        # _log.debug("Finished mask arrays for smearing")
        # # Fetching values
        # smearing_val = np.array([[
        #     np.sum(y_smear[mask]["fractional_counts"].values.reshape((int(len(y_smear[mask]["fractional_counts"].values) / 440)), 440), axis=1) for mask in esub
        # ] for esub in eamasks], dtype=object)
        # smearing_egrid = np.array([[
        #     (y_smear[mask]["E_rec_min"].values + y_smear[mask]["E_rec_max"].values).reshape((int(len(y_smear[mask]["fractional_counts"].values) / 440)), 440)[:, 0] / 2 for mask in esub
        # ] for esub in eamasks], dtype=object)
        smearing_val = np.array([[
            np.sum(y_smear[np.logical_and(mask, esub)]["fractional_counts"].values.reshape((int(len(y_smear[np.logical_and(mask, esub)]["fractional_counts"].values) / 440)), 440), axis=1) for mask in emasks
        ] for esub in amasks], dtype=object)
        smearing_egrid = np.array([[
            (y_smear[np.logical_and(mask, esub)]["E_rec_min"].values + y_smear[np.logical_and(mask, esub)]["E_rec_max"].values).reshape((int(len(y_smear[np.logical_and(mask, esub)]["fractional_counts"].values) / 440)), 440)[:, 0] / 2 for mask in emasks
        ] for esub in amasks], dtype=object)
        return smearing_val, smearing_egrid

    def smearing_splines(
            self, 
            smearing_egrid: np.array,
            smearing_val: np.array):
        """ generates splines of the smearing functions. This can be used to unify
        the energy grids

        Parameters
        ----------
        smearing_egrid: np.array
            The energy grids
        smearing_val: np.array
            The smearing values

        Returns
        -------
        smearing_splines: np.array
            Array of the spline functions
        """
        def zero_func(x):
            return np.zeros(len(x))
        tmp = []
        for i in range(len(smearing_egrid)):
            tmp2 = []
            for j in range(len(smearing_egrid[i])):
                try:
                    tmp2.append(UnivariateSpline(np.sort(smearing_egrid[i][j]), smearing_val[i][j], k=1, ext=1, s=0))
                except:
                    tmp2.append(zero_func)
            tmp.append(tmp2)

        # tmp = np.array([[
        #     UnivariateSpline(smearing_egrid[i][j], smearing_val[i][j], k=1, ext=1, s=0) for j in range(len(smearing_egrid[i]))
        # ] for i in range(len(smearing_egrid))])
        return tmp

    def _sim_to_dec_icecube(
            self,
            unigrid: np.array,
            e_grid: np.array,
            thetas: np.array, year: int):
        """ generates the conversion tables to go from an injected energy and
        angle to realistic counts. Note this will need to be weighted by a flux after the fact

        Parameters
        ----------
        unigrid: np.array
            The energy grid to evaluate on as log10(E/GeV)
        e_grid: np.array
            The (injected) energies to evaluate for
        thetas: np.array
            The (injected) theta angles to evaluate for
        year: int
            The year of interest

        Returns
        -------
        smeared_counts: np.array
            3d numpy array with all values of aeff for the e_grid and thetas.
            The shape will be (len(thetas), len(e_grid), len(unigrid)), with the rows corresponding
            to the angles while the columns to the energies of injection. The final dimension is then
            the energy grid (unigrid)
        """
        _log.debug("Generating unnormalized counts")
        # Converts simulation data to detector data
        unnormalized_counts = self.effective_area_func(e_grid, thetas, year)
        _log.debug("Smearing the counts")
        y, x = self.smearing_function(
            e_grid,
            thetas, year
        )
        _log.debug("Finished smearing counts")
        spl = self.smearing_splines(x, y)
        smeared_counts = np.array([[
            unnormalized_counts[i][j] * spl[i][j](unigrid) / np.trapz(spl[i][j](unigrid), x=unigrid)
            if np.sum(spl[i][j](unigrid)) > 0. else np.zeros(len(unigrid))
            for j in range(len(unnormalized_counts[i]))
            ] for i in range(len(unnormalized_counts))], dtype=float)
        return smeared_counts
