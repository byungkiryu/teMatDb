# -*- coding: utf-8 -*-
"""
Created on Fri Mar  9 18:55:33 2018

@author: Jaywan Chung
"""

def print_progress(progress_ratio):
    """
    Print progress string on the console. Ratio is a floating number between 0 and 1.
    """
    fill = int(progress_ratio*100)
    if fill > 100:
        fill = 100
    if fill < 0:
        fill = 0
    print("\r|" + "#"*fill + ' '*(100-fill)+'|', end='')