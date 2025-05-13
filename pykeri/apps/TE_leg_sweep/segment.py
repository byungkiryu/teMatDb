# -*- coding: utf-8 -*-
"""
Created on Mon Jun  5 09:22:39 2017

@author: Jaywan Chung

Last modified on Oct 10 2017: compatible with TEProp.
"""

import numpy as np

class Segment:
    """
    Construct a thermoelectric segment from the given lengths and materials.
    This class contains x-grid points and the corresponding functions.
    """
    def __init__(self, lengths, materials, min_length_per_grid, max_num_of_grid_per_interval=50):
        (self._xs, self._interval_indices) = lengths_to_xs( lengths, min_length_per_grid, max_num_of_grid_per_interval )
        self._mats = tuple( materials )
        
    def composition(self, func_name, Ts):
        """
        Return the vector of values evaluated by func(Ts)(xs)
        """
        result = np.array([])
        for idx, interval_index in enumerate(self._interval_indices):
            (start, end) = interval_index
            # modified on Oct 10 2017
            func = getattr(self._mats[idx], func_name)
            result = np.append( result, func(Ts[start:end+1]) )
        return result
    
    def gradient(self, Ts):
        """
        Return the gradient dT/dx.
        """
        result = np.array([])
        for interval_index in self._interval_indices:
            (start, end) = interval_index
            dx = self._xs[start+1] - self._xs[start]
            result = np.append( result, np.gradient(Ts[start:end+1],dx,edge_order=2) )
        return result

    
    def grid(self):
        return self._xs
    
    def composition_with_given_function(self, Ts):
        """
        Return the vector of values evaluated by func(Ts)(xs)
        """
        result = np.array([])
        for idx, interval_index in enumerate(self._interval_indices):
            (start, end) = interval_index
            result = np.append( result, self._mats[idx](Ts[start:end+1]) )  # here "_mats" means a function, instead of a material
        return result
    



def lengths_to_xs( lengths, min_length_per_grid, max_num_of_grid_per_interval, start=0 ):
    accum = start
    grid_start = 0
    interval_indices = []
    xs = np.array([])
    for idx, length in enumerate(lengths):
        num_grid = max_num_of_grid_per_interval
        length_per_grid = length / (num_grid-1)
        if length_per_grid < min_length_per_grid:
            num_grid = int( (length / min_length_per_grid)+1 )
        grid = np.linspace( accum, accum+length, num_grid )
        interval_indices.append( tuple( (grid_start, grid_start + num_grid-1) ) )
        xs = np.append( xs, grid )
        accum += length
        grid_start += num_grid
    return (xs, tuple(interval_indices))


if __name__ == '__main__':
    seg = Segment([1,2,3], ['a','b','c'], 1)
    print( seg._xs, seg._interval_indices, seg._mats )