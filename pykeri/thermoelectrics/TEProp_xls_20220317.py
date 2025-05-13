# -*- coding: utf-8 -*-
"""
Created on Tue Mar 06 2018

@author: Jaywan Chung

updated on Tue Aug 22 2018: add "max_raw_T" and "min_raw_T" properties
updated on Fri Mar 09 2018: added "color" option in "__init__": "color" is used for plot in Leg or Device.
updated on Thu Mar 08 2018: added "mat_name" option in "__init__".
"""

#from pykeri.scidata.matprop import MatProp
from pykeri.scidata.read import read_sheet_from_excel_scidata, sci_table
from pykeri.scidata.matprop import MatProp

class TEPropNotFoundError(Exception):
    pass

class TEProp:
    """
    Read the thermoelectric material properties from a formatted excel file.
    
    >>> mat = TEProp("TEProp_xls_input_ex.xlsx", "mat1")
    >>> mat.elec_resi.raw_data()
    ((200, 1e-05), (300, 1e-05), (400, 1e-05), (500, 1e-05), (600, 1e-05), (700, 1e-05), (800, 1e-05), (900, 1e-05), (1000, 1e-05))
    >>> mat.Seebeck.raw_data()
    ((200, 0.0002), (300, 0.0002), (400, 0.0002), (500, 0.0002), (600, 0.0002), (700, 0.0002), (800, 0.0002), (900, 0.0002), (1000, 0.0002))
    >>> mat.thrm_cond.raw_data()
    ((200, 1), (300, 1), (400, 1), (500, 1), (600, 1), (700, 1), (800, 1), (900, 1), (1000, 1))
    """
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
    
    def __init__(self,xls_filename,sheetname, mat_name=None, color=None):
        self._xls_filename = xls_filename
        self._sheetname = sheetname
        if color is not None:
            self.color = color
        self.load_from_xls_sheet(xls_filename,sheetname, mat_name=mat_name)
    
    def __repr__(self):
        return "TEProp('"+self._xls_filename+"',"+self._sheetname+")"

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
    
    def load_from_xls_sheet(self,xls_filename,sheetname, mat_name=None):
        tables = read_sheet_from_excel_scidata(xls_filename, sheetname, ignore_settings=True)
        
        df = tables[3]  # target table is the fourth table
        table = sci_table(df.iloc[:,range(0,6)], col_irow=0, unit_irow=1)
        # dataframes
        elec_cond_df = table.iloc[:,[0,1]].dropna()
        Seebeck_df   = table.iloc[:,[2,3]].dropna()
        thrm_cond_df = table.iloc[:,[4,5]].dropna()
        # check the integrity of the data
        if len(elec_cond_df)==0:
            raise TEPropNotFoundError("No electrical conductivity in the sheet.")
        if len(Seebeck_df)==0:
            raise TEPropNotFoundError("No Seebeck coefficient in the sheet.")
        if len(thrm_cond_df)==0:
            raise TEPropNotFoundError("No thermal conductivity in the excel file.")
        # convert from elec_cond to elec_resi
        elec_resi_df  = elec_cond_df.copy()
        elec_resi_df.columns = ('T [K]','resi [Ohm m]')
        elec_resi_df.iloc[:,1] = 1/elec_resi_df.iloc[:,1]
        # raw_data ready
        elec_resi_raw = elec_resi_df.values
        Seebeck_raw   = Seebeck_df.values
        thrm_cond_raw = thrm_cond_df.values
        # convert to MatProp
        self.elec_resi = TEProp.def_elec_resi(elec_resi_raw)
        self.Seebeck   = TEProp.def_Seebeck(Seebeck_raw)
        self.thrm_cond = TEProp.def_thrm_cond(thrm_cond_raw)      
        # remember name
        self.name = mat_name
        
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
    def from_dict(a_dict):
        """
        'a_dict' is a dictionary containing 'xls_filename' and 'sheetname'.
        Returns a TEProp object.
        """
        xls_filename = a_dict.get('xls_filename')
        sheetname = a_dict.get('sheetname')
        mat_name = a_dict.get('mat_name', sheetname)  # if no name for material, use the sheetname
        color = a_dict.get('color')
        return TEProp(xls_filename, sheetname, mat_name, color)

    def plot(self, T, **kwargs):
        """
        Plot thermoelectric properties on 'T' variable and returns a Figure handle.
        """
        show_grid = kwargs.get('show_grid', True)
        show_each_title = kwargs.get('show_each_title', False)
        show_title = kwargs.get('show_title', True)
        
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
    
if __name__ == "__main__":
    import doctest
    doctest.testmod()