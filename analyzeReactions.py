import pandas as pd
from oscillatorDB import mongoMethods as mm
'''
For each reaction in the database:
1. Count reactions
2. Make dictionary of reaction types
3. Upload reaction type dictionary 
    no autocatalyis: T/F

Let's make the pandas spread sheet average portions

4. append average portions to list


'''

def countReactions(astr):
    # Returns dictionary of reaction counts
    uni_uni = 0
    uni_bi = 0
    bi_uni = 0
    bi_bi = 0
    degrade = 0
    autocatalysis = 0
    total = 0
    lines = astr.splitlines()
    for line in lines:
        if '->' in line and not line.startswith('#'):
            total += 1
            line = line.replace(' ', '')  # strip spaces
            # separate products and reactants by splitting at ->
            reaction = line.split('->')
            reactants = reaction[0]
            # Remove the rate constant part
            products = reaction[1].split(';')[0]
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

            if rxnType == 'uni-uni':
                uni_uni += 1
            elif rxnType == 'uni-bi':
                uni_bi += 1
                # Separate products (reactants is already just one item
                products = products.split('+')
                if reactants in products:
                    autocatalysis += 1
            elif rxnType == 'bi-uni':
                bi_uni += 1
                # products is already one item, need to split reactants
                reactants = reactants.split('+')
                if products in reactants:
                    degrade += 1
            else:  # bi-bi
                bi_bi += 1
                # We should have already checked for null reactions, where reactant and product are the same,
                # so we're not going to check for that here.
                # Separate products and reactants
                reactants = reactants.split('+')
                products = products.split('+')
                if reactants[0] in products or reactants[1] in products:
                    autocatalysis += 1
        else:  # if the line is not a reaction, move to the next line
            continue
    # This dictionary contains the PORTION of each reaction type
    rxnDict = {
        'uni-uni': uni_uni/total,
        'bi-uni': bi_uni/total,
        'uni-bi': uni_bi/total,
        'bi-bi': bi_bi/total,
        'autocatalysis': autocatalysis/total,
        'degradation': degrade/total,
        'total': total
    }
    return rxnDict


query = {'num_nodes': 3, 'oscillator': True}
models = mm.query_database(query)

all_nReactions = []

all_uniuni_portion = []
all_unibi_portion = []
all_biuni_portion = []
all_bibi_portion = []

all_degradation_portion = []
all_autocatalysis_portion = []

no_autocatalysis = []

all_ID = []
all_massConserved = []


for model in models:
    all_ID.append(model['ID'])
    all_massConserved.append(model['mass_conserved'])
    reactions = countReactions(model['model'])
    all_nReactions.append(reactions['total'])
    all_uniuni_portion.append(reactions['uni-uni'])
    all_unibi_portion.append(reactions['uni-bi'])
    all_biuni_portion.append(reactions['bi-uni'])
    all_bibi_portion.append(reactions['bi-bi'])
    all_degradation_portion.append(reactions['degradation'])
    all_autocatalysis_portion.append(reactions['autocatalysis'])
    if reactions['autocatalysis'] == 0:
        no_autocatalysis.append(True)
    else:
        no_autocatalysis.append(False)

df = pd.DataFrame()
df['ID'] = all_ID
df['Mass Conserved'] = all_massConserved
df['No Autocatalysis'] = no_autocatalysis
df['Portion Degradation'] = all_degradation_portion
df['Portion Autocatalysis'] = all_autocatalysis_portion
df['Portion Uni-Uni'] = all_uniuni_portion
df['Portion Uni-Bi'] = all_unibi_portion
df['Portion Bi-Uni'] = all_biuni_portion
df['Portion Bi-Bi'] = all_bibi_portion
df['Total Reactions'] = all_nReactions
df.set_index('ID')
df.to_csv(path_or_buf='/home/hellsbells/Desktop/ReactionCounts/3NodeOscillator.csv')