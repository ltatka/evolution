import teUtils as tu
import numpy as np
import random
import matplotlib.pyplot as plt

import cleanUpMethods
import damped_analysis
import readObjData
import evalFitness
from commonTypes import TModel_
import copy, sys, os, math, getopt, json, time, zipfile
import evolUtils, uModel
from uModel import TReaction
from pprint import pprint
from datetime import date
from datetime import datetime
import evolve as ev
import damped_analysis as damp
from uLoadCvode import TCvode
import uLoadCvode


tu.buildNetworks.Settings.ReactionProbabilities.UniUi = 0.1
tu.buildNetworks.Settings.ReactionProbabilities.UniBi = 0.4
tu.buildNetworks.Settings.ReactionProbabilities.BiUni = 0.4
tu.buildNetworks.Settings.ReactionProbabilities.BiBi = 0.1

config = {"sizeOfPopulation": 100,
          "numSpecies": 3,
          "numReactions": 12,
          "rateConstantScale": 50,
          "seed": -1,
          "numGens": 100,
          "percentCloned": 0.1
          }

if config['seed'] == -1:
    seed = random.randrange(sys.maxsize)
else:
    seed = config['seed']

candidate_dir = os.path.join(os.getcwd(), "modelCandidates")
oscillator_dir = os.path.join(os.getcwd(), "oscillator")

if not os.path.exists(candidate_dir):
    os.mkdir(candidate_dir)

tu.buildNetworks.Settings.rateConstantScale = config["rateConstantScale"]

sizeOfPopulation = config["sizeOfPopulation"]

topElite = math.trunc(config['percentCloned'] * sizeOfPopulation)
population = []

from scipy.signal import find_peaks
import tellurium as te

def isModelDampled(antstr):
    dampled = False
    r = te.loada(antstr)
    try:
        m = r.simulate(0, 100, 100)
        peaks, _ = find_peaks(m[:, 2], prominence=1)
        if len(peaks) == 0:
            dampled = True
        else:
            # It could be damped
            try:
                m = r.simulate(0, 10, 500)
                peaks, _ = find_peaks(m[:, 2], prominence=1)
                if len(peaks) == 0:
                    dampled = True

            except Exception:
                dampled = True

    except Exception:
        dampled = True
    return dampled



numNotDamped = 0
for i in range(sizeOfPopulation):
    amodel = ev.makeModel(config['numSpecies'], config['numReactions'])
    population.append(amodel)
    astr = evolUtils.convertToAntimony2(amodel)
    damped = isModelDampled(astr)
    if not damped:
        numNotDamped += 1

print(f" found {numNotDamped} oscillators")



#
# ev.computeFitness(population)
# population.sort(key=lambda x: x.fitness)
#
# protoOsc = []
# for model in population:
#     if model.fitness < 1000:
#         protoOsc.append(model)
#     else:
#         break
# print(len(protoOsc))
#

#
# for gen in range(config["numGens"]):
#     ev.computeFitness(population)
#     population.sort(key=lambda x: x.fitness)
#     # for model in population:
#     #     nth, change = ev.mutateRateConstant(model)
#     #     model.reactions[nth].rateConstant += change
#
#     print(f"gen {gen} top fitness: {population[0].fitness}")
#
#     newPopulation = []
#     for i in range(topElite):
#         newPopulation.append(uModel.clone(population[i]))
#
#     candidates = list(range(sizeOfPopulation))
#     for i in range(topElite, sizeOfPopulation):
#         r1, r2 = random.choices(candidates, k=2)
#
#         if population[r1].fitness < population[r2].fitness:
#             amodel = uModel.clone(population[r1])
#         else:
#             amodel = uModel.clone(population[r2])
#         n, change = ev.mutateRateConstant(amodel)
#         amodel.reactions[n].rateConstant += change
#         newPopulation.append(amodel)
#     population = newPopulation



#
# # os.chdir(candidate_dir)
# for i, model in enumerate(population):
#     antstr = evolUtils.convertToAntimony2(model)
#     path = os.path.join(candidate_dir, f"model_{i}.ant")
#     print(f"writing to {path}")
#     with open(path, "w") as f:
#         f.write(antstr)
#         f.close()
#


# damp.process_damped(candidate_dir, oscillator_dir)