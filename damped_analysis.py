import os
import cleanUpMethods as clean
import tellurium as te
from scipy.signal import find_peaks
import math
import copy
import zipfile

import os
import numpy as np
from scipy.signal import find_peaks
import tellurium as te
import antUtils



def check_infinity(result):
    row, col = np.shape(result)
    # find max value at end
    max= 0
    maxCol = None
    for i in range(1, col):
        if result[row-1, i] > max:
            max = result[row-1, i]
            maxCol = i
    # If nothing ever exceeds max, then maxCol never is assigned. That means that concentrations either become
    # negative, or they huddle around zero (ie -1.23279e-15). Either way, we want to throw out this model,
    # so we'll return True even though it doesn't technically go to infinity.
    if not maxCol:
        return True
    # Get the average of a few clusters of points on the line and see if
    # they are increasing
    pts1 = np.mean([result[round(row/3), maxCol], result[round(row/3)+2, maxCol], result[round(row/3)+4, maxCol]])
    pts2 = np.mean([result[2*round(row / 3), maxCol], result[2*round(row / 3) + 2, maxCol],
                   result[2*round(row / 3) + 4, maxCol]])
    pts3 = np.mean([result[row-5, maxCol], result[row-3, maxCol], result[row-1, maxCol]])
    if pts1 < pts2 and pts2 < pts3 and pts3 > 2*pts1:
        return True # Goes to infinity
    else:
        return False


# Return True if the model is damped
def isModelDampled(antstr):
    r = te.loada(antstr)
    try:
        m1 = r.simulate(0, 100, 1000)
        m2 = r.simulate(0, 1000, 5000)
    except Exception:
       return True, None
    _, col = np.shape(m1)
    goesToInf = check_infinity(m2)
    #Look at each species:
    for i in range(1, col):
        peaks1, _ = find_peaks(m1[:, i], prominence=1)
        # If there are too few peaks, move on to next species
        # Otherwise simulate longer to check for damping
        if len(peaks1) < 4:
            continue
        peaks2, _ = find_peaks(m2[1000:, i], prominence=1)
        if len(peaks2) < 2: #* len(peaks1):
            continue
        else:
            return False, goesToInf
    return True, goesToInf



def process_damped(parent_dir, save_dir):
    antUtils.checkMakeDir(parent_dir)
    antUtils.checkMakeDir(save_dir)
    for filename in os.listdir(parent_dir):
        os.chdir(parent_dir)
        if not filename.endswith('.ant'):
            continue
        ant = antUtils.loadAntimonyText_noLines(filename)
        try:
            isDamped, toInf = isModelDampled(ant)
            if not isDamped and not toInf:
                os.chdir(save_dir)
                with open(f'{filename}', "w") as f:
                    f.write(ant)
                    f.close()
        except Exception as e:
            print(f"Fail: {filename}\n{e}")