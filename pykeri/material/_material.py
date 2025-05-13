# -*- coding: utf-8 -*-
"""
Created on Mon Jun  5 08:05:16 2017

@author: Jaywan Chung
"""

import numpy as np

# various constants for material properties
ELEC_COND = 'electric conductivity'
SEEBECK = 'Seebeck coefficient'
THRM_COND = 'thermal conductivity'

class Material:
    name = ''
    
    def __init__(self, name):
        self._property_dict = {}
        self._function_dict = {}
        self._unit_dict = {}
        self.name = name
        
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return 'Material: ' + self.name
    
    def get_property(self, property_name):
        return self._property_dict.get(property_name)
    
    def set_property(self, property_name, content):
        self._property_dict[property_name] = content
        
    def get_unit(self, property_name):
        return self._unit_dict.get(property_name)
    
    def set_unit(self, property_name, unit):
        self._unit_dict[property_name] = unit
        
    def set_interp(self, interp_name, xp_name, fp_name):
        self._function_dict[interp_name] = lambda x: np.interp(x, self.get_property(xp_name), self.get_property(fp_name))
        
    def get_func(self, func_name):
        return self._function_dict.get(func_name)