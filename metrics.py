import os
from zipfile import ZipFile
import tellurium as te
from scipy.signal import find_peaks
from copy import deepcopy
from cleanUP import isModelDampled
import tellurium as te
import matplotlib.pyplot as plt

parent_dir = "C:\\Users\\tatka\\Desktop\\Models"
trim_dir = "C:\\Users\\tatka\\Desktop\\Models\\TRIMMED"

untouched = 0
change_pass = 0
change_fail = 0
os.chdir(trim_dir)

for filename in os.listdir(trim_dir):
    os.chdir(filename)

    with open('trim_summary.txt', "r") as f:
        lines = f.read()
        f.close()
    lines = lines.splitlines()
    if len(lines) > 0:
        rxnsGone = int(lines[0].split(' = ')[1])
        damped = bool(lines[1].split(' = ')[1])
        if rxnsGone == 0:
            untouched += 1
        elif damped:
            change_fail += 1
        else:
            change_pass += 1
    else: change_fail += 1
    os.chdir(trim_dir)
#
#
summary = open('summary.txt', "w")
summary.write(f'untouched models = {untouched}\n')
summary.write(f'modified and failed = {change_fail}\n')
summary.write(f'modified and pass = {change_pass}\n')
summary.close()
#
# #
# # ### METRIC LISTS
# # ID = []
# # isAutoCat = []  ##
# # isDamped = []
#
# for filename in os.listdir(trim_dir):
#     os.chdir(os.path.join(trim_dir, filename))
#     f = open('trim_antimony.txt')
#     ant = f.read()
#     try:
#         isDamped = isModelDampled(ant)
#     except Exception:
#         isDamped = True
#     if not isDamped:
#         lines = ant.split('\n')
#         for line in lines:
#             if '->' in line:
#                 print(line)
#
#
#     r = te.loada(ant)
#     try:
#         m= r.simulate(0, 100, 100)
#         plt.plot(m)
#         plt.savefig(filename+'-plot.png')
#     except:
#         print(filename + ' broken')
