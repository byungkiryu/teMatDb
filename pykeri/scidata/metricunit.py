# -*- coding: utf-8 -*-
"""
Created on Fri May 19 08:48:12 2017

@author: Jaywan Chung

updated on Mon May 29 2017: Add __hash__. Use HashDict, an immutable dict.
updated on Fri May 26 2017: Supports LRU(least recently used) cache partially. Need to text more.
updated on Thu May 25 2017
"""

from pykeri.scidata.metricunitdef import MetricPrefix, MetricNonprefix
from pykeri.util.hashdict import HashDict
from fractions import Fraction
import pyparsing as pp
import unittest
import copy
from functools import lru_cache

class MetricUnit:
    SYMBOL_STYLE_DIVISOR = 'divisor'
    SYMBOL_STYLE_ONLY_EXPONENT = 'exponent'

    _conversion_factor = Fraction(1)
    @property
    def conversion_factor(self):
        return self._conversion_factor
    
    _unit_dic = HashDict({})
    @property
    def unit_dic(self):
        return self._unit_dic.copy()
    
    def __hash__(self):
        return hash( (self._conversion_factor, self._unit_dic) )

    _symbol_style = SYMBOL_STYLE_DIVISOR
    @property
    def symbol_style(self):
        return self._symbol_style
    @symbol_style.setter
    def symbol_style(self, option):
        POSSIBLE_SYMBOL_STYLE = [MetricUnit.SYMBOL_STYLE_DIVISOR, MetricUnit.SYMBOL_STYLE_ONLY_EXPONENT]
        if option in POSSIBLE_SYMBOL_STYLE:
            self._symbol_style = option
        else:
            raise ValueError('Not a possible symbol style.')

    _dict_unit_to_prefix = {}
    _dict_unit_to_nonprefix = {}
    _dict_unit_to_preference = {}
    _num_prefix = len(MetricPrefix.symbols())
    for nonprefix_preference, nonprefix in enumerate(MetricNonprefix.symbols()):
        for prefix_preference, prefix in enumerate(MetricPrefix.symbols()):
            _dict_unit_to_prefix[ prefix+nonprefix ] = prefix
            _dict_unit_to_nonprefix[ prefix+nonprefix ] = nonprefix
            _dict_unit_to_preference[ prefix+nonprefix ] = nonprefix_preference * _num_prefix + prefix_preference
    
    _all_SI_base_unit = tuple(['kg' if symbol == 'g' else symbol for symbol in MetricNonprefix.base_symbols()])

    def symbol(self):
        if self.conversion_factor !=1:
            cf_str = "{:.1e} ".format(float(self.conversion_factor))
        else:
            cf_str = ''
        return cf_str + self.unit_symbol()

    @lru_cache()
    def to_string(self):
        return self.symbol()
    
    def __init__( self, strg_or_dict = '', conversion_factor = Fraction(1) ):
        if isinstance(strg_or_dict, str):
            strg = strg_or_dict
            if strg.strip() == '':
                strg = '1'  # dimensionless unit
            self._conversion_factor = conversion_factor
            self._unit_dic = MetricUnit._parse_and_eval( strg )
        elif isinstance(strg_or_dict, dict):
            self._conversion_factor = conversion_factor
            self._unit_dic = HashDict(strg_or_dict)
        elif isinstance(strg_or_dict, HashDict):
            self._conversion_factor = conversion_factor
            self._unit_dic = strg_or_dict
        elif  isinstance(strg_or_dict, MetricUnit):
            self._conversion_factor = strg_or_dict.conversion_factor
            self._unit_dic = strg_or_dict.unit_dic.copy()
        else:
            raise TypeError("Cannot create a MetricUnit.")

    def __repr__(self):
        return 'MetricUnit: ' + self.to_string()
    
    def __str__(self):
        return self.to_string()
    
    @lru_cache()
    def __pow__(self, exponent):
        """
        self ** exponent
        """
        unit_dic = self._unit_dic * Fraction(exponent)  # a HashDict
        conversion_factor = self.conversion_factor ** exponent
        return MetricUnit( unit_dic, conversion_factor )

    def __eq__(self, other):
        """
        self == other
        CAUTION: The identity operator does NOT compare the conversion factor; only the same unit suffices.
        """
        try:
            other = MetricUnit(other)
            return (self.unit_dic == other.unit_dic) and (self.conversion_factor == other.conversion_factor)
        except TypeError:
            return False

    @lru_cache()
    def is_SI_base(self):
        """
        Check if the given unit is written only in the SI base units.
        """
        for symbol in self.unit_dic.keys():
            if not(symbol in MetricUnit._all_SI_base_unit):
                return False
        return True

    def copy(self):
        return copy.deepcopy(self)

    @lru_cache()
    def is_single_unit(self):
        if len(self.unit_dic) == 1:
            return True
        else:
            return False
    
    @lru_cache()
    def from_single_unit_to(self, single_symbol, to_symbol, conversion_factor = Fraction(1)):
        """
        Change all the single units to the second unit.
        1 single_symbol = conversion_factor * to_symbol.
        """
        single_unit = MetricUnit(single_symbol)
        if not(single_unit.is_single_unit()):
            raise ValueError('The first symbol should be a single unit.')        
        (single_symbol, single_exponent) = tuple( single_unit.unit_dic.items() )[0]
        to_unit = MetricUnit(to_symbol)
        to_unit_dic = to_unit.unit_dic
        
        plain_dic = self.unit_dic.to_dict()    # using a (plain) dict instead of a (immutable) HashDict
        exponent = (plain_dic.get(single_symbol) or 0)
        if exponent:
            del plain_dic[single_symbol]
        for new_symbol in to_unit_dic.keys():
            plain_dic[new_symbol] = Fraction( (plain_dic.get(new_symbol) or 0) + to_unit_dic[new_symbol] * exponent / single_exponent )
        multiplier = Fraction( pow(conversion_factor, Fraction(exponent,single_exponent)) )

        return MetricUnit( plain_dic, self.conversion_factor * multiplier )

    def drop_zero_exponent(self):
        """
        Erase all the units with 0 exponent.
        Return the simplified MetricUnit.
        """
        return MetricUnit( self.unit_dic.drop_zeros(), self.conversion_factor )

    @lru_cache()
    def to_SI_base(self):
        """
        Rewrite the given unit using the SI base units.
        """
        unit = self.copy()
        while(not(unit.is_SI_base())):
            udic = unit.unit_dic.copy()
            for symbol in udic.keys():
                if not(symbol in MetricUnit._all_SI_base_unit):
                    if symbol == 'g':   # an exception: a nonprefix but should be converted to 'kg'
                        unit = unit.from_single_unit_to('g', 'kg', Fraction(1e-3))
                    else:
                        prefix = MetricUnit._dict_unit_to_prefix[symbol]
                        nonprefix = MetricUnit._dict_unit_to_nonprefix[symbol]
                        cf_prefix = MetricPrefix.conversion_factor(prefix)
                        (equiv_unit, cf_nonprefix) = MetricNonprefix.equivalent(nonprefix)
                        unit = unit.from_single_unit_to(symbol, nonprefix, cf_prefix)   # eliminate the prefix first
                        unit = unit.from_single_unit_to(nonprefix, equiv_unit, cf_nonprefix)   # reduce closer to a base unit
            unit = unit.drop_zero_exponent()
            if udic == unit.unit_dic:  # if nothing improved, something is wrong
                raise ValueError("MetricUnit: conversion to SI base units failed.")
        return unit.drop_zero_exponent()

    def is_equivalent_to(self, unit):
        """
        If the given unit is convertible to the other unit, returns True.
        """
        self_SI = self.to_SI_base()
        try:
            other_SI = MetricUnit(unit).to_SI_base()
            return self_SI.unit_dic == other_SI.unit_dic
        except TypeError:
            return False

    @lru_cache()    
    def to_only(self, *args_of_symbols):
        """
        Rewrite the unit only using the symbols in the argument.
        """
        if len(args_of_symbols) == 0:
            raise ValueError('In the list, at least one symbol should be given.')

        return MetricUnit._rewrite_only_with( self, *args_of_symbols )
            
    def _rewrite_only_with( metricunit, *args_of_symbols ):
        """
        Rewrite the MetricUnit only using the symbols in the argument.
        LRU cached so no repetitious computation.
        """
        unit = MetricUnit( args_of_symbols[0] )
        given_unit = metricunit
        possible_exponents = set( (given_unit.to_SI_base().unit_dic.divide_and_project_to( unit.to_SI_base().unit_dic )).values() )
        if len(args_of_symbols) == 1:
            if len(possible_exponents) == 1:
                exponent = possible_exponents.pop()
                if given_unit.is_equivalent_to(unit ** exponent):
                    return given_unit.to(unit ** exponent)
            else:
                return None
        else:
            for exponent in possible_exponents:
                new_unit = given_unit / (unit ** exponent)
                result = MetricUnit._rewrite_only_with( new_unit, *args_of_symbols[1:])
                if result != None:
                    return (unit ** exponent) * result
                else:
                    return None

    def to(self, symbol):
        """
        Convert to the given metric unit.
        """
        try:
            unit = MetricUnit(symbol)
        except TypeError:
            raise TypeError('Cannot convert to ' + type(symbol).__name__ + ' type; input a string or a MetricUnit.')
        result = (self / unit).to_SI_base()
        result *= unit
        return result

    def __mul__(self, other):
        """
        self * other
        """
        try:
            other = MetricUnit(other)
        except TypeError:
            raise TypeError('Cannot multiply to a MetricUnit.')
        return MetricUnit( self.unit_dic + other.unit_dic, self.conversion_factor * other.conversion_factor )

    def __truediv__(self, other):
        """
        self / other
        """
        try:
            other = MetricUnit(other)
        except TypeError:
            raise TypeError('Cannot do divison to a MetricUnit.')
        return MetricUnit( self.unit_dic - other.unit_dic, self.conversion_factor / other.conversion_factor )

    @lru_cache()
    def unit_symbol(self, style='default'):
        if style == 'default':
            style = self.symbol_style            
        symbol = ''
        udic = self.unit_dic  # for brevity
        nonnegative_exponent = [unit for unit in udic.keys() if udic[unit]>=0]  # preference for units with nonnegative exponents
        negative_exponent = [unit for unit in udic.keys() if udic[unit]<0]      # preference for units with negative exponents
        nonnegative_preference = sorted(nonnegative_exponent, key=lambda unit:MetricUnit._dict_unit_to_preference[unit])
        negative_preference = sorted(negative_exponent, key=lambda unit:MetricUnit._dict_unit_to_preference[unit])
        preference = nonnegative_preference + negative_preference
        # the first divisor is not allowed: s^-1 will be used instead of 1/s for convenience using measured values.
        for idx,unit in enumerate(preference):
            exponent = udic[unit]
            if style == MetricUnit.SYMBOL_STYLE_ONLY_EXPONENT or idx == 0:                
                symbol += ' ' + unit
                if exponent != 1:
                    symbol += '^' + str(exponent)
            elif style == MetricUnit.SYMBOL_STYLE_DIVISOR:
                if exponent == 1:
                    symbol += ' ' + unit
                elif exponent == -1:
                    symbol += '/' + unit
                elif exponent < 0:
                    symbol += '/' + unit + '^' + str(-exponent)
                else:
                    symbol += ' ' + unit + '^' + str(exponent)
        if len(symbol) >=1:
            symbol = symbol[1:]
        return symbol

    @lru_cache()
    def _parse_and_eval( strg ):
        parsed = MetricUnit._parse( strg )
        return MetricUnit._eval_parsed( parsed )
        
    @lru_cache()
    def _parse( strg ):
        """
        Parse a string and return a list of symbols.
        """
        expr_stack = []
        def push_all( strg, loc, toks ):
            expr_stack.extend( toks )
        parser = MetricUnit.get_parser( push_all )
        try:
            parser.parseString(strg)
        except pp.ParseException:
            raise ValueError("Invalid symbol: is '" + strg + "' a metric unit?")
        return expr_stack
    
    def _eval_parsed( parsed ):
        """
        Evaluate a parsed list of symbols.
        For the BNF syntax, refer to MetricUnit.get_parser() function.
        """
        parsed = parsed.copy()
        dict_stack = []
        while( len(parsed) > 0):
            symbol = parsed.pop(0)
            if symbol == '*':
                right_element = dict_stack.pop()
                left_element  = dict_stack.pop()
                dict_stack.append( left_element + right_element )
            elif symbol == '/':
                right_element = dict_stack.pop()
                left_element  = dict_stack.pop()
                dict_stack.append( left_element - right_element )
            elif symbol == '^':
                element= dict_stack.pop()
                exponent = Fraction(parsed.pop(0))
                dict_stack.append( element * exponent )
            elif symbol == '1':
                dict_stack.append( HashDict({}) )
            else:  # if units
                dict_stack.append( HashDict({symbol: 1}) )
        return dict_stack.pop(0)

    @lru_cache()
    def get_parser( parse_action ):
        """
        atom    :: '1' | unit | '(' term ')'
        number  :: integer | fraction | real | '(' number ')'
        factor  :: atom + expop + number | atom
        term    :: factor [ multop factor ]*
        """
        # parser for elementary operations
        mult  = pp.Literal( "*" ) | pp.White(max=1)
        div   = pp.Literal( "/" )
        lpar  = pp.Literal( "(" ).suppress()
        rpar  = pp.Literal( ")" ).suppress()
        #multop = div | pp.Optional(mult, default='*')
        multop = div | pp.Optional(mult, default='*')
        expop = pp.Literal( "^" )        
        
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
        
        # parser for units        
        prefix_symbols = ''.join(' '+symbol for symbol in MetricPrefix.symbols())
        nonprefix_symbols = ''.join(' '+symbol for symbol in MetricNonprefix.symbols())
        prefix = pp.oneOf(prefix_symbols)
        nonprefix = pp.oneOf(nonprefix_symbols)
        unit = pp.Combine(prefix + nonprefix) | nonprefix
        
        # define BNF(Backus-Naur Form)
        term = pp.Forward()
        atom = pp.Literal("1").setParseAction(parse_action) | unit.setParseAction(parse_action) | ( lpar + term.suppress() + rpar )
        factor = atom + pp.ZeroOrMore( ( pp.Optional(expop,default='^') + number_term ).setParseAction(parse_action) )
        term <<  factor + pp.ZeroOrMore( (multop + factor.suppress()).setParseAction(parse_action) )
        bnf = pp.Literal("[") + term + pp.Literal("]") | term
        
        return bnf

    def is_dimensionless(self):
        unit = self.to_SI_base().drop_zero_exponent()
        if len(unit.unit_dic) == 0:
            return True
        else:
            return False
        
    @lru_cache()
    def to_prefix(self, *symbols_with_prefix):
        """
        Rewrite the unit with the unit having the same prefix.
        For example, when 'unit_with_prefix = 'cm'', all the units having nonprefix 'm' will be changed to 'cm'.
        """
        conversion_factor = self.conversion_factor
        prev_dic = self.unit_dic.to_dict()
        for symbol_with_prefix in symbols_with_prefix:
            if MetricPrefix.is_prefix(symbol_with_prefix):  # if only a prefix is givan, change all the nonprefixes
                new_prefix = symbol_with_prefix
                nonprefixes = MetricNonprefix.symbols()
            else:
                new_prefix = MetricUnit._dict_unit_to_prefix[symbol_with_prefix]
                nonprefixes = [ MetricUnit._dict_unit_to_nonprefix[symbol_with_prefix] ]
            unit_dic = prev_dic.copy()    # unit_dic is a plain dic
            for key in prev_dic.keys():
                old_prefix = MetricUnit._dict_unit_to_prefix[key]
                nonprefix = MetricUnit._dict_unit_to_nonprefix[key]
                if (nonprefix in nonprefixes) and (old_prefix != new_prefix):
                    exponent = unit_dic.pop(key)
                    unit_dic[new_prefix + nonprefix] = exponent
                    conversion_factor *= (MetricPrefix.conversion_factor(old_prefix)) ** exponent
                    conversion_factor /= (MetricPrefix.conversion_factor(new_prefix)) ** exponent
            prev_dic = unit_dic
        return MetricUnit( unit_dic, conversion_factor )
    
    def has_same_unit_with(self, other):
        try:
            other = MetricUnit(other)
        except TypeError:
            return False
        return self.unit_dic == other.unit_dic
    
    def no_conversion_factor(self):
        return MetricUnit( self._unit_dic )

# Test Case
class TestMetricUnit(unittest.TestCase):
    def test_has_same_unit_with(self):
        unit1 = MetricUnit('kg m/s^2')
        unit2 = MetricUnit('m s^-2 kg')
        self.assertEqual(unit1, unit2)
    def test_to_SI_base(self):
        unit = MetricUnit('N')
        self.assertEqual(unit.to_SI_base(), MetricUnit('kg m/s^2'))
        unit = MetricUnit('cm/s')
        self.assertEqual( str(unit.to_SI_base()), '1.0e-02 m/s')
        self.assertEqual( str(MetricUnit('J s/N').to_SI_base()), 'm s')
    def test_is_dimensionless(self):
        unit = MetricUnit('N/(kg m/s^2)')
        self.assertTrue(unit.is_dimensionless())
    def test_is_equivalent_to(self):
        unit = MetricUnit('N')
        self.assertTrue(unit.is_equivalent_to('kg m/s^2'))
    def test_to(self):
        self.assertEqual(str(MetricUnit('kg^2 m/s^2').to('N')), 'N kg')
    def test_to_only(self):
        unit = MetricUnit('N')
        self.assertEqual(str(unit.to_only('kg', 'm', 's')), 'kg m/s^2')
        self.assertEqual(unit.to_only('kg', 'm'), None)
    def test_to_prefix(self):
        self.assertEqual( str(MetricUnit('kg km^2 / s^2').to_prefix('cm')), '1.0e+10 kg cm^2/s^2')
        self.assertEqual( str(MetricUnit('kg m/s^2').to_prefix('g', 'cm')), '1.0e+05 g cm/s^2')
    def power(self):
        self.assertEqual( str(MetricUnit('kg').power(3), 'kg^3') )


if __name__=='__main__':
    # unit test
    suite = unittest.defaultTestLoader.loadTestsFromTestCase( TestMetricUnit )
    unittest.TextTestRunner().run(suite)
    # check the lru_cache() effect
    suite = unittest.defaultTestLoader.loadTestsFromTestCase( TestMetricUnit )
    unittest.TextTestRunner().run(suite)
    
    # demo
    from pykeri.demo.metricunitdemo import MetricUnitDemo
    MetricUnitDemo.run()