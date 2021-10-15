'''
1. Determine the number of random models that go to infinity.
2. Of those that do NOT go to infinity, how many have autocatalytic reactions?
'''

from oscillatorDB import mongoMethods as mm
import damped_analysis


query = {"num_nodes": 3, "oscillator": True}
results = mm.query_database(query)

infinityModels = 0
isDamped = 0

for model in results:
    astr = model["model"]
    ID = model["ID"]
    damped, goesToInf = damped_analysis.isModelDampled(astr)
    query = {"ID": ID}
    if goesToInf:
        infinityModels += 1
    if damped:
        isDamped +=1
    newEntry = {"$set": {"isDamped": damped,
                         "goesToInf": goesToInf}}
    mm.collection.update_one(query, newEntry)

print(f"Found {infinityModels} models that go to infinity and {isDamped} damped")
#
# query = {"num_nodes": 3, "oscillator": True, "reactionsCounted": True}
# hasAutocatalysis_inf = 0
# hasAutocatalysis_notInf = 0
# hasAutocatalysis_None = 0
# results = mm.query_database(query)
# hasAutocatalysis_inf_IDs = []
# hasAutocatalysis_None_IDs = []
# for model in results:
#     query = {"ID": model["ID"]}
#     rxnDict = model['reactionCounts']
#     autocatalysis = rxnDict['Autocatalysis'] > 0.
#     if model["goesToInf"]:
#         hasAutocatalysis_inf += int(autocatalysis)
#         hasAutocatalysis_inf_IDs.append(model["ID"])
#     elif model["goesToInf"] == False:
#         hasAutocatalysis_notInf += int(autocatalysis)
#     elif model["goesToInf"] == None:
#         hasAutocatalysis_None += int(autocatalysis)
#         hasAutocatalysis_None_IDs.append(model["ID"])
#     newEntry = {"$set": {'Autocatalysis Present': autocatalysis}}
#     mm.collection.update_one(query, newEntry)
#
# print(f'Found {hasAutocatalysis_inf} infinity models with autocatalysis')
# print(f'Found {hasAutocatalysis_notInf} not infinity models with autocatalysis')
# print(f'Found {hasAutocatalysis_None} un-simulated models with autocatalysis')
#
