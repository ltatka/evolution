from oscillatorDB import mongoMethods as mm
import postprocessReactions as pp
import os
import damped_analysis
import tellurium as te

'''
This script was used (in uncommented chunks) to confirm or fix oscillators and controls. 
It was last used 2021-10-15 and the database was fixed to contain 586 3-node oscillators, 1000 3-node controls.
Every model has been processed. All controls are random (as opposed to broken or failed oscillators).
All oscillators are true oscillators that are not damped and do not go to infinity. 
This version of the database is backedup in the oscillator_backup repo on 2021-10-15
'''

# results = mm.query_database({"oscillator": True, "num_nodes": 3, "processed": False})
#
# updated = []
# incorrectAnalysis = []
# for model in results:
#     r = te.loada(model['model'])
#     r.simulate(0,1000,1000)
#     r.plot()
#     damped, toInf = damped_analysis.isModelDampled(model['model'])
#     print(f'Model is damped: {damped}\nModel goes to infinity: {toInf}')
#     answer = mm.yes_or_no('Is this correct?')
#     if answer:
#         newEntry = {"$set": {"oscillator": not damped,
#                              "isDamped": damped,
#                              "toInf": toInf}}
#         print(newEntry)
#         answer2 = mm.yes_or_no("Is this new entry correct?")
#         if answer2:
#             mm.collection.update_one({'ID': model["ID"]}, newEntry)
#             updated.append(model["ID"])
#         else:
#             incorrectAnalysis.append(model["ID"])
#     else:
#         incorrectAnalysis.append(model["ID"])

results = mm.query_database({"num_nodes": 3, "oscillator": True})
for model in results:
    if not model['ID'].startswith('control'):
        mm.delete_by_query({model['ID']})

# uploaded = []
# bad = []
# for index, model in enumerate(results):
#     r = te.loada(model["model"])
#     r.simulate(0,1000,1000)
#     r.plot(title='before')
#
#     ID = model["ID"]
#     amodel = pp.AntimonyModel(model['model'])
#     amodel.combineDuplicateRxns()
#     amodel.deleteUnnecessaryReactions()
#
#     r = te.loada(amodel.ant)
#     r.simulate(0,1000,1000)
#     r.plot(title='after')
#
#     uploadCorrect = mm.yes_or_no("Would you like to upload the modified model?")
#     if uploadCorrect:
#         updatedEntry = {"$set": {"model": amodel.ant,
#                                  "combinedReactions": amodel.combinedReactions,
#                                  "deletedReactions": amodel.deletedRxns,
#                                  "processed": True}}
#         query = {"ID": ID}
#         mm.collection.update_one(query, updatedEntry)
#         uploaded.append(ID)
#     else:
#         bad.append(ID)
#
# print(f"Updated {len(uploaded)} models.")
# # path = '/home/hellsbells/Desktop/3nodeControls'
# # os.chdir(path)
# # for file in os.listdir(path):
# #     with open(file, "r") as f:
# #         astr = f.read()
# #         f.close()
# #     ID = f'control{file[:-4]}'
# #     amodel = pp.AntimonyModel(astr)
# #     amodel.combineDuplicateRxns()
# #     entry = {"ID": ID,
# #              "num_nodes": 3,
# #              "num_reactions": len(amodel.reactions),
# #              "combinedReactions": amodel.combinedReactions,
# #              "deletedReactions": amodel.deletedRxns,
# #              "oscillator": False,
# #              "model": amodel.ant,
# #              "processed": True}
# #     mm.collection.insert_one(entry)
#
# query = {"num_nodes":3, "oscillator": False}
# results = mm.query_database(query)
# nRandomOscillators = 0
# for model in results:
#     astr = model["model"]
#     damped, toInf = damped_analysis.isModelDampled(astr)
#     if not damped and not toInf:
#         ID = model["ID"]
#         nRandomOscillators += 1
#         updatedEntry = {"$set": {"random_oscillator": True}}
#         query = {"ID": ID}
#         mm.collection.update_one(query, updatedEntry)
#
# print(f"Found {nRandomOscillators} random oscillators")