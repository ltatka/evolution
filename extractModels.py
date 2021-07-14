import sys
import cleanUpMethods as clean
import os

'''
This script extracts models from zip files in the given directory. 
If you want to extract AND add models to the databse, use extract_add_models.py.
'''

'''
Args:
0: ./ extractModels.py
1: Source path
-1: destination path
'''

dest_dir = sys.argv[-1]



total = len(sys.argv[1:-1])

count = 0
for file in sys.argv[1:-1]:
    try:
        os.chdir(dest_dir)
        ant = clean.extractAnt(file)
        with open(f'{file[:-4]}.ant', "w") as f:
            f.write(ant)
            f.close()
        count += 1
    except:
        continue

print(f"extracted {count} of {total} models")