# -*- coding: utf-8 -*-
"""
Created on Thu Sep 14 08:48:17 2017

Example for pykeri.timer.Timer
    Timer()
    Timer().elapsed(time)
    Timer().restart()

@author: Jaywan Chung
"""

from pykeri.util.timer import Timer

timer = Timer()
print("Give me 3 sec!")
count = 0
while(1):
    if timer.elapsed(0.5):    # 1 sec elapsed
        count += 0.5
        timer.restart()
        print(count)
    if count >= 3:
        print("Ready!")
        break