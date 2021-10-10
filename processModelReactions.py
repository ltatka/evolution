from oscillatorDB import mongoMethods as mm
import postprocessReactions as pp


results = mm.query_database({"oscillator": True, "num_nodes": 3, "processed": False})
for index, model in enumerate(results):
    if index%10 == 0:
        print(f'Working on model {index}')
    ID = model["ID"]
    amodel = pp.AntimonyModel(model['model'])
    amodel.combineDuplicateRxns()
    amodel.deleteUnnecessaryReactions()

    updatedEntry = {"$set": {"model": amodel.ant,
                             "combinedReactions": amodel.combinedReactions,
                             "deletedReactions": amodel.deletedRxns,
                             "processed": True}}
    query = {"ID": ID}
    mm.collection.update_one(query, updatedEntry)

