import os
import cleanUpMethods as clean
import tellurium as te
from scipy.signal import find_peaks
import math
import copy
import zipfile

old = "C:\\Users\\tatka\\Desktop\\Models\\Archive\\10node_oscillator\\OSCILLATOR"
new = "C:\\Users\\tatka\\Desktop\\Models\\10node_oscillator3"

new_fails = []

new_list = os.listdir(new)

old_list = os.listdir(old)



for filename in os.listdir(old):
    if filename not in new_list:
        print(filename)
        new_fails.append(filename)
#
# parent_dir = "C:\\Users\\tatka\\Desktop\\Models\\Archive\\OSCILLATOR"
#
#
# damp_dir = "C:\\Users\\tatka\\Desktop\\Models\\10node_damped3"
# pass_dir = "C:\\Users\\tatka\\Desktop\\Models\\10node_oscillator3"
#
#
# if not os.path.isdir(damp_dir):
#     os.mkdir(damp_dir)
# if not os.path.isdir(pass_dir):
#     os.mkdir(pass_dir)
#
# failures_present = False
# total_processed = 0
# total_damped = 0
#
# os.chdir(parent_dir)
#
# # ant = clean.loadAntimonyText_noLines("Model_4897215793805515578.ant")
# #
# # print(clean.isModelDampled(ant))
# #
# # import tellurium as te
# # #
# # r = te.loada(ant)
# # result = r.simulate(0,1000,5000)
# # # r.plot()
# #
# # import pylab
# # pylab.plot (result[4900:,2])
# # pylab.show()
# #
# # from scipy.signal import find_peaks
# # peaks, _ = find_peaks(result[4900:,2], prominence=0.5)
# # print(f'Peaks found: {len(peaks)}')
#
#
#
#
# count = 0
# total = len(os.listdir(parent_dir))
# for filename in os.listdir(parent_dir):
#     count += 1
#     if count%50 ==0:
#         print(f'working on model {count} of {total}...')
#
#     os.chdir(parent_dir)
#     if not filename.endswith('.ant'):
#         continue
#     ant = clean.loadAntimonyText_noLines(filename)
#     try:
#         isDamped = clean.isModelDampled(ant)
#         if isDamped:
#             total_damped += 1
#             os.chdir(damp_dir)
#         else:
#             os.chdir(pass_dir)
#         with open(f'{filename}', "w") as f:
#             f.write(ant)
#             f.close()
#             total_processed += 1
#     except:
#         failures_present = True
#         # with open(f'damped-analysis_failures.txt', "a") as f:
#         #     f.write(f'{filename}: Could not run isDamped()\n')
#         #     f.close()
#         #     total_processed += 1
#
#
# print(f'Processed {total_processed} models and found {total_damped} damped models.')

