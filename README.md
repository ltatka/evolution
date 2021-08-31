# Evolve Oscillating Models

# Build sundials 
## (works for linux)

```
git submodule update --init --recursive

cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=sundials-install-linux sundials 

cmake --build . --target install --config Release -j 12`
```

# Setting up environment
To set up a conda evironment with all the dependencies
```conda env create -f env.yml```
(This works in linux, but not sure if it will elsewhere...)

# Quick start
To run a batch of evolution with the default parameters:
(first make sure you're in the sub directory evolution, (eg. /home/yourname/evolution/evolution)
```
python batchrun.py

```
# Change number of batches
To change the number of batches from the default (10), pass an optional argument:
```
python batchrun.py --runs 50
```

# Change parameters
Create a new .json file with desired parameters. Here's a template with the default configuration:
```
{"maxGenerations": 400,
  "sizeOfPopulation": 40,
  "massConserved": "True",
  "toZip": "False",
  "numSpecies": 10,
  "numReactions": 14,
  "rateConstantScale": 50,
  "probabilityMutateRateConstant": 0.7,
  "initialConditions": [1, 5, 9, 3, 10, 3, 7, 1, 6, 3, 10, 11, 4, 6, 2, 7, 1,9, 5, 7, 2, 4, 5, 10, 4, 1, 6, 7, 3, 2, 7, 8],
  "percentageCloned": 0.1,
  "percentageChangeInParameter": 0.15,
  "seed": -1,
  "threshold": 10.5,
  "frequencyOfOutput": 10}
  ```
When you run an evolution trial, you will have to pass the name of the new configuration file as an optional argument. 
```
python batchrun.py --newConfigFile <yourNewConfig>.json
```
