import modTeUtils as tu
import numpy as np
import random
import matplotlib.pyplot as plt

import evalFitness
from uModel import TModel_
import sys, os, math, json, time, zipfile
import uModel
from uModel import TReaction
from datetime import date
from datetime import datetime
from configLoader import loadConfiguration
from uLoadCvode import TCvode
import uLoadCvode

class PostInitCaller(type):
    def __call__(cls, *args, **kwargs):
        obj = type.__call__(cls, *args, **kwargs)
        obj.post_init()
        return obj

class Evolver(object, metaclass=PostInitCaller):


    def __init__(self, configuration=None, antimony = None, probabilities = None):
        # If no configuration is given, load the default
        if not configuration:
            self.currentConfig = loadConfiguration()
        else:
            self.currentConfig = loadConfiguration(configFile=configuration)
        self.builder = tu # Evolver's instance of teUtils for preserving settings
        # self.objectiveData = readObjectiveFunction()
        # self.fitnessEvaluator = evalFitness.FitnessEvaluator(configuration)
        self.makeTracker()
        self.setReactionProbabilities([0.1, 0.4, 0.4, 0.1])  # Set default reaction probabilities
        self.antimony = antimony # If we're evolving parameters only, this is the seed

    def post_init(self):
        self.topElite = math.trunc(self.currentConfig['percentageCloned'] * self.currentConfig['sizeOfPopulation'])
        self.remainder = self.currentConfig["sizeOfPopulation"] - self.topElite
        self.seed = self.currentConfig['seed']
        if self.seed == -1:
            self.seed = random.randrange(sys.maxsize)
        random.seed(self.seed)
        if self.currentConfig["massConserved"] == "True":
            self.builder.Settings.allowMassViolatingReactions = False
        else:
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
        # self.fitnessEvaluator = evalFitness.FitnessEvaluator(configFile=configFile)

    def setMaxGeneration(self, maxNumber):
        self.currentConfig["maxGenerations"] = maxNumber
    #_________________________________________________________________________________
    #    METHODS TO SET UP EVOLUTION PARAMETERS
    #_________________________________________________________________________________

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

    def makeTracker(self):
        self.tracker = {"fitnessArray": [],
                        "savedPopulations": [],
                        "startTime": time.time(),
                        "nAddReaction": 0,
                        "nDeleteReactions": 0,
                        "nParameterChanges": 0,
                        "timetaken": 0}

    def setReactionProbabilities(self, probabilityList):
        if sum(probabilityList) != 1.0:
            raise ValueError('Probabilities do not add up to 1!')
        self.builder.Settings.ReactionProbabilities.UniUni = probabilityList[0]
        self.builder.Settings.ReactionProbabilities.UniBi = probabilityList[1]
        self.builder.Settings.ReactionProbabilities.BiUni = probabilityList[2]
        self.builder.Settings.ReactionProbabilities.BiBI = probabilityList[3]

    #_________________________________________________________________________________
    #    METHODS FOR INDIVIDUAL EVOLUTION
    #_________________________________________________________________________________

    def addReaction(self, model):
        nSpecies = self.currentConfig['numSpecies']
        self.tracker["nAddReaction"] += 1
        floats = range(0, model.numFloats)  # numFloats = number of floating species
        rt = random.randint(0, 3)  # Reaction type
        reaction = TReaction()
        reaction.reactionType = rt
        reaction.rateConstant = random.random() * self.currentConfig['rateConstantScale']

        if rt == tu.TReactionType.UniUni:
            # UniUni
            reactant = random.randint(0, nSpecies - 1)
            product = random.randint(0, nSpecies - 1)
            # Disallow S1 -> S1 type of reaction
            while product == reactant:
                product = random.randint(0, nSpecies - 1)
            reaction.reactant1 = reactant
            reaction.product1 = product
            model.reactions.append(reaction)

        elif rt == tu.TReactionType.BiUni:
            # BiUni
            # Pick two reactants
            reactant1 = random.randint(0, nSpecies - 1)
            reactant2 = random.randint(0, nSpecies - 1)
            if tu.Settings.allowMassViolatingReactions:
                product = random.randint(0, nSpecies - 1)
            else:
                # pick a product but only products that don't include the reactants
                species = range(nSpecies)
                # Remove reactant1 and 2 from the species list
                species = np.delete(species, [reactant1, reactant2], axis=0)
                if len(species) == 0:
                    raise Exception("Unable to pick a species why maintaining mass conservation")
                # Then pick a product from the reactants that are left
                product = species[random.randint(0, len(species) - 1)]
            reaction.reactant1 = reactant1
            reaction.reactant2 = reactant2
            reaction.product1 = product

        elif rt == tu.TReactionType.UniBi:
            # UniBi
            reactant1 = random.randint(0, nSpecies - 1)
            if self.autocatalysis or tu.Settings.allowMassViolatingReactions:
                product1 = random.randint(0, nSpecies - 1)
                product2 = random.randint(0, nSpecies - 1)
            # If we don't want autocatalysis, then UniBi reactions must be mass conserved.
            else:
                # pick a product but only products that don't include the reactant
                species = range(nSpecies)
                # Remove reactant1 from the species list
                species = np.delete(species, [reactant1], axis=0)
                if len(species) == 0:
                    raise Exception("Unable to pick a species why maintaining mass conservation")

                # Then pick a product from the reactants that are left
                product1 = species[random.randint(0, len(species) - 1)]
                product2 = species[random.randint(0, len(species) - 1)]
            reaction.reactant1 = reactant1
            reaction.product1 = product1
            reaction.product2 = product2

        elif rt == tu.TReactionType.BiBi:
            # BiBi
            reactant1 = random.randint(0, nSpecies - 1)
            reactant2 = random.randint(0, nSpecies - 1)
            if not self.autocatalysis:
                # If we don't want autocatalysis, then neither of the products can be the same as the reactant
                species = range(nSpecies)
                # Remove reactant1 and 2 from the species list
                species = np.delete(species, [reactant1, reactant2], axis=0)
                if len(species) == 0:
                    raise Exception("Unable to pick a species why mainting mass conservation")
                    # Then pick a product from the reactants that are left
                product1 = species[random.randint(0, len(species) - 1)]
                product2 = species[random.randint(0, len(species) - 1)]
            else:
                # if we allow autocatalyis, then we can pick any products, the only risk being that they are the same
                # as the reactants so the reaction is irrelevant
                product1 = random.randint(0, nSpecies - 1)
                product2 = random.randint(0, nSpecies - 1)
            reaction.reactant1 = reactant1
            reaction.reactant2 = reactant2
            reaction.product1 = product1
            reaction.product2 = product2
        model.reactions.append(reaction)
        return model

    def deleteReaction(self, model):
        self.tracker["nDeleteReactions"] += 1
        nReactions = len(model.reactions)
        if nReactions > 2:
            n = random.randint(1, nReactions - 1)
            del model.reactions[n]

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


    # Either delete or add a new reaction, 50/50 chance
    def mutateReaction(self, model):
        if random.random() > 0.5:
            self.deleteReaction(model)
        else:
            self.addReaction(model)

    def mutateRateConstant(self, model):
        self.tracker["nParameterChanges"] += 1
        # pick a random reaction
        nReactions = len(model.reactions)
        nth = random.randint(0, nReactions - 1)  # pick a reaction
        rateConstant = model.reactions[nth].rateConstant
        x = self.currentConfig['percentageChangeInParameter'] * rateConstant
        change = random.uniform(-x, x)
        return nth, change

    def mutateModel(self, model, pAcceptWorse=0.25):
        newModel = uModel.clone(model)
        if self.antimony is None:
            if random.random() > self.currentConfig['probabilityMutateRateConstant']:
                self.mutateReaction(newModel)
            else:
                n, change = self.mutateRateConstant(newModel)
                newModel.reactions[n].rateConstant += change
        else:  # If there's a seeded model, then only change rate constants
            n, change = self.mutateRateConstant(newModel)
            newModel.reactions[n].rateConstant += change
        # If the new model is better, keep it. Otherwise reject 75% of the time
        evalFitness.computeFitnessOfIndividual(newModel, self.currentConfig['initialConditions'])
        if newModel.fitness < model.fitness or random.random() > 1 - pAcceptWorse:
            return newModel
        else:
            return model


    def computeFitness(self, population):
        for model in population:
            # Fitness is stored in the individual model object
            evalFitness.computeFitnessOfIndividual(model, self.currentConfig['initialConditions'])



    # _________________________________________________________________________________
    #    METHODS FOR MANAGING POPULATIONS
    # _________________________________________________________________________________

    def makePopulation(self):
        population = []
        if self.antimony is None:
            for i in range(self.currentConfig['sizeOfPopulation']):
                amodel = self.makeModel(self.currentConfig['numSpecies'], self.currentConfig['numReactions'])
                population.append(amodel)
        else:
            model = convertToTModel(self.antimony)
            evalFitness.computeFitnessOfIndividual(model, self.currentConfig['initialConditions'])
            population.append(model)
            for i in range(1, self.currentConfig['sizeOfPopulation']):
                nextModel = uModel.clone(model)
                model = self.mutateModel(nextModel, pAcceptWorse=1)
                population.append(nextModel)
        return population

    def makeModel(self, nSpecies, nReactions):
        model = self.builder.getRandomNetworkDataStructure(nSpecies, nReactions, allowAutocatalysis=self.autocatalysis)
        nFloats = len(model[0])
        nBoundary = len(model[1])
        model.insert(0, nFloats)
        model.insert(1, nBoundary)
        # Append boundary to float list
        model[2] = list(np.append(model[2], model[3]))
        model.insert(4, self.currentConfig["initialConditions"][:nFloats + nBoundary])
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

    def getNextGen(self, population):
        # self.computeFitness(population) This is computed in the selection step
        # Sort the population according to fitness
        population.sort(key=lambda x: x.fitness)
        newPopulation = []
        self.tracker["fitnessArray"].append(population[0].fitness)
        newPopulation.append(uModel.clone(population[0]))
        for i in range(self.topElite - 1):
            newPopulation.append(uModel.clone(population[i]))
        selections = self.tournamentSelect(population)
        newPopulation = newPopulation + selections
        return newPopulation

    def tournamentSelect(self, population):
        selectedPopulation = []
        for i in range(self.remainder):
            # pick two models at random, then pick the best and mutate it
            r1 = random.randint(1, self.currentConfig["sizeOfPopulation"] - 1)
            r2 = random.randint(1, self.currentConfig["sizeOfPopulation"] - 1)
            # TODO: Allow worse models to get accepted from time to time?
            if population[r1].fitness < population[r2].fitness:
                model = uModel.clone(population[r1])
            else:
                model = uModel.clone(population[r2])
            model = self.mutateModel(model)
            selectedPopulation.append(model)
        return selectedPopulation

    def clonePopulation(self, population):
        p = []
        for pop in population:
            p.append(uModel.clone(pop))
        return p


    def evolve(self):
        self.printCurrentConfig()
        self.makeTracker()
        population = self.makePopulation()
        if self.antimony is None:
            self.computeFitness(population)  # Only need to do this once because fitness is computed during selection
        try:
            for i in range(self.currentConfig['maxGenerations']):
                population = self.getNextGen(population)
                self.savePopulation(population)
                self.printProgress(i, population)
                if population[0].fitness <= self.currentConfig['threshold']:
                    saveFileName = f"{str(self.seed)}"
                    self.saveRun(saveFileName, population)
                    print("\n\nSUCCESS!\n")
                    break
            if population[0].fitness > self.currentConfig['threshold']:
                print("\n\nFAIL\n")
                saveFileName = f"FAIL_{str(self.seed)}"
                self.saveRun(saveFileName, population)
            self.printSummary(population)
        except KeyboardInterrupt:
            return None


    # _________________________________________________________________________________
    #    METHODS FOR PRINTING AND SAVING PROGRESS
    # _________________________________________________________________________________

    def printProgress(self, genNum, population):
        if genNum % self.currentConfig['frequencyOfOutput'] == 0:
            print(flush=True)
            print("gen[" + str(genNum) + "] fitness=",
                  "{:.4f}".format(population[0].fitness),
                  end='', flush=True)
        else:
            print('.', end='', flush=True)

    def savePopulation(self, population):
        if self.currentConfig["toZip"] == "True":
            p = self.clonePopulation(population)
            self.tracker['savedPopulations'].append(p)


    def saveRun(self, saveFileName, population):
        save_directory = os.path.join(os.path.dirname(os.getcwd()), "saved_models/")
        if not os.path.isdir(save_directory):
            os.mkdir(save_directory)
        saveFileName = save_directory + saveFileName
        if self.currentConfig["toZip"] == "False":
            saveFileName = saveFileName + ".ant"
            astr = convertToAntimony(population[0])
            with open(saveFileName, "w") as f:
                f.write(astr)
                f.close()
        else:
            saveFileName = saveFileName + ".zip"
            zf = zipfile.ZipFile(saveFileName, mode="w", compression=zipfile.ZIP_DEFLATED)
            try:
                json_string = json.dumps(self.tracker["fitnessArray"])
                zf.writestr("fitnessList.txt", json_string)

                astr = convertToAntimony(population[0])
                zf.writestr("best_antimony.ant", astr)
                zf.writestr("seed_" + str(self.seed) + ".txt", str(self.seed))
                zf.writestr("config.txt", json.dumps(self.currentConfig) + '\n')

                today = date.today()
                now = datetime.now()
                summaryStr = 'Date:' + today.strftime("%b-%d-%Y") + '\n'

                summaryStr += 'Time:' + now.strftime("%H:%M:%S") + '\n'
                self.tracker["timeTaken"] = time.time() - self.tracker["startTime"]
                summaryStr += 'Time taken in seconds:' + str(math.trunc(self.tracker["timetaken"] * 100) / 100) + "\n"
                summaryStr += 'Time taken (hrs:min:sec):' + str(
                    time.strftime("%H:%M:%S", time.gmtime(self.tracker["timetaken"]))) + "\n"
                summaryStr += '#Seed=' + str(self.seed) + '\n'
                summaryStr += '#Final_number_of_generations=' + str(len(self.tracker["savedPopulations"])) + '\n'
                summaryStr += '#Size_of_population=' + str(self.currentConfig["sizeOfPopulation"]) + '\n'
                summaryStr += '#Number_of_added_reactions=' + str(self.tracker["nAddReaction"]) + '\n'
                summaryStr += '#Number_of_deleted_reactions=' + str(self.tracker["nDeleteReactions"]) + '\n'
                summaryStr += '#Number_of_parameter_changes=' + str(self.tracker["nParameterChanges"]) + '\n'
                summaryStr += '#Final_fitness=' + str(population[0].fitness) + '\n'
                zf.writestr('summary.txt', summaryStr)

                for index, pop in enumerate(self.tracker["savedPopulations"]):
                    for j in range(len(pop)):
                        fileName = "populations/generation_" + str(index) + '/individual_' + str(j) + '.txt'
                        popSummary = '# Fitness = ' + str(pop[j].fitness) + '\n'
                        popSummary += convertToAntimony(pop[j]);
                        zf.writestr(fileName, popSummary)
            finally:
                zf.close()

    def printSummary(self, population):
        print("Final fitness = ", population[0].fitness)
        self.tracker["timeTaken"] = time.time() - self.tracker["startTime"]
        print("Time taken in seconds = ", math.trunc(self.tracker["timeTaken"] * 100) / 100)
        print("Time taken (hrs:min:sec): ", time.strftime("%H:%M:%S", time.gmtime(self.tracker["timeTaken"])))
        print("Seed = ", self.seed)
        print('Number of added reactions = ', self.tracker["nAddReaction"])
        print('Number of deleted reactions = ', self.tracker["nDeleteReactions"])
        print('Number of parameter changes = ', self.tracker["nParameterChanges"])

    # _________________________________________________________________________________
    #    METHODS FOR PLOTTING RESULTS
    # _________________________________________________________________________________

    def plotFitnessPopulationHist(self, population):
        data = []
        for model in population:
            data.append(model.fitness)
        plt.hist(data)
        plt.show()

    def plotFitnessOfIndividuals(self, population):
        data = []
        for model in population:
            data.append(model.fitness)
        plt.plot(data)
        plt.show()

    def plotPopulationPlots(self, population):
        n = math.trunc(math.sqrt(len(population)))
        fig, axs = plt.subplots(n, n, figsize=(13, 11))
        count = 0
        for i in range(n):
            for j in range(n):
                t, y = self.fitnessEvaluator.runSimulation(population[count], 1.25, 100,
                                                           self.currentConfig['initialConditions'])
                axs[i, j].plot(t, y)
                count += 1

    def plotFitnessArray(self):
        plt.plot(self.tracker["fitnessArray"])
        plt.show()

    @staticmethod
    def plotFitnesssFromFile(fileName):
        data = np.loadtxt(fileName, delimiter=',')
        plt.plot(data[:, 0], data[:, 1])
        plt.show()

    @staticmethod
    def displayFitness(population):
        for p in population:
            print(p.fitness)

    @staticmethod
    def printModel(model):
        print("Model details:")
        print('Num floats:', model.numFloats, 'num boundary:', model.numBoundary, 'Num reactions:',
              len(model.reactions),
              'fitness:', math.trunc(model.fitness * 100) / 100);
        for r in model.reactions:
            print(r.reactionType, r.reactants, r.products, r.rateConstant)



def convertToAntimony(model):
    nFloats = model.numFloats
    nBoundary = model.numBoundary
    reactions = model.reactions
    nReactions = len(reactions)
    astr = ''
    for index in range(nFloats):
        astr += 'var S' + str(index) + '\n'

    for b in range(nBoundary):
        astr += 'ext S' + str(b + nFloats) + '\n'

    for i in range(nReactions):
        reaction = reactions[i]
        if reaction.reactionType == tu.TReactionType.UniUni:
            S1 = 'S' + str(reaction.reactant1)
            S2 = 'S' + str(reaction.product1)
            astr += S1 + ' -> ' + S2
            astr += '; k' + str(i) + '*' + S1 + '\n'
        if reaction.reactionType == tu.TReactionType.BiUni:
            S1 = 'S' + str(reaction.reactant1)
            S2 = 'S' + str(reaction.reactant2)
            S3 = 'S' + str(reaction.product1)
            astr += S1 + ' + ' + S2 + ' -> ' + S3
            astr += '; k' + str(i) + '*' + S1 + '*' + S2 + '\n'
        if reaction.reactionType == tu.TReactionType.UniBi:
            S1 = 'S' + str(reaction.reactant1)
            S2 = 'S' + str(reaction.product1)
            S3 = 'S' + str(reaction.product2)
            astr += S1 + ' -> ' + S2 + '+' + S3
            astr += '; k' + str(i) + '*' + S1 + '\n'
        if reaction.reactionType == tu.TReactionType.BiBi:
            S1 = 'S' + str(reaction.reactant1)
            S2 = 'S' + str(reaction.reactant2)
            S3 = 'S' + str(reaction.product1)
            S4 = 'S' + str(reaction.product2)
            astr += S1 + ' + ' + S2 + ' -> ' + S3 + ' + ' + S4
            astr += '; k' + str(i) + '*' + S1 + '*' + S2 + '\n'

    for i in range(nReactions):
        reaction = reactions[i]
        astr += 'k' + str(i) + ' = ' + str(reaction.rateConstant) + '\n'
    for i in range(nFloats + nBoundary):
        astr += 'S' + str(i) + ' = ' + str(model.initialConditions[i]) + '\n'

    return astr

def convertToTModel(antimony):
    nFloats = 0
    nBoundary = 0
    reactions_preprocess = []
    rates_preprocess = []
    initialConditions = []
    reactions = []
    lines = antimony.split("\n")
    for line in lines:
        if line.startswith('#'):
            continue
        if line.startswith('var'):
            nFloats += 1
        elif line.startswith('ext'):
            nBoundary += 1
        elif '->' in line:
            reactions_preprocess.append(line)
        elif line.startswith('k'):
            rates_preprocess.append(line)
        elif line.startswith("S"):
            line = line.replace(" ", "")
            initialConditions.append(float(line.split("=")[1]))

    for i, r in enumerate(reactions_preprocess):
        reaction = convertReactionLine(r)
        reaction.rateConstant = convertRateLine(rates_preprocess[i])
        reactions.append(reaction)

    model = uModel.TModel()
    model.numFloats = nFloats
    model.numBoundary = nBoundary
    model.initialConditions = initialConditions
    model.reactions = reactions
    model.fitness = 10E17
    model.cvode = TCvode(uLoadCvode.CV_BDF)
    return model

def convertRateLine(line):
    line = line.replace(" ", "")
    k = line.split("=")[1]
    k = k.split("#")[0]
    return float(k)


def convertReactionLine(line):
    '''
    UniUni = 0
    BiUni = 1
    UniBi = 2
    BiBi = 3
    '''
    line = line.replace(" ", "")  #remove spaces
    line = line.replace("S","")  #remove species label S
    reactants, products = line.split("->")
    products = products.split(';')[0]
    reactants = reactants.split('+')
    products = products.split('+')


    reaction = TReaction()
    reaction.reactant1 = int(reactants[0])
    reaction.product1 = int(products[0])

    #Get Reaction Type:
    if len(reactants) == 2:
        reaction.reactant2 = int(reactants[1])
        if len(products) == 2:
            reaction.product2 = int(products[1])
            reaction.reactionType = 3  # bibi
        else:
            reaction.reactionType = 1  # biuni
    else:
        if len(products) == 2:
            reaction.product2 = int(products[1])
            reaction.reactionType = 2  # unibi
        else:
            reaction.reactionType = 0  #unini
    return reaction




ant = '''var S0
var S1
var S2
S1 + S2 -> S2 + S2; k0*S1*S2
S1 + S0 -> S1 + S1; k1*S1*S0
S1 -> S1+S0; k2*S1
S2 + S0 -> S0; k3*S2*S0
k0 = 1.9920416329912947
k1 = 47.54258428799684
k2 = 26.347064160356418
k3 = 32.59216460314004
S0 = 1.0
S1 = 5.0
S2 = 9.0
'''
model = convertToTModel(ant)

