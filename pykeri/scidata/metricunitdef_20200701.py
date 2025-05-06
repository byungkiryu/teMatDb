# -*- coding: utf-8 -*-
"""
Created on Thu May 11 15:54:50 2017

@author: Jaywan Chung

updated on Tue Aug 22 2018: due to FutureWarning of 'pandas.concat' option: add 'sort=True' option.
updated on Fri May 26 2017: now supports LRU(least recently used) cache.
updated on Mon May 22 2017
"""

import pandas as pd
import numpy as np
from fractions import Fraction
import unittest
from functools import lru_cache

class MetricNonprefix:
    """
    Define units without prefixes.
    """
    _NAME = 'name'
    _SYMBOL = 'symbol'
    _MEASURE = 'measure'
    _DIMENSION_SYMBOL = 'dimension symbol'
    _CONVERSION_FACTOR = 'conversion factor'
    _EQUIVALENT = 'equivalent'
    # You MAY ADD units (withtout any prefixes) in '_user_def'. The order of appearance is the order of preference when we write them.
    # CAUTION: the equivalent formula should AVOID CIRCULAR LOGIC;
    #          for example, if you define 'S' -> '1/Ω' and 'Ω' -> '1/S', both 'S' and 'Ω' CANNOT be represented by base units.
    _user_def = pd.DataFrame([['electronvolt',   'eV',    'electronvolt',              1.60217656535e-19,  'J']],
                    columns = [_NAME,            _SYMBOL, _MEASURE,                    _CONVERSION_FACTOR, _EQUIVALENT])

    # Defines 'SI derived units'. The order of appearance is the order of preference when we write them.
    _SI_derived = pd.DataFrame([['hertz',          'Hz',  'frequency',                              1, '1/s'],
                                ['radian',         'rad', 'angle',                                  1, 'm/m'],
                                ['steradian',      'sr',  'solid angle',                            1, 'm^2/m^2'],
                                ['newton',         'N',   'force',                                  1, 'kg m/s^2'],
                                ['pascal',         'Pa',  'pressure',                               1, 'N/m^2'],
                                ['joule',          'J',   'energy',                                 1, 'N m'],
                                ['watt',           'W',   'power',                                  1, 'J/s'],
                                ['coulomb',        'C',   'electric charge',                        1, 's A'],
                                ['volt',           'V',   'voltage',                                1, 'W/A'],
                                ['farad',          'F',   'electrical capacitance',                 1, 'C/V'],
                                ['ohm',            'Ω',   'electrical resistance',                  1, 'V/A'],
                                ['ohm',            'Ohm', 'electrical resistance',                  1, 'V/A'],
                                ['ohm',            'ohm', 'electrical resistance',                  1, 'V/A'],
                                ['siemens',        'S',   'electrical conductance',                 1, '1/Ω'],
                                ['weber',          'Wb',  'magnetic flux',                          1, 'J/A'],
                                ['tesla',          'T',   'magnetic field strength',                1, 'V s/m^2'],
                                ['henry',          'H',   'electrical inductance',                  1, 'Ω s'],
                                ['degree Celsius', '°C',  'temperature relative to 273.15 K',       np.nan, 'K'],  # 'np.nan' means multiplicative conversion is NOT possible
                                ['degree Celsius', 'degC','temperature relative to 273.15 K',       np.nan, 'K'],
                                ['degree Fahrenheit', '°F',  'temperature scale proposed by Fahrenheit',       np.nan, 'K'],
                                ['degree Fahrenheit', 'degF','temperature scale proposed by Fahrenheit',       np.nan, 'K'],
                                ['lumen',          'lm',  'luminous flux',                          1, 'cd sr'],
                                ['lux',            'lx',  'illuminance',                            1, 'lm/m^2'],
                                ['becquerel',      'Bq',  'radioactivity (decays per unit time)',   1, '1/s'],
                                ['gray',           'Gy',  'absorbed dose (of ionizing radiation)',  1, 'J/kg'],
                                ['sievert',        'Sv',  'equivalent does (of ionizing radiation)',1, 'J/kg'],
                                ['katal',          'kat', 'catalytic activity',                     1, 'mol/s']],
                                columns = [_NAME, _SYMBOL, _MEASURE, _CONVERSION_FACTOR, _EQUIVALENT])

    # Defines base units. There is only one difference with 'SI base units'; here 'g' instead of 'kg' is used because PREFIX is NOT ALLOWED.
    _base = pd.DataFrame([['ampere',  'A',    'electric current',           'I'],
                          ['gram',    'g',    'mass',                       'M'],
                          ['metre',   'm',    'length',                     'L'],
                          ['mole',    'mol',  'amount of substance',        'N'],
                          ['second',  's',    'time',                       'T'],
                          ['kelvin',  'K',    'thermodynamic temperature',  'Θ'],
                          ['candela', 'cd',   'luminous intensity',         'J']],
                columns = [_NAME,    _SYMBOL, _MEASURE,                     _DIMENSION_SYMBOL])
    _base[_CONVERSION_FACTOR] = [1]*len(_base)  # fulfill omitted conversion factors as one.
    _base[_EQUIVALENT] = _base[_SYMBOL]         # fulfill omitted equivalent formulas as itself.
    
    _all = pd.concat([_user_def, _SI_derived, _base], sort=True).set_index(keys=_SYMBOL)  # list all units
    _all[_CONVERSION_FACTOR] = _all[_CONVERSION_FACTOR].apply(lambda factor:Fraction(factor) if np.isfinite(float(factor)) else np.nan)   # prefer a fraction rather than a float for conversion factors

    @lru_cache()
    def name(symbol):
        return MetricNonprefix._all.ix[symbol, MetricNonprefix._NAME]
    @lru_cache()
    def names():
        return tuple(MetricNonprefix._all[MetricNonprefix._NAME])
    @lru_cache()
    def is_nonprefix_unit(symbol):
        return (symbol in MetricNonprefix.symbols())
    @lru_cache()
    def symbols():
        return tuple(MetricNonprefix._all.index.values)
    @lru_cache()
    def base_symbols():
        return tuple(MetricNonprefix._base[MetricNonprefix._SYMBOL])
    @lru_cache()
    def measure(symbol):
        return MetricNonprefix._all.ix[symbol, MetricNonprefix._MEASURE]
    @lru_cache()
    def dimension_symbol(symbol):
        from pykeri.scidata.metricunit import MetricUnit
        base_dic = MetricUnit(symbol).to_SI_base()._unit_dic
        symbol = ''
        for key in base_dic.keys():
            exponent = Fraction(base_dic[key])
            if key == 'kg':
                key = 'g'
            if exponent == 1:
                symbol += ' ' + MetricNonprefix._all.ix[key, MetricNonprefix._DIMENSION_SYMBOL]
            else:
                symbol += ' ' + MetricNonprefix._all.ix[key, MetricNonprefix._DIMENSION_SYMBOL] + '^' + str(exponent)
        if len(symbol) > 0:
            symbol = symbol[1:]
        return symbol
    @lru_cache()
    def equivalent(symbol):
        """
        Returns a tuple of the form (equivalent unit, necessary conversion factor)
        """
        return (MetricNonprefix._all.ix[symbol, MetricNonprefix._EQUIVALENT], MetricNonprefix._all.ix[symbol, MetricNonprefix._CONVERSION_FACTOR])

# Test Case
class TestMetricNonprefix(unittest.TestCase):
    def test_name(self):
        self.assertEqual(MetricNonprefix.name('lx'), 'lux')
    def test_names(self):
        self.assertTrue('gram' in MetricNonprefix.names())
    def test_is_nonprefix_unit(self):
        self.assertTrue(MetricNonprefix.is_nonprefix_unit('Wb'))
        self.assertFalse(MetricNonprefix.is_nonprefix_unit('JChung'))
    def test_symbols(self):
        self.assertTrue('sr' in MetricNonprefix.symbols())
    def test_measure(self):
        self.assertEqual(MetricNonprefix.measure('s'), 'time')
    def test_dimension_symbol(self):
        self.assertEqual(MetricNonprefix.dimension_symbol('cd'), 'J')
        self.assertEqual(MetricNonprefix.dimension_symbol('N'), 'M L T^-2')
    def test_equivalent(self):
        self.assertTrue(MetricNonprefix.equivalent('mol'), ('mol',1))
        # check no circular logic for conversion
        for symbol in MetricNonprefix.symbols():
            (_, conversion_factor) = MetricNonprefix.equivalent(symbol)
            if np.isfinite(float(conversion_factor)):                
                from pykeri.scidata.metricunit import MetricUnit
                # too time consuming; temporarily skip
                # previous: Ran 11 tests in 0.514s
                MetricUnit(symbol).to_SI_base()


class MetricPrefix:
    """
    Define metric prefixes.
    """
    _NAME = 'name'
    _SYMBOL = 'symbol'
    _CONVERSION_FACTOR = 'conversion factor'
    _all = pd.DataFrame([['yotta', 'Y',  1e24],
                         ['zetta', 'Z',  1e21],
                         ['exa',   'E',  1e18],
                         ['peta',  'P',  1e15],
                         ['tera',  'T',  1e12],
                         ['giga',  'G',  1e09],
                         ['mega',  'M',  1e06],
                         ['kilo',  'k',  1e03],
                         ['hecto', 'h',  1e02],
                         ['deca',  'da', 1e01],
                         ['',      '',   1e00],
                         ['deci',  'd',  1e-01],
                         ['centi', 'c',  1e-02],
                         ['milli', 'm',  1e-03],
                         ['micro', 'μ',  1e-06],
                         ['micro', 'u',  1e-06],
                         ['nano',  'n',  1e-09],
                         ['pico',  'p',  1e-12],
                         ['femto', 'f',  1e-15],
                         ['atto',  'a',  1e-18],
                         ['zepto', 'z',  1e-21],
                         ['yocto', 'y',  1e-24]],
        columns = [_NAME, _SYMBOL, _CONVERSION_FACTOR])
    _all.set_index(_all[_SYMBOL].values, inplace=True)  # set index
    _all[_CONVERSION_FACTOR] = _all[_CONVERSION_FACTOR].apply(lambda factor:Fraction(factor))  # conversion factor as Fraction

    @lru_cache()
    def name(symbol):
        return MetricPrefix._all.ix[symbol, MetricPrefix._NAME]    
    @lru_cache()
    def conversion_factor(symbol):
        return MetricPrefix._all.ix[symbol, MetricPrefix._CONVERSION_FACTOR]
    @lru_cache()
    def names():
        return tuple(MetricPrefix._all[MetricPrefix._NAME])
    @lru_cache()
    def symbols(): # preferential order as manually typed
        return tuple(MetricPrefix._all[MetricPrefix._SYMBOL])
    @lru_cache()
    def is_prefix(symbol):
        return symbol in MetricPrefix.symbols()

# Test Case
class TestMetricPrefix(unittest.TestCase):
    def test_name(self):
        self.assertEqual(MetricPrefix.name('c'), 'centi')
    def test_conversion_factor(self):        
        self.assertEqual(MetricPrefix.conversion_factor('h'), 1e02) # test value
        self.assertTrue(isinstance(MetricPrefix.conversion_factor('p'), Fraction))         # test type: should be Fraction
    def test_names(self):
        self.assertTrue('nano' in MetricPrefix.names())
    def test_symbols(self):
        idx_deca = MetricPrefix.symbols().index('da')
        idx_none = MetricPrefix.symbols().index('')
        self.assertTrue( idx_deca < idx_none ) # deca prefix is preferential than nothing

if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestMetricNonprefix)
    other_suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestMetricPrefix)
    suite.addTest(other_suite)
    unittest.TextTestRunner().run(suite)