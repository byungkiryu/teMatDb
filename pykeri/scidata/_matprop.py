# -*- coding: utf-8 -*-
"""
Created on Mon Sep 18 08:27:22 2017

@author: Jaywan Chung
"""

from scipy.interpolate import interp1d
from pykeri.scidata.measured import Measured


class MatProp:
    INTERP_LINEAR = 'linear_wo_extrap'
    
    def __init__(self,names,units,raw_data,interp=INTERP_LINEAR):
        if len(names) != len(units):
            raise ValueError("'names' and 'units' arguments must have the same lengths.")
            
        self.__names = tuple(names)
        self.__units = tuple(units)
        self.__raw_data = tuple( [tuple(item) for item in raw_data] )
        self.set_interp_func(interp)
        self.__interp_str = interp

        pass
    
    def __call__(self,xs):
        xs = to_real_values(xs,self.__units[:-1])
        return self.__interp_func(xs)
        pass
    
    def __repr__(self):
        repr_str  = 'MatProp(names=' + str(self.__names) + ', '
        repr_str += 'units=' + str(self.__units) + ', '
        repr_str += 'raw_data=' + str(self.__raw_data) + ', '
        repr_str += "interp='" + self.__interp_str +"')"
        return repr_str
    
    def set_interp_func(self,interp):
        if len(self.__names) == 2:
            if interp == MatProp.INTERP_LINEAR:
                x = tuple( [item[0] for item in self.__raw_data] )
                y = tuple( [item[1] for item in self.__raw_data] )
                #self.__interp_func = interp1d(x,y,kind='linear')
                self.__interp_func = interp1d(x,y,kind='linear')
            else:
                raise ValueError("Invalid interpolation method.")
        else:
            raise ValueError("Sorry we do not support 2D or more dimensions for now.")
            
    
    def unit(self):
        return self.__units[-1]
    
    def input_units(self):
        return self.__units[:-1]
    
    def raw_data(self):
        return self.__raw_data
    
    def raw_input(self,col=0):
        result = []
        for row in self.__raw_data:
            result.append(row[col])
        return tuple(result)
    
    def raw_output(self):
        return self.raw_input(col=-1)
    
    def raw_interval(self,col=0):
        raw = self.raw_input(col)
        return (min(raw), max(raw))
        
    
def to_real_values(xs,units):
    is_not_iterable = False
    try:
        _ = iter(xs)
    except TypeError:
        # not a iterable
        xs = (xs,)
        is_not_iterable = True
    try:
        _ = iter(units)
    except TypeError:
        units = (units,)
    result = []
    for row in xs:
        row_item = []
        is_a_single_xp = False
        try:
            _ = iter(row)
        except TypeError:
            row = (row,)
            is_a_single_xp = True
        for idx,col in enumerate(row):
            default_unit = units[idx]
            if isinstance(col,Measured):
                col = col.to(default_unit).drop_zero_exponent().value  # unit conversion
            row_item.append(float(col))
        if is_a_single_xp:
            result.append(row_item[0])
        else:
            result.append(tuple(row_item))
    if is_not_iterable:
        result = result[0]
    else:
        result = tuple(result)
    return result