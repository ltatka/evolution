import os
import cleanUpMethods as clean
import tellurium as te

dir = 'C:\\Users\\tatka\\Desktop\\Models\\3node_oscillator\\trimmed_antimony'

os.chdir(dir)

for filename in os.listdir(dir):
    # if not filename.startswith('Model'):
    #     continue
    if not filename.endswith('.ant'):
        continue
    with open(filename, "r") as f:
        ant = f.read()
        f.close()
    r = te.loada(ant)
    ode = te.getODEsFromModel(r)
    f.close()

    with open(filename[:-4]+'_ode.txt', "w") as f:
        f.write(ode)

    ode = ode.split('\n')

    rates = {}
    count = 0

    newOde = []

    for line in ode:
        if line.startswith('v_'):
            splitLine = line.split(' = ')
            rates[splitLine[0]] = splitLine[1]
    for line in ode:
        if line.startswith('d'):
            for key in rates:
                line = line.replace(key, rates[key])
            newOde.append(line)

    with open(filename[:-4]+'_ode.txt', "a") as f:
        f.write('\n')
        for line in newOde:
            f.write(line + '\n')
    f.close()






    # with open(filename[:-4]+'_ode.txt', "w") as f:
    #     f.write(ode)

    # ant = clean.loadAntimonyText_noLines(os.path.join(dir, filename))
    # isDamped = clean.isModelDampled(ant)
    # if isDamped:
    #     print("Found a damped model")
    #     break