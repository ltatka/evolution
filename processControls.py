import postprocessReactions as pp
from oscillatorDB import mongoMethods as mm

# Delete the current 3-node non-oscillators in database

query = {"num_nodes": 3, "oscillator": False}

results = mm.query_database(query)
for model in results:
    ID = model["ID"]
    mm.collection.delete_one({"ID": ID})