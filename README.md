# Evolve Oscillating Models

### Note: I wrote and tested everything in Linux (Ubuntu) and I'm not sure if it works on other platforms


# Installation
Clone or fork this repo. To clone: 

```git clone https://github.com/really-lilly/evolution.git```

# Build sundials 
Navigate to the evolution directory (```cd evolution```)

Run this code block to initialize the submodules, navigate to the build files in Sundials, build Sundials (the ODE solver), and then return to the evolution directory.

<b> Be sure to replace <platform> with whatever system you're using (eg sundials-install-linux). </b>
  * Linux: linux
  * Windows: win32

Your system is the output of the python command ```sys.platform```

```
git submodule update --init --recursive

cd sundials

mkdir build
cd build
 
# If you are using the cluster, use 'module load cmake' here 

cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=../../sundials-install-<platform> ..
cmake --build . --target install --config Release -j 12

cd ../..
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
  "toZip": "True",
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
# Error Fixes
 If you build and run the program on the cluster and come across this error:
 ![image](https://user-images.githubusercontent.com/63520222/171741202-c1610d8a-0ba5-4c54-af42-0fec5675debf.png)
 
 This is annoying but the way I ended up fixing this was to clone the sundials repo from https://github.com/LLNL/sundials.git
And then build using the following commands:
 ```
 cd sundials
 
 mkdir builddir
 cd builddir
 
 cmake -DCMAKE_INSTALL_PREFIX=../install-release -DCMAKE_BUILD_TYPE=Release -DEXAMPLES_ENABLE=ON -DBUILD_SHARED_LIBS=ON ..

 make -j12

 make install
```
 You might want to check if this version of sundials works by running one of the examples.
 
 Building sundials will create a directory called ```install-release```. Note the location of this directory. 
 
 Then go back into the evolution directory and edit the uLoadCvode.py file. Edit the file so that the variable SUNDIALS_INSTALL_PREFIX is the path to the install-release directory. 
 
 This is super sketchy and I'll maybe make a more official fix later, but writing this down in case this issue comes up again.
 
