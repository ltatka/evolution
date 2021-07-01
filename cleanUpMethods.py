import tellurium as te
import roadrunner
import copy, sys, os, math, getopt, json, time, zipfile, shutil
from scipy.signal import find_peaks
import json
import numpy as np


def readSavedRun(fileName):
    zf = zipfile.ZipFile(fileName, 'r')
    data = zf.read('summary.txt').decode("utf-8")
    data = data.splitlines()
    numGenerations = int(data[5].split('=')[1])
    numPopulation = int(data[6].split('=')[1])
    # print ("Number of Generations = ", numGenerations)
    # print ("Size of population in each generation =", numPopulation)
    return zf


def getNumGenerations(zip_file):
    data = zip_file.read('summary.txt').decode("utf-8")
    data = data.splitlines()
    return int(data[5].split('=')[1])


def readModel(zf, generation, individual):
    fileName = "populations/generation_" + str(generation) + '/individual_' + str(individual) + '.txt'
    ant = zf.read(fileName).decode("utf-8")
    ant = ant.splitlines()
    if ant[0].startswith('#'):
        ant = ant[1:]
    zf.close()
    return ant


def test_readModel():
    zf = readSavedRun("C:\\Users\\tatka\\Desktop\\Models\\FAIL\\FAIL_Model_128987634590189990.zip")
    ant = readModel(zf, 499, 0)
    print(ant)


def findStart(lines):
    for index, line in enumerate(lines):
        line = line.split(' ')
        if line[0] != 'var' and (line[0] != 'ext'):
            return index


def findEnd(lines):
    for index, line in enumerate(lines):
        if line[0] == 'k':
            return index


def countEig(eig):
    numConjugates = 0
    for eigenvalue in eig:
        if abs(eigenvalue.imag) > 0.1:
            numConjugates += 1
    return numConjugates


# Return True if the model is damped
def isModelDampled_OLD(antstr):
    dampled = False
    r = te.loada(antstr)
    try:
        m = r.simulate(0, 100, 1000)
        peaks, _ = find_peaks(m[:, 2], prominence=1)
        nPeaks = len(peaks)
        print(f"100sec peaks: {nPeaks}")
        if nPeaks <= 4:
            return True
        else:
            # It could be damped
            try:
                m = r.simulate(0, 1000, 5000)
                peaks, _ = find_peaks(m[:, 2], prominence=1)
                nPeaks2 = len(peaks)
                print(nPeaks2)
                if nPeaks2 == 0 or nPeaks2 <= nPeaks * 3:
                    m = r.simulate(500, 600, 1000)
                    peaks, _ = find_peaks(m[500:, 2], prominence=1)
                    nPeaks3 = len(peaks)
                    print(nPeaks3)
                    return True

            except Exception:
                return True
    except Exception:
        return True
    return dampled

''' I think I need to totally rewrite this so it looks at every species for oscillation and damped'''

# Return True if the model is damped
def isModelDampled(antstr):

    r = te.loada(antstr)
    try:
        m1 = r.simulate(0, 100, 1000)
        m2 = r.simulate(0, 1000, 5000)
    except Exception:
        return True
    _, col = np.shape(m1)
    #Look at each species:
    for i in range(1, col):
        peaks1, _ = find_peaks(m1[:, i], prominence=1)
        # If there are too few peaks, move on to next species
        # Otherwise simulate longer to check for damping
        if len(peaks1) < 4:
            continue
        peaks2, _ = find_peaks(m2[:, i], prominence=1)
        if len(peaks2) < 2 * len(peaks1):
            continue
        else:
            return False # If we get this far, it's NOT damped
    return True # DAMPED


def choose_iter(elements, length):
    for i in range(len(elements)):
        if length == 1:
            yield (elements[i],)
        else:
            for next in choose_iter(elements[i + 1:len(elements)], length - 1):
                yield (elements[i],) + next


def choose(l, k):
    return list(choose_iter(l, k))


def nChooseK(n, k):
    return int(math.factorial(n) / (math.factorial(k) * math.factorial(n - k)))


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


def loadAntimonyText(path):
    with open(path, "r") as f:
        ant = f.read()
        f.close()
    lines = ant.split('\n')
    # First line is comment for fitness, ignore
    if lines[0].startswith('#'):
        lines = lines[1:]
    return lines


def loadAntimonyText_noLines(path):
    # THIS WILL INCLUDE THE FIRST COMMENTED LINE!
    with open(path, "r") as f:
        ant = f.read()
        f.close()
    return ant


def getNumReactions(ant):
    # Takes a list of strings for each line in ant file
    nReactions = 0
    for line in ant:
        if not line.startswith('var'):
            if line.startswith('k'):
                break
            nReactions += 1
    return nReactions
