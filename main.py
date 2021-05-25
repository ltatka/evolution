
import os


BATCHNUM = 50

for i in range(BATCHNUM):
    command = 'python ./evolve.py'
    os.system(command)
