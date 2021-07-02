import os
import tellurium as te
import roadrunner as rr

import cleanUpMethods as clean

dir = 'C:\\Users\\tatka\\Desktop\\Models\\3node_fail'

SBMLdir = 'C:\\Users\\tatka\\Desktop\\Models\\3node_fail\\antimony'

os.chdir(dir)

for filename in os.listdir(dir):
    os.chdir(dir)
    if not filename.startswith('FAIL_Model'):
        continue


    # Change file extension for the SBML output
    base = os.path.splitext(filename)[0]
    base = base + '.ant'
    print(filename)
    zf = clean.readSavedRun(os.path.join(dir, filename))
    # Pull out the original antimony model
    numGenerations = clean.getNumGenerations(zf)
    ant = clean.readModel(zf, numGenerations - 1, 0)
    ant = '\n'.join(ant)
    zf.close()
    os.chdir(SBMLdir)
    with open(base, "w") as f:
        f.write(ant)
        f.close()

    # r = te.loada(ant)
    # r.exportToSBML(os.path.join(SBMLdir, base))
