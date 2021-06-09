import os
import cleanUpMethods as clean

dir = 'C:\\Users\\tatka\\Desktop\\Models\\OSCILLATOR'

os.chdir(dir)

for filename in os.listdir(dir):
    if not filename.startswith('Model'):
        continue
    ant = clean.loadAntimonyText_noLines(os.path.join(dir, filename))
    isDamped = clean.isModelDampled(ant)
    if isDamped:
        print("Found a damped model")
        break