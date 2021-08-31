import os


def checkMakeDir(dir):
    if not os.path.exists(dir) or not os.path.isdir(dir):
        os.mkdir(dir)


def loadAntimonyText(path):
    with open(path, "r") as f:
        ant = f.read()
        f.close()
    lines = ant.split('\n')
    # First line is comment for fitness, ignore
    if lines[0].startswith('#'):
        lines = lines[1:]
    return lines


def loadAntimonyText_noLines(path):
    # THIS WILL INCLUDE THE FIRST COMMENTED LINE!
    with open(path, "r") as f:
        ant = f.read()
        f.close()
    return ant


def getNumReactions(ant):
    # Takes a list of strings for each line in ant file
    nReactions = 0
    for line in ant:
        if not line.startswith('var'):
            if line.startswith('k'):
                break
            nReactions += 1
    return nReactions
