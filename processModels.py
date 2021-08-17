import isMassConserved
from oscillatorDB import mongoMethods as mm
import antimony_ev2 as aModel
import damped_analysis as da
updateDatabase = False
import os
from shutil import move
collection = mm.collection


if updateDatabase:
    QUERY = {'num_nodes': 10, 'oscillator': True}
    models = mm.query_database(QUERY)
    print(models[0]['model'])
    #print(f'Found {len(models)}')
    count = 0
    for model in models:
        antModel = aModel.AntimonyModel(model['model'])
        nReactions = len(antModel.reactions)
        update = {"$set" : {'model' : antModel.ant, "num_reactions" : nReactions}}
        collection.update_one(QUERY, update)
        count += 1
        if count%10 == 0:
            print(count)
    print(f'processed {count} models')

else:
    PATH = '/home/hellsbells/Desktop/4-node-massconserved'
    save_dir = '/home/hellsbells/Desktop/3node-oscillate'
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


