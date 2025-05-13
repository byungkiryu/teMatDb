# -*- coding: utf-8 -*-
"""
Created on Fri Mar 24 08:36:31 2017

    The class "IndexRect" is used for parsing tables in a DataFrame.
    It represents a coordinate rectangle in a DataFrame and
    can be expanded to four directions (upward,downward,left,right).
    Also it checks bounding edges; a edge consists of NaN's.

@author: Jaywan Chung

Last updated on Fri Mar 24 2017
"""

import pandas as pd
import numpy as np

class IndexRect:
    ulrow = ulcol = lrrow = lrcol = 0
    border_ulrow = border_ulcol = border_lrrow = border_lrcol = 0
    expand_directions = ['upward', 'downward', 'left', 'right']
    def __init__(self, ulrow, ulcol, lrrow, lrcol):
        assert( (ulrow>=0) and (ulcol>=0) and (lrrow>=0) and (lrcol>=0) )
        assert( (ulrow <= lrrow) and (ulcol <= lrcol) )
        self.ulrow, self.ulcol, self.lrrow, self.lrcol \
            = ulrow, ulcol, lrrow, lrcol
        self.border_ulrow, self.border_ulcol, self.border_lrrow, self.border_lrcol \
            = ulrow, ulcol, lrrow, lrcol
    def set_border(self, ulrow, ulcol, lrrow, lrcol):
        assert( (ulrow>=0) and (ulcol>=0) and (lrrow>=0) and (lrcol>=0) )
        assert( (ulrow <= lrrow) and (ulcol <= lrcol) )
        self.border_ulrow, self.border_ulcol, self.border_lrrow, self.border_lrcol \
            = ulrow, ulcol, lrrow, lrcol
    def __str__(self):
        return 'IndexRect: upper left corner (%d,%d) and lower right corner (%d %d)' \
            % (self.ulrow,self.ulcol, self.lrrow,self.lrcol)
    def expand(self, direction):
        """
        The IndexBox is expanded to the given direction.
        Four directions are possible: 'upward', 'downward', 'left' and 'right'.
        """
        assert(direction in IndexRect.expand_directions)
        dir_id = IndexRect.expand_directions.index(direction)
        if (dir_id == 0) and (self.ulrow > self.border_ulrow): # upward
           self.ulrow -= 1
        if (dir_id == 1) and (self.lrrow < self.border_lrrow): # downward
           self.lrrow += 1
        if (dir_id == 2) and (self.ulcol > self.border_ulcol): # left
           self.ulcol -= 1
        if (dir_id == 3) and (self.lrcol < self.border_lrcol): # right
           self.lrcol += 1
    def mask(self, dataframe):
        """
        Return the elements of DataFrame only in the IndexRect
        """
        return dataframe.iloc[self.ulrow:self.lrrow+1,self.ulcol:self.lrcol+1]
    def fillna(self, dataframe):
        """
        Fill a rectangle of NaN's(np.nan) on DataFrame
        """
        dataframe.iloc[self.ulrow:self.lrrow+1,self.ulcol:self.lrcol+1] = np.nan
    def has_bounding_edge(self, dataframe, direction):
        """
        Returns True if the edge on the given direction is a bounding edge of the dataframe.
        The bounding edge is filled by only NaN (np.nan)'s or touches the border.
        """
        assert(direction in IndexRect.expand_directions)
        dir_id = IndexRect.expand_directions.index(direction)
        df = dataframe; na = np.nan
        edge = pd.Series([na])
        if (dir_id == 0) and (self.ulrow > self.border_ulrow): # upward
            edge = df.iloc[self.ulrow, self.ulcol:self.lrcol+1]
        if (dir_id == 1) and (self.lrrow < self.border_lrrow): # downward
            edge = df.iloc[self.lrrow, self.ulcol:self.lrcol+1]
        if (dir_id == 2) and (self.ulcol > self.border_ulcol): # left
            edge = df.iloc[self.ulrow:self.lrrow+1, self.ulcol]
        if (dir_id == 3) and (self.lrcol < self.border_lrcol): # right
            edge = df.iloc[self.ulrow:self.lrrow+1, self.lrcol]        
        if edge.isnull().all():
            return True
        else:
            return False
    def is_bounding_box_of(self, dataframe):
        """
        Returns True if the IndexRect is a bounding box of the DataFrame.
        The bounding box is enclosed by a rectangle of NaN (np.nan)'s.
        """
        if all([self.has_bounding_edge(dataframe, direction) for direction in IndexRect.expand_directions]):
            return True
        else:
            return False
