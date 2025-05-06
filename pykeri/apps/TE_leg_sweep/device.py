# -*- coding: utf-8 -*-
"""
Created on Mon Jun  5 08:07:20 2017

@author: Jaywan Chung
"""

class Device:
    """
    Define a thermoelectric device.
    """
    def __init__( self, segment, A ):
        self.seg = segment
        self.A = A
        self.xs = segment.grid()
        self.L = self.xs[-1]
        self.mesh_size = len(self.xs)