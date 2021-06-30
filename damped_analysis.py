import os
import cleanUpMethods as clean
import tellurium as te
from scipy.signal import find_peaks
import math
import copy
import zipfile


parent_dir = "C:\\Users\\tatka\\Desktop\\Models\\3node_oscillator\\3node_trimmed_antimony"

damp_dir = "C:\\Users\\tatka\\Desktop\\Models\\3node_damped2"
pass_dir = "C:\\Users\\tatka\\Desktop\\Models\\3node_oscillator2"

if not os.path.isdir(damp_dir):
    os.mkdir(damp_dir)
if not os.path.isdir(pass_dir):
    os.mkdir(pass_dir)

failures_present = False
total_processed = 0
total_damped = 0

os.chdir(parent_dir)

for filename in os.listdir(parent_dir):


    os.chdir(parent_dir)
    if not filename.endswith('.ant'):
        continue
    ant = clean.loadAntimonyText_noLines(filename)
    print(filename)
    try:
        isDamped = clean.isModelDampled(ant)
        if isDamped:
            total_damped += 1
            os.chdir(damp_dir)
        else:
            os.chdir(pass_dir)
        with open(f'{filename}.ant', "w") as f:
            f.write(ant)
            f.close()
            total_processed += 1
    except:
        failures_present = True
        # with open(f'damped-analysis_failures.txt', "a") as f:
        #     f.write(f'{filename}: Could not run isDamped()\n')
        #     f.close()
        #     total_processed += 1


print(f'Processed {total_processed} models and found {total_damped} damped models.')

# os.chdir(parent_dir)
# with open(f'damped_analysis_summary.txt', "w") as f:
#     f.write(f"total processed = {total_processed}\n")
#     f.write(f"total damped = {total_damped}\n")
#     f.write(f"failures present = {failures_present}")
#     f.close()
#     total_processed += 1