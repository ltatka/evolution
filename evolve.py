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
import teUtils as tu
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

tu.buildNetworks.Settings.ReactionProbabilities.UniUi = 0.1
tu.buildNetworks.Settings.ReactionProbabilities.UniBi = 0.4
tu.buildNetworks.Settings.ReactionProbabilities.BiUni = 0.4
tu.buildNetworks.Settings.ReactionProbabilities.BiBi = 0.1


# [UNIUNI, [6], [1], 0.4044825260841083]

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


# Not currently used
def mutateReactionOld(model):
    nReactions = model[TModel.reactionList][0]
    floats = model[2][0:model[TModel.nFloats]]
    n = random.randint(1, nReactions)
    # create a new reaction by overwriting the nth reaction
    rt = random.randint(0, 3)
    rxns = model[TModel.reactionList]
    rxn = rxns[n]
    rxn[0] = rt
    if rt == tu.buildNetworks.TReactionType.UNIUNI:
        rxn[1] = [random.choice(floats)]
        rxn[2] = [random.choice(floats)]
    if rt == tu.buildNetworks.TReactionType.BIUNI:
        rxn[1] = [random.choice(floats), random.choice(floats)]
        rxn[2] = [random.choice(floats)]
    if rt == tu.buildNetworks.TReactionType.UNIBI:
        rxn[1] = [random.choice(floats)]
        rxn[2] = [random.choice(floats), random.choice(floats)]
    if rt == tu.buildNetworks.TReactionType.BIBI:
        rxn[1] = [random.choice(floats), random.choice(floats)]
        rxn[2] = [random.choice(floats), random.choice(floats)]

    # rate constant
    rxn[3] = random.random() * 10
    return model


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

    reaction.rateConstant = random.random() * defaultConfig['rateConstantScale']
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


def computeFitness(population):
    for index, model in enumerate(population):
        # if keyboard.is_pressed("q"):
        #   print ("keyboard break")
        #   sys.exit() 
        evalFitness.computeFitnessOfIndividual(index, model, objectiveData)


def testSimulation(model, timeEnd, numberOfPoints):
    t, y = evalFitness.runSimulation(model, timeEnd, numberOfPoints)
    plt.plot(t, y)
    plt.show()


def refactor(model):
    nFloats = model[TModel_.nFloats]
    nBoundary = model[TModel_.nBoundary]
    reactions = model[TModel_.reactionList]
    nReactions = model[TModel_.reactionList][0]

    # Create map
    rm = list(model[TModel_.fullSpeciesList])
    # This is the mapping structure, two lists [[X], [Y]], X maps to Y
    rm = [rm] + [(list(range(len(model[TModel_.fullSpeciesList]))))]

    model[TModel_.fullSpeciesList] = rm[1]
    model[TModel_.boundaryList] = rm[1][nFloats:]

    for r in model[TModel_.reactionList][1:]:  # don't include the number of reactions
        if r[0] == tu.buildNetworks.TReactionType.UNIUNI:
            oldr = r[1][0]
            new = rm[0].index(oldr)
            r[1][0] = new

            oldr = r[2][0]
            new = rm[0].index(oldr)
            r[2][0] = new

        if r[0] == tu.buildNetworks.TReactionType.BIUNI:
            oldr = r[1][0];
            r[1][0] = rm[0].index(oldr);
            oldr = r[1][1];
            r[1][1] = rm[0].index(oldr);

            oldr = r[2][0];
            r[2][0] = rm[0].index(oldr)

        if r[0] == tu.buildNetworks.TReactionType.UNIBI:
            oldr = r[1][0];
            r[1][0] = rm[0].index(oldr);

            oldr = r[2][0];
            r[2][0] = rm[0].index(oldr)
            oldr = r[2][1];
            r[2][1] = rm[0].index(oldr)

        if r[0] == tu.buildNetworks.TReactionType.BIBI:
            oldr = r[1][0];
            r[1][0] = rm[0].index(oldr);
            oldr = r[1][1];
            r[1][1] = rm[0].index(oldr);

            oldr = r[2][0];
            r[2][0] = rm[0].index(oldr)
            oldr = r[2][1];
            r[2][1] = rm[0].index(oldr)

    return model


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

    model = refactor(model)

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


if __name__ == "__main__":
    # ---------------------------------------------------------------------

    ## This is the real default config
    # defaultConfig = {"maxGenerations": 450,
    #           "sizeOfPopulation": 100,
    #           "numSpecies": 10,
    #           "numReactions": 14,
    #           "rateConstantScale": 50,
    #           "probabilityMutateRateConstant": 0.7, # 0.9 much worse
    #           "percentageCloned": 0.1,
    #           "percentageChangeInParameter": 0.15,
    #           "seed": -1,  # means no specific seed
    #           "threshold": 10.5, # a fitness below this we stop
    #           "frequencyOfOutput": 10,
    #           "multi": {"item 1": "item 2"},
    #           "key2": "value2"}

    defaultConfig = {"maxGenerations": 450,
                     "massConserved": True,
                     "toZip": False,
                     "sizeOfPopulation": 40,
                     "numSpecies": 3,
                     "numReactions": 9,
                     "rateConstantScale": 50,
                     "probabilityMutateRateConstant": 0.7,  # 0.9 much worse
                     "percentageCloned": 0.1,
                     "percentageChangeInParameter": 0.15,
                     "seed": -1,  # means no specific seed
                     "threshold": 10.5,  # a fitness below this we stop
                     "frequencyOfOutput": 10,
                     "multi": {"item 1": "item 2"},
                     "key2": "value2"}

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
    if not os.path.exists('defaultConfig.json'):
        print("not os")
        with open('defaultConfig.json', 'w') as f:
            json.dump(defaultConfig, f)

    if newConfigFile == '':
        print("Default configuration in use")
        currentConfig = defaultConfig
    else:
        currentConfig = newConfigFile()

    # revert to default if not set
    if maxGenerations == -1:
        maxGenerations = currentConfig['maxGenerations']

    print("Maximum Generations = ", maxGenerations)

    objectiveData = readObjectiveFunction()
    # seed can be set at the cmd line using -s 1234
    # otherwise check config file, if that is not set
    # draw a random seed
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
