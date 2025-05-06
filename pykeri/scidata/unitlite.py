# -*- coding: utf-8 -*-
"""
Created on Thu Jun 15 08:41:19 2017

@author: Jaywan Chung

updated on Mon Jun 19 2017: can initialize a tuple; the output is a numpy.array.
"""

from pykeri.scidata.metricunit import MetricUnit
import unittest
import numpy as np

class unit(object):
    """A singleton managing MetricUnits to variables.
       The variables are identified by their ids (memory address).
       WARNING: this is a CLASSIC singleton, so DO NOT INHERIT this class."""
    _var_to_unit = {}
    def __new__(cls, *args, **kwargs):  # SINGLETON
        if not hasattr(cls, 'self'):
            cls.self = object.__new__(cls)
            cls.self._var_to_unit = cls._var_to_unit  # shared dictionary
        return cls.self
    
    def __init__(self, var, unit_strg):
        self._var_to_unit[id(var)] = unit_strg

    def __repr__(self):
        return 'unit: attaching units to variables'
    
    def __str__(self):
        return str(self._var_to_unit)
    
    @staticmethod
    def metric_unit(var):
        unit_strg = unit._var_to_unit.get(id(var))
        if unit_strg is None:
            raise AttributeError('No metric unit is imposed on the given variable.')
        return MetricUnit(unit_strg)
    
    @staticmethod
    def of(var, style='divisor'):
        munit = unit.metric_unit(var)
        return (var, munit.unit_symbol(style=style))

    @staticmethod
    def pop(var):
        return unit._var_to_unit.pop(id(var), None)

    @staticmethod
    def pop_id(var_id):
        return unit._var_to_unit.pop(var_id, None)
    
    @staticmethod
    def clear():
        unit._var_to_unit.clear()
        
    @staticmethod
    def _output(var, metric_unit, style):
        try:
            value = var * metric_unit.conversion_factor
        except:
            value = np.array(var) * metric_unit.conversion_factor
        return (value, metric_unit.unit_symbol(style=style))

    @staticmethod    
    def to_prefix(var, *symbols_with_prefix, style='divisor'):
        """
        Rewrite the unit with the unit having the same prefix.
        For example, when 'unit_with_prefix = 'cm'', all the units having nonprefix 'm' will be changed to 'cm'.
        """
        munit = unit.metric_unit(var).to_prefix(*symbols_with_prefix)
        return unit._output(var, munit, style)

    @staticmethod
    def to_only(var, *args_of_symbols, style='divisor'):
        """
        Rewrite the unit only using the symbols in the list_of_symbols
        """
        munit = unit.metric_unit(var).to_only(*args_of_symbols)
        return unit._output(var, munit, style)

    @staticmethod
    def to_SI_base(var, style='divisor'):
        """
        Convert the measured value in a SI base unit
        """
        munit = unit.metric_unit(var).to_SI_base()
        return unit._output(var, munit, style)

    @staticmethod
    def to(var, symbol, style='divisor'):
        """
        Convert the measured value in the given metric unit.
        """
        munit = unit.metric_unit(var).to(symbol)
        return unit._output(var, munit, style)

# Test Case
class TestUnit(unittest.TestCase):
    def test_to_prefix(self):
        a = 1.0
        unit(a, 'kg m/s^2')
        self.assertEqual( unit.to_prefix(a, 'g', 'cm'), (1e5,'g cm/s^2') )
    def test_to_only(self):
        a = 1.0
        unit(a, 'N')
        self.assertEqual( unit.to_only(a, 'kg','cm','s'), (1e2,'kg cm/s^2') )
        a = 6.0
        unit(a, 'N')
        self.assertEqual( unit.to_only(a, 'cm', 'g', 's'), (6e5,'g cm/s^2') )
    def test_to_SI_base(self):
        a = 1.0
        unit(a, 'cm/s')
        self.assertEqual( unit.to_SI_base(a), (1e-2,'m/s') )
        import numpy as np
        a = np.array((1.0,2.0), dtype=np.float64)
        unit(a, 'cm/s')
        val, unit_strg = unit.to_SI_base(a)
        self.assertTrue( np.array_equal(val, np.array((1e-2,2e-2), dtype=np.float64)) and unit_strg=='m/s' )
    def test_to(self):
        a = 1.0
        unit(a, 'kg m/s^2')
        self.assertEqual( unit.to(a, 'uN'), (1e6,'uN') )
        a = 6.0
        unit(a, 'J s')
        self.assertEqual( unit.to(a, 'N'), (6e0,'N m s') )        


if __name__=='__main__':
    # unit test
    suite = unittest.defaultTestLoader.loadTestsFromTestCase( TestUnit )
    unittest.TextTestRunner().run(suite)