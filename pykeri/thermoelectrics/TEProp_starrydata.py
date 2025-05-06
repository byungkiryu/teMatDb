# -*- coding: utf-8 -*-
"""
Created on Mon Sep 07 20:42:00 2020

@author: Jaywan Chung

"""

import json
import numpy as np
import pandas as pd

from pykeri.scidata.matprop import MatProp


def _get_starrydata_teprop_df(json_filename):
    print("Loading {} ...".format(json_filename))
    with open(json_filename, 'r') as file:
        dict_data = json.load(file)
    print("Loading complete.".format(json_filename))

    df_data = pd.DataFrame(dict_data['rawdata'])
    df_figures = pd.DataFrame(dict_data['figure'])
    df_merged = pd.merge(df_data,
                         df_figures[["figureid", "propertyname_x", "propertyname_y", "unitname_x", "unitname_y"]],
                         left_on="figureid", right_on="figureid")
    df_teprop = df_merged[df_merged["propertyname_x"] == "Temperature"].copy()
    print("Dataframe initialized.")

    return df_teprop


def _convert_starrydata_data_to_numpy(starrydata_data):
    if isinstance(starrydata_data, str):
        starrydata_data = eval(starrydata_data)
    size_data = len(starrydata_data)
    np_array = np.empty((size_data, 2), dtype=float)
    for idx, elem in enumerate(starrydata_data):
        elem = starrydata_data[idx]
        np_array[idx, 0] = float(elem['x'])
        np_array[idx, 1] = float(elem['y'])
    np_array = np.sort(np_array, axis=0)

    return np_array


class TEProp:
    _dict_filename_to_teprop_df = {}

    def __new__(self, json_filename, sampleid=None):
        if json_filename not in self._dict_filename_to_teprop_df:
            df_teprop = _get_starrydata_teprop_df(json_filename)
            self._dict_filename_to_teprop_df[json_filename] = df_teprop

        if sampleid is None:
            return np.sort(df_teprop.sampleid.unique())

        return TEProp_starrydata(self._dict_filename_to_teprop_df[json_filename], sampleid,
                                 first_argument_name=json_filename)


class TEProp_starrydata:
    TEP_TEMP = 'Temperature'
    TEP_TEMP_UNIT = 'K'
    TEP_ELEC_RESI = 'Electrical_Resistivity'
    TEP_ELEC_RESI_UNIT = 'Ohm m'    
    TEP_SEEBECK = 'Seebeck_Coefficient'
    TEP_SEEBECK_UNIT = 'V/K'
    TEP_THRM_COND = 'Thermal_Conductivity'
    TEP_THRM_COND_UNIT = 'W/m/K'
    
    # DB structure
    DB_ELEC_RESI_NAMES = [TEP_TEMP,TEP_ELEC_RESI]
    DB_ELEC_RESI_UNITS = [TEP_TEMP_UNIT,TEP_ELEC_RESI_UNIT]
    DB_SEEBECK_NAMES = [TEP_TEMP,TEP_SEEBECK]
    DB_SEEBECK_UNITS   = [TEP_TEMP_UNIT,TEP_SEEBECK_UNIT]
    DB_THRM_COND_NAMES = [TEP_TEMP,TEP_THRM_COND]
    DB_THRM_COND_UNITS = [TEP_TEMP_UNIT,TEP_THRM_COND_UNIT]

    # complementary property; implicitly driven from ELEC_RESI
    TEP_ELEC_COND = 'Electrical_Conductivity'
    TEP_ELEC_COND_UNIT = 'S/m'
    
    elec_resi = None
    Seebeck = None
    thrm_cond = None
    name = None

    def __init__(self, df_teprop, sampleid, first_argument_name):
        self._first_argument_name = first_argument_name
        self._sampleid = sampleid
        self.load_from_dataframe(df_teprop, sampleid)

    def __repr__(self):
        return "TEProp('"+self._first_argument_name+"', "+str(self._sampleid)+")"

    def elec_cond(self,xs):
        return 1/self.elec_resi(xs)
    
    def thrm_resi(self,xs):
        return 1/self.thrm_cond(xs)
    
    @property
    def max_raw_T(self):
        """
        Returns the maximum possible temperature in raw data;
        the raw data is possible for all temperatures less than this value.
        """
        result = self.elec_resi.raw_interval()[1]
        result = min(self.Seebeck.raw_interval()[1], result)
        result = min(self.thrm_cond.raw_interval()[1], result)
        return result
    
    @property
    def min_raw_T(self):
        """
        Returns the minimum possible temperature in raw data;
        the raw data is possible for all temperatures greater than this value.
        """
        result = self.elec_resi.raw_interval()[0]
        result = max(self.Seebeck.raw_interval()[0], result)
        result = max(self.thrm_cond.raw_interval()[0], result)
        return result

    def set_interp_opt(self,interp_opt):
        self.elec_resi.set_interp_opt(interp_opt)
        self.Seebeck.set_interp_opt(interp_opt)
        self.thrm_cond.set_interp_opt(interp_opt)
    
    def load_from_dataframe(self, df_teprop, sampleid):
        SEEBECK_PAIRS = {
            ('Seebeck coefficient', 'V/K'), ('TEP', 'V/K'), ('S', 'V/K'),
        }
        ELEC_RESI_PAIRS = {
            ('Electrical resistivity', 'ohm*m'), ('Resistivity', 'ohm*m^-1'),
        }
        ELEC_COND_PAIRS = {
            ('Electrical conductivity', 'S*m^(-1)'), ('Conductivity', 'S/m'),
        }
        THRM_COND_PAIRS = {
            ('Thermal conductivity', 'W*m^(-1)*K^(-1)'), ('total thermal conductivity', 'W*m^(-1)*K^(-1)'),
        }

        df_sample = df_teprop[df_teprop.sampleid == sampleid]

        Seebeck_raw = None
        elec_resi_raw = None
        elec_cond_raw = None
        thrm_cond_raw = None
        for idx, row in df_sample.iterrows():
            if (row.propertyname_y, row.unitname_y) in SEEBECK_PAIRS:
                Seebeck_raw = _convert_starrydata_data_to_numpy(row['data'])
            elif (row.propertyname_y, row.unitname_y) in ELEC_RESI_PAIRS:
                elec_resi_raw = _convert_starrydata_data_to_numpy(row['data'])
            elif (row.propertyname_y, row.unitname_y) in ELEC_COND_PAIRS:
                elec_cond_raw = _convert_starrydata_data_to_numpy(row['data'])
            elif (row.propertyname_y, row.unitname_y) in THRM_COND_PAIRS:
                thrm_cond_raw = _convert_starrydata_data_to_numpy(row['data'])

        if elec_resi_raw is None:
            if elec_cond_raw is None:
                raise ValueError("Electrical resistivity and electrical conductivity are not available!")
            elec_resi_raw = 1/elec_cond_raw
        if (Seebeck_raw is None) or (elec_resi_raw is None) or (thrm_cond_raw) is None:
            raise ValueError("TEP is not available!")

        # convert to MatProp
        self.Seebeck   = TEProp_starrydata.def_Seebeck(Seebeck_raw)
        self.elec_resi = TEProp_starrydata.def_elec_resi(elec_resi_raw)
        self.thrm_cond = TEProp_starrydata.def_thrm_cond(thrm_cond_raw)

    @staticmethod
    def def_elec_resi(raw_data,units=DB_ELEC_RESI_UNITS):
        names = TEProp_starrydata.DB_ELEC_RESI_NAMES
        return MatProp(names,units,raw_data) 
    
    @staticmethod
    def def_Seebeck(raw_data,units=DB_SEEBECK_UNITS):
        names = TEProp_starrydata.DB_SEEBECK_NAMES
        return MatProp(names,units,raw_data)
    
    @staticmethod
    def def_thrm_cond(raw_data,units=DB_THRM_COND_UNITS):
        names = TEProp_starrydata.DB_THRM_COND_NAMES
        return MatProp(names,units,raw_data)
    
    def plot(self, T, show_grid=True, show_each_title=False, show_title=True):
        """
        Plot thermoelectric properties on 'T' variable and returns a Figure handle.
        """
        
        import matplotlib.pyplot as plt
        elec_cond = self.elec_cond(T)
        elec_res = self.elec_resi(T)
        seebeck = self.Seebeck(T)
        thrm_cond = self.thrm_cond(T)
                
        fig = plt.figure(figsize=(8,10))
        
        x = T
        x_label = 'Temperature [K]'
        y_datas = [('Electrical Conductivity', '[S/cm]', elec_cond *1e-2),
                   ('Electrical Resistivity', '[$\mu\Omega$ m]', elec_res *1e6),
                   ('Seebeck Coefficient', '[$\mu$V/K]', seebeck *1e6),
                   ('Thermal Conductivity', '[W/m/K]', thrm_cond),
                   ('Power Factor', '[mW/m/K$^2$]', seebeck**2*elec_cond *1e3),
                   ('Figure of Merit (ZT)', '[1]', seebeck**2*elec_cond/thrm_cond*T)]
        
        for idx, data in enumerate(y_datas):
            plt.subplot(3,2,idx+1)
            title, unit, y = data
            if y is None:
                plt.text(0.5, 0.5, 'pykeri by JChung,BKRyu', horizontalalignment='center')
                plt.axis('off')
                continue
            plt.plot(x, y)
            plt.xlabel(x_label)
            if show_each_title:
                plt.ylabel(unit)
                plt.title(title)
            else:
                plt.ylabel(title+'\n'+unit)
            plt.grid(show_grid)
        
        fig.tight_layout(pad=2)

        if show_title:
            fig.suptitle('Thermoelectric Properties of '+self.name, size=16)
            if show_each_title:
                fig.subplots_adjust(top=0.9)
            else:
                fig.subplots_adjust(top=0.93)

        return fig