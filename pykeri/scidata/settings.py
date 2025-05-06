# -*- coding: utf-8 -*-
"""
Created on Fri Mar 24 13:28:35 2017

    The class "Settings" handles a list of tuples with exactly two elements.
    The two elements are a key and its setting value for scientific settings.

@author: Jaywan Chung

Last updated on Tue Mar 28 2017
"""

class Settings:
    """
    Settings is a list of tuples having exactly two elements.
    """
    _list_of_tuples = []
    
    def __init__(self, list_of_tuples):
        list_of_tuples = list(list_of_tuples)
        assert(Settings._is_list_of_tuples(list_of_tuples))
        self._list_of_tuples = list_of_tuples
        
    def __iter__(self):   # iteratable as a list
        self.iterator = self._list_of_tuples.__iter__()
        return self
    
    def __next__(self):
        return self.iterator.__next__()
    
    def __getitem__(self, key):
        return self._list_of_tuples.__getitem__(key)

    def __setitem__(self, key, item):
        if isinstance(item,tuple) and (len(item) == 2):
            self._list_of_tuples[key] = item
        else:
            raise TypeError('Settings should have a tuple of exactly two elements: key and value.')

    def __repr__(self):
        return 'Settings: ' + self._list_of_tuples.__str__()
        
    def __str__(self):
        return self._list_of_tuples.__str__()

    def __list__(self):
        return self.list()
    
    def list(self):
        return self._list_of_tuples.copy()
    
    def values_of(self, setting_name):
        """
        Find all the second elements matching the first element name with the setting_name.
        Returns a list of such second elements.
        """
        result = []
        for first_elem, second_elem in self._list_of_tuples:
            if str(first_elem) == str(setting_name):
                result.append(second_elem)
        return result
    
    def value_of(self, setting_name):
        """
        Find the second elements matching the first element name with the setting_name.
        Returns only the last element of them.
        """
        values = self.values_of(setting_name)
        if len(values) > 0:
            return values[-1]
        else:
            return None
        
    def keys(self):
        """
        Return a list of all keys (first elements) in the Settings.
        """
        result = []
        for key,value in self._list_of_tuples:
            result.append(key)
        return result
        
    def describe(self):
        """
        Print all the setting infos.
        """
        for key, value in self._list_of_tuples:
            print(str(key) + ' is ' + str(value))
            
    def _is_list_of_tuples(list_of_tuples, show_msg=False):
        """
        Check the given list is a setting list; i.e., check if the list is
        a list of tuples having exactly two elements.
        """
        if not isinstance(list_of_tuples,list):
            if show_msg: print('not a list')
            return False
        for items in list_of_tuples:
            if not isinstance(items,tuple):
                if show_msg: print('element of the list should be tuples')
                return False
            if not(len(items) == 2):
                if show_msg: print('tuples should have exactly two elements')
                return False
        return True
