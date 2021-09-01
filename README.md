# Evolve Oscillating Models

# Build sundials 

```
git submodule update --init --recursive

cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=sundials-install-linux sundials 

cmake --build . --target install --config Release -j 12
```

# Setting up environment
To set up a conda evironment with all the dependencies
```conda env create -f environment.yml```
(This works in linux, but not sure if it will elsewhere...)

# Quick start
To run a batch of evolution with the default parameters:
(first make sure you're in the sub directory evolution, (eg. /home/yourname/evolution/evolution)
```
python batchrun.py
```
# Optional arguments
There are four optional arguments that can be used in any combination and order. 

```python batchrun.py --runs 50``` Change the number of times the evolution script is run. The default is 10. 

```python batchrun.py --numGenerations 500```Change the number of generations evolved with each run. The default is 400.

```python batchrun.py --probabilities 0.3 0.3 0.3 0.1``` Change the probability of each reaction type when generating random networks. Order is UniUni, UniBi, BiUni, BiBi. The default is 0.1, 0.4, 0.4, 0.1

```python batchrun.py --newConfigFile newParams.json```Use a new configuration file (see 'Change parameters' section below for defaults and instructions.


# Change parameters
Create a new .json file with desired parameters. Here's a template with the default configuration:
```
{"maxGenerations": 400,
  "sizeOfPopulation": 40,
  "massConserved": "False",
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
To use your new configuration, pass it as an optional argument when running batchrun
```
python batchrun.py --newConfigFile <yourNewConfig>.json
```
