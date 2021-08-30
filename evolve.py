# -*- coding: utf-8 -*-
"""
Created on Tue Apr 27 20:52:33 2021

@author: hsauro
"""

# Wierd issue with macos: https://github.com/ray-project/ray/issues/5250
# importing numba after some other packages causes bug. So we move the numba import
# to top of the execution stack and hope the problem goes away.
#   https://github.com/numba/numba/issues/4256
from numba import jit

import tellurium as te
import roadrunner
from teUtils import teUtils as tu
import numpy as np
import random
import matplotlib.pyplot as plt
import readObjData
import evalFitness
from uModel import TModel_
import copy, sys, os, math, getopt, json, time, zipfile
import evolUtils, uModel
from uModel import TReaction
from pprint import pprint
from datetime import date
from datetime import datetime
# import keyboard

from uLoadCvode import TCvode
import uLoadCvode

# # Expected Output
# timeStart 0.0
# timeEnd 1.25
# numberOfPoints 9
# 5
# 30.0
# 5
# 30.0
# 5
# 30.0
# 5
# 30.0
# 5

nDeleteReactions = 0
nAddReaction = 0
nParameterChanges = 0
timetaken = 0














if __name__ == "__main__":
    # ---------------------------------------------------------------------



    # todo you should use argparse for this in python. Its waaaaay easier and standard practice.
    seed = -1
    maxGenerations = -1
    newConfigFile = ''
    argv = sys.argv[1:]
    options, args = getopt.getopt(argv, 's:g:c:hv', [])
    for opt, arg in options:
        if opt in ('-s', ''):
            seed = int(arg)
        if opt in ('-g', ''):
            maxGenerations = int(arg)
        if opt in ('-c', ''):
            newConfigFile = arg
            if not newConfigFile.endswith('.json'):
                newConfigFile += '.json'
            print(newConfigFile + ' in use')
        if opt in ('-v', ''):
            print("version 1.0")
            sys.exit()
        if opt in ('-h', ''):
            print("Help:")
            print("Set the seed:  -s 54545353")
            print("Set the number of generations to use:  -g 1000")
            sys.exit()

    print("------------------------------")
    print("Press ctrl+q to interupt a run")
    print("------------------------------\n")



    # Create initial random population
    sizeOfPopulation = currentConfig['sizeOfPopulation']
    population = []
    for i in range(sizeOfPopulation):
        amodel = makeModel(currentConfig['numSpecies'], currentConfig['numReactions'])
        population.append(amodel)

    model = population[0]
    topElite = math.trunc(defaultConfig['percentageCloned'] * sizeOfPopulation)

    # Main loop
    fitnessArray = []
    savedPopulations = []
    startTime = time.time()
    for gen in range(0, maxGenerations):

        computeFitness(population)

        # Sort the population according to fitness
        population.sort(key=lambda x: x.fitness)

        # Create the next population
        newPopulation = []
        if gen % currentConfig['frequencyOfOutput'] == 0:
            print(flush=True)
            print("gen[" + str(gen) + "] fitness=",
                  "{:.4f}".format(population[0].fitness),
                  str(len(population[0].reactions)), end='', flush=True)
        else:
            print('.', end='', flush=True)
        # Record the best fitness
        fitnessArray.append(population[0].fitness)

        # Clone in the best individual from the current population
        newPopulation.append(uModel.clone(population[0]))
        # Copy over the top elite of the popoulation
        for i in range(topElite - 1):
            newPopulation.append(uModel.clone(population[i]))

        # For the remainder use tournament selction on pairs of
        # individuals, picking the best and mutating it.
        remainder = sizeOfPopulation - topElite

        for i in range(remainder):

            # pick two models at random, then pick the best and mutate it
            r1 = random.randint(1, sizeOfPopulation - 1)
            r2 = random.randint(1, sizeOfPopulation - 1)

            if population[r1].fitness < population[r2].fitness:
                if random.random() > currentConfig['probabilityMutateRateConstant']:
                    mutateReaction(population[r1])
                else:
                    n, change = mutateRateConstant(population[r1])
                    amodel = uModel.clone(population[r1])
                    amodel.reactions[n].rateConstant += change
                newPopulation.append(amodel)
            else:
                if random.random() > currentConfig['probabilityMutateRateConstant']:
                    mutateReaction(population[r2])
                else:
                    n, change = mutateRateConstant(population[r2])
                    amodel = uModel.clone(population[r2])
                    amodel.reactions[n].rateConstant += change;
                newPopulation.append(amodel)

            # if keyboard.is_pressed("ctrl+q"):
            #   print ("keyboard break")
            #   sys.exit()

        population = newPopulation
        savePopulation(gen, population)

        if population[0].fitness < currentConfig['threshold']:
            break

    print('\n')
    if newPopulation[0].fitness < 100:
        print("Success.......")

        if defaultConfig["toZip"]:
            saveFileName = "Model_" + str(seed) + ".zip"
            print("Saving entire state to --- ", saveFileName)
            saveRun(seed, saveFileName)
        else:
            saveFileName = "Model_" + str(seed) + ".ant"
            print("Saving entire state to --- ", saveFileName)
            astr = evolUtils.convertToAntimony2(newPopulation[0])
            with open(saveFileName, "w") as f:
                f.write(astr)
                f.close()
    else:

        if defaultConfig["toZip"]:
            print("Trial failed.....")
            saveFileName = "FAIL_Model_" + str(seed) + ".zip"
            print("Saving entire state to --- ", saveFileName)
            saveRun(seed, saveFileName)
        else:
            print("Trial failed.....")
            saveFileName = "FAIL_Model_" + str(seed) + ".ant"
            print("Saving entire state to --- ", saveFileName)
            #saveRun(seed, saveFileName)
            astr = evolUtils.convertToAntimony2(newPopulation[0])

            with open(saveFileName, "w") as f:
                f.write(astr)
                f.close()

    timetaken = time.time() - startTime

    print("Final fitness = ", population[0].fitness)
    print("Time taken in seconds = ", math.trunc(timetaken * 100) / 100)
    print("Time taken (hrs:min:sec): ", time.strftime("%H:%M:%S", time.gmtime(timetaken)))
    print("Seed = ", seed)
    print('Number of added reactions = ', nAddReaction)
    print('Number of deleted reactions = ', nDeleteReactions)
    print('Number of parameter changes = ', nParameterChanges)
    # if newPopulation[0].fitness < 100:
    #    astr = evolUtils.convertToAntimony2 (newPopulation[0]);
    #    print (astr)
    #    f = open("model_" + str(seed) + ".txt", "w")
    #    writeOutConfigForModel (f, currentConfig)
    #    f.write ("Time taken in seconds = " + str (math.trunc (timetaken*100)/100))
    #    f.write ("Time taken (hrs:min:sec): " + str (time.strftime("%H:%M:%S", time.gmtime(timetaken))))
    #    f.write ('# Seed = ' + str (seed) + '\n')
    #    f.write ('# Number of added reactions = ' + str(nAddReaction) + '\n')
    #    f.write ('# Number of deleted reactions = ' + str (nDeleteReactions) + '\n')
    #    f.write ('# Number of parameter changes = ' + str (nParameterChanges) + '\n')
    #    f.write ('# Final fitness = ' + str(newPopulation[0].fitness) + '\n')
    #    f.write(astr)
    #    f.close()

    #    # f = open("fitness_" + str(seed) + ".txt", "w")
    #    # for index, fitness in enumerate (fitnessArray):
    #    #     f.write (str (index) + ', ' + str(fitness) + '\n')
    #    # f.close()
    # else:
    #    f = open("fail" + str(seed) + ".txt", "w")
    #    f.write(str(newPopulation[0].fitness))
    #    f.close()
