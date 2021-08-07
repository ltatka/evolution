import numpy as np
import tellurium as te
from dataclasses import dataclass
import readObjData
from evolve import readObjectiveFunction
import random
from copy import deepcopy

initialConditions = [1, 5, 9, 3, 10, 3, 7, 1, 6, 3, 10, 11, 4, 6, 2, 7, 1, 9, 5, 7, 2, 4, 5, 10, 4, 1, 6, 7, 3, 2, 7, 8]

# Fitness = 7.372410996154274
antStr = '''
var S0
var S1
var S2
var S3
var S4
ext S5
ext S6
ext S7
ext S8
ext S9
S3 + S2 -> S1 + S2; k5*S3*S2
S1 -> S1; k12*S1
S1 -> S0; k0*S1
S2 -> S4; k1*S2
S6 -> S4+S6; k2*S6
S3 -> S0; k3*S3
S4 + S0 -> S1; k4*S4*S0
S4 -> S1+S4; k6*S4
S4 -> S1+S4; k7*S4
S1 + S0 -> S3; k8*S1*S0
S0 + S0 -> S0 + S0; k9*S0*S0
S2 + S0 -> S0; k10*S2*S0
S2 + S1 -> S2 + S0; k11*S2*S1
S0 + S1 -> S3; k12*S0*S1
S2 -> S3+S1; k13*S2
S4 -> S3; k14*S4
k0 = 11.0073864078374
k1 = 20.834047235150877
k2 = 25.86274972867825
k3 = 49.94562904979901
k4 = 35.396880649350614
k5 = 22.610393366712717
k6 = 128.6797779260811
k7 = 32.182988029374265
k8 = 27.151163612671933
k9 = 8.84493678326487
k10 = 28.435636484961123
k11 = 35.243886618860095
k12 = 36.970775715909255
k13 = 11.973346291514053
k14 = 0.05810930278888904
S0 = 1.0
S1 = 5.0
S2 = 9.0
S3 = 3.0
S4 = 10.0
S5 = 3.0
S6 = 7.0
S7 = 1.0
S8 = 6.0
S9 = 3.0
'''
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
        self.rxnDict[(reaction.reactant, reaction.product)] = self.rxnDict[(reaction.reactant, reaction.product)] + reaction.k

@dataclass
class AntimonyModel:
    ant: str
    objectiveData = readObjectiveFunction()
    antLines = []
    reactions = []
    nSpecies: int = 0
    speciesList = []
    initialConditions = []
    rateConstants = []
    nFloats: int = 0
    fitness: float = 1E17

    rxnSet = {}
    pDeleteRxn = .50
    pDelete1 = .45
    pDelete2 = .35
    rateConstantRange = .1
    pKeepWorseModel = .3

    def __post_init__(self):
        lines = self.ant.split('\n')
        newAnt = ''
        for line in lines:
            if not line.startswith('#'):
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
        self.ant = newAnt



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
                else: reactant = [reactant]
                if '+' in product:
                    product = product.split('+')
                else: product = [product]
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
        return rxnSet


    def convertRxnSet(self):
        self.makeRxnSet()
        reactionList = []
        rateConstantList= []

        for index, item in enumerate(self.rxnSet.rxnDict):

            reaction = ''
            rateLaw = f'; k{index}*'
            rateConstant = f'k{index} = '
            # If there are two reactants, put a '+' between them
            if len(item[0]) == 2:
                for species in item[0]:
                    reaction += species + '+'
                    rateLaw += species + '*'
                rateLaw = rateLaw[:-1] #remove second '*'
                reaction = reaction[:-1] #remove the second '+'
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
        newAntStr = ''
        for line in model:
            newAntStr += line[0] + '\n'
        self.ant = newAntStr


    def simulate(self):
        numberOfPoints = self.objectiveData.numberOfPoints
        timeEnd = self.objectiveData.timeEnd
        r = te.loada(self.ant)
        result = r.simulate(0, timeEnd, numberOfPoints)
        t = result['time']
        y = [row[1:] for row in result]
        return t, y

    def evalFitness(self):
        try:
            t, y = self.simulate()
            nFloats = self.nFloats
            # compute fitness with respect to each node
            deviation = np.zeros (nFloats) # Size = number of floats
            smallestDeviation = 1E18
            for j in range (nFloats): # loop all nFloats
                deviation[j] = 0;
                for i in range (self.objectiveData.numberOfPoints - 1):
                    deviation[j] = deviation[j] + (y[i, j] - self.objectiveData.outputData[i])**2
                    if smallestDeviation > deviation[j]:
                        smallestDeviation = deviation[j]
            # Size penalty:
            smallestDeviation = smallestDeviation + 100 * len(self.nReactions)
        except Exception as err:
             # Assign high fitness
             self.fitness = 1E17
             return 1E17
        self.fitness = smallestDeviation
        return smallestDeviation

    def deleteReaction(self):
        oldReactions = deepcopy(self.reactions)
        oldFitness = deepcopy(self.fitness)
        if len(self.reactions) > 5:
            nDelete = random.choices([1, 2, 3], weights=[self.pDelete1, self.pDelete2,
                                                         1 - (self.pDelete1 + self.pDelete2)], k=1)
        else: # if 5 or fewer reactions, just delete 1
            nDelete = [1]
        rxnDelete = random.choices(list(range(len(self.reactions))), k=nDelete[0])
        for i in rxnDelete:
            self.reactions[i] = -1
        self.reactions = list(filter((-1).__ne__, self.reactions))
        newFitness = self.evalFitness()
        if oldFitness < newFitness:
            p = random.random()
            if p < self.pKeepWorseModel:
                self.reactions = oldReactions
                self.fitness = oldFitness

    def mutateRateConstant(self):
        multiplier = (random.random() - self.rateConstantRange)/(10*self.rateConstantRange)
        #TODO: select so it's only one of the rate constants that has a reaction



model = AntimonyModel(antStr)
model.deleteReaction()
rxns, rate = model.convertRxnSet()


print(rxns)
