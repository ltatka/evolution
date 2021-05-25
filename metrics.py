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

