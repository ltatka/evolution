import sys
import mongoMethods as mm
import cleanUpMethods as clean

num_nodes = int(sys.argv[-2])
oscillator = bool(sys.argv[-1])

total = len(sys.argv[1:-2])

count = 0
for file in sys.argv[1:-2]:
    try:
        ant = clean.extractAnt(file)
        num_reactions = mm.get_nReactions(ant)
        filename = file.split('/')[-1]
        ID = mm.extract_id(filename)
        dictionary = {
            'ID' : ID,
            'num_nodes' : num_nodes,
            'num_reactions' : num_reactions,
            'oscillator' : oscillator,
            'model' : ant
        }
        mm.add_one(dictionary)
        count += 1
    except:
        continue

print(f"Added {count} of {total} models")