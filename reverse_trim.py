import numpy as np
import os
import copy
import zipfile
import json
import math
import tellurium as te
import shutil
import cleanUpMethods as clean
from datetime import datetime

NUM_TO_ADD = 8

model_directory = 'C:\\Users\\tatka\\Desktop\\Models\\OSCILLATOR\\'

save_fail_dir = os.path.join(model_directory, f'FAIL-addBack{NUM_TO_ADD}')
if not os.path.isdir(save_fail_dir):
    os.mkdir(save_fail_dir)

save_pass_dir = os.path.join(model_directory, 'PASS')
if not os.path.isdir(save_pass_dir):
    os.mkdir(save_pass_dir)

idx_dict = clean.loadNonEssRxnDict('C:\\Users\\tatka\\Desktop\\Models\\OSCILLATOR\\oscillators_dict.json')

errors = []

for filename in os.listdir(model_directory):
    if filename.endswith('.ant'):
        shortFileName = filename[:-4]
    else: shortFileName = filename
    if shortFileName in os.listdir(save_fail_dir):
        continue
    if not filename.startswith('Model'):
        continue
    count = 0
    os.chdir(model_directory)

    try:
        lines = clean.loadAntimonyText(filename)
    except Exception as e:
        errors.append(e)
        continue
    if filename.endswith('.zip') or filename.endswith('.ant'):
        filename = filename[:-4]

    # indices of non essential reactions:
    indices = idx_dict[filename]


    # Skip if there is 1 or 0 non essential reactions
    if len(indices) == 0 or len(indices) <= NUM_TO_ADD:
        continue

    # Comment out all the non essential reactions:
    for i in indices:
        lines[i] = '#' + lines[i]
    #Save the model with all non essential reactions commented out
    originalModel = copy.deepcopy(lines)
    # Make a list of every combo of <NUM_TO_ADD> reactions
    combos = clean.choose(indices, NUM_TO_ADD)
    # Uncomment one reaction at a time and see if it oscillates:
    for combo in combos:
        lines = copy.deepcopy(originalModel)
        for i in range(NUM_TO_ADD):
            lines[combo[i]] = lines[combo[i]][1:]  # Add the reactions
        ant = ''.join(lines)
        try:
            isDamped = clean.isModelDampled(ant)
        except Exception:
            isDamped = True

        if isDamped:
            saveTo = os.path.join(save_fail_dir, filename)
        else:
            saveTo = os.path.join(save_fail_dir,filename)

        if not os.path.isdir(saveTo):
            os.mkdir(saveTo)
        os.chdir(saveTo)
        name = os.path.join(saveTo, f'{filename}_{count}.ant')
        count += 1
        with open(name, 'w') as f:
            f.write(ant)
            f.close()

print(errors)
