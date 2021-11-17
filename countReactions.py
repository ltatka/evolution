import os
import numpy as np
import pandas as pd

import damped_analysis
from oscillatorDB import mongoMethods as mm
from scipy.stats import chi2_contingency
import random


# import isMassConserved
# import damped_analysis as da
#
# import antimony_ev2 as aModel
# from shutil import rmtree


def getReactionType(reaction):
    reaction = reaction.replace(' ', '')
    reactants, products = reaction.split('->')
    if '+' in reactants:
        rxnType = 'Bi-'
    else:
        rxnType = 'Uni-'
    if '+' in products:
        rxnType += 'Bi'
    else:
        rxnType += 'Uni'
    return rxnType

def findBadRateLaws(listID):
    badRateLaws = {}
    for ID in listID:
        result = mm.query_database({'ID': ID})
        astr = result[0]['model']
        astr = astr.splitlines()
        for line in astr:
            if '->' in line and not line.startswith('#'):
                if rateLawIsIncorrect(line):
                    if ID not in badRateLaws.keys():
                        badRateLaws[ID] = [line]
                    else:
                        badRateLaws[ID].append(line)
    return badRateLaws

def rateLawIsIncorrect(reaction):
    components = getRateLawSpecies(reaction)
    reactants, _ = splitReactantsProducts(reaction)
    if len(reactants) != len(components):
        return True
    elif reactants[0] not in components:
        return True
    elif len(reactants) == 2 and reactants[1] not in components:
        # eg. S1 + S2 -> S0; k1*S1*S1
        return True
    else:
        return False


def getRateLawSpecies(reaction):
    rateLaw = reaction.split(';')[1]
    rateLaw = rateLaw.replace(' ', '')
    rateLaw = rateLaw.replace('\n', '')
    components = rateLaw.split('*')
    return components[1:]

def splitReactantsProducts(reaction, returnType=False):
    rType = getReactionType(reaction)
    reaction = reaction.replace(' ', '')
    reactants, products = reaction.split('->')
    products = products.split(';')[0]
    if rType.startswith('Bi'):
        reactants = reactants.split('+')
    else:
        reactants = [reactants]
    if rType.endswith('Bi'):
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
    if rType.endswith('Uni'):
        return False
    if rType.startswith('Uni'):
        return reactants[0] in products and products[0] == products[1]
    else:  # bi+bi
        return not reactantEqualsProduct(reaction) and products[0] == products[1] and \
               (reactants[0] in products or reactants[1] in products)


def isDegradation(reaction):
    reactants, products, rType = splitReactantsProducts(reaction, returnType=True)
    return rType == 'Bi-Uni' and products[0] in reactants


def countReactions(astr):
    # Returns dictionary of reaction counts
    reactionCounts = {'Uni-Uni': 0,
                      'Uni-Bi': 0,
                      'Bi-Uni': 0,
                      'Bi-Bi': 0,
                      'Degradation': 0,
                      'Autocatalysis': 0,
                      'Total': 0}
    lines = astr.splitlines()
    for line in lines:
        if '->' in line and not line.startswith('#'):
            reactionCounts['Total'] += 1
            reactionCounts[getReactionType(line)] += 1
            if isAutocatalytic(line):
                reactionCounts['Autocatalysis'] += 1
            if isDegradation(line):
                reactionCounts['Degradation'] += 1
        else:  # if the line is not a reaction (or is commented out), move to the next line
            continue
    return reactionCounts

def gatherCounts_query(query):
    models = mm.query_database(query)
    allModelCounts = {'Total': [],
                      'Uni-Uni': [],
                      'Uni-Bi': [],
                      'Bi-Uni': [],
                      'Bi-Bi': [],
                      'Degradation': [],
                      'Degradation Present': [],
                      'Autocatalysis': [],
                      'Autocatalysis Present': [],
                      'ID': []
                      }
    for model in models:
        reactionDict = model["reactionCounts"]
        # Add the reaction count dictionary info to the overall counting dict
        allModelCounts = updateCounter(reactionDict, allModelCounts, model["ID"])
    return allModelCounts

def countAllReactions_query(query):
    models = mm.query_database(query)
    allModelCounts = {'Total': [],
                      'Uni-Uni': [],
                      'Uni-Bi': [],
                      'Bi-Uni': [],
                      'Bi-Bi': [],
                      'Degradation': [],
                      'Degradation Present': [],
                      'Autocatalysis': [],
                      'Autocatalysis Present': [],
                      'ID': []
                      }
    for model in models:
        astr = model["model"]
        ID = model['ID']
        reactionDict = countReactions(astr)
        # Add the reaction count dictionary to the database
        query = {"ID": ID}
        newEntry = {"$set": {"reactionCounts": reactionDict,
                             "reactionsCounted": True,
                             "Autocatalysis Present": reactionDict["Autocatalysis"] > 0,
                             "Degradation Present": reactionDict["Degradation"] > 0,
                             "reactionsCounted": True}}
        mm.collection.update_one(query, newEntry)
        # Add the reaction count dictionary info to the overall counting dict
        allModelCounts = updateCounter(reactionDict, allModelCounts, ID)
    return allModelCounts


def countAllReactions_directory(directory):
    allModelCounts = {'Total': [],
                      'Uni-Uni': [],
                      'Uni-Bi': [],
                      'Bi-Uni': [],
                      'Bi-Bi': [],
                      'Degradation': [],
                      'Degradation Present': [],
                      'Autocatalysis': [],
                      'Autocatalysis Present': [],
                      'ID': []
                      }
    os.chdir(directory)
    for file in os.listdir(directory):
        with open(file, 'r') as f:
            astr = f.read()
            f.close()
        ID = file[:-4]
        reactionDict = countReactions(astr)
        # Add the reaction count dictionary info to the overall counting dict
        allModelCounts = updateCounter(reactionDict, allModelCounts, ID)
    return allModelCounts

def updateCounter(reactionDict, allModelCounts, ID):
    for key in reactionDict.keys():
        try:
            allModelCounts[key].append(reactionDict[key])
        except KeyError:
            continue
    allModelCounts['Autocatalysis Present'].append(int(reactionDict['Autocatalysis'] > 0))
    allModelCounts['Degradation Present'].append(int(reactionDict['Degradation'] > 0))
    allModelCounts['ID'].append(ID)
    return allModelCounts



def writeOutCounts(path, allCountsDict):
    df = pd.DataFrame()
    df['ID'] = allCountsDict['ID']
    df['Autocatalysis Present'] = allCountsDict['Autocatalysis Present']
    df['Autocatalysis'] = allCountsDict['Autocatalysis']
    df['Degradation'] = allCountsDict['Degradation']
    df['Degradation Present'] = allCountsDict['Degradation Present']
    df['Uni-Uni'] = allCountsDict['Uni-Uni']
    df['Uni-Bi'] = allCountsDict['Uni-Bi']
    df['Bi-Uni'] = allCountsDict['Bi-Uni']
    df['Bi-Bi'] = allCountsDict['Bi-Bi']
    df['Total'] = allCountsDict['Total']
    df.set_index('ID')
    df.to_csv(path_or_buf=path)
    return df


def pAutocatalysisPortion(control, oscillator):
    control = list(control)
    oscillator = list(oscillator)
    # Make 2x2 contingency table:
    ###            Num autocatalysis    Num non-autocatalysis
    #   control        ____                 ____
    #   oscillator     ____                 ____
    controlRow = [np.sum(control), len(control)-sum(control)]
    oscillatorRow = [np.sum(oscillator), len(oscillator) - np.sum(oscillator)]
    contingencyTable = np.array([controlRow,
                                oscillatorRow])
    result = chi2_contingency(contingencyTable)
    # Return only p value
    return result


def permutationTest(control, treatment):
    control = list(control)
    treatment = list(treatment)
    true_mean_diff = np.abs(np.mean(control) - np.mean(treatment))
    pooled_sample = control + treatment
    test_mean_diffs = []
    random_control = random.sample(pooled_sample, len(control))
    for i in range(1000):
        random_treatment = [x for x in pooled_sample if x not in random_control]
        mean_diff = np.abs(np.mean(random_control) - np.mean(random_treatment))
        test_mean_diffs.append(int(mean_diff > true_mean_diff))
    print(np.sum(test_mean_diffs))
    return np.mean(test_mean_diffs)

def makeList(query, key):
    result = mm.query_database(query)
    resultList = []
    for model in result:
        resultList.append(model[key])
    return resultList