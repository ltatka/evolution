import os
import cleanUpMethods as clean
import tellurium as te
from scipy.signal import find_peaks
import math
import copy
import zipfile



parent_dir = "C:\\Users\\tatka\\Desktop\\Models\\TEST"

damp_dir = os.path.join(parent_dir, "Damped")
pass_dir = os.path.join(parent_dir, "Oscillate")
pass_inf = os.path.join(pass_dir, "Infinity")
damp_inf = os.path.join(damp_dir, "Infinity")
pass_unk = os.path.join(damp_dir, "unknown")
damp_unk = os.path.join(damp_dir, "unknown")
#
#

def checkMakeDir(dir, parent):
    if not os.path.isdir(dir):
        os.mkdir(dir)
        os.chdir(parent)


if not os.path.isdir(damp_dir):
    os.mkdir(damp_dir)
    os.chdir(parent_dir)
if not os.path.isdir(pass_dir):
    os.mkdir(pass_dir)
    os.chdir(parent_dir)
if not os.path.isdir(damp_inf):
    os.mkdir(damp_inf)
    os.chdir(parent_dir)
if not os.path.isdir(pass_inf):
    os.mkdir(pass_inf)
    os.chdir(parent_dir)
if not os.path.isdir(damp_unk):
    os.mkdir(damp_unk)
    os.chdir(parent_dir)
if not os.path.isdir(pass_unk):
    os.mkdir(pass_unk)
    os.chdir(parent_dir)



total_processed = 0
total_damped = 0

os.chdir(parent_dir)


count = 0
total = len(os.listdir(parent_dir))
for filename in os.listdir(parent_dir):
    count += 1
    if count%50 ==0:
        print(f'working on model {count} of {total}...')

    os.chdir(parent_dir)
    if not filename.endswith('.ant'):
        continue
    ant = clean.loadAntimonyText_noLines(filename)
    try:
        isDamped, toInf = clean.isModelDampled(ant)
        if isDamped:
            total_damped += 1
            os.chdir(damp_dir)
            inf_dir = damp_inf
            unk_dir = damp_unk
        else:
            os.chdir(pass_dir)
            inf_dir = pass_inf
            unk_dir = pass_unk
        if isDamped and toInf:
            os.chdir(damp_inf)
        elif isDamped and toInf == 'unknown':
            os.chdir(damp_unk)
        elif isDamped and not toInf:
            os.chdir(damp_dir)
        elif not isDamped and toInf:
            os.chdir(pass_inf)
        elif not isDamped and toInf == 'unknown':
            os.chdir(pass_unk)
        elif not isDamped and not toInf:
            os.chdir(pass_dir)


        with open(f'{filename}', "w") as f:
            f.write(ant)
            f.close()
            total_processed += 1

    except Exception as e:
        print(f"Fail: {filename}\n{e}")


print(f'Processed {total_processed} models and found {total_damped} damped models.')

#
# ant = clean.loadAntimonyText_noLines("C:\\Users\\tatka\\Desktop\\Models\\TEST\\osc4.ant")

# r = te.loada(ant)
# m = r.simulate(0,100,1000)
# clean.check_infinity(m)
#
#
# damped = clean.isModelDampled(ant)
# print(f'Is damped: {damped}')
# #
# import tellurium as te
# #
# r = te.loada(ant)
# result = r.simulate(0,1000,5000)
# # r.plot()
#
# import pylab
# pylab.plot (result[4900:,2])
# pylab.show()
#
# from scipy.signal import find_peaks
# peaks, _ = find_peaks(result[4900:,2], prominence=1)
# print(f'Peaks found: {len(peaks)}')
#
#
