from json import load

def loadConfiguration(configFile=None):
    if not configFile:
        f = open('defaultConfig.json')
        currentConfig = load(f)
    else:
        f = open(configFile)
        currentConfig = load(f)
    return currentConfig