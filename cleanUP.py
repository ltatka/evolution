# Clean up a model
# modelToCleanUp = 'Model_242338397427699976.zip'  # Model_3267184786043346636.zip'

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



#
import matplotlib.pyplot as plt
# ####################################################################
parent_dir = "C:\\Users\\tatka\\Desktop\\Models"
trim_dir = "C:\\Users\\tatka\\Desktop\\Models\\TRIMMED"
directory = "C:\\Users\\tatka\\Desktop\\Models\\PASS"
save_dir = "C:\\Users\\tatka\\Desktop\\Models\\TRIM_choose2"

percentSuccess = []

for filename in os.listdir(directory):
    os.chdir(directory)
    try:
        # Open the zip file
        zf = readSavedRun(os.path.join(directory, filename))
        # Pull out the antimony model
        ant = readModel(zf, numGenerations - 1, 0)
        zf.close()

        # split into lines but ignore the first line which is a comment
        lines = ant.splitlines()[1:]

        # Get the start and end of the reactions lines
        start = findStart(lines)
        end = findEnd(lines) - 1

        # We'll keep an unmodified copy of the model
        originalModel = copy.deepcopy(lines)

        count = 1
        # Create a status array, entry of False means this reaction
        # is not important and can be removed
        status = [False] * ((end + 1) - start)
        for variant in range(start, end + 1):
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
                count += 1
                # If roadrunner crashes then the reaction must be important
            except Exception as err:
                status[variant - start] = True
                count += 1
        # Get locations of non-essential reactions
        indices = []
        for i in range(len(status)):
            if not status[i]:
                indices.append(i + start) # add start value to get the index in the antimony model
        combos = choose(indices, 2) # all possible combos of 2 non essential reactions
        os.chdir(save_dir)
        savePath = os.path.join(save_dir, filename[:-4])
        count = 0
        successes = 0
        # Remove every combo of reactions and test
        for i in range(len(combos)):
            lines = copy.deepcopy(originalModel)
            lines[combos[i][0]] = '#' + lines[combos[i][0]]
            lines[combos[i][1]] = '#' + lines[combos[i][1]]
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
                        with open(filename[6:-4]+'_'+str(count)+'.ant', "w") as f:
                            count += 1
                            f.write(antstr)
                            f.close()
                # Let's save it even if it fails because it might be interesting to see which reactions broke it
                if len(peaks) == 0 or len(peaks2) == 0:
                    if not os.path.isdir(savePath):
                        os.mkdir(savePath)
                    os.chdir(savePath)
                    with open('FAIL_' + filename[6:-4] + '_' + str(count) + '.ant', "w") as f:
                        count += 1
                        f.write(antstr)
                        f.close()
            except Exception:
                if not os.path.isdir(savePath):
                    os.mkdir(savePath)
                os.chdir(savePath)
                with open('FAIL_' + filename[6:-4] + '_' + str(count) + '.ant', "w") as f:
                    count += 1
                    f.write(antstr)
                    f.close()
        savePath = os.path.join(save_dir, filename[:-4])
        # If a save folder for the ancestor model doesn't already exist, make it
        if not os.path.isdir(savePath):
            os.mkdir(savePath)
        os.chdir(savePath)
        with open(filename[6:-4] + '_' + str(count) + '_summary.txt', "w") as f:
            f.write(f'ancestor = {filename[:-4]}\n')
            f.write(f'total reactions = {len(status)}\n')
            f.write(f'non essential reactions = {len(indices)}\n')
            f.write(f'total 2 reaction combos: {nChooseK(len(indices), 2)}\n')
            f.write(f'successful trims = {successes}\n')
            f.close()
        percentSuccess.append(successes/nChooseK(len(indices), 2))
        # # Zip it up
        # os.chdir(save_dir)
        # with zipfile.ZipFile(filename, "w") as newzip:
        #     for file in os.listdir(savePath):
        #         newzip.write(file)
        #     newzip.close()
        # shutil.rmtree(savePath)
    except Exception:
        pass


with open(os.path.join(save_dir, 'percent_success.txt'), "w") as f:
    f.write(f'average success rate = {sum(percentSuccess)/len(percentSuccess)}\n')
    f.close()
"""
# parent_dir = "C:\\Users\\tatka\\Desktop\\Models"
# trim_dir = "C:\\Users\\tatka\\Desktop\\Models\TRIMMED"
# directory = "C:\\Users\\tatka\\Desktop\\Models\\PASS"
#
# total_processed = 0
# total_damped = 0
# errCount = 0
# errModels = []
#
# for filename in os.listdir(directory):
#     try:
#         # Open the zip file
#         zf = readSavedRun(os.path.join(directory, filename))
#         # Pull out the antimony model
#         ant = readModel(zf, numGenerations - 1, 0)
#         zf.close()
#
#         # split into lines but ignore the first line which is a comment
#         lines = ant.splitlines()[1:]
#
#         # Get the start and end of the reactions lines
#         start = findStart(lines)
#         end = findEnd(lines) - 1
#
#         # We'll keep an unmodified copy of the model
#         originalModel = copy.deepcopy(lines)
#
#         count = 1
#         # Create a status array, entry of False means this reaction
#         # is not important and can be removed
#         status = [False] * ((end + 1) - start)
#         for variant in range(start, end + 1):
#             lines = copy.deepcopy(originalModel)
#             lines[variant] = '#' + lines[variant]
#             antstr = '\n'.join(lines)
#             r = te.loada(antstr)
#             try:
#                 m = r.simulate(0, 100, 100)
#                 peaks, _ = find_peaks(m[:, 2], prominence=1)
#                 if len(peaks) == 0:
#                     status[variant - start] = True
#                 else:
#                     # It could be damped
#                     m = r.simulate(0, 10, 500)
#                     peaks, _ = find_peaks(m[:, 2], prominence=1)
#                     if len(peaks) == 0:
#                         status[variant - start] = True
#                 count += 1
#                 # If roadrunner crashes then the reaction must be important
#             except Exception as err:
#                 status[variant - start] = True
#                 count += 1
#
#         # Now to remove the non essential reactions:
#         trimLines = copy.deepcopy(originalModel)
#
#         nReactions = len(status)
#         count = 0
#         nonEssentials = 0
#         for i in range(start, end + 1):
#             if not status[count]:  # Comment out non essential reactions
#                 trimLines[i] = '#' + trimLines[i]
#                 nonEssentials += 1
#             count += 1
#
#         antstr = '\n'.join(trimLines)
#
#         numDeleted = f'num non-essential reactions = {nonEssentials}\n'
#         isDamped = isModelDampled(antstr)
#         isDampedStr = f'damped or non-oscillating = {isDamped}'
#
#         total_processed += 1
#         if isDamped:
#             total_damped += 1
#         else:
#             try:
#                 r = te.loada(antstr)
#                 r.simulate()
#             except Exception:
#                 total_damped += 1
#
#
#
#         newFilename = 'trim2_' + filename[:-4]
#         os.mkdir(os.path.join(trim_dir, newFilename))
#         os.chdir(os.path.join(trim_dir, newFilename))
#         # Write out
#         f = open('trim_antimony.txt', "w")
#         f.write(antstr)
#         f.close()
#
#         f = open('trim_summary.txt', "w")
#         f.write(numDeleted + isDampedStr)
#         f.close()
#     except Exception as e:
#         errCount += 1
#         errModels.append(filename)
# try:
#     os.chdir(parent_dir)
#     summary = open('summary.txt', "w")
#     summary.write(f'total processed = {total_processed}\n')
#     summary.write(f'total damped or broken = {total_damped}')
#     if errCount > 0:
#         summary.write(f'num errors = {errCount}\nfailed models:\n')
#         for filename in errModels:
#             summary.write(filename+'\n')
#     summary.close()
# except Exception as e:
#     print("Couldn't save summary but everything else worked.")
"""