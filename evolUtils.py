# -*- coding: utf-8 -*-
"""
Created on Fri Apr 30 15:55:44 2021

@author: LTatka
"""

from uModel import TModel_

from uModel import TModel
from uModel import TReaction
from numba import jit

import tellurium as te
import roadrunner
import modTeUtils as tu
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
from configLoader import loadConfiguration
from uLoadCvode import TCvode
import uLoadCvode



class PostInitCaller(type):
    def __call__(cls, *args, **kwargs):
        obj = type.__call__(cls, *args, **kwargs)
        obj.post_init()
        return obj

class EvolveSettings(object, metaclass=PostInitCaller):


    def __init__(self, configuration=None, probabilities=None):
        # If no configuration is given, load the default
        if not configuration:
            self.currentConfig = loadConfiguration()
        else:
            self.currentConfig = loadConfiguration(configFile=configuration)
        self.builder = tu # Evolver's instance of teUtils for preserving settings
        self.objectiveData = readObjectiveFunction()
        self.makeTracker()
        self.setReactionProbabilities([0.1, 0.4, 0.4, 0.1])  # Set default reaction probabilites


    def post_init(self):
        self.topElite = math.trunc(self.currentConfig['percentageCloned'] * self.currentConfig['sizeOfPopulation'])
        self.remainder = self.currentConfig["sizeOfPopulation"] - \
                         math.trunc(self.currentConfig['percentageCloned'] * self.currentConfig['sizeOfPopulation'])
        self.seed = self.currentConfig['seed']
        if self.seed == -1:
            self.seed = random.randrange(sys.maxsize)
        random.seed(self.seed)
        if self.currentConfig["massConserved"] == "True":
            self.massConserved = True
            self.builder.Settings.allowMassViolatingReactions = False
        else:
            self.massConserved = False
            self.builder.Settings.allowMassViolatingReactions = True
        if self.currentConfig["allowAutocatalysis"] == "True":
            self.autocatalysis = True
        else:
            self.autocatalysis = False
        self.builder.Settings.rateConstantScale = self.currentConfig['rateConstantScale']


    def setRandomSeed(self, seed):
        self.seed = seed
        random.seed(seed)


    def loadNewConfig(self, configFile):
        self.currentConfig = loadConfiguration(configFile=configFile)


    def setMaxGeneration(self, maxNumber):
        self.currentConfig["maxGenerations"] = maxNumber


    def setReactionProbabilities(self, probabilityList):
        if sum(probabilityList) != 1.0:
            raise ValueError('Probabilities do not add up to 1!')
        self.builder.Settings.ReactionProbabilities.UniUni = probabilityList[0]
        self.builder.Settings.ReactionProbabilities.UniBi = probabilityList[1]
        self.builder.Settings.ReactionProbabilities.BiUni = probabilityList[2]
        self.builder.Settings.ReactionProbabilities.BiBI = probabilityList[3]


    def makeTracker(self):
        self.tracker = {"fitnessArray": [],
                        "savedPopulations": [],
                        "startTime": time.time(),
                        "nAddReactions": 0,
                        "nDeleteReactions": 0,
                        "nParameterChanges": 0,
                        "timetaken": 0}


    def writeOutConfigForModel(self, f):
        f.write("# " + json.dumps(self.currentConfig))
        f.write('\n')


    def printCurrentConfig(self):
        for item in self.currentConfig:
            if item == 'seed':
                print(f'seed: {self.seed}')
            elif item == 'initialConditions':
                print(f'initialConditions: {self.currentConfig["initialConditions"][:self.currentConfig["numSpecies"]]}')
            else:
                print(f"{item}: {self.currentConfig[item]}")
        print(f'Reaction probabilities: \n \
        UniUni: {self.builder.Settings.ReactionProbabilities.UniUni}\n \
        UniBi: {self.builder.Settings.ReactionProbabilities.UniBi}\n \
        BiUni: {self.builder.Settings.ReactionProbabilities.BiUni}\n \
        BiBi: {self.builder.Settings.ReactionProbabilities.BiBI}')


    def printSummary(self, population):
        print("Final fitness = ", population[0].fitness)
        self.tracker["timeTaken"] = time.time() - self.tracker["startTime"]
        print("Time taken in seconds = ", math.trunc(self.tracker["timeTaken"] * 100) / 100)
        print("Time taken (hrs:min:sec): ", time.strftime("%H:%M:%S", time.gmtime(self.tracker["timeTaken"])))
        print("Seed = ", self.seed)
        print('Number of added reactions = ', self.tracker["nAddReaction"])
        print('Number of deleted reactions = ', self.tracker["nDeleteReactions"])
        print('Number of parameter changes = ', self.tracker["nParameterChanges"])


ev = EvolveSettings()



#_________________________________________________________________________________
#    FUNCTIONS FOR EVOLVING INDIVIDUALS
#_________________________________________________________________________________

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




# OLD VERSION
def addReaction(model):
    ev.tracker["nAddReactions"] += 1
    floats = range(0, model.numFloats)
    rt = random.randint(0, 3)  # Reaction type
    reaction = TReaction()
    reaction.reactionType = rt
    if rt == tu.TReactionType.UniUni:
        r1 = [random.choice(floats)]
        p1 = [random.choice(floats)]
        # Disallow S1 -> S1 type of reaction
        # while p1[0] == r1[0]:
        #     p1 = [random.randint(0, nSpecies - 1)]
        reaction.reactant1 = r1[0]
        reaction.product1 = p1[0]

    elif rt == tu.TReactionType.BiUni:
        r1 = [random.choice(floats), random.choice(floats)]
        p1 = [random.choice(floats)]
        reaction.reactant1 = r1[0]
        reaction.reactant2 = r1[1]
        reaction.product1 = p1[0]

    elif rt == tu.TReactionType.UniBi:
        r1 = [random.choice(floats)]
        p1 = [random.choice(floats), random.choice(floats)]
        reaction.reactant1 = r1[0]
        reaction.product1 = p1[0]
        reaction.product2 = p1[1]

    elif rt == tu.TReactionType.BiBi:
        r1 = [random.choice(floats), random.choice(floats)]
        p1 = [random.choice(floats), random.choice(floats)]
        reaction.reactant1 = r1[0]
        reaction.reactant2 = r1[1]
        reaction.product1 = p1[0]
        reaction.product2 = p1[1]

    reaction.rateConstant = random.random() * ev.currentConfig['rateConstantScale']
    model.reactions.append(reaction)
    return model


def deleteReaction(model):
    ev.tracker["nDeleteReactions"] += 1
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
    ev.tracker["nParameterChanges"] += 1
    # pick a random reaction
    nReactions = len(model.reactions)
    nth = random.randint(0, nReactions - 1)  # pick a reaction
    rateConstant = model.reactions[nth].rateConstant
    x = ev.currentConfig['percentageChangeInParameter'] * rateConstant

    change = random.uniform(-x, x)
    return nth, change


def computeFitness(population, objectiveData):
    for index, model in enumerate(population):
        # if keyboard.is_pressed("q"):
        #   print ("keyboard break")
        #   sys.exit()
        evalFitness.computeFitnessOfIndividual(index, model, objectiveData)


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


# _________________________________________________________________________________
#    METHODS FOR MANAGING POPULATIONS
# _________________________________________________________________________________


def makeModel(nSpecies, nReactions):
    # Using the settings builder because it has the reaction probabilities we want
    model = ev.builder.getRandomNetworkDataStructure(nSpecies, nReactions)
    nFloats = len(model[0])
    nBoundary = len(model[1])
    model.insert(0, nFloats)
    model.insert(1, nBoundary)
    # Append boundary to float list
    model[2] = list(np.append(model[2], model[3]))
    model.insert(4, ev.currentConfig["initialConditions"][:nFloats + nBoundary])
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
        if reaction.reactionType == tu.TReactionType.BiUni or reaction.reactionType == tu.TReactionType.BiBi:
            reaction.reactant2 = r[1][1]

        reaction.product1 = r[2][0]
        if reaction.reactionType == tu.TReactionType.UniBi or reaction.reactionType == tu.TReactionType.BiBi:
            reaction.product2 = r[2][1]

        reaction.rateConstant = r[3]
        amodel.reactions.append(reaction)
        amodel.initialConditions = np.zeros(model[TModel_.nFloats] + model[TModel_.nBoundary])
        for index, ic in enumerate(model[TModel_.initialCond]):
            amodel.initialConditions[index] = ic
        amodel.fitness = 0

    return amodel

def makePopulation():
    population = []
    for i in range(ev.currentConfig['sizeOfPopulation']):
        amodel = makeModel(ev.currentConfig['numSpecies'], ev.currentConfig['numReactions'])
        population.append(amodel)
    return population

def tournamentSelect(population):
    selectedPopulation = []
    for i in range(ev.remainder):
        # pick two models at random, then pick the best and mutate it
        r1 = random.randint(1, ev.currentConfig["sizeOfPopulation"] - 1)
        r2 = random.randint(1, ev.currentConfig["sizeOfPopulation"] - 1)

        if population[r1].fitness < population[r2].fitness:
            model = uModel.clone(population[r1])
        else:
            model = uModel.clone(population[r2])
        if random.random() > ev.currentConfig['probabilityMutateRateConstant']:
            mutateReaction(model)
        else:
            n, change = mutateRateConstant(model)
            model.reactions[n].rateConstant += change
        selectedPopulation.append(model)
    return selectedPopulation


def clonePopulation(population):
    p = []
    for pop in population:
        p.append(uModel.clone(pop))
    return p


def getNextGen(population):
    computeFitness(population)
    # Sort the population according to fitness
    population.sort(key=lambda x: x.fitness)
    newPopulation = []
    ev.tracker["fitnessArray"].append(population[0].fitness)
    newPopulation.append(uModel.clone(population[0]))
    for i in range(ev.topElite - 1):
        newPopulation.append(uModel.clone(population[i]))
    selections = tournamentSelect(population)
    newPopulation = newPopulation + selections
    return newPopulation

def printProgress(genNum, population):
    if genNum % ev.currentConfig['frequencyOfOutput'] == 0:
        print(flush=True)
        print("gen[" + str(genNum) + "] fitness=",
              "{:.4f}".format(population[0].fitness),
              end='', flush=True)
    else:
        print('.', end='', flush=True)

def evolve():
    ev.printCurrentConfig()
    ev.makeTracker()
    population = makePopulation()
    for i in range(ev.currentConfig['maxGenerations']):
        population = getNextGen(population)
        savePopulation(population)
        printProgress(i, population)
        if population[0].fitness <= ev.currentConfig['threshold']:
            saveFileName = os.path.join(os.getcwd(), f"{str(ev.seed)}")
            saveRun(saveFileName, population)
            print("\n\nSUCCESS!\n")
            break
    if population[0].fitness > ev.currentConfig['threshold']:
        print("\n\nFAIL\n")
        saveFileName = os.path.join(os.getcwd(), f"FAIL_{str(ev.seed)}")
        saveRun(saveFileName, population)
    ev.printSummary(population)

def saveRun(saveFileName, population):
    if ev.currentConfig["toZip"] == "False":
        saveFileName = saveFileName + ".ant"
        astr = convertToAntimony2(population[0])
        with open(saveFileName, "w") as f:
            f.write(astr)
            f.close()
    else:
        saveFileName = saveFileName + ".zip"
        zf = zipfile.ZipFile(saveFileName, mode="w", compression=zipfile.ZIP_DEFLATED)
        try:
            json_string = json.dumps(ev.tracker["fitnessArray"])
            zf.writestr("fitnessList.txt", json_string)

            astr = convertToAntimony2(population[0])
            zf.writestr("best_antimony.ant", astr)
            zf.writestr("seed_" + str(ev.seed) + ".txt", str(ev.seed))
            zf.writestr("config.txt", json.dumps(ev.currentConfig) + '\n')

            today = date.today()
            now = datetime.now()
            summaryStr = 'Date:' + today.strftime("%b-%d-%Y") + '\n'

            summaryStr += 'Time:' + now.strftime("%H:%M:%S") + '\n'
            ev.tracker["timeTaken"] = time.time() - ev.tracker["startTime"]
            summaryStr += 'Time taken in seconds:' + str(math.trunc(ev.tracker["timetaken"] * 100) / 100) + "\n"
            summaryStr += 'Time taken (hrs:min:sec):' + str(
                time.strftime("%H:%M:%S", time.gmtime(ev.tracker["timetaken"]))) + "\n"
            summaryStr += '#Seed=' + str(ev.seed) + '\n'
            summaryStr += '#Final_number_of_generations=' + str(len(ev.tracker["savedPopulations"])) + '\n'
            summaryStr += '#Size_of_population=' + str(ev.currentConfig["sizeOfPopulation"]) + '\n'
            summaryStr += '#Number_of_added_reactions=' + str(ev.tracker["nAddReaction"]) + '\n'
            summaryStr += '#Number_of_deleted_reactions=' + str(ev.tracker["nDeleteReactions"]) + '\n'
            summaryStr += '#Number_of_parameter_changes=' + str(ev.tracker["nParameterChanges"]) + '\n'
            summaryStr += '#Final_fitness=' + str(population[0].fitness) + '\n'
            zf.writestr('summary.txt', summaryStr)

            for index, pop in enumerate(ev.tracker["savedPopulations"]):
                for j in range(len(pop)):
                    fileName = "populations/generation_" + str(index) + '/individual_' + str(j) + '.txt'
                    popSummary = '# Fitness = ' + str(pop[j].fitness) + '\n'
                    popSummary += convertToAntimony2(pop[j]);
                    zf.writestr(fileName, popSummary)
        finally:
            zf.close()


def savePopulation(gen, population):
    p = clonePopulation(population)
    ev.tracker["savedPopulations"].append(p)


# def saveRun(seed, saveFileName):
#     global timetaken
#     zf = zipfile.ZipFile(saveFileName, mode="w", compression=zipfile.ZIP_DEFLATED)
#     try:
#         json_string = json.dumps(ev.tracker["fitnessArray"])
#         zf.writestr("fitnessList.txt", json_string)
#
#         astr = evolUtils.convertToAntimony2(newPopulation[0]);
#         zf.writestr("best_antimony.ant", astr)
#         zf.writestr("seed_" + str(seed) + ".txt", str(seed))
#
#         zf.writestr("config.txt", json.dumps(ev.currentConfig) + '\n')
#
#         today = date.today()
#         now = datetime.now()
#         summaryStr = 'Date:' + today.strftime("%b-%d-%Y") + '\n'
#         summaryStr += 'Time:' + now.strftime("%H:%M:%S") + '\n'
#         summaryStr += 'Time taken in seconds:' + str(math.trunc(timetaken * 100) / 100) + "\n"
#         summaryStr += 'Time taken (hrs:min:sec):' + str(time.strftime("%H:%M:%S", time.gmtime(timetaken))) + "\n"
#         summaryStr += '#Seed=' + str(seed) + '\n'
#         summaryStr += '#Final_number_of_generations=' + str(len(savedPopulations)) + '\n'
#         summaryStr += '#Size_of_population=' + str(sizeOfPopulation) + '\n'
#         summaryStr += '#Number_of_added_reactions=' + str(nAddReaction) + '\n'
#         summaryStr += '#Number_of_deleted_reactions=' + str(nDeleteReactions) + '\n'
#         summaryStr += '#Number_of_parameter_changes=' + str(nParameterChanges) + '\n'
#         summaryStr += '#Final_fitness=' + str(newPopulation[0].fitness) + '\n'
#         zf.writestr('summary.txt', summaryStr)
#
#         for index, pop in enumerate(savedPopulations):
#             for j in range(len(pop)):
#                 fileName = "populations/generation_" + str(index) + '/individual_' + str(j) + '.txt'
#                 popSummary = '# Fitness = ' + str(pop[j].fitness) + '\n'
#                 popSummary += evolUtils.convertToAntimony2(pop[j]);
#                 zf.writestr(fileName, popSummary)
#     finally:
#         zf.close()
#     pass


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
    plt.plot(ev.tracker["fitnessArray"])
    plt.show()


def plotFitnesssFromFile(fileName):
    data = np.loadtxt(fileName, delimiter=',')
    plt.plot(data[:, 0], data[:, 1])
    plt.show()


def displayFitness(population):
    for p in population:
        print(p.fitness)



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
        if reaction.reactionType == tu.TReactionType.UniUni:
           S1 = 'S' + str (reaction.reactant1)
           S2 = 'S' + str (reaction.product1)
           astr += S1 + ' -> ' + S2
           astr += '; k' + str(i) + '*' + S1 + '\n'
        if reaction.reactionType == tu.TReactionType.BiUni:
           S1 = 'S' + str (reaction.reactant1)
           S2 = 'S' + str (reaction.reactant2)
           S3 = 'S' + str (reaction.product1)
           astr += S1 + ' + ' + S2 + ' -> ' + S3
           astr += '; k' + str(i) + '*' + S1 + '*' + S2 + '\n'
        if reaction.reactionType == tu.TReactionType.UniBi:
           S1 = 'S' + str (reaction.reactant1)
           S2 = 'S' + str (reaction.product1)
           S3 = 'S' + str (reaction.product2)
           astr += S1 + ' -> ' + S2 + '+' + S3
           astr += '; k' + str(i) + '*' + S1 + '\n'
        if reaction.reactionType == tu.TReactionType.BiBi:
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

# ## New Version
# def addReaction(model):
#         nSpecies = ev.currentConfig['numSpecies']
#         ev.tracker["nAddReactions"] += 1
#         rt = random.randint(0, 3)  # Reaction type
#         reaction = TReaction()
#         reaction.reactionType = rt
#         reaction.rateConstant = random.random() * ev.currentConfig['rateConstantScale']
#
#         if rt == tu.TReactionType.UniUni:
#             # UniUni
#             reactant = random.randint(0, nSpecies - 1)
#             product = random.randint(0, nSpecies - 1)
#             # Disallow S1 -> S1 type of reaction
#             while product == reactant:
#                 product = random.randint(0, nSpecies - 1)
#             reaction.reactant1 = reactant
#             reaction.product1 = product
#         #
#         #
#         # elif rt == tu.TReactionType.BiUni:
#         #     # BiUni
#         #     # Pick two reactants
#         #     reactant1 = random.randint(0, nSpecies - 1)
#         #     reactant2 = random.randint(0, nSpecies - 1)
#         #     if tu.Settings.allowMassViolatingReactions:
#         #         product = random.randint(0, nSpecies - 1)
#         #     else:
#         #         # pick a product but only products that don't include the reactants
#         #         species = range(nSpecies)
#         #         # Remove reactant1 and 2 from the species list
#         #         species = np.delete(species, [reactant1, reactant2], axis=0)
#         #         if len(species) == 0:
#         #             raise Exception("Unable to pick a species why maintaining mass conservation")
#         #         # Then pick a product from the reactants that are left
#         #         product = species[random.randint(0, len(species) - 1)]
#         #     reaction.reactant1 = reactant1
#         #     reaction.reactant2 = reactant2
#         #     reaction.product1 = product
#         #
#         # elif rt == tu.TReactionType.UniBi:
#         #     # UniBi
#         #     reactant1 = random.randint(0, nSpecies - 1)
#         #     if ev.autocatalysis or tu.Settings.allowMassViolatingReactions:
#         #         product1 = random.randint(0, nSpecies - 1)
#         #         product2 = random.randint(0, nSpecies - 1)
#         #     # If we don't want autocatalysis, then UniBi reactions must be mass conserved.
#         #     else:
#         #         # pick a product but only products that don't include the reactant
#         #         species = range(nSpecies)
#         #         # Remove reactant1 from the species list
#         #         species = np.delete(species, [reactant1], axis=0)
#         #         if len(species) == 0:
#         #             raise Exception("Unable to pick a species why maintaining mass conservation")
#         #
#         #         # Then pick a product from the reactants that are left
#         #         product1 = species[random.randint(0, len(species) - 1)]
#         #         product2 = species[random.randint(0, len(species) - 1)]
#         #     reaction.reactant1 = reactant1
#         #     reaction.product1 = product1
#         #     reaction.product2 = product2
#         #
#         # elif rt == tu.TReactionType.BiBi:
#         #     # BiBi
#         #     reactant1 = random.randint(0, nSpecies - 1)
#         #     reactant2 = random.randint(0, nSpecies - 1)
#         #     if not ev.autocatalysis:
#         #         # If we don't want autocatalysis, then neither of the products can be the same as the reactant
#         #         species = range(nSpecies)
#         #         # Remove reactant1 and 2 from the species list
#         #         species = np.delete(species, [reactant1, reactant2], axis=0)
#         #         if len(species) == 0:
#         #             raise Exception("Unable to pick a species why mainting mass conservation")
#         #             # Then pick a product from the reactants that are left
#         #         product1 = species[random.randint(0, len(species) - 1)]
#         #         product2 = species[random.randint(0, len(species) - 1)]
#         #     else:
#         #         # if we allow autocatalyis, then we can pick any products, the only risk being that they are the same
#         #         # as the reactants so the reaction is irrelevant
#         #         product1 = random.randint(0, nSpecies - 1)
#         #         product2 = random.randint(0, nSpecies - 1)
#         #     reaction.reactant1 = reactant1
#         #     reaction.reactant2 = reactant2
#         #     reaction.product1 = product1
#         #     reaction.product2 = product2
#         model.reactions.append(reaction)
#         return model
