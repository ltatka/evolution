# Evolve Oscillating Models

# Build sundials 
## (I'm not sure if this works all the time...)

    cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=../../sundials-install-mac ..
    cmake --build . --target install --config Release -j 12

This produces the standard sundials install tree inside the "sundials" folder.

# Setting up environment
To set up a conda evironment with all the dependencies
```conda env create -f env.yml```
(This works in linux, but not sure if it will elsewhere...)

# Change parameters
The parameters are located at line ~460 in evolve.py in a dictionary named defaultConfig. Edit as needed.

# Change number of batches
A batch is a single trial of the evolve.py script. Go to main.py and edit the BATCHNUM variable.

# To run
Open a terminal and navigate to folder where this module is stored. 
Don't forget to activate the conda environment: ```conda activate evolution-linux```
```python main.py```

I'll make this suck less later, I swear. 


