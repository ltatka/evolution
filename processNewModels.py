from oscillatorDB import mongoMethods as mm
import os
from damped_analysis import isModelDampled
import postprocessReactions as pp
import countReactions as cr

def isInDatabase(ID):
    result = mm.query_database({"ID": ID})
    try:
        result[0]
        return True
    except IndexError:
        return False


possibleDupes = []

directory = "/home/hellsbells/Desktop/0104Controls"
os.chdir(directory)
for model in os.listdir(directory):
    if not model.startswith("Control"):
        continue

    #
    ID = model[:-4]
    # print(ID)
    # if isInDatabase(ID):
    #     print("lol")
    #     possibleDupes.append(ID)
    #     continue

    with open(model, "r") as f:
        antimony = f.read()
        f.close()

    # # Check if it's damped or infinity
    # damped, toInf = isModelDampled(antimony)
    # if damped or toInf or toInf == None:
    #     continue

    amodel = pp.AntimonyModel(antimony)
    amodel.combineDuplicateRxns()

    amodel.deleteUnnecessaryReactions()
    damped, toInf = isModelDampled(amodel.ant)
    # if damped or toInf or toInf == None:
    #     continue

    newEntry = { "ID": ID,
                 # "num_nodes": 3,
                 # "oscillator": False,
                 # "initialProbabilities": [0.1, 0.4, 0.4, 0.1],
                 # "addReactionProbabilities": [0.1, 0.4, 0.4, 0.1],
                 # "isDamped": damped,
                 # "goesToInf": toInf,
                 "model": amodel.ant,
                 "combinedReactions": amodel.combinedReactions,
                 "deletedReactions": amodel.deletedRxns,
                 "processed": True,
                 "num_reactions": len(amodel.reactions),
                 # "isControl": True,
                 # "allowAC": True
                 }
    mm.collection.insert_one(newEntry)
#
query = {"num_nodes": 3, "oscillator": True} #"Autocatalysis Present": False}
counts = cr.countAllReactions_query(query)
# counts = cr.gatherCounts_query(query)

path = "/home/hellsbells/Desktop/0104ProbAC_control.csv"
cr.writeOutCounts(path,counts)
print(possibleDupes)

