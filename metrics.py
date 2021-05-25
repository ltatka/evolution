import os
from zipfile import ZipFile
import tellurium as te
from scipy.signal import find_peaks
from copy import deepcopy
from cleanUP import isModelDampled


parent_dir = "C:\\Users\\tatka\\Desktop\\Models"
trim_dir = "C:\\Users\\tatka\\Desktop\\Models\TRIMMED"

### METRIC LISTS
ID = []
isAutoCat = []  ##
isDamped = []

for filename in os.listdir(trim_dir):
    print(filename)
    # os.chdir(os.path.join(trim_dir, filename))
    # f = open('trim_antimony.txt')
    # ant = f.read()
    # isDamped = isModelDampled(ant)
    #
    # lines = f.readlines()
    # # for line in lines:
    # #     if line.startswith('S'):