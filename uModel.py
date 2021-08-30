"""
Created on Fri Apr 30 18:54:00 2021

@author: hsauro
"""

import copy
from dataclasses import dataclass


class TReaction:

    def __init__(self):
        self.reactionType = 0
        self.reactant1 = 0
        self.reactant2 = 0
        self.product1 = 0
        self.product2 = 0
        self.rateConstant = 0


class TModel:

    def __init__(self):
        self.numFloats = 0
        self.numBoundary = 0
        self.initialConditions = 0
        self.reactions = []
        self.fitness = 0
        self.cvode = 0


@dataclass
class TModel_:
    nFloats = 0
    nBoundary = 1
    fullSpeciesList = 2
    boundaryList = 3
    initialCond = 4
    reactionList = 5
    fitness = 7


def clone(model):
    amodel = TModel()
    amodel.numBoundary = model.numBoundary
    amodel.numFloats = model.numFloats
    amodel.fitness = model.fitness
    amodel.initialConditions = copy.deepcopy(model.initialConditions)
    amodel.reactions = []
    amodel.cvode = model.cvode
    for oldrxn in model.reactions:
        newrxn = TReaction()

        newrxn.reactant1 = oldrxn.reactant1
        newrxn.reactant2 = oldrxn.reactant2
        newrxn.product1 = oldrxn.product1
        newrxn.product2 = oldrxn.product2

        newrxn.rateConstant = oldrxn.rateConstant
        newrxn.reactionType = oldrxn.reactionType
        amodel.reactions.append(newrxn)
    return amodel
