import sys
import glob
from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.shortcuts import ProgressBar

import tellurium as te
import roadrunner
import copy, sys, os, math, getopt, json, time, zipfile
import matplotlib.pyplot as plt
import matplotlib
import tkinter
matplotlib.use('TkAgg')

# zip file handle
zf = 0
numGenerations = 0
numPopulation = 0

# Returns all the models in a given generation
def getModels (zf, generation):
    models = []
    for i in range (numPopulation):
        fileName = "populations/generation_" + str(generation) + '/individual_' + str (i) + '.txt'
        ant = zf.read (fileName).decode ("utf-8")
        models.append (ant)
    return models
    
def readModel (zf, generation, individual):
    fileName = "populations/generation_" + str(generation) + '/individual_' + str (individual) + '.txt'
    ant = zf.read (fileName).decode ("utf-8")
    return ant


def readSavedRun (fileName):
    global zf
    global numPopulation
    global numGenerations
    try:
      zf = zipfile.ZipFile (fileName, 'r')
    except Exception as msg:
        print ('Error:', msg)
        return False
    data = zf.read('summary.txt').decode("utf-8") 
    data = data.splitlines()
    numGenerations = int (data[5].split ('=')[1])
    numPopulation = int (data[6].split ('=')[1])
    print ("Number of Generations = ", numGenerations)
    print ("Size of population in each generation =", numPopulation)
    return True
  
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
    plt.show()
    
def plotAllFitness():
    if type (zf) == zipfile.ZipFile:
       zf.close()
    plt.figure(figsize=(8,5))
    for fileName in zipFileList:
        print (fileName)
        readSavedRun (fileName)
        data = zf.read('fitnessList.txt').decode("utf-8") 
        fitnesslist = json.loads (data)
        plt.plot (fitnesslist)  
        zf.close()
    plt.show()        

def getBestIndivdials():
       p = []
       for i in range (numGenerations-1):
           p.append (readModel (zf, i, 0))
       return p
       
def plotPopulationPlots (models):
    n = math.trunc (math.sqrt (len (models)))
    fig, axs = plt.subplots(n,n,figsize=(10,8))
    count = -1
    with ProgressBar() as pb:
         for i in pb(range (n)):
           for j in range (n):
              count += 1
              r = te.loada (models[count])
              m = r.simulate (0, 2, 100)
              axs[i, j].plot(m[:,0], m[:,1:])
    plt.setp(plt.gcf().get_axes(), xticks=[], yticks=[]);
    plt.show()

def printOutStats (fileName):
    pass
          
print ("Type quit to exit and help to get help")
print ("Commands: help, run, ant, stats, plotbest, snapshot, count, list, fitness, evolution, allfitness, quit")

zipFileList = glob.glob('Model*.zip')
zipCompleter = WordCompleter(zipFileList, ignore_case=True)
   
dataRead = False   
while 1:
    user_input = prompt('>',
                        history=FileHistory('history.txt'),
                        completer=zipCompleter,
                       )
    if user_input == 'x' or user_input == "quit":
       if type (zf) == zipfile.ZipFile:
          zf.close()
       sys.exit()
    if user_input == 'help':
        print ("count                  Print out how many trials there are in the directory")
        print ("list                   List all trials")
        print ("evolution <trial>      Plot a grid of simulations from the best model per generation")
        print ("run <trial>            Run a simulation of the best model")
        print ("ant <trial>            Print out the best antimony model")
        print ("fitness <trial>        Plot the fitness profile using the best individuals")
        print ("snapshot <gen> <trial> Plot simulations of all models in a given generation")
        print ("allfitness             Plot all fitness profiles")
        print ("stats <trial>          Display various stats for a trial")
        print ("plotbest <number>      Plot the best models form the first <number> of trials (NOT IMPLEMENTED)")
        print ("quit                   Quit the program")
        
    if user_input == 'list':
        print ('\n'.join(zipFileList))
        #print (zipFileList)
              
    if user_input.split(' ')[0] == 'fitness':
       fileName = user_input.split(' ')[1]
       if readSavedRun (fileName):
          plotFitness()
              
    if user_input.split(' ')[0] == 'stats':
       fileName = user_input.split(' ')[1]
       if readSavedRun (fileName):
          printOutStats (fileName)
          
    if user_input.split(' ')[0]  == 'evolution':
       fileName = user_input.split(' ')[1]
       if readSavedRun (fileName):
          p = getBestIndivdials()
          plotPopulationPlots (p)               
          
    if user_input == 'allfitness':
       plotAllFitness ()  
             
    if user_input.split(' ')[0]  == 'run':
       fileName = user_input.split(' ')[1]
       if readSavedRun (fileName):
          ant = readModel (zf, numGenerations-1, 0)
          r = te.loada (ant)
          timeEnd = 20
          m = r.simulate (0, timeEnd, 300)
          nFloats = r.getNumFloatingSpecies()
          plt.figure(figsize=(8,5))
          for i in range (nFloats):
              plt.plot (m[:,0], m[:,i+1])
          plt.show()
          
    if user_input.split(' ')[0] == 'snapshot':
       splits= user_input.split(' ')
       generation = splits[1] 
       if len (splits) > 2:
          fileName = user_input.split(' ')[2]
          if type (zf) == zipfile.ZipFile:
             zf.close()
          readSavedRun (fileName) 
       p = getModels (zf, generation)
       plotPopulationPlots (p)       
        
    if user_input.split(' ')[0]  == 'ant':
       fileName = user_input.split(' ')[1]
       if readSavedRun (fileName):
          print (readModel(zf, numGenerations-1, 0))             

    # Not implemented.
    # if user_input.split(' ')[0]  == 'plotbest':
    #    number = int (user_input.split(' ')[1])
    #    if readSavedRun (fileName):
    #       for i in range (number):
    #           p = getModels (zf, generation)                 
          
    if user_input == 'count':
        print ("Number of models = ", len (zipFileList))
       

    
       
       
    