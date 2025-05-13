# -*- coding: utf-8 -*-
"""
Created on Thu Sep 14 08:44:01 2017

@author: Jaywan Chung
"""

from time import time

class Timer:
    def __init__(self):
        self.restart()
        
    def restart(self):
        self._tic = time()
        
    def elapsed(self,time_interval):
        toc = time()
        if toc-self._tic >= time_interval:
            return True
        else:
            return False
        
    def passed(self):
        toc = time()
        passed_time = toc-self._tic
        self.restart()
        return passed_time
    
    def print_passed(self, prefix=''):
        print(prefix + str(self.passed()) + ' sec passed.')