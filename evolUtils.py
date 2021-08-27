# -*- coding: utf-8 -*-
"""
Created on Fri Apr 30 15:55:44 2021

@author: hsauro
"""

from commonTypes import TModel_
from teUtils import teUtils as tu
from uModel import TModel
from uModel import TReaction

def convertToAntimony (model):
    nFloats = model[TModel_.nFloats]
    nBoundary = model[TModel_.nBoundary]
    boundaryList = model[TModel_.boundaryList]
    fullList = model[TModel_.fullSpeciesList]
    reactions = model[TModel_.reactionList]
    nReactions = model[TModel_.reactionList][0]
    astr = ''
    for f in fullList[:nFloats]:
        astr += 'var S' + str(f) + '\n'
        
    for b in boundaryList:
        astr += 'ext S' + str(b) + '\n'  
        
    for i in range (nReactions):
        reaction = reactions[i+1]
        if reaction[0] == tu.buildNetworks.TReactionType.UniUni:
           S1 = 'S' + str (reaction[1][0])
           S2 = 'S' + str (reaction[2][0])
           astr += S1 + ' -> ' + S2
           astr += '; k' + str(i) + '*' + S1 + '\n'
        if reaction[0] == tu.buildNetworks.TReactionType.BiUni:
           S1 = 'S' + str (reaction[1][0])
           S2 = 'S' + str (reaction[1][1])
           S3 = 'S' + str (reaction[2][0])
           astr += S1 + ' + ' + S2 + ' -> ' + S3
           astr += '; k' + str(i) + '*' + S1 + '*' + S2 + '\n'
        if reaction[0] == tu.buildNetworks.TReactionType.UniBi:
           S1 = 'S' + str (reaction[1][0])
           S2 = 'S' + str (reaction[2][0])
           S3 = 'S' + str (reaction[2][1])
           astr += S1 + ' -> ' + S2 + '+' + S3
           astr += '; k' + str(i) + '*' + S1 + '\n'
        if reaction[0] == tu.buildNetworks.TReactionType.BiBi:
           S1 = 'S' + str (reaction[1][0])
           S2 = 'S' + str (reaction[1][1])
           S3 = 'S' + str (reaction[2][0])
           S4 = 'S' + str (reaction[2][1])
           astr += S1 + ' + ' + S2 + ' -> ' + S3 + ' + ' + S4
           astr += '; k' + str(i) + '*' + S1 + '*' + S2 + '\n'
           
    for i in range (nReactions):
        reaction = reactions[i+1]
        astr += 'k' + str (i) + ' = ' + str (reaction[3]) + '\n'
    initCond = model[TModel_.initialCond]
    for i in range (nFloats+nBoundary):
        astr += 'S' + str(fullList[i]) + ' = ' + str (initCond[i]) + '\n'
    
    return astr

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
        if reaction.reactionType == tu.buildNetworks.TReactionType.UniUni:
           S1 = 'S' + str (reaction.reactant1)
           S2 = 'S' + str (reaction.product1)
           astr += S1 + ' -> ' + S2
           astr += '; k' + str(i) + '*' + S1 + '\n'
        if reaction.reactionType == tu.buildNetworks.TReactionType.BiUni:
           S1 = 'S' + str (reaction.reactant1)
           S2 = 'S' + str (reaction.reactant2)
           S3 = 'S' + str (reaction.product1)
           astr += S1 + ' + ' + S2 + ' -> ' + S3
           astr += '; k' + str(i) + '*' + S1 + '*' + S2 + '\n'
        if reaction.reactionType == tu.buildNetworks.TReactionType.UniBi:
           S1 = 'S' + str (reaction.reactant1)
           S2 = 'S' + str (reaction.product1)
           S3 = 'S' + str (reaction.product2)
           astr += S1 + ' -> ' + S2 + '+' + S3
           astr += '; k' + str(i) + '*' + S1 + '\n'
        if reaction.reactionType == tu.buildNetworks.TReactionType.BiBi:
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
