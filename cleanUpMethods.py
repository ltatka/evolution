import tellurium as te
import roadrunner
import copy, sys, os, math, getopt, json, time, zipfile, shutil
from scipy.signal import find_peaks
import json
import numpy as np







def stringToList(indices):
    indices = indices.split(', ')
    indices[0] = indices[0][1:]
    if len(indices) > 1:
        indices[-1] = indices[-1][:-2]
    for i in range(len(indices)):
        indices[i] = int(indices[i])
    return indices


def makeNonEssRxnDict(modelPath, savePath):
    # e.g. file = './data.json'
    modelPath = 'C:\\Users\\tatka\\Desktop\\Models\\OSCILLATOR'
    indices_dict = {}
    for filename in os.listdir(modelPath):
        os.chdir(modelPath)
        if filename.startswith('Model'):
            modelPath = os.path.join(modelPath, filename)
            os.chdir(modelPath)
            for file in os.listdir(modelPath):
                if file.endswith('summary.txt'):
                    with open(file, "r") as f:
                        lines = f.readlines()
                        f.close()
                    model = lines[0].split(' = ')[1][:-5]
                    indices = lines[4].split(' = ')[1]
                    indices = stringToList(indices)
                    indices_dict[model] = indices
    with open(os.path.join(modelPath, 'oscillators_dict.json'), 'w') as f:
        json.dump(indices_dict, f)


def loadNonEssRxnDict(path):
    with open(path, 'r') as f:
        idx_dict = json.load(f)
    return idx_dict


