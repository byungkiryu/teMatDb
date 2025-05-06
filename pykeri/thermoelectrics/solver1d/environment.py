# -*- coding: utf-8 -*-
"""
Created on Mon Jun  5 08:09:25 2017

@author: Jaywan Chung

updated on Wed Mar 07 2018: added "deltaT" property.
updated on Tue Mar 06 2018: added "from_dict" method.
"""

from pykeri.scidata.metricunit import MetricUnit

class Environment:
    """
    Define the environment where a thermoelectric leg or device is working.
    """
    def __init__(self, Th, Tc):
        self.Th = Th
        self.Tc = Tc
        self.Th_unit = MetricUnit('K')
        self.Tc_unit = MetricUnit('K')
        
    @property
    def deltaT(self):
        return self.Th - self.Tc
        
    def from_dict(a_dict):
        """
        'a_dict' is a dictionary containing the following information on thermoelectric environment:
            'Th': hot side temperature,
            'Tc': cold side temperature
        
        Create and return a Environment object.
        """
        Th = a_dict['Th']
        Tc = a_dict['Tc']
        return Environment(Th, Tc)