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
        self.combinedReactions = [] # Reactions that are fused go here
        self.uneccessaryRxns = [] # Reactions that are removed without affecting oscillation go here

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
                return True
        return False

    def removeDuplicateRxns(self):
        self.makeRxnDict()
        self.reactions, self.rateConstants = self.processRxnDict()
        self.refactorModel()



    def makeRxnDict(self):
        # Create a dictionary for all reactions that has reaction and products sets as a tuple as the key and the
        # rate constant as a value. If a reaction is already in the dictionary, add the rate constants together.
        rxnDict = {}
        for i, rxn in enumerate(self.reactions):
            # Process products and reactants in reaction
            reactant, product = self.parseReactionString(rxn)
            # Get the rate constant value for the reaction
            k = float(self.rateConstants[i].split(' ')[2])
            # Make sure that product(s) and reactant(s) are not the same, then either add to
            # the reaction dictionary or update rate constant
            if reactant != product:
                reaction = self.reactionToString(Reaction(reactant, product, k))
                if self.rxnDictContains(reaction):
                    self.combinedReactions.append(rxn)
                    rxnDict[reaction] += k
                else:
                    rxnDict[reaction] = k
        self.rxnDict = rxnDict
        return rxnDict

    def reactantEqualProduct(self, reactant, product):


    # def getReadableRxnDict(self):
    #     readDict = {}
    #     for reaction in self.rxnDict.keys():
    #         readDict[self.reactionToString(reaction)] = reaction.k
    #     return readDict

    # def reactionToString(self, reaction):
    #     reactionStr = ''
    #     reactionStr += reaction.reactant[0]
    #     if len(reaction.reactant) == 2:
    #         reactionStr += f' + {reaction.reactant[1]}'
    #     reactionStr += f' -> {reaction.product[0]}'
    #     if len(reaction.product) == 2:
    #         reactionStr += f' + {reaction.product[1]}'
    #     return reactionStr

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
            return (reactants1 == reactants2) and (products1 == products1)
        # Bi-___: Check if reactants are equal and if they're equal when order is reversed
        if len(reactants1) == 2:
            sameReactants = (reactants1 == reactants2) or \
                            ([reactants1[1], reactants1[0]] == reactants2)
        else:
            sameReactants = reactants1 == reactants2
        if len(products1) == 2:
            sameProducts = (products1 == products2) or \
                            ([products1[1], products1[0]] == reactants2)
        else:
            sameProducts = products1 == products2
        return sameProducts and sameReactants

    def processRxnDict(self):
        # Make a reaction dictionary to combine duplicates
        # Convert the dictionary into two lists of strings: reactions and rate constants
        reactionList = []
        rateConstantList = []
        for index, item in enumerate(self.rxnDict):
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
            rateConstant = rateConstant + str(self.rxnDict[item])
            reactionList.append(reaction)
            rateConstantList.append(rateConstant)
        return reactionList, rateConstantList

    def refactorModel(self):
        # Combine lists of species, reactions, rate constants, and intitial conditions into an updated antimony model
        model = self.speciesList + self.reactions + self.rateConstants + self.initialConditions
        self.antLines = model
        self.ant = joinAntimonyLines(model)

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


ant = '''var S0
var S1
var S2
S2 -> S0; k0*S2
S0 -> S1+S0; k1*S0
S1 -> S0+S1; k2*S1
S1 -> S0+S2; k3*S1
S2 -> S0; k4*S2
S2 + S1 -> S2; k5*S2*S1
S0 -> S1+S0; k6*S0
S2 -> S1+S1; k7*S2
S2 -> S2+S2; k8*S2
S1 -> S0; k9*S1
S2 + S0 -> S1 + S2; k10*S2*S0
S1 + S1 -> S0 + S1; k11*S1*S1
S0 -> S0+S1; k12*S0
k0 = 7.314829248542936
k1 = 35.95227823979854
k2 = 41.54190920864631
k3 = 4.7667514994980555
k4 = 11.830987147018757
k5 = 15.50936673547638
k6 = 5.400180372157445
k7 = 8.171034267002623
k8 = 15.252690388653708
k9 = 7.202857436875558
k10 = 13.147047088765943
k11 = 7.20304738000393
k12 = 48.71489357141781
S0 = 1.0
S1 = 5.0
S2 = 9.0'''
#
model = AntimonyModel(ant)
model.makeRxnDict()
print(model.getReadableRxnDict())


# TODO:
'''
1. Method to check if products and reactants are the same
2. Finish make reaction dict
3. Test: parse, reactionEqualsProduct, dictContains, makeReactionDict
4. Move on the the other methods and fix/test those
'''