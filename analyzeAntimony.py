import os
import numpy as np
import pandas as pd
import isMassConserved
import damped_analysis as da
from oscillatorDB import mongoMethods as mm
import antimony_ev2 as aModel
from shutil import rmtree


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
            elif rxnType == 'bi-bi':  # bi-bi
                bi_bi += 1
                # We should have already checked for null reactions, where reactant and product are the same,
                # so we're not going to check for that here.
                # Separate products and reactants
                reactants = reactants.split('+')
                products = products.split('+')
                if (reactants[0] == products[0] and reactants[0] == products[1]) or \
                        (reactants[1] == products[0] and reactants[1] == products[1]):
                    autocatalysis += 1
        else:  # if the line is not a reaction, move to the next line
            continue
    # This dictionary contains the PORTION of each reaction type
    rxnDict = {
        'uni-uni': uni_uni / total,
        'bi-uni': bi_uni / total,
        'uni-bi': uni_bi / total,
        'bi-bi': bi_bi / total,
        'autocatalysis': autocatalysis / total,
        'degradation': degrade / total,
        'total': total
    }
    return rxnDict


def analyzeReactions(writeOutPath, fromDatabase=True, query=None, directory=None):
    if fromDatabase and not query:
        raise ValueError('Database analyses require a query')
    elif not fromDatabase and not directory:
        raise ValueError('Local analyses require a directory')
    if fromDatabase:
        models = mm.query_database(query)
    else:
        os.chdir(directory)
        models = os.listdir(directory)
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
        if fromDatabase:
            ID = model['ID']
            astr = model['model']
            mass_conserved = model['mass_conserved']
        else:
            ID = model[:-4]
            with open(model, "r") as f:
                astr = f.read()
                f.close()
            mass_conserved = isMassConserved.isMassConserved_single(astr)
        all_ID.append(ID)
        all_massConserved.append(mass_conserved)
        reactions = countReactions(astr)
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
    # Create and write out dataframe:
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
    df.to_csv(path_or_buf=writeOutPath)

    print(np.mean(all_uniuni_portion), np.mean(all_unibi_portion), np.mean(all_biuni_portion),
          np.mean(all_bibi_portion))

def processModels(source_dir):
    save_dir = os.path.join(os.getcwd(), 'oscillators')
    os.mkdir(save_dir)
    rxn_processed_dir = os.path.join(os.getcwd(), 'rxnProcessed')
    os.mkdir(rxn_processed_dir)
    true_dir = os.path.join(os.getcwd(), 'massConserved')
    os.mkdir(true_dir)
    false_dir = os.path.join(os.getcwd(), 'massNotConserved')
    os.mkdir(false_dir)
    # Check if any of the models are damped or go to infinity:
    da.process_damped(source_dir, save_dir)
    # Get rid of duplicate or null reactions:
    for model in os.listdir(save_dir):
        os.chdir(save_dir)
        # Open the model and read the antimony string:
        with open(model, 'r') as f:
            ant_str = f.read()
            f.close()
        # process the antimony string and eliminate any duplicate or null reactions:
        antModel = aModel.AntimonyModel(ant_str)
        antimony = antModel.ant
        # Save the processed model:
        path = os.path.join(rxn_processed_dir, model)
        with open(path, 'w') as f:
            f.write(antimony)
            f.close()
        del antModel
    # Sort the processed models to mass conserved or not:
    isMassConserved.isMassConserved(rxn_processed_dir, true_dir, false_dir)
    # Delete the temporary directories
    rmtree(rxn_processed_dir)
    rmtree(save_dir)
    print(f'Processed models stored in:\n{true_dir}\n{false_dir}')



