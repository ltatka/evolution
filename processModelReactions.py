from oscillatorDB import mongoMethods as mm
import postprocessReactions as pp
import countReactions as cr

query = {"oscillator": True, "num_nodes": 3}

models = mm.query_database(query)

for model in models:
    amodel = pp.AntimonyModel(model["model"])
    amodel.combineDuplicateRxns()
    amodel.deleteUnnecessaryReactions()

    updatedEntry = {"$set": {"model": amodel.ant,
                             "combinedReactions": amodel.combinedReactions,
                             "deletedReaction": amodel.deletedRxns,
                             "num_reactions": len(amodel.reactions)}}
    mm.collection.update_one({"ID": model["ID"]}, updatedEntry)

cr.countAllReactions_query(query)
