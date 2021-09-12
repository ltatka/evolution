# -*- coding: utf-8 -*-
"""
Created on Sat May  1 22:11:57 2021

@author: hsauro
"""

import os, sys, getopt 
import time
from datetime import date
from datetime import datetime
import multiprocessing

numberOfRuns = 10 # default

def runEvolution():
    os.system('python evolve.py' + ' -g 500')



argv = sys.argv[1:]
options, args = getopt.getopt(argv, 'r:', [])
for opt, arg in options: 
    if opt in ('-r', ''):
       numberOfRuns = int (arg)
       
print ("Batch set up for " + str (numberOfRuns) + " runs")

today = date.today()
now = datetime.now()

print ("Run Started on: ", today.strftime("%b-%d-%Y"))
print ("at time: ", now.strftime("%H:%M:%S"), '\n')


start = time.time()

processes = []
for i in range(numberOfRuns):
    p = multiprocessing.Process(target=runEvolution)
    processes.append(p)
    p.start()
for process in processes:
    process.join()


print ("Time taken to do batch runs = ", time.time() - start)
# for i in range (numberOfRuns):
#     print ("-----------------------------------------------------")
#     print (" --- BATCH NUMBER --- " + str (i+1) + ' out of ' + str (numberOfRuns) + ' total.')
#     print ("-----------------------------------------------------")
#     os.system('python evolve.py' + ' -g 500')
#
# print ("Time taken to do batch runs = ", time.time() - start)
