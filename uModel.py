# # -*- coding: utf-8 -*-
# """
# Created on Fri Apr 30 18:54:00 2021

# @author: hsauro
# """

# import copy

# class TReaction:

#   def __init__(self):
#     self.reactionType = 0
#     self.reactant1 = 0
#     self.reactant2 = 0
#     self.product1 = 0
#     self.product2 = 0
#     self.rateConstant = 0
       
# class TModel:
    
#     def __init__(self):
#       self.numFloats = 0
#       self.numBoundary = 0
#       self.initialConditions = 0
#       self.reactions = []
#       self.fitness = 0
#       self.originEncoding = 0
#       self.cvode = 0

# def clone (model):
#     amodel = TModel()
#     amodel.numBoundary = model.numBoundary
#     amodel.numFloats = model.numFloats
#     amodel.fitness = model.fitness
#     amodel.initialConditions = copy.deepcopy (model.initialConditions)
#     amodel.reactions = []
#     amodel.originEncoding = copy.deepcopy(model.originEncoding)
#     amodel.cvode = model.cvode
#     for oldrxn in model.reactions:
#         newrxn = TReaction()
#         newrxn.reactant1 = oldrxn.reactant1
#         newrxn.reactant2 = oldrxn.reactant2
        
#         newrxn.product1 = oldrxn.product1
#         newrxn.product2 = oldrxn.product2

#         newrxn.rateConstant = oldrxn.rateConstant
#         newrxn.reactionType = oldrxn.reactionType
#         amodel.reactions.append (newrxn)  
#     return amodel
    
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 30 18:54:00 2021

@author: hsauro
"""

import copy

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
      self.ID = ''

def clone (model):
    amodel = TModel()
    amodel.numBoundary = model.numBoundary
    amodel.numFloats = model.numFloats
    amodel.fitness = model.fitness
    amodel.initialConditions = copy.deepcopy (model.initialConditions)
    amodel.reactions = []
    amodel.cvode = model.cvode
    amodel.ID = model.ID
    for oldrxn in model.reactions:
        newrxn = TReaction()
        
        newrxn.reactant1 = oldrxn.reactant1
        newrxn.reactant2 = oldrxn.reactant2
        newrxn.product1 = oldrxn.product1
        newrxn.product2 = oldrxn.product2
 
        newrxn.rateConstant = oldrxn.rateConstant
        newrxn.reactionType = oldrxn.reactionType
        amodel.reactions.append (newrxn)  
    return amodel
    
    
    
    
    
    
    
    
    
    