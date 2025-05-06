# -*- coding: utf-8 -*-
"""
Created on Mon Sep 18 14:17:02 2017 testtest

@author: Jaywan Chung

updated on Tue Aug 22 2018: add "max_raw_T" and "min_raw_T" properties
updated on Wed Apr 11 2018: add "from_raw_data()" function.
updated on Thu Mar 08 2018: add 'mat_name' option but the string of 'id_num' will be used as a 'name'.
updated on Tue Mar 06 2018: add the function "set_interp_opt".
updated on ??? Oct 10 2017: use the option "overwrite" instead of "override".
"""

from pykeri.scidata.matprop import MatProp
from pykeri.scidata.matdb import MatDB

class TEProp:
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

    def __init__(self,db_filename=None,id_num=None, mat_name=None, color=None):
        # "name" option is not allowed for now.
        if mat_name is not None:
            raise ValueError("Cannot specify 'mat_name': the string 'id_num' will be used as a name.")
        self._db_filename = db_filename
        self._id_num = id_num
        if db_filename is None:  # allow empty TEProp class
            self._db_filename = "no_db"
        else:
            self.load_from_DB(db_filename,id_num)
        if id_num is None:
            self._id_num = 0
            self.name = "no_id"
        else:
            self.name = str(id_num)
        if color is not None:
            self.color = color
    
    def __repr__(self):
        return "TEProp('"+self._db_filename+"',"+str(self._id_num)+")"

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
    
    def load_from_DB(self,db_filename,id_num):
        db = MatDB(db_filename)
        self.elec_resi = db.load(self.TEP_ELEC_RESI,id_num)
        self.Seebeck   = db.load(self.TEP_SEEBECK,  id_num)
        self.thrm_cond = db.load(self.TEP_THRM_COND,id_num)
        self.name = str(id_num)   # the string of 'id_num' will be used as a 'name'.
    
    def save_to_DB(db_filename,id_num,matprop_elec_resi,matprop_Seebeck,matprop_thrm_cond,overwrite=False):
        db = MatDB(db_filename)  # open the material db
        # match the units
        elec_resi = matprop_elec_resi.to_units(TEProp.DB_ELEC_RESI_UNITS)
        Seebeck   = matprop_Seebeck.to_units(TEProp.DB_SEEBECK_UNITS)
        thrm_cond = matprop_thrm_cond.to_units(TEProp.DB_THRM_COND_UNITS)
        # check the structure
        assert(elec_resi.has_structure(TEProp.DB_ELEC_RESI_NAMES,TEProp.DB_ELEC_RESI_UNITS))
        assert(Seebeck.has_structure(TEProp.DB_SEEBECK_NAMES,TEProp.DB_SEEBECK_UNITS))
        assert(thrm_cond.has_structure(TEProp.DB_THRM_COND_NAMES,TEProp.DB_THRM_COND_UNITS))
        # save the material properties
        written1 = db.save(elec_resi,id_num,overwrite=overwrite)
        written2 = db.save(Seebeck,  id_num,overwrite=overwrite)
        written3 = db.save(thrm_cond,id_num,overwrite=overwrite)
        return written1 and written2 and written3
        
    @staticmethod
    def def_elec_resi(raw_data,units=DB_ELEC_RESI_UNITS):
        names = TEProp.DB_ELEC_RESI_NAMES
        return MatProp(names,units,raw_data) 
    
    @staticmethod
    def def_Seebeck(raw_data,units=DB_SEEBECK_UNITS):
        names = TEProp.DB_SEEBECK_NAMES
        return MatProp(names,units,raw_data)
    
    @staticmethod
    def def_thrm_cond(raw_data,units=DB_THRM_COND_UNITS):
        names = TEProp.DB_THRM_COND_NAMES
        return MatProp(names,units,raw_data)
    
    @staticmethod
    def from_raw_data(elec_resi_raw_data, Seebeck_raw_data, thrm_cond_raw_data, name=None, color=None):
        """
        Define TEProp manually from three raw_data. Units are default SI units.
        """
        tep = TEProp()
        tep.elec_resi = TEProp.def_elec_resi(elec_resi_raw_data)
        tep.Seebeck   = TEProp.def_Seebeck(Seebeck_raw_data)
        tep.thrm_cond = TEProp.def_thrm_cond(thrm_cond_raw_data)
        if name is None:
            tep.name = "No_name"
        else:
            tep.name = name
        
        if color is None:
            tep.color = (100/255, 100/255, 255/255)
        else:
            tep.color = color
        return tep
    
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