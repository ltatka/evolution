"""
The purpose of this script is to analyze reactions that were deleted from models because they did
not impact oscillation.
"""

import os
import numpy as np
import pandas as pd
from oscillatorDB import mongoMethods as mm


def split_reaction(reaction):
    reaction = reaction.replace(' ', '')  # strip spaces
    reaction = reaction.split('->') # separate products and reactants by splitting at ->
    reactants = reaction[0]
    products = reaction[1].split(';')[0] # Remove the rate constant part
    return reactants, products

def is_null_reaction(reaction, rxnType):
    if rxnType == 'uni-bi' or rxnType == 'bi-uni':
        return False
    reactants, products = split_reaction(reaction)
    if rxnType == 'uni-uni':
        return reactants == products
    else:  # bi-bi
        return reactants[0] == reactants[1] == products[0] == products[1]

def is_autocatalytic(reaction, rxnType):
    if rxnType == 'uni-uni' or rxnType == 'bi-uni':
        return False
    reactants, products = split_reaction(reaction)
    products = products.split('+')
    if rxnType == 'uni-bi':
        return reactants in products and products[0] == products[1]
    else:
        return ((reactants[0] == products[0] and reactants[0] == products[1]) or
                (reactants[1] == products[0] and reactants[1] == products[1]))

def get_reaction_type(reaction):
    reactants, products = split_reaction(reaction)
    rxnType = ''
    # Get reaction type by number of reactants and products
    if '+' in reactants:
        rxnType += 'bi-'
    else:
        rxnType += 'uni-'
    # Now we do the same thing for the product half
    if '+' in products:
        rxnType += 'bi'
    else:
        rxnType += 'uni'
    return rxnType

def classify_reaction(reaction):
    rxnType = get_reaction_type(reaction)
    if is_null_reaction(reaction, rxnType):
        raise Exception('Null reaction')
    return rxnType, is_autocatalytic(reaction, rxnType)

def tally_reactions():
    query = {'oscillator': True, 'num_nodes':3}
    result, length = mm.query_database(query, returnLength=True)

    reaction_tally = {'uni-uni': 0,
                      'uni-bi': 0,
                      'bi-uni': 0,
                      'bi-bi': 0}
    total_autocatalysis = 0
    models_with_autocatalysis_deleted = 0

    for r in result:
        reactions = r['deletedReactions']
        deletedAutocatalysis = 0
        for rxn in reactions:
            rxnType, autocatalysis = classify_reaction(rxn)
            reaction_tally[rxnType] += 1
            total_autocatalysis += autocatalysis
            deletedAutocatalysis += autocatalysis
        if deletedAutocatalysis > 0:
            models_with_autocatalysis_deleted += 1
    print(f"total models processed: {length}\n"
          f"total deleted autocatalysis reactions: {total_autocatalysis}\n"
          f"models with at least 1 deleted autocatalysis reaction: {models_with_autocatalysis_deleted}\n\n"
          "REACTION TALLIES:")
    for key in reaction_tally:
        print(f"{key}: {reaction_tally[key]}")


def get_max_rate_constant(model):
    astr = model['model']
    lines = astr.splitlines()
    max_k = 0
    for line in lines:
        if line.startswith("k"):
            k = float(line.split(' = ')[1])
            if k > max_k:
                max_k = k
    return max_k


