import countReactions
import json
import os

from oscillatorDB import mongoMethods as mm

# Label Degradation



# Count Autocatal.
query = {"num_nodes": 3, "oscillator": True, "Autocatalysis Present": True}
models = mm.query_database(query)
for model in models:
    reactionDict = model["reactionCounts"]
    if reactionDict["Degradation"] > 0:
        newEntry = {"$set": {"Degradation Present": True}}
    else:
        newEntry = {"$set": {"Degradation Present": False}}
    mm.collection.update_one({'ID': model['ID']}, newEntry)


reactionDicts_control = countReactions.countAllReactions_query(query)
save_path = '~/Desktop/3nodeCounts_AutoOsc.csv'
auto_df = countReactions.writeOutCounts(save_path, reactionDicts_control)

# Count non Auto catal
query = {"num_nodes": 3, "oscillator": True, "Autocatalysis Present": False}
models = mm.query_database(query)
for model in models:
    reactionDict = model["reactionCounts"]
    if reactionDict["Degradation"] > 0:
        newEntry = {"$set": {"Degradation Present": True}}
    else:
        newEntry = {"$set": {"Degradation Present": False}}
    mm.collection.update_one({'ID': model['ID']}, newEntry)

reactionDicts_oscillator = countReactions.countAllReactions_query(query)
save_path = '~/Desktop/3nodeCounts_nonAutoOsc.csv'
non_auto_df = countReactions.writeOutCounts(save_path, reactionDicts_oscillator)

# store count dicts as json files
os.chdir('/home/hellsbells/Desktop')
with open('controlCountDict.json', 'w') as outfile1:
    json.dump(reactionDicts_control, outfile1)
with open('oscillatorCountDict.json', 'w') as outfile2:
    json.dump(reactionDicts_oscillator, outfile2)

stat = countReactions.pAutocatalysisPortion(auto_df['Degradation Present'], non_auto_df['Degradation Present'])
print(stat)


