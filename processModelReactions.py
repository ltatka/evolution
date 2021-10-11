from oscillatorDB import mongoMethods as mm
import postprocessReactions as pp
import os


# results = mm.query_database({"oscillator": True, "num_nodes": 3, "processed": False})
# for index, model in enumerate(results):
#     if index%10 == 0:
#         print(f'Working on model {index}')
#     ID = model["ID"]
#     amodel = pp.AntimonyModel(model['model'])
#     amodel.combineDuplicateRxns()
#     amodel.deleteUnnecessaryReactions()
#
#     updatedEntry = {"$set": {"model": amodel.ant,
#                              "combinedReactions": amodel.combinedReactions,
#                              "deletedReactions": amodel.deletedRxns,
#                              "processed": True}}
#     query = {"ID": ID}
#     mm.collection.update_one(query, updatedEntry)

path = '/home/hellsbells/Desktop/3nodeControls'
os.chdir(path)
for file in os.listdir(path):
    with open(file, "r") as f:
        astr = f.read()
        f.close()
    ID = f'control{file[:-4]}'
    amodel = pp.AntimonyModel(astr)
    amodel.combineDuplicateRxns()
    entry = {"ID": ID,
             "num_nodes": 3,
             "num_reactions": len(amodel.reactions),
             "combinedReactions": amodel.combinedReactions,
             "deletedReactions": amodel.deletedRxns,
             "oscillator": False,
             "model": amodel.ant,
             "processed": True}
    mm.collection.insert_one(entry)