# -*- coding: utf-8 -*-
"""
Created on Fri Apr 30 15:55:44 2021

@author: hsauro
"""

from uModel import TModel_
import teUtils as tu
from uModel import TModel
from uModel import TReaction
from numba import jit

import tellurium as te
import roadrunner
import teUtils as tu
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
import configLoader
from uLoadCvode import TCvode
import uLoadCvode

nDeleteReactions = 0
nAddReaction = 0
nParameterChanges = 0
timetaken = 0

savedPopulations = []

currentConfig = configLoader.loadConfiguration()

initialConditions = currentConfig["initialConditions"]



def makeTracker():
    tracker = {"fitnessArray": [],
                "savedPopulations": [],
                "startTime": time.time(),
                "nAddReaction": 0,
                "nDeleteReactions": 0,
                "nParameterChanges": 0,
                "timetaken": 0}
    return tracker


def readObjectiveFunction():
    result = readObjData.ObjectiveFunctionData()
    f = open("objectivefunction.txt", "r")
    astr = f.readline()  # Dump the first comment line
    astr = f.readline()
    aList = astr.split()
    result.timeStart = float(aList[1])

    astr = f.readline();
    aList = astr.split();
    result.timeEnd = float(aList[1])

    astr = f.readline()
    aList = astr.split()
    result.numberOfPoints = int(aList[1])

    for i in range(result.numberOfPoints):
        result.outputData.append(float(f.readline()))
    f.close()
    return result

def addReaction(model):
    global nAddReaction
    nAddReaction += 1
    floats = range(0, model.numFloats)  # numFloats = number of floating species
    rt = random.randint(0, 3)  # Reaction type
    reaction = TReaction()
    reaction.reactionType = rt
    if rt == tu.buildNetworks.TReactionType.UNIUNI:
        r1 = [random.choice(floats)]
        p1 = [random.choice(floats)]
        reaction.reactant1 = r1[0]
        reaction.product1 = p1[0]

    if rt == tu.buildNetworks.TReactionType.BIUNI:
        r1 = [random.choice(floats), random.choice(floats)]
        p1 = [random.choice(floats)]
        reaction.reactant1 = r1[0]
        reaction.reactant2 = r1[1]
        reaction.product1 = p1[0]
    if currentConfig["massConserved"] == True:
        count = 0
        while reaction.product1 == reaction.reactant1 or reaction.product1 == reaction.reactant2:
            p1 = [random.choice(floats)]
            reaction.product1 = p1[0]
            count += 1
            if count > 50:  # quit trying after 50 attempts
                return model

    if rt == tu.buildNetworks.TReactionType.UNIBI:
        r1 = [random.choice(floats)]
        p1 = [random.choice(floats), random.choice(floats)]
        reaction.reactant1 = r1[0]
        reaction.product1 = p1[0]
        reaction.product2 = p1[1]
    if currentConfig["massConserved"] == True:
        count += 1
        while reaction.reactant1 == reaction.product1 or reaction.reactant1 == reaction.product2:
            r1 = [random.choice(floats)]
            reaction.reactant1 = r1[0]
            count += 1
            if count > 50:  # quit trying after 50 attempts
                return model

    if rt == tu.buildNetworks.TReactionType.BIBI:
        r1 = [random.choice(floats), random.choice(floats)]
        p1 = [random.choice(floats), random.choice(floats)]
        reaction.reactant1 = r1[0]
        reaction.reactant2 = r1[1]
        reaction.product1 = p1[0]
        reaction.product2 = p1[1]

    reaction.rateConstant = random.random() * currentConfig['rateConstantScale']
    model.reactions.append(reaction)
    return model


def deleteReaction(model):
    global nDeleteReactions
    nDeleteReactions += 1
    nReactions = len(model.reactions)
    if nReactions > 2:
        n = random.randint(1, nReactions - 1)
        del model.reactions[n]


# Either delete or add a new reaction, 50/50 chance
def mutateReaction(model):
    if random.random() > 0.5:
        deleteReaction(model)
    else:
        addReaction(model)


def mutateRateConstant(model):
    global nParameterChanges
    nParameterChanges += 1
    # pick a random reaction
    nReactions = len(model.reactions)
    nth = random.randint(0, nReactions - 1)  # pick a reaction
    rateConstant = model.reactions[nth].rateConstant
    x = currentConfig['percentageChangeInParameter'] * rateConstant

    change = random.uniform(-x, x)
    return nth, change


def computeFitness(population, objectiveData):
    for index, model in enumerate(population):
        # if keyboard.is_pressed("q"):
        #   print ("keyboard break")
        #   sys.exit()
        evalFitness.computeFitnessOfIndividual(index, model, objectiveData)


def testSimulation(model, timeEnd, numberOfPoints):
    t, y = evalFitness.runSimulation(model, timeEnd, numberOfPoints)
    plt.plot(t, y)
    plt.show()


def refactorMmodel(model):
    find = model[TModel_.fullSpeciesList]
    space = model[TModel_.reactionList]
    for i, rxn in enumerate(space):
        if i == 0:
            continue
        else:
            for ii, species in enumerate(rxn):
                if (ii > 0 and ii < 3):
                    for x in range(len(species)):
                        species[x] = find.index(species[x])  # essentially you are asking what
                        # the number should be and change it
    return ([model[0], model[1], find, model[4], False, 0])





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

    # model = refactor(model)

    amodel = uModel.TModel()
    amodel.numFloats = nFloats
    amodel.numBoundary = nBoundary
    amodel.cvode = TCvode(uLoadCvode.CV_BDF)
    for r in model[TModel_.reactionList][1:]:
        reaction = uModel.TReaction()
        reaction.reactionType = r[0]

        reaction.reactant1 = r[1][0]
        if reaction.reactionType == tu.buildNetworks.TReactionType.BIUNI or reaction.reactionType == tu.buildNetworks.TReactionType.BIBI:
            reaction.reactant2 = r[1][1]

        reaction.product1 = r[2][0]
        if reaction.reactionType == tu.buildNetworks.TReactionType.UNIBI or reaction.reactionType == tu.buildNetworks.TReactionType.BIBI:
            reaction.product2 = r[2][1]

        reaction.rateConstant = r[3]
        amodel.reactions.append(reaction)
        amodel.initialConditions = np.zeros(model[TModel_.nFloats] + model[TModel_.nBoundary])
        for index, ic in enumerate(model[TModel_.initialCond]):
            amodel.initialConditions[index] = ic
        amodel.fitness = 0

    return amodel


def clonePopulation(population):
    p = []
    for pop in population:
        p.append(uModel.clone(pop))
    return p


def savePopulation(gen, population):
    p = clonePopulation(population)
    savedPopulations.append(p)


def saveRun(seed, saveFileName):
    global timetaken
    zf = zipfile.ZipFile(saveFileName, mode="w", compression=zipfile.ZIP_DEFLATED)
    try:
        json_string = json.dumps(fitnessArray)
        zf.writestr("fitnessList.txt", json_string)

        astr = evolUtils.convertToAntimony2(newPopulation[0]);
        zf.writestr("best_antimony.ant", astr)
        zf.writestr("seed_" + str(seed) + ".txt", str(seed))

        zf.writestr("config.txt", json.dumps(currentConfig) + '\n')

        today = date.today()
        now = datetime.now()
        summaryStr = 'Date:' + today.strftime("%b-%d-%Y") + '\n'
        summaryStr += 'Time:' + now.strftime("%H:%M:%S") + '\n'
        summaryStr += 'Time taken in seconds:' + str(math.trunc(timetaken * 100) / 100) + "\n"
        summaryStr += 'Time taken (hrs:min:sec):' + str(time.strftime("%H:%M:%S", time.gmtime(timetaken))) + "\n"
        summaryStr += '#Seed=' + str(seed) + '\n'
        summaryStr += '#Final_number_of_generations=' + str(len(savedPopulations)) + '\n'
        summaryStr += '#Size_of_population=' + str(sizeOfPopulation) + '\n'
        summaryStr += '#Number_of_added_reactions=' + str(nAddReaction) + '\n'
        summaryStr += '#Number_of_deleted_reactions=' + str(nDeleteReactions) + '\n'
        summaryStr += '#Number_of_parameter_changes=' + str(nParameterChanges) + '\n'
        summaryStr += '#Final_fitness=' + str(newPopulation[0].fitness) + '\n'
        zf.writestr('summary.txt', summaryStr)

        for index, pop in enumerate(savedPopulations):
            for j in range(len(pop)):
                fileName = "populations/generation_" + str(index) + '/individual_' + str(j) + '.txt'
                popSummary = '# Fitness = ' + str(pop[j].fitness) + '\n'
                popSummary += evolUtils.convertToAntimony2(pop[j]);
                zf.writestr(fileName, popSummary)
    finally:
        zf.close()
    pass


def plotFitnessPopulationHist(population):
    data = []
    for model in population:
        data.append(model.fitness)
    plt.hist(data)
    plt.show()


def plotFitnessOfIndividuals(population):
    data = []
    for model in population:
        data.append(model.fitness)
    plt.plot(data)
    plt.show()


def plotPopulationPlots(population):
    n = math.trunc(math.sqrt(len(population)))
    fig, axs = plt.subplots(n, n, figsize=(13, 11))
    count = 0
    for i in range(n):
        for j in range(n):
            t, y = evalFitness.runSimulation(population[count], 1.25, 100)
            axs[i, j].plot(t, y)
            count += 1


def plotFitnessArray():
    plt.plot(fitnessArray)
    plt.show()


def plotFitnesssFromFile(fileName):
    data = np.loadtxt(fileName, delimiter=',')
    plt.plot(data[:, 0], data[:, 1])
    plt.show()


def displayFitness(population):
    for p in population:
        print(p.fitness)


def test(tag):
    if gen == 7:
        evalFitness.computeFitnessOfIndividual(newPopulation[0], objectiveData)
        print("fitness at 7 (tag) = ", tag, newPopulation[0].fitness)


def printModel(model):
    print("Model details:")
    print('Num floats:', model.numFloats, 'num boundary:', model.numBoundary, 'Num reactions:', len(model.reactions),
          'fitness:', math.trunc(model.fitness * 100) / 100);
    for r in model.reactions:
        print(r.reactionType, r.reactants, r.products, r.rateConstant)


def writeOutConfigForModel(f, config):
    f.write("# " + json.dumps(config))
    f.write('\n')


def pause():
    programPause = input("Press the <ENTER> key to continue...")

def convertToAntimony (model):
    nFloats = model[TModel_.nFloats]
    nBoundary = model[TModel_.nBoundary]
    boundaryList = model[TModel_.boundaryList]
    fullList = model[TModel_.fullSpeciesList]
    reactions = model[TModel_.reactionList]
    nReactions = model[TModel_.reactionList][0]
    astr = ''
    for f in fullList[:nFloats]:
        astr += 'var S' + str(f) + '\n'
        
    for b in boundaryList:
        astr += 'ext S' + str(b) + '\n'  
        
    for i in range (nReactions):
        reaction = reactions[i+1]
        if reaction[0] == tu.buildNetworks.TReactionType.UNIUNI:
           S1 = 'S' + str (reaction[1][0])
           S2 = 'S' + str (reaction[2][0])
           astr += S1 + ' -> ' + S2
           astr += '; k' + str(i) + '*' + S1 + '\n'
        if reaction[0] == tu.buildNetworks.TReactionType.BIUNI:
           S1 = 'S' + str (reaction[1][0])
           S2 = 'S' + str (reaction[1][1])
           S3 = 'S' + str (reaction[2][0])
           astr += S1 + ' + ' + S2 + ' -> ' + S3
           astr += '; k' + str(i) + '*' + S1 + '*' + S2 + '\n'
        if reaction[0] == tu.buildNetworks.TReactionType.UNIBI:
           S1 = 'S' + str (reaction[1][0])
           S2 = 'S' + str (reaction[2][0])
           S3 = 'S' + str (reaction[2][1])
           astr += S1 + ' -> ' + S2 + '+' + S3
           astr += '; k' + str(i) + '*' + S1 + '\n'
        if reaction[0] == tu.buildNetworks.TReactionType.BIBI:
           S1 = 'S' + str (reaction[1][0])
           S2 = 'S' + str (reaction[1][1])
           S3 = 'S' + str (reaction[2][0])
           S4 = 'S' + str (reaction[2][1])
           astr += S1 + ' + ' + S2 + ' -> ' + S3 + ' + ' + S4
           astr += '; k' + str(i) + '*' + S1 + '*' + S2 + '\n'
           
    for i in range (nReactions):
        reaction = reactions[i+1]
        astr += 'k' + str (i) + ' = ' + str (reaction[3]) + '\n'
    initCond = model[TModel_.initialCond]
    for i in range (nFloats+nBoundary):
        astr += 'S' + str(fullList[i]) + ' = ' + str (initCond[i]) + '\n'
    
    return astr

def convertToAntimony2 (model):
    nFloats = model.numFloats
    nBoundary = model.numBoundary
    reactions = model.reactions
    nReactions = len (reactions)
    astr = ''
    for index in range (nFloats):
        astr += 'var S' + str(index) + '\n'
        
    for b in range (nBoundary):
        astr += 'ext S' + str(b+nFloats) + '\n'  
        
    for i in range (nReactions):
        reaction = reactions[i]
        if reaction.reactionType == tu.buildNetworks.TReactionType.UNIUNI:
           S1 = 'S' + str (reaction.reactant1)
           S2 = 'S' + str (reaction.product1)
           astr += S1 + ' -> ' + S2
           astr += '; k' + str(i) + '*' + S1 + '\n'
        if reaction.reactionType == tu.buildNetworks.TReactionType.BIUNI:
           S1 = 'S' + str (reaction.reactant1)
           S2 = 'S' + str (reaction.reactant2)
           S3 = 'S' + str (reaction.product1)
           astr += S1 + ' + ' + S2 + ' -> ' + S3
           astr += '; k' + str(i) + '*' + S1 + '*' + S2 + '\n'
        if reaction.reactionType == tu.buildNetworks.TReactionType.UNIBI:
           S1 = 'S' + str (reaction.reactant1)
           S2 = 'S' + str (reaction.product1)
           S3 = 'S' + str (reaction.product2)
           astr += S1 + ' -> ' + S2 + '+' + S3
           astr += '; k' + str(i) + '*' + S1 + '\n'
        if reaction.reactionType == tu.buildNetworks.TReactionType.BIBI:
           S1 = 'S' + str (reaction.reactant1)
           S2 = 'S' + str (reaction.reactant2)
           S3 = 'S' + str (reaction.product1)
           S4 = 'S' + str (reaction.product2)
           astr += S1 + ' + ' + S2 + ' -> ' + S3 + ' + ' + S4
           astr += '; k' + str(i) + '*' + S1 + '*' + S2 + '\n'
           
    for i in range (nReactions):
        reaction = reactions[i]
        astr += 'k' + str (i) + ' = ' + str (reaction.rateConstant) + '\n'
    for i in range (nFloats+nBoundary):
        astr += 'S' + str(i) + ' = ' + str (model.initialConditions[i]) + '\n'
    
    return astr
