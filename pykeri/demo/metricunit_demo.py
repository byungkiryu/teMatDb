# -*- coding: utf-8 -*-
"""
Created on Tue May 23 13:39:18 2017

@author: Jaywan Chung

Last updated on Tue May 23 2017
"""
import random
from pykeri.scidata.metricunitdef import MetricPrefix, MetricNonprefix
from pykeri.scidata.metricunit import MetricUnit
import numpy as np

class MetricUnitDemo:
    
    _all_single_unit = []
    for nonprefix in MetricNonprefix.symbols():
        if not( MetricNonprefix.equivalent(nonprefix)[1] is np.nan):
            for prefix in MetricPrefix.symbols():
                _all_single_unit.append( prefix+nonprefix )    
    
    @staticmethod
    def generate_single_unit():
        return random.choice( MetricUnitDemo._all_single_unit )
    
    @staticmethod
    def generate_number():
        chosen = random.choice(['fraction', 'integer'])
        sign = random.choice(['+', '-'])
        numerator = random.randrange(3)
        denominator = random.randrange(3) + 1
        if chosen == 'fraction':
            number_str = sign + str(numerator) + '/' + str(denominator)
        else:
            number_str = sign + str(numerator)
        return number_str
    
    @staticmethod
    def generate_unit(depth, stack):
        if depth == 0:
            unit = MetricUnitDemo.generate_single_unit()
            stack.append(unit)
            return unit
        chosen = random.choice(['*', ' ', '/', '^', 'unit'])
        if chosen == '*' or chosen == ' 'or chosen == '/':  # binary operation
            if chosen == '*' or chosen == ' ':
                chosen = '*'
            result ='(' + MetricUnitDemo.generate_unit(depth-1,stack) + chosen + MetricUnitDemo.generate_unit(depth-1,stack) + ')'
            stack.append(chosen)
            return result
        elif chosen == '^':  # unary operation
            number = MetricUnitDemo.generate_number()
            result = '(' + MetricUnitDemo.generate_unit(depth-1,stack) +')' + chosen + number
            stack.append(chosen)
            stack.append(number)
            return result
        elif chosen == 'unit':
            unit = MetricUnitDemo.generate_single_unit()
            stack.append(unit)
            return unit
        
    @staticmethod
    def run(iteration=10, depth=3):
        print( '<<Demo for the MetricUnit class>>' )
        for idx in range(iteration):
            expr_stack = []
            symbol = MetricUnitDemo().generate_unit(depth,expr_stack)
            generated_dic = MetricUnit._eval_parsed(expr_stack)
            unit = MetricUnit(symbol)
            print( str(idx) + ': ' + symbol)
            print(' ==> ' + str(unit) )
            assert( generated_dic == unit._unit_dic )
            print( " ==>", unit.to_SI_base(), "(in SI base)" )
        print('<<End of Demo.>>')
        
if __name__ == '__main__':
    MetricUnitDemo.run()