import os
import tellurium as te
from scipy.signal import find_peaks
import math
import copy
import zipfile

def readSavedRun(fileName):
    global numPopulation
    global numGenerations
    zf = zipfile.ZipFile(fileName, 'r')
    data = zf.read('summary.txt').decode("utf-8")
    data = data.splitlines()
    numGenerations = int(data[5].split('=')[1])
    numPopulation = int(data[6].split('=')[1])
    # print ("Number of Generations = ", numGenerations)
    # print ("Size of population in each generation =", numPopulation)
    return zf


def readModel(zf, generation, individual):
    fileName = "populations/generation_" + str(generation) + '/individual_' + str(individual) + '.txt'
    ant = zf.read(fileName).decode("utf-8")
    return ant




# Return True if the model is damped
def isModelDampled(antstr):
    dampled = False
    r = te.loada(antstr)
    try:
        m = r.simulate(0, 100, 100)
        peaks, _ = find_peaks(m[:, 2], prominence=1)
        if len(peaks) == 0:
            dampled = True
        else:
            # It could be damped
            try:
                m = r.simulate(0, 10, 500)
                peaks, _ = find_peaks(m[:, 2], prominence=1)
                if len(peaks) == 0:
                    dampled = True

            except Exception:
                dampled = True

    except Exception:
        dampled = True
    return dampled


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
    return int(math.factorial(n)/ (math.factorial(k) * math.factorial(n-k)))

def convertIndices(str):
    indices = []
    nums = str.split(', ')
    nums[0] = nums[0][1:]
    nums[-1] = nums[-1][:-2]
    for num in nums:
        indices.append(int(num))
    return indices


# ####################################################################
parent_dir = "C:\\Users\\tatka\\Desktop\\Models\\LT3-Good"

damp_dir = "C:\\Users\\tatka\\Desktop\\Models\\DAMPED"
pass_dir = "C:\\Users\\tatka\\Desktop\\Models\\OSCILLATOR"



failures_present = False
total_processed = 0
total_damped = 0

os.chdir(parent_dir)

for filename in os.listdir(parent_dir):

    # GET THE ANTIMONY STRING FROM THE ORIGINAL ZIP FILE
    os.chdir(parent_dir)
    if not filename.startswith('Model'):
        continue
    if filename.endswith('.zip'):
        filename = filename[:-4]
    try:
        zf = readSavedRun(os.path.join(parent_dir, filename + ".zip"))
        # Pull out the original antimony model
        ant = readModel(zf, numGenerations - 1, 0)
        zf.close()
    except Exception as e :
        failures_present = True
        with open(f'damped-analysis_failures.txt', "a") as f:
            f.write(f'{filename}: Could not open file\n')
            f.close()
            total_processed += 1
        continue
    try:
        isDamped = isModelDampled(ant)
        if isDamped:
            os.chdir(damp_dir)
        else:
            os.chdir(pass_dir)
        with open(f'{filename}.ant', "w") as f:
            f.write(ant)
            f.close()
            total_processed += 1
    except:
        failures_present = True
        with open(f'damped-analysis_failures.txt', "a") as f:
            f.write(f'{filename}: Could not run isDamped()\n')
            f.close()
            total_processed += 1

os.chdir(parent_dir)
with open(f'damped_analysis_summary.txt', "w") as f:
    f.write(f"total processed = {total_processed}\n")
    f.write(f"total damped = {total_damped}\n")
    f.write(f"failures present = {failures_present}")
    f.close()
    total_processed += 1