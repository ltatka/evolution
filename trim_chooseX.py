import tellurium as te
import roadrunner
import copy, sys, os, math, getopt, json, time, zipfile, shutil
from scipy.signal import find_peaks


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
parent_dir = "C:\\Users\\tatka\\Desktop\\Models\\OSCILLATOR"

save_dir = "C:\\Users\\tatka\\Desktop\\Models\\TRIM\\TRIM_choose3_2"

percentSuccess = []
total_processed = 0
NUM_DELETED = 3

os.chdir(parent_dir)

for filename in os.listdir(parent_dir):

    # GET THE ANTIMONY STRING FROM THE ORIGINAL ZIP FILE
    os.chdir(parent_dir)
    if not filename.startswith('Model'):
        continue
    if filename.endswith('.zip'):
        filename = filename[:-4]

    if filename in os.listdir(save_dir):
        continue

    try:

        with open(os.path.join(parent_dir, filename), "r") as f:
            ant = f.read()
            f.close()

    except Exception as e:
        print(os.getcwd())
        print("here", e)
        os.chdir(save_dir)
        with open(f'trim{NUM_DELETED}_failures.txt', "a") as f:
            f.write(f'{filename}: {e}\n')
            f.close()
            total_processed += 1
        continue

    # split into lines but ignore the first line which is a comment
    lines = ant.splitlines()[1:]
    originalModel = copy.deepcopy(lines)
    start = findStart(lines)
    end = findEnd(lines)

    # GET THE NON ESSENTIAL REACTION INDICES
    status = [False] * (end - start)  ### end + 1 ?
    for variant in range(start, end):
        lines = copy.deepcopy(originalModel)
        lines[variant] = '#' + lines[variant]
        antstr = '\n'.join(lines)
        r = te.loada(antstr)

        try:

            m = r.simulate(0, 100, 100)
            peaks, _ = find_peaks(m[:, 2], prominence=1)
            if len(peaks) == 0:
                status[variant - start] = True
            else:
                # It could be damped
                m = r.simulate(0, 10, 500)
                peaks, _ = find_peaks(m[:, 2], prominence=1)
                if len(peaks) == 0:
                    status[variant - start] = True

            # If roadrunner crashes then the reaction must be important
        except Exception as err:

            status[variant - start] = True
    # Get locations of non-essential reactions
    indices = []
    for i in range(len(status)):
        if not status[i]:
            indices.append(i + start)  # add start value to get the index in the antimony model

    # skip if there are not enough reactions to delete
    if len(indices) <= NUM_DELETED:

        os.chdir(save_dir)
        with open(f'trim{NUM_DELETED}_failures.txt', "a") as f:
            f.write(f'{filename}: not enough non essential reactions to choose {NUM_DELETED}\n')
            f.close()
            total_processed += 1
        continue

    try:

        combos = choose(indices, NUM_DELETED) # all possible combos of NUM_DELETED non essential reactions
        os.chdir(save_dir)
        savePath = os.path.join(save_dir, filename)
        count = 0
        successes = 0
        # Remove every combo of reactions and test
        for i in range(len(combos)):
            lines = copy.deepcopy(originalModel)
            for j in range(NUM_DELETED):
                if lines[combos[i][j]].startswith('k'):
                    raise TypeError("WENT TOO FAR")
                lines[combos[i][j]] = '#' + lines[combos[i][j]]
            antstr = '\n'.join(lines)
            r = te.loada(antstr)
            try:
                m = r.simulate(0, 100, 100)
                peaks, _ = find_peaks(m[:,2], prominence=1)
                if len(peaks) > 0:
                    m = r.simulate(0, 10, 500)
                    peaks2, _ = find_peaks(m[:, 2], prominence=1)
                    if len(peaks2) > 0:
                        # If we got here, then the model oscillates and is not damped, so we save it
                        # If a save folder for the ancestor model doesn't already exist, make it
                        successes += 1
                        if not os.path.isdir(savePath):
                            os.mkdir(savePath)
                        os.chdir(savePath)
                        with open(filename[6:]+'_'+str(count)+'.ant', "w") as f:
                            count += 1
                            f.write(antstr)
                            f.close()
                # Let's save it even if it fails because it might be interesting to see which reactions broke it
                if len(peaks) == 0 or len(peaks2) == 0:
                    if not os.path.isdir(savePath):
                        os.mkdir(savePath)
                    os.chdir(savePath)
                    with open('FAIL_' + filename[6:] + '_' + str(count) + '.ant', "w") as f:
                        count += 1
                        f.write(antstr)
                        f.close()
            except Exception:
                if not os.path.isdir(savePath):
                    os.mkdir(savePath)
                os.chdir(savePath)
                with open('FAIL_' + filename[6:] + '_' + str(count) + '.ant', "w") as f:
                    count += 1
                    f.write(antstr)
                    f.close()
        savePath = os.path.join(save_dir, filename)

        # If a save folder for the ancestor model doesn't already exist, make it
        if not os.path.isdir(savePath):
            os.mkdir(savePath)
        os.chdir(savePath)
        with open(filename[6:] + '_' + str(count) + '_summary.txt', "w") as f:
            f.write(f'ancestor = {filename}\n')
            f.write(f'total reactions = {end-start}\n')
            f.write(f'non essential reactions = {len(indices)}\n')
            f.write(f'start = {start}\n')
            f.write(f'indices = {indices}\n')
            f.write(f'total {NUM_DELETED} reaction combos: {nChooseK(len(indices), NUM_DELETED)}\n')
            f.write(f'successful trims = {successes}\n')
            f.close()
        total_processed += 1
        percentSuccess.append(successes/nChooseK(len(indices), NUM_DELETED))
    except Exception:
        os.chdir(save_dir)
        with open(f'trim{NUM_DELETED}_failures.txt', "a") as f:
            f.write(f'{filename}: exception thrown\n')
            f.close()
            total_processed += 1
        continue

with open(os.path.join(save_dir, 'percent_success.txt'), "w") as f:
    f.write(f'average success rate = {sum(percentSuccess)/len(percentSuccess)}\n')
    f.write(f'total processed = {total_processed}')
    f.close()







