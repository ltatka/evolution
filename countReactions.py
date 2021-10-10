import os
import numpy as np
import pandas as pd


# import isMassConserved
# import damped_analysis as da
# from oscillatorDB import mongoMethods as mm
# import antimony_ev2 as aModel
# from shutil import rmtree


def getReactionType(reaction):
    reaction = reaction.replace(' ', '')
    reactants, products = reaction.split('->')
    if '+' in reactants:
        rxnType = 'bi-'
    else:
        rxnType = 'uni-'
    if '+' in products:
        rxnType += 'bi'
    else:
        rxnType += 'uni'
    return rxnType


def splitReactantsProducts(reaction, returnType=False):
    rType = getReactionType(reaction)
    reaction = reaction.replace(' ', '')
    reactants, products = reaction.split('->')
    products = products.split(';')[0]
    if rType.startswith('bi'):
        reactants = reactants.split('+')
    else:
        reactants = [reactants]
    if rType.endswith('bi'):
        products = products.split('+')
    else:
        products = [products]
    if returnType:
        return reactants, products, rType
    return reactants, products


def reactantEqualsProduct(reaction):
    reactant, product = splitReactantsProducts(reaction)
    if len(reactant) != len(product):
        return False
    if len(reactant) == 1:
        return reactant == product
    return reactant == product or [reactant[1], reactant[0]] == product


def isAutocatalytic(reaction):
    reactants, products, rType = splitReactantsProducts(reaction, returnType=True)
    if rType.endswith('uni'):
        return False
    if rType.startswith('uni'):
        return reactants[0] in products and products[0] == products[1]
    else:  # bi+bi
        return not reactantEqualsProduct(reaction) and products[0] == products[1] and \
               (reactants[0] in products or reactants[1] in products)

def isDegradation(reaction):
    reactants, products, rType = splitReactantsProducts(reaction, returnType=True)
    return rType == 'bi-uni' and products[0] in reactants

def getPortions(reactionDict):
    total = reactionDict['total']
    newDict = {}
    for key in reactionDict.keys():
        if key != 'total':
            newKey = key + ' portion'
            newDict[newKey] = reactionDict[key]/total
            newDict[key] = reactionDict[key]
    newDict['total'] = reactionDict['total']
    return newDict

def countReactions(astr):
    # Returns dictionary of reaction counts
    reactionCounts = {'uni-uni': 0,
                      'uni-bi': 0,
                      'bi-uni': 0,
                      'bi-bi': 0,
                      'degradation': 0,
                      'autocatalysis': 0,
                      'total': 0}
    lines = astr.splitlines()
    for line in lines:
        if '->' in line and not line.startswith('#'):
            reactionCounts['total'] += 1
            reactionCounts[getReactionType(line)] += 1
            if isAutocatalytic(line):
                reactionCounts['autocatalysis'] += 1
            if isDegradation(line):
                reactionCounts['degradation'] += 1
        else:  # if the line is not a reaction, move to the next line
            continue
    # This dictionary contains the PORTION of each reaction type
    return getPortions(reactionCounts)



