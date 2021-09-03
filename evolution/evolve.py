import evolUtils as ev
import argparse


evolver = ev.Evolver()

parser = argparse.ArgumentParser()
parser.add_argument("--seed", default=None, type=int, help="Change the random seed")
parser.add_argument("--newConfigFile", default=None, type=str, help="Use a different configuration file")
parser.add_argument("--numGenerations", default=None, type=int, help="Set the max number of generations")
parser.add_argument("--probabilities", default=None, nargs=4, type=float, help="Set random network reaction probabilities")
args = parser.parse_args()

if args.seed:
    evolver.setRandomSeed(args.seed)
if args.newConfigFile:
    evolver.loadNewConfig(args.newConfigFile)
if args.numGenerations:
    evolver.setMaxGeneration(args.numGenerations)
if args.probabilities:
    print(type(args.probabilities))
    evolver.setReactionProbabilities(args.probabilities)

evolver.evolve()
