# -*- coding: utf-8 -*-
"""
Created on Fri Oct 22 16:50:53 2021

@author: byungkiryu
"""


import datetime


# formattedDate, yyyymmdd, HHMMSS = now_string()
def now_string():
    
    now = datetime.datetime.now()
    formattedDate = now.strftime("%Y%m%d_%H%M%S")
    yyyymmdd = formattedDate[0:8]
    HHMMSS   = formattedDate[-6:]
    
    return formattedDate, yyyymmdd, HHMMSS


# def printstring_time_progress(time_delta,counter,sample_id):
    