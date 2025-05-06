# -*- coding: utf-8 -*-
"""
Created on Mon May 29 09:33:06 2017

@author: 정재환

updated on Mon May 2017
"""

import unittest
from functools import lru_cache
import copy

class HashDict:
    """
    Creates an immutable dict.
    Arithmetic operations (+,-,*,/) are allowed if the items in HashDict allows those operations.
    """
    _dict = {}
    
    def __hash__(self):
        return hash( frozenset(self._dict.items()) )

    def __eq__(self, other):
        """ self == other """
        if isinstance(other, HashDict):
            return self._dict == other._dict
        elif isinstance(other, dict):
            return self._dict == other
        else:
            return False
    
    def to_dict(self):
        """ return a dictionary """
        return self._dict.copy()
    
    def to_string(self):
        return str( self.to_dict() )

    def __repr__(self):
        return 'HashDict: ' + self.to_string()
    
    def __str__(self):
        return self.to_string()
    
    def __init__(self, a_dict):
        if isinstance(a_dict, dict):
            self._dict = a_dict.copy()
        elif isinstance(a_dict, HashDict):
            self._dict = a_dict.to_dict()
        else:
            raise TypeError('Cannot create a HashDict.')

    @lru_cache()
    def _add_hashdicts( hashdict1, hashdict2 ):
        """ Add two HashDicts and return a HashDict. """
        dict1 = hashdict1._dict
        dict2 = hashdict2._dict
        all_keys = list(dict1.keys())
        for key in dict2.keys():
            if not(key in all_keys):
                all_keys.append(key)
        added_dict = {}
        for key in all_keys:
            added_dict[key] = (dict1.get(key) or 0) + (dict2.get(key) or 0)
        return HashDict( added_dict )
    
    def __add__(self, other):
        """ self + other """
        try:
            other = HashDict(other)
            return HashDict._add_hashdicts( self, other )            
        except TypeError: # treat as an element
            self_dict = self.to_dict()
            for key in self_dict.keys():
                try:
                    self_dict[key] += other
                except:
                    raise TypeError("Cannot be added to a HashDict.")
            return HashDict( self_dict )
        
    def __radd__(self, other):
        """ other + self = self + other """
        return self + other   # additive operation is commutative

    @lru_cache()
    def _mul_hashdicts( hashdict1, hashdict2 ):
        """ Multiply two dicts and return a HashDict. """
        dict1 = hashdict1._dict
        dict2 = hashdict2._dict        
        mul_dict = {}
        for key in dict1.keys():
            val = dict2.get(key)
            if not(val == None):
                mul_dict[key] = dict1[key] * val
        return HashDict( mul_dict )
    
    def __mul__(self, other):
        """
        self * other
        if a key is contained only in one HashDict (self or other), treat its value as 0 so omit the key.
        """
        try:
            other = HashDict(other)
            return HashDict._mul_hashdicts( self, other )            
        except TypeError:  # treat as an element
            self_dict = self.to_dict()
            for key in self_dict.keys():
                try:
                    self_dict[key] *= other
                except:
                    raise TypeError("Cannot be multiplied to a HashDict.")
            return HashDict( self_dict )

    def __rmul__(self, other):
        """ other * self = self * other """
        return self * other   # multiplicative operation is commutative

    def __neg__(self):
        """ -self = self * (-1) """
        return self * (-1)
    
    def __sub__(self, other):
        """ self - other = self + (-other) """
        return self + (-other)

    @lru_cache()
    def _div_hashdicts( hashdict1, hashdict2 ):
        """ Divide first dict by second dict and return a HashDict. """
        dict1 = hashdict1._dict
        dict2 = hashdict2._dict
        div_dict = {}
        for key in dict1.keys():
            val = dict2.get(key)
            if not(val == None):
                div_dict[key] = dict1[key] / val
        return HashDict( div_dict )

    def __truediv__(self, other):
        """
        self / other
        if a key is contained only in one HashDict (self or other), omit the key.
        """
        try:
            other = HashDict(other)
            return HashDict._div_hashdicts( self, other )
        except TypeError:  # treat as an element
            self_dict = self.to_dict()
            for key in self_dict.keys():
                try:
                    self_dict[key] /= other
                except:
                    raise TypeError("Cannot divide with a HashDict.")
            return HashDict( self_dict )
        
    def __rtruediv__(self, other):
        """
        other / self
        if a key is contained only in one HashDict (self or other), omit the key.
        """
        try:
            other = HashDict(other)
            return HashDict._div_hashdicts( other, self )
        except TypeError:  # treat as an element
            self_dict = self.to_dict()
            for key in self_dict.keys():
                try:
                    self_dict[key] = other / self_dict[key]
                except:
                    raise TypeError("Cannot divide with a HashDict.")
            return HashDict( self_dict )

    def __iter__(self):
        return self._dict.__iter__()
            
    def __len__(self):
        return len(self._dict)
            
    def __getitem__(self, key):
        return self._dict[key]
    
    def items(self):
        return self._dict.items()
    
    def get(self, key, default=None):
        return self._dict.get(key, default)
    
    def keys(self):
        return self._dict.keys()
    
    def values(self):
        return self._dict.values()
    
    def drop_zeros(self):
        self_dict = self.to_dict()
        for key in self.keys():
            if self.get(key) == 0:
                self_dict.pop(key)
        return HashDict(self_dict)
    
    def project_to(self, keys_tuple, default_value=0):
        self_dict = self.to_dict()
        arranged_list = []
        for key in keys_tuple:
            arranged_list.append( (key, (self_dict.get(key) or default_value)) )
        return HashDict( dict(arranged_list) )
    
    @lru_cache()
    def divide_and_project_to( self, hashdict ):
        """
        Divide the exponents of "hashdict1" by the exponents of "hashdict2".
        Only the keys in "hashdict2" is considered. And the missing key in "hashdict1" is assumed to have the zero exponent.
        For example: {'kg':3, 's':2} / {'m':1, 's':2} = {'m':0, 's':1}
        Returns a HashDict.
        """
        usually_divided = self / hashdict
        result = usually_divided.project_to( hashdict.keys() )
        return result
    
    def pop(self, key, default=None):
        """
        Return a tuple consists of the corresponding item to the given key and a HashDict the key is removed from.
        REMEMBER a HashDict is immutable.
        """
        self_dict = self.to_dict()
        item = self_dict.pop(key, default)
        return (item, HashDict(self_dict))

    def copy(self):
        """ Return a shallow of copy of self. """
        return copy.copy(self)
    
# Test Case
class TestHashDict(unittest.TestCase):
    
    def setUp(self):
        self.dct = HashDict( {'kg':1, 'm':2, 's':-1} )
    def test__add__(self):
        dct1 = HashDict({'kg':1, 'm':2, 's':-1})
        dct2 = HashDict({'kg':-1, 'm':0, 's':-1})
        self.assertEqual(str(dct1+dct2), "{'kg': 0, 'm': 2, 's': -2}")
    def test__mul__(self):
        self.assertEqual(str(self.dct * -3), "{'kg': -3, 'm': -6, 's': 3}")
        dct1 = HashDict({'kg':1, 'm':2, 's':-1})
        dct2 = HashDict({'kg':-1, 'm':0, 's':-1})
        self.assertEqual(str(dct1 * dct2), "{'kg': -1, 'm': 0, 's': 1}")
    def test__sub__(self):
        dct1 = HashDict( {'kg':3, 's':2} )
        dct2 = HashDict( {'m':1, 's':2} )
        result = dct1 - dct2
        self.assertEqual( str(result), "{'kg': 3, 's': 0, 'm': -1}" )
    def test_drop_zeros(self):
        dct = HashDict({'kg':1, 'm':2, 's':0})
        self.assertEqual(str(dct.drop_zeros()), "{'kg': 1, 'm': 2}")
    def test_divide_and_project_to(self):
        dct1 = HashDict({'kg':3, 's':2})
        dct2 = HashDict({'m':1, 's':2})
        result = dct1.divide_and_project_to( dct2 )
        self.assertEqual( str(result), "{'m': 0, 's': 1.0}" )
    def test_pop(self):
        dct = HashDict({'kg':3, 's':2})
        (item, dic) = dct.pop('s')
        self.assertEqual( item, 2 )
        self.assertEqual( str(dic), "{'kg': 3}" )

if __name__=='__main__':
    # unit test
    suite = unittest.defaultTestLoader.loadTestsFromTestCase( TestHashDict )
    unittest.TextTestRunner().run(suite)