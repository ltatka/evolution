import numpy as np
import tellurium as te
import random
from copy import deepcopy
from damped_analysis import isModelDampled




def joinAntimonyLines(antLines):
    if antLines[0] == '':
        antLines = antLines[1:]
    return '\n'.join(antLines)







class PostInitCaller(type):
    def __call__(cls, *args, **kwargs):
        obj = type.__call__(cls, *args, **kwargs)
        obj.post_init()
        return obj


class AntimonyModel(object, metaclass=PostInitCaller):
    rxnDict = {}
    # pDeleteRxn = .50
    # pDelete1 = .45
    # pDelete2 = .35
    # rateConstantRange = .1
    # pKeepWorseModel = 1

    def __init__(self, ant_str, delUnnecessaryRxn=True):
        # If delUnnecessaryRxn, then try to remove reactions one by one and maintain oscillation
        self.ant = ant_str
        self.antLines = []
        self.reactions = []
        self.speciesList = []
        self.initialConditions = []
        self.rateConstants = []
        self.nFloats = 0
        self.fitness = 1E17
        self.nSpecies = 0
        self.rxnDict = {}
        self.combinedReactions = [] # Reactions that are fused go here
        self.deletedRxns = [] # Reactions that are removed without affecting oscillation go here

    def post_init(self):
        # Separate antimony model into lists of reactions, floating and boundary species, rate contsants,
        # and initial conditions
        # Then fuse duplicate reactions
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
        # del self.ant
        self.ant = newAnt
        # self.removeDuplicateRxns()

    def rxnDictContains(self, reaction):
        for key in self.rxnDict.keys():
            if self.rxnIsEqual(reaction, key):
                return True, key
        return False, None

    def combineDuplicateRxns(self):
        if not self.rxnDict:
            self.makeRxnDict()
        self.reactions, self.rateConstants = self.processRxnDict()
        self.refactorModel()
        return self.ant



    def makeRxnDict(self):
        # Create a dictionary for all reactions that has reaction and products sets as a tuple as the key and the
        # rate constant as a value. If a reaction is already in the dictionary, add the rate constants together.
        for i, rxn in enumerate(self.reactions):
            # Get the rate constant value for the reaction
            reaction, k = self.isolateReaction(rxn)
            # Make sure that product(s) and reactant(s) are not the same, then either add to
            # the reaction dictionary or update rate constant
            if not self.reactantEqualsProduct(rxn):
                contains, key = self.rxnDictContains(reaction)
                if contains:
                    self.combinedReactions.append(reaction)
                    self.rxnDict[key] += k
                else:
                    self.rxnDict[reaction] = k
        return self.rxnDict

    def reactantEqualsProduct(self, reaction):
        reactant, product = self.parseReactionString(reaction)
        if len(reactant) != len(product):
            return False
        if len(reactant) == 1:
            return reactant == product
        return reactant == product or [reactant[1], reactant[0]] == product


    def isolateReaction(self, reaction):
        # separate the rate law portion of a reaction
        reaction = reaction.replace('\n', '') # remove newline character if present
        reaction = reaction.split(';')
        k = self.getK(reaction[1])
        return reaction[0], k

    def getK(self, rateLaw):
        rateLaw = rateLaw.replace(' ', '')
        k = rateLaw.split('*')[0]
        for constant in self.rateConstants:
            if constant.startswith(k):
                k = constant.split('=')[1]
                return float(k.split('#')[0])# remove commented out value, if present

    def parseReactionString(self, reaction):
        rxn = reaction.replace(' ', '')
        reactionSplit = rxn.split('->')
        reactant = reactionSplit[0]
        productSplit = reactionSplit[1].split(';')
        product = productSplit[0]
        if '+' in reactant:
            reactant = reactant.split('+')
        else:
            reactant = [reactant]
        if '+' in product:
            product = product.split('+')
        else:
            product = [product]
        return reactant, product

    def rxnIsEqual(self, rxn1, rxn2):
        reactants1, products1 = self.parseReactionString(rxn1)
        reactants2, products2 = self.parseReactionString(rxn2)
        # If they are different sizes, then obviously they're not the same reaction
        if (len(reactants1) != len(reactants2)) or (len(products1) != len(products2)):
            return False
        # Uni-uni: just check if reactants and products are the same for both reactions
        if len(reactants1) == 1 and len(products1) == 1:
            return (reactants1 == reactants2) and (products1 == products2)
        # Bi-___: Check if reactants are equal and if they're equal when order is reversed
        if len(reactants1) == 2:
            sameReactants = (reactants1 == reactants2) or \
                            ([reactants1[1], reactants1[0]] == reactants2)
        else:
            sameReactants = reactants1 == reactants2
        if len(products1) == 2:
            sameProducts = (products1 == products2) or \
                            ([products1[1], products1[0]] == products2)
        else:
            sameProducts = products1 == products2
        return sameProducts and sameReactants

    def processRxnDict(self):
        # Make a reaction dictionary to combine duplicates
        # Convert the dictionary into two lists of strings: reactions and rate constants
        reactionList = []
        rateConstantList = []
        for index, key in enumerate(self.rxnDict.keys()):
            rateConstant = f'k{index} = {self.rxnDict[key]}'
            # Add rate law to the reaction string:
            reaction = key
            rateLaw = f'; k{index}*'
            reactant, _ = self.parseReactionString(key)
            rateLaw += reactant[0]
            if len(reactant) == 2:
                rateLaw += f'*{reactant[1]}'
            reaction = reaction + rateLaw
            reactionList.append(reaction)
            rateConstantList.append(rateConstant)
        self.reactions = reactionList
        self.rateConstants = rateConstantList
        return reactionList, rateConstantList

    def refactorModel(self):
        # Combine lists of species, reactions, rate constants, and intitial conditions into an updated antimony model
        model = self.speciesList + self.reactions + self.rateConstants + self.initialConditions
        self.antLines = model
        self.ant = joinAntimonyLines(model)
        return self.ant

    def deleteUnnecessaryReactions(self):
        idxToRemove = []
        for i, reaction in enumerate(self.reactions):
            self.reactions[i] = '#' + self.reactions[i]
            self.refactorModel()
            damped, toInf = isModelDampled(self.ant)
            # If it the commented reaction does not break the model, add it to list of deleted rate reactions
            # and tag it's index for deletion. Keep it commented
            if not damped and toInf==False:
                idxToRemove.append(i)
                self.deletedRxns.append(self.reactions[i][1:])
            # if it needs the reaction to oscillate, uncomment it
            else:
                self.reactions[i] = self.reactions[i][1:]
                self.refactorModel()
        # Delete the tagged indices in rate constant list and reaction list
        self.rateConstants = [i for j, i in enumerate(self.rateConstants) if j not in idxToRemove]
        self.reactions = [i for j, i in enumerate(self.reactions) if j not in idxToRemove]
        self.refactorModel()


