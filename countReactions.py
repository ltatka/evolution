import os
import numpy as np
import pandas as pd
from oscillatorDB import mongoMethods as mm
from scipy.stats import ttest_ind, binom_test, normaltest
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
            newDict[newKey] = reactionDict[key] / total
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



def countAllReactions_query(query):
    models = mm.query_database(query)
    allModelCounts = {'all totals': [],
                      'all uni-uni portion': [],
                      'all uni-bi portion': [],
                      'all bi-uni portion': [],
                      'all bi-bi portion': [],
                      'all degradation portion': [],
                      'all autocatalysis portion': [],
                      'has autocatalytic reaction': [],
                      'all IDs': []
                      }
    for model in models:
        astr = model["model"]
        ID = model['ID']
        reactionDict = countReactions(astr)
        # Add the reaction count dictionary to the database
        query = {"ID": ID}
        newEntry = {"$set": {"reactionCounts": reactionDict,
                             "reactionsCounted": True}}
        mm.collection.update_one(query, newEntry)
        # Add the reaction count dictionary info to the overall counting dict
        allModelCounts = updateCounter(reactionDict, allModelCounts, ID)
    return allModelCounts


def countAllReactions_directory(directory):
    allModelCounts = {'all totals': [],
                      'all uni-uni portion': [],
                      'all uni-bi portion': [],
                      'all bi-uni portion': [],
                      'all bi-bi portion': [],
                      'all degradation portion': [],
                      'all autocatalysis portion': [],
                      'has autocatalytic reaction': [],
                      'all IDs': []
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
        newKey = 'all ' + key
        try:
            allModelCounts[newKey].append(reactionDict[key])
        except KeyError:
            continue
    allModelCounts['has autocatalytic reaction'].append(int(reactionDict['autocatalysis'] == 0))
    allModelCounts['all IDs'].append(ID)
    allModelCounts['all totals'].append(reactionDict['total'])
    return allModelCounts



def writeOutCounts(path, allCountsDict):

    # Create and write out dataframe:
    df = pd.DataFrame()
    df['ID'] = allCountsDict['all IDs']
    df['Autocatalysis Present'] = allCountsDict['has autocatalytic reaction']
    df['Portion Degradation'] = allCountsDict['all degradation portion']
    df['Portion Autocatalysis'] = allCountsDict['all autocatalysis portion']
    df['Portion Uni-Uni'] = allCountsDict['all uni-uni portion']
    df['Portion Uni-Bi'] = allCountsDict['all uni-bi portion']
    df['Portion Bi-Uni'] = allCountsDict['all bi-uni portion']
    df['Portion Bi-Bi'] = allCountsDict['all bi-bi portion']
    df['Total Reactions'] = allCountsDict['all totals']
    df.set_index('ID')
    df.to_csv(path_or_buf=path)
    return df

def getPValues(path, controldf, oscdf):
    results = pd.DataFrame()
    # Binomial test for portion of models containing autocatalytic reactions
    controlAutoCat = np.mean(controldf['Autocatalysis Present'])
    oscAutoCat = np.sum(oscdf['Autocatalysis Present'])
    null_p = controlAutoCat/len(oscdf['Autocatalysis Present'])
    p_AutocatPresent = binom_test(oscAutoCat, n=len(oscdf['Autocatalysis Present']), p=null_p)
    results['Population prevalence of autocatalysis'] = p_AutocatPresent
    # Two sided t test for everything else:
    for key in controldf.keys():
        if key != 'Autocatalysis Present' and key != 'ID':
            results[key] = ttest_ind(controldf[key], oscdf[key])
    results.to_csv(path_or_buf=path)
    return results

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
