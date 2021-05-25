import json

config = {"key1": 1.2, 
              "address": {"house": "Penrodyn"}, 
          "key2": "value2"}

with open('config1.json', 'w') as f:
    json.dump(config, f)
    
with open('config1.json', 'r') as f:
    config = json.load(f)

#edit the data
config['key1'] = 3.1415

#write it back to the file
with open('config1.json', 'w') as f:
    json.dump(config, f)
    
    