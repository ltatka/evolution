import isMassConserved
from oscillatorDB import mongoMethods as mm
import antimony_ev2 as aModel
import os
from cleanUpMethods import isModelDampled
import damped_analysis as da

updateDatabase = True
collection = mm.collection


if updateDatabase:
    QUERY = {'num_nodes': 10, 'oscillator': True}
    models = mm.query_database(QUERY)
    count = 0
    for model in models:
        print(model['ID'])
        idQuery = {'ID': model['ID']}
        antModel = aModel.AntimonyModel(model['model'])
        antModel.deleteUnecessaryReactions()
        nReactions = len(antModel.reactions)
        damped, toInf = isModelDampled(antModel.ant)
        mass = isMassConserved.isMassConserved_single(antModel.ant)
        if not damped and not toInf:
            update = {"$set": {
                'model': antModel.ant,
                "num_reactions": nReactions,
                'mass_conserved': mass}}
            collection.update_one(idQuery, update)
        count += 1
        if count%10 == 0:
            print(count)
    print(f'processed {count} models')

else:
    PATH = '/home/hellsbells/Desktop/unprocessedModels'
    save_dir = '/home/hellsbells/Desktop/oscillators'
    rxn_processed_dir = '/home/hellsbells/Desktop/rxnProcessed'
    source_dir = save_dir
    true_dir = '/home/hellsbells/Desktop/MassConserved'
    false_dir = '/home/hellsbells/Desktop/massNotConserved'
    # Check if any of the models are damped or go to infinity:
    da.process_damped(PATH, save_dir)
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


