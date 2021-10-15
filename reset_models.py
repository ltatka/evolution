from oscillatorDB import mongoMethods as mm
import tellurium as te
from damped_analysis import isModelDampled


results = mm.query_database({"num_nodes": 3, "oscillator": True, "goesToInf": True})

updatedModels = []

notHere = []

for result in results:
    ID = result["ID"]
    try:
        with open(f'/home/hellsbells/Desktop/untarOsc/Model_{ID}.ant', 'r') as f:
            astr = f.read()
            f.close()
    except FileNotFoundError:
        notHere.append(ID)
        continue

    damped, infinity = isModelDampled(astr)

    if not damped and infinity==False:
        newEntry = {"$set": {"isDamped": False,
                             "processed": False},
                    "$unset": {"damped":1}}
        updatedModels.append(ID)
        mm.collection.update_one({'ID': ID}, newEntry)

print(f"fixed {len(updatedModels)} models")


query = {"num_nodes": 3, "oscillator": True, "goesToInf": True}
mm.query_database(query)

'''
Not yet fixed, in oscillator_backup
['37997',
 '41815',
 '4590',
 '61318',
 '68081',
 '72437',
 '75714',
 '2081027095831562333',
 '3943901525921347288',
 '2118106241530941419',
 '3568885974314290930',
 '1456575769372837239']

'''