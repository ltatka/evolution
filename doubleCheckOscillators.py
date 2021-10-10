from oscillatorDB import mongoMethods as mm
import damped_analysis as da
import os

# results = mm.query_database({"oscillator": True, "num_nodes":3})
#
# fakers = 0
# faker_list = []
# for model in results:
#     damped, toInf = da.isModelDampled(model["model"])
#     if damped or toInf:
#         query = {"ID": model['ID']}
#         newVal = {"$set": {"oscillator": False}}
#         mm.collection.update_one(query, newVal)
#

dir = '/home/hellsbells/oldEv/PASS3'

def countReactions(astr):
    astr = astr.splitlines()
    reactionCount = 0
    for line in astr:
        if '->' in line and not line.startswith('#'):
            reactionCount += 1
        if line.startswith('k'):
            break
    return reactionCount

def isInDatabase(ID):
    ID = str(ID)
    query = {"ID": ID}
    result = mm.query_database(query)
    try:
        r = result[0]
        return True
    except IndexError:
        return False



fakers = 0
for file in os.listdir(dir):

    with open(os.path.join(dir, file), "r") as f:
        astr = f.read()
        f.close()

    damped, toInf = da.isModelDampled(astr)
    if damped or toInf:
        fakers += 1
        continue
    ID = file[6:-4]
    if not isInDatabase(ID):

        entry = {"ID": file[6:-4],
                 "num_nodes": 3,
                 "num_reactions": countReactions(astr),
                 "oscillator": True,
                 "model": astr,
                 "processed": False}

        mm.collection.insert_one(entry)
print(f'There are {fakers} fakers')