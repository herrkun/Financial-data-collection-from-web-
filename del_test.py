# -*- coding: utf-8 -*-
"""
Created on Sat Apr 27 10:46:51 2019

@author: hit
"""

import threading
import time

counter=1

def hello():
    global counter
    print (counter)
    counter=counter+1

    global timer
    timer = threading.Timer(5.0, hello, [])
    timer.start()

if __name__ == "__main__":
    timer = threading.Timer(5.0, hello, [])
    timer.start()
    timer.join()