# -*- coding: utf-8 -*-
"""
Created on Mon Jun  5 08:09:25 2017

@author: Jaywan Chung
"""

from pykeri.scidata.metricunit import MetricUnit

class Environment:
    """
    Define the environment where a thermoelectric device is working.
    """
    def __init__(self, Th, Tc):
        self.Th = Th
        self.Tc = Tc
        self.Th_unit = MetricUnit('K')
        self.Tc_unit = MetricUnit('K')