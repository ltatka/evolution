import numpy as np
import tellurium as te
from evolUtils import readObjectiveFunction
import random
from copy import deepcopy
from damped_analysis import isModelDampled




def joinAntimonyLines(antLines):
    if antLines[0] == '':
        antLines = antLines[1:]
    return '\n'.join(antLines)


class Reaction():
    def __init__(self, reactant, product, k):
        if isinstance(reactant, frozenset) and isinstance(product, frozenset):
            self.reactant = reactant
            self.product = product
        else:
            self.reactant = frozenset(reactant)
            self.product = frozenset(product)
        self.k = k

    def isEqual(self, other):
        return self.reactant == other.reactant and self.product == other.product


class ReactionSet():
    def __init__(self):
        self.rxnDict = {}

    def add(self, reaction):
        self.rxnDict[(reaction.reactant, reaction.product)] = reaction.k

    def contains(self, reaction):
        return (reaction.reactant, reaction.product) in self.rxnDict

    def updateRateConstant(self, reaction):
        self.rxnDict[(reaction.reactant, reaction.product)] = self.rxnDict[
                                                                  (reaction.reactant, reaction.product)] + reaction.k


class PostInitCaller(type):
    def __call__(cls, *args, **kwargs):
        obj = type.__call__(cls, *args, **kwargs)
        obj.post_init()
        return obj


class AntimonyModel(object, metaclass=PostInitCaller):
    rxnSet = {}
    pDeleteRxn = .50
    pDelete1 = .45
    pDelete2 = .35
    rateConstantRange = .1
    pKeepWorseModel = 1

    def __init__(self, ant_str, removeDupes=True, objectiveData=False):
        #TODO:
        '''
        processReactions: if False, will not go through and delete duplicates
        objectiveData: if False, no objective data will be read ( won't be able to test fitness)
        '''
        if objectiveData:
            self.objectiveData = readObjectiveFunction()
        self.removeDupes = removeDupes
        self.ant = ant_str
        self.antLines = []
        self.reactions = []
        self.speciesList = []
        self.initialConditions = []
        self.rateConstants = []
        self.nFloats = 0
        self.fitness = 1E17
        self.nSpecies = 0

    def post_init(self):
        lines = self.ant.split('\n')
        newAnt = ''
        for line in lines:
            if not line.startswith('#') and line != '':
                if '->' in line:
                    self.reactions.append(line)
                elif line.startswith('var'):
                    self.nFloats += 1
                    self.nSpecies += 1
                    self.speciesList.append(line)
                elif line.startswith('ext'):
                    self.nSpecies += 1
                    self.speciesList.append(line)
                elif line.startswith('k'):
                    self.rateConstants.append(line)
                elif line.startswith('S') and '=' in line:
                    self.initialConditions.append(line)
                newAnt += line + '\n'
                self.antLines.append(line)
        del self.ant
        self.ant = newAnt
        if self.removeDupes:
            self.removeDuplicateRxns()

    def removeDuplicateRxns(self):
        # self.makeRxnSet()
        self.reactions, self.rateConstants = self.processRxnSet()
        self.refactorModel()

    def makeRxnSet(self):
        rxnSet = ReactionSet()
        for line in self.antLines:
            if not line.startswith('#') and '->' in line:
                line = line.replace(' ', '')
                reactionSplit = line.split('->')
                reactant = reactionSplit[0]
                productSplit = reactionSplit[1].split(';')
                product = productSplit[0]
                rateLaw = productSplit[1]
                if '+' in reactant:
                    reactant = reactant.split('+')
                else:
                    reactant = [reactant]
                if '+' in product:
                    product = product.split('+')
                else:
                    product = [product]
                k = rateLaw.split('*')[0]
                for l in self.antLines:
                    if l.startswith(k):
                        rateConstant = l.split(' = ')[1]
                        rateConstant = float(rateConstant.split('#')[0])
                reactant = frozenset(reactant)
                product = frozenset(product)
                if reactant != product:
                    reaction = Reaction(reactant, product, rateConstant)
                    if rxnSet.contains(reaction):
                        rxnSet.updateRateConstant(reaction)
                    else:
                        rxnSet.add(reaction)
        self.rxnSet = rxnSet

    def processRxnSet(self):
        self.makeRxnSet()
        reactionList = []
        rateConstantList = []
        for index, item in enumerate(self.rxnSet.rxnDict):
            reaction = ''
            rateLaw = f'; k{index}*'
            rateConstant = f'k{index} = '
            # If there are two reactants, put a '+' between them
            if len(item[0]) == 2:
                for species in item[0]:
                    reaction += species + '+'
                    rateLaw += species + '*'
                rateLaw = rateLaw[:-1]  # remove second '*'
                reaction = reaction[:-1]  # remove the second '+'
            else:
                # If there's only one reactant, just add it
                for species in item[0]:
                    reaction += species
                    rateLaw += species
            reaction += '->'
            # Now do the same for products
            if len(item[1]) == 2:
                for species in item[1]:
                    reaction += species + '+'
                reaction = reaction[:-1]
            else:
                for species in item[1]:
                    reaction += species
            reaction = reaction + rateLaw
            rateConstant = rateConstant + str(self.rxnSet.rxnDict[item])
            reactionList.append(reaction)
            rateConstantList.append(rateConstant)
        return reactionList, rateConstantList

    def refactorModel(self):
        model = self.speciesList + self.reactions + self.rateConstants + self.initialConditions
        self.antLines = model
        self.ant = joinAntimonyLines(model)

    def simulate(self):
        numberOfPoints = self.objectiveData.numberOfPoints
        timeEnd = self.objectiveData.timeEnd
        r = te.loada(self.ant)
        result = r.simulate(0, timeEnd, numberOfPoints)
        t = result['time']
        y = [row[1:] for row in result]
        return t, y

    def evalFitness(self):
        self.refactorModel()
        try:
            t, y = self.simulate()
            nFloats = self.nFloats
            # compute fitness with respect to each node
            deviation = np.zeros(nFloats)  # Size = number of floats
            smallestDeviation = 1E18
            for j in range(nFloats):  # loop all nFloats
                deviation[j] = 0;
                for i in range(self.objectiveData.numberOfPoints - 1):
                    # list integers must be indices or slices
                    deviation[j] = deviation[j] + (y[i][j] - self.objectiveData.outputData[i]) ** 2
                if smallestDeviation > deviation[j]:
                    smallestDeviation = deviation[j]
            # Size penalty:
            smallestDeviation = smallestDeviation + 100 * len(self.reactions)
        except Exception as err:
            # Assign high fitness
            self.fitness = 1E17
            return 1E17
        self.fitness = smallestDeviation
        return smallestDeviation

    def deleteReaction(self):
        oldReactions = deepcopy(self.reactions)
        oldFitness = deepcopy(self.fitness)
        oldRateConstants = deepcopy(self.rateConstants)
        if len(self.reactions) > 5:
            nDelete = random.choices([1, 2, 3], weights=[self.pDelete1, self.pDelete2,
                                                         1 - (self.pDelete1 + self.pDelete2)], k=1)
        else:  # if 5 or fewer reactions, just delete 1
            nDelete = [1]
        rxnDelete = random.choices(list(range(len(self.reactions))), k=nDelete[0])
        for i in rxnDelete:
            self.reactions[i] = -1
            self.rateConstants[i] = -1
        self.reactions = list(filter((-1).__ne__, self.reactions))
        self.rateConstants = list(filter((-1).__ne__, self.rateConstants))
        newFitness = self.evalFitness()
        if oldFitness < newFitness:
            p = random.random()
            if p < self.pKeepWorseModel:
                self.reactions = oldReactions
                self.fitness = oldFitness
                self.rateConstants = oldRateConstants
                self.refactorModel()

    def mutateRateConstant(self):
        multiplier = (random.random() - self.rateConstantRange) / (10 * self.rateConstantRange)
        i = random.randint(0, len(self.rateConstants) - 1)
        oldRateConstant = deepcopy(self.rateConstants[i])
        oldFitness = deepcopy(self.fitness)
        k, num = self.rateConstants[i].split(' = ')
        num = multiplier * float(num)
        self.rateConstants[i] = k + ' = ' + str(num)
        newFitness = self.evalFitness()
        if oldFitness < newFitness:
            p = random.random()
            if p < self.pKeepWorseModel:
                self.rateConstants[i] = oldRateConstant
                self.fitness = oldFitness
                self.refactorModel()

    def mutateReactions(self):
        p = random.random()
        if p < 0.5:
            self.mutateReactions()
        else:
            self.mutateRateConstant()

    def deleteUnecessaryReactions(self):
        for index, line in enumerate(self.antLines):
            if not line.startswith('#') and '->' in line:
                # Comment out the reaction
                self.antLines[index] = '#' + line
                # Join the new antimony lines
                newModel = joinAntimonyLines(self.antLines)

                damped, toInf = isModelDampled(newModel)
                # If it the deleted reaction does not break the model, then delete it's rate constant
                if not damped and not toInf:
                    # subtract length of speciesList because we're indexing entire model to adjust indices
                    del self.rateConstants[index - len(self.speciesList)]
                    # subtract number of species for same reason as above
                    del self.reactions[index - len(self.speciesList)]
                    del self.antLines[index]
                # uncomment the 'deleted' reaction if it is necessary for oscillation
                else:
                    self.antLines[index] = self.antLines[index][1:]
        # Store any changes
        self.refactorModel()

#
# def evolveStage2(queryOrPath, ze=450, portionElite=0.1
#     if isinstance(queryOrPath, dict):
#         query = queryOrPath
#         pop
#     for i in range(genSize):
#         population.append(deepcopy(model))
#
#     for i in range(numGen):
#         newGen = deepcopy(population[:numElite])
#         # Tournament selection:
#         for j in range(genSize - numElite):
#             model1, model2 = random.choices(population, k=2)
#             if model1.fitness <= model2.fitness:
#                 model1.mutateReactions()
#                 newGen.append(model1)
#             else:
#                 model2.mutateReactions
#                 newGen.append(model2)
#         # Sort by fitness
#         newGen.sort(key=operator.attrgetter('fitness'))
#         population = newGen
#         if i%10 == 0:
#             print(f'GENERATION: {i}')
#             print(population[0].fitness)
#
#