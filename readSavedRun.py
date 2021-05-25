# -*- coding: utf-8 -*-
"""
Created on Thu May  6 16:05:50 2021

@author: hsauro
"""

import tellurium as te
import roadrunner
import copy, sys, os, math, getopt, json, time, zipfile
import matplotlib.pyplot as plt

# Read a saved run

# zip file handle
zf = 0
numGenerations = 0
numPopulation = 0

def readModel (zf, generation, individual):
    fileName = "populations/generation_" + str(generation) + '/individual_' + str (individual) + '.txt'
    ant = zf.read (fileName).decode ("utf-8")
    return ant
    
def readSavedRun (fileName):
    global zf
    global numPopulation
    global numGenerations
    zf = zipfile.ZipFile (fileName, 'r')
    data = zf.read('summary.txt').decode("utf-8") 
    data = data.splitlines()
    numGenerations = int (data[5].split ('=')[1])
    numPopulation = int (data[6].split ('=')[1])
    print ("Number of Generations = ", numGenerations)
    print ("Size of population in each generation =", numPopulation)

def getBestIndivdials():
       p = []
       for i in range (numGenerations-1):
           p.append (readModel (zf, i, 0))
       return p
   
def plotFitness():
    data = zf.read('fitnessList.txt').decode("utf-8") 
    fitnesslist = json.loads (data)
    plt.figure(figsize=(8,5))
    plt.plot (fitnesslist)
    
def plotPopulationPlots (models):
    n = math.trunc (math.sqrt (len (models)))
    fig, axs = plt.subplots(n,n,figsize=(16,13))
    count = 0
    for i in range (n):
        for j in range (n):
            r = te.loada (models[count])
            m = r.simulate (0, 2, 100)
            axs[i, j].plot(m[:,0], m[:,1:])
            count += 1
    plt.show()
            
try:
    fileName = ''
    argv = sys.argv[1:]
    options, args = getopt.getopt(argv, 'm:', [])
    for opt, arg in options: 
        if opt in ('-m', ''):
           fileName = arg
           
    fileName = 'Model_802344057895124091.zip'
    fileName = 'Model_4150298340504616518.zip'
    
    if fileName == '':
       print ("Specify a saved rule zip file") 
    else:
       readSavedRun (fileName) 
       # plot the best model in each generation
       #p = getBestIndivdials()
       #plotPopulationPlots (p)  
       alist = plotFitness()
finally:
  zf.close()
   

