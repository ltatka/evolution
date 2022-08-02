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
from commonTypes import TModel_
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

tu.buildNetworks.Settings.ReactionProbabilities.UniUni = 0.1
tu.buildNetworks.Settings.ReactionProbabilities.UniBi = 0.4
tu.buildNetworks.Settings.ReactionProbabilities.BiUni = 0.4
tu.buildNetworks.Settings.ReactionProbabilities.BiBi = 0.1


initialConditions = [1, 5, 9, 3, 10, 3, 7, 1, 6, 3, 10, 11, 4, 6, 2, 7, 1, 9, 5, 7, 2, 4, 5, 10, 4, 1, 6, 7, 3, 2, 7, 8]


def makeModel(nSpecies, nReactions):

    model = tu.buildNetworks.getRandomNetworkDataStructure(nSpecies, nReactions)
    nFloats = len(model[0])
    nBoundary = len(model[1])
    model.insert(0, nFloats)
    model.insert(1, nBoundary)
    # Append boundary to float list
    model[2] = list(np.append(model[2], model[3]))
    model.insert(4, initialConditions[:nFloats + nBoundary])
    model.append(0.0)  # Append fitness variable
    #Initiate the TModel class:
    amodel = uModel.TModel()
    amodel.numFloats = nFloats
    amodel.numBoundary = nBoundary
    amodel.cvode = TCvode(uLoadCvode.CV_BDF)

    # Go through the reacions in the weird teUtil model form that we refactored earlier
    for r in model[TModel_.reactionList][1:]: # again skip the first because it's just the number of reactions
        reaction = uModel.TReaction()
        reaction.reactionType = r[0]

        reaction.reactant1 = r[1][0] # Put the species number as the reacant (which is now a float for some reason)
        # If there's a second reactant, put that in there too.
        if reaction.reactionType == tu.buildNetworks.TReactionType.BiUni or reaction.reactionType == tu.buildNetworks.TReactionType.BiBi:
            reaction.reactant2 = r[1][1]
        # Same for product
        reaction.product1 = r[2][0]
        if reaction.reactionType == tu.buildNetworks.TReactionType.UniBi or reaction.reactionType == tu.buildNetworks.TReactionType.BiBi:
            reaction.product2 = r[2][1]
        #Add rate constant
        reaction.rateConstant = r[3]
        amodel.reactions.append(reaction)
        amodel.initialConditions = np.zeros(model[TModel_.nFloats] + model[TModel_.nBoundary])
        for index, ic in enumerate(model[TModel_.initialCond]):
            amodel.initialConditions[index] = ic
        amodel.fitness = 0

    return amodel



if __name__ == "__main__":
    # ---------------------------------------------------------------------

    defaultConfig = {"maxGenerations": 1,
                     "massConserved": False, # Not sure that this is actually working
                     "toZip": False,
                     "sizeOfPopulation": 100,
                     "numSpecies": 5,
                     "numReactions": 15,
                     "rateConstantScale": 50,
                     "probabilityMutateRateConstant": 0.7,  # 0.9 much worse
                     "percentageCloned": 0.1,
                     "percentageChangeInParameter": 0.15,
                     "seed": -1,  # means no specific seed
                     "threshold": 10.5,  # a fitness below this we stop
                     "frequencyOfOutput": 10,
                     "multi": {"item 1": "item 2"},
                     "key2": "value2"}


    seed = -1
    maxGenerations = -1
    newConfigFile = ''

    if not os.path.exists('defaultConfig.json'):
        print("not os")
        with open('defaultConfig.json', 'w') as f:
            json.dump(defaultConfig, f)


    currentConfig = defaultConfig



    if seed == -1:
        if defaultConfig['seed'] == -1:
            seed = random.randrange(sys.maxsize)
        else:
            seed = currentConfig['seed']
    print('seed = ', seed)
    # seed = 456789
    random.seed(seed)

    tu.buildNetworks.Settings.allowMassViolatingReactions = not currentConfig['massConserved']
    tu.buildNetworks.Settings.rateConstantScale = currentConfig['rateConstantScale']

    # Create initial random population
    sizeOfPopulation = currentConfig['sizeOfPopulation']
    population = []
    save_dir = '/home/hellsbells/Desktop/Random3Node/'
    if not os.path.exists(save_dir) or not os.path.isdir(save_dir):
        os.mkdir(save_dir)
    os.chdir(save_dir)
    for i in range(sizeOfPopulation):
        amodel = makeModel(currentConfig['numSpecies'], currentConfig['numReactions'])
        saveFileName = 'RANDOM_' + str(i) + '.ant'
        astr = evolUtils.convertToAntimony(amodel)
        with open(saveFileName, "w") as f:
            f.write(astr)
            f.close()


