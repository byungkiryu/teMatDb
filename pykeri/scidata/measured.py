# -*- coding: utf-8 -*-
"""
Created on Mon May 15 18:06:39 2017

@author: Jaywan Chung

updated on Tue May 30 2017: Add __hash__. An immutable object.
updated on Fri May 26 2017: progress on LRU(least recently used) cache partially. Need to build more.
updated on Tue May 23 2017
"""

from pykeri.scidata.metricunit import MetricUnit
from fractions import Fraction
import pyparsing as pp
import unittest


class Measured:
    """
    Handles a value with a metric unit.
    """
    _value = Fraction(0)
    @property
    def value(self):
        return self._value
    
    _unit = MetricUnit('')  # dimensionless
    @property
    def unit(self):
        return self._unit
    
    def __hash__(self):
        return hash( (self._value, self._unit) )

    def __init__(self, value_or_unit, unit_text=''):
        value_and_unit = ''
        if isinstance(value_or_unit, Measured):
            measured = value_or_unit
            self._value = measured.value
            self._unit = measured.unit
        elif isinstance(unit_text, MetricUnit):
            self._value = value_or_unit
            self._unit = unit_text
        elif isinstance(value_or_unit, str):
            value_and_unit = value_or_unit + unit_text
            (self._value, self._unit) = Measured.parse_value_and_unit( value_and_unit )
        else:
            self._value = value_or_unit
            self._unit = MetricUnit( unit_text )
    
    def to_string(self):
        return ("{:.1e} ".format(float(self.value)) + str(self.unit)).rstrip()

    def __repr__(self):
        return 'Measured: ' + self.to_string()

    def __str__(self):
        return self.to_string()

    def __eq__(self, other):
        """
        (self == other) or (other == self)
        Conversion of unit is NOT considered; because this class uses __hash__.
        """
        try:
            other = Measured(other)
        except TypeError:
            return False
        return (self.value == other.value) and (self.unit == other.unit)  # have same value and same unit

    def to_prefix(self, *symbols_with_prefix):
        """
        Rewrite the unit with the unit having the same prefix.
        For example, when 'unit_with_prefix = 'cm'', all the units having nonprefix 'm' will be changed to 'cm'.
        """
        unit = self.unit.to_prefix(*symbols_with_prefix)
        value = self.value * unit.conversion_factor
        return Measured( value, unit.no_conversion_factor() )  # omit conversion factor
    
    def to_only(self, *args_of_symbols):
        """
        Rewrite the unit only using the symbols in the list_of_symbols
        """
        unit = self.unit.to_only(*args_of_symbols)
        value = self.value * unit.conversion_factor
        return Measured( value, unit.no_conversion_factor() )  # omit conversion factor
    
    def to_SI_base(self):
        """
        Convert the measured value in a SI base unit
        """
        unit = self.unit.to_SI_base()
        value = self.value * unit.conversion_factor
        return Measured( value, unit.no_conversion_factor() )  # omit conversion factor

    def to(self, symbol):
        """
        Convert the measured value in the given metric unit.
        """
        unit = self.unit.to(symbol)
        value = self.value * unit.conversion_factor
        return Measured( value, unit.no_conversion_factor() )  # omit conversion factor

    def __mul__(self, other):
        """
        self * other
        Returns the resulting Measured.
        """
        try:
            other = Measured(other)
        except TypeError:
            raise TypeError("Cannot multiply to a Measured class.")
        return Measured( self.value * other.value, self.unit * other.unit )
    
    def __rmul__(self, other):
        """
        other * self = self * other
        """
        return self * other

    def __truediv__(self, other):
        """ self / other """
        try:
            other = Measured(other)
        except TypeError:
            raise TypeError("Cannot divide with a Measured class.")
        return Measured( self.value / other.value, self.unit / other.unit )

    def __rtruediv__(self, other):
        """ other / self """
        try:
            other = Measured(other)
        except TypeError:
            raise TypeError("Cannot divide with a Measured class.")
        return Measured( other.value / self.value , other.unit / self.unit )
    
    @staticmethod
    def add(first_measured, second_measured):
        first_unit = first_measured.unit
        second_unit = second_measured.unit
        if first_unit.has_same_unit_with(second_unit):
            return Measured( first_measured.value + second_measured.value, first_unit )
        elif first_unit.is_equivalent_to(second_unit):
            if len(first_unit.unit_symbol()) < len(second_unit.unit_symbol()):
                short_measured = first_measured
                long_measured = second_measured.to(first_unit)
            else:
                short_measured = second_measured
                long_measured = first_measured.to(second_unit)
        else:
            raise ValueError('Cannot add non-equivalent measured values; their dimensions are different.')
        return Measured( short_measured.value + long_measured.value, short_measured.unit )
    
    def __add__(self, other):
        """ self + other """
        try:
            other = Measured(other)
        except TypeError:
            raise TypeError("Cannot add to a Measured class.")
        return Measured.add(self, other)
    
    def __radd__(self, other):
        """ other + self = self + other """
        return self + other

    def __neg__(self):
        """ -self """
        return Measured( -self.value, self.unit )

    def __sub__(self, other):
        """ self - other """
        return self + (-other)

    def __rsub__(self, other):
        """ other - self = -self + other """
        return (-self) + other

    def __pow__(self, exponent):
        """ self ** exponent """
        return Measured( self.value ** exponent, self.unit ** exponent )
    
    def drop_zero_exponent(self):
        return Measured( self.value, self.unit.drop_zero_exponent() )
    
    def to_precise_string(self):
        return (str(self.value) + ' ' + str(self.unit)).rstrip()
    
    @staticmethod
    def parse_value_and_unit( text ):
        """
        When a text is given by "value (unit)", returns them.
        value :: fracion | real | integer
        NO arithmetic operation is allowed.
        """
        # elementary operations
        div   = pp.Literal("/")
        lpar  = pp.Literal( "(" ).suppress()
        rpar  = pp.Literal( ")" ).suppress()
        # parser for numbers
        nums = pp.nums
        integer = pp.Word( "+-"+nums, nums )
        point = pp.Literal(".")
        e     = pp.CaselessLiteral( "e" )
        fraction = pp.Combine( integer + div + integer )
        real = pp.Combine( pp.Word( "+-"+nums, nums ) \
                           + pp.Optional( point + pp.Optional( pp.Word( nums ) ) ) \
                           + pp.Optional( e + pp.Word( "+-"+nums, nums ) ) )
        number_term = pp.Forward()
        number = fraction | real | integer | (lpar + number_term + rpar)
        number_term << number
                
        # define BNF(Backus-Naur Form)
        #bnf = number_term + pp.ZeroOrMore( pp.Word( " ()[]*/^+-"+pp.alphas+nums) )
        bnf = number_term + pp.restOfLine()
        
        result = bnf.parseString(text)
        
        value = 0
        unit_strg = ''
        if len(result) > 0:
            value_strg = result[0]
            if '/' in value_strg:   # if a fraction
                value = Fraction(value_strg)
            elif ('.' in value_strg) or ('e' in value_strg):  # if a real number
                value = float(value_strg)
            else:
                value = int(value_strg)
        if len(result) > 1:
            unit_strg = result[1]
        
        return (value, MetricUnit(unit_strg))
    
    def is_dimensionless(self):
        return self.unit.is_dimensionless()


# Test Case
class TestMeasured(unittest.TestCase):
    def test_to_prefix(self):
        self.assertEqual( str( Measured('1 kg m/s^2').to_prefix('g', 'cm') ), '1.0e+05 g cm/s^2' )
    def test_to_only(self):
        self.assertEqual( str( Measured('1 N').to_only('kg','cm','s') ), '1.0e+02 kg cm/s^2' )
        self.assertEqual( str( Measured(6, 'N').to_only('cm', 'g', 's')), '6.0e+05 g cm/s^2')
    def test_to_SI_base(self):
        self.assertEqual( str( Measured('1 cm/s').to_SI_base() ), '1.0e-02 m/s' )
    def test_to(self):
        self.assertEqual( str( Measured(1, 'kg m/s^2').to('uN') ), '1.0e+06 uN' )
        self.assertEqual( str( Measured(6, 'J s').to('N')), '6.0e+00 N m s' )
    def test_mul(self):
        measured1 = Measured('1 kg m/s^2')
        measured2 = Measured('2 N')
        self.assertEqual( str( measured1 * measured2 ), '2.0e+00 N kg m/s^2' )
    def test_div(self):
        measured1 = Measured('1 kg m/s^2')
        measured2 = Measured('2 N')
        self.assertEqual( str( measured1 / measured2 ), '5.0e-01 kg m/N/s^2' )
    def test_add(self):
        added = Measured(1, 'kg m/s^2') + Measured( Fraction(1,2), 'N')
        self.assertEqual( added.to_precise_string(), '3/2 N' )
        


if __name__=='__main__':
    # unit test
    suite = unittest.defaultTestLoader.loadTestsFromTestCase( TestMeasured )
    unittest.TextTestRunner().run(suite)
    # check the lru_cache() effect
    suite = unittest.defaultTestLoader.loadTestsFromTestCase( TestMeasured )
    unittest.TextTestRunner().run(suite)