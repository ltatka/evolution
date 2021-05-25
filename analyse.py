# -*- coding: utf-8 -*-
"""
Created on Mon May  3 22:17:28 2021

@author: hsauro
"""

import tellurium as te
import roadrunner
import sys, os, getopt
import matplotlib.pyplot as plt

def plotFitnesssFromFile (fileName):
    data = np.loadtxt(fileName, delimiter=',')
    plt.plot(data[:,0], data[:,1])
    plt.show()
    
    
fileName = ''
argv = sys.argv[1:]
print (argv)
options, args = getopt.getopt(argv, 'f:', [])
for opt, arg in options: 
    if opt in ('-f', ''):
       fileName = arg
       print (fileName)
       
if os.path.exists(fileName):
   items = fileName.split('_')
   print (items)
   if items[0] == 'model':
      items = items[1].split('.')
      print ("Seed code = ", items[0])
else:
    print ('Specify a model file using -f')
   
plt.plot ([1,4,5,6], [7,5,4,3])
plt.show()