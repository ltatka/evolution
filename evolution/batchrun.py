import os
import time
from datetime import date
from datetime import datetime
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("--runs", default=10, type=int, help="Change the number of evolution trials")
parser.add_argument("--newConfigFile", default=None, type=str, help="Use a different configuration file")
parser.add_argument("--probabilities", default=None, nargs=4,  type=float, help="Set random network reaction probabilities")
parser.add_argument("--numGenerations", default=None, type=int, help="Set the max number of generations")
args = parser.parse_args()

def parseProbabilities(probabilities):
    probString = ''
    for p in probabilities:
        probString += str(p) + ' '
    return probString


command = 'python ./evolve.py'
if args.newConfigFile:
    command += f' --newConfigFile {args.newConfigFile}'
if args.numGenerations:
    command += f' --numGenerations {str(args.numGenerations)}'
if args.probabilities:
    command += f' --probabilities {parseProbabilities(args.probabilities)}'

print ("Batch set up for " + str(args.runs) + " runs")

today = date.today()
now = datetime.now()

print("Run Started on: ", today.strftime("%b-%d-%Y"))
print("at time: ", now.strftime("%H:%M:%S"), '\n')

start = time.time()
for i in range(args.runs):
    print("-----------------------------------------------------")
    print(" --- BATCH NUMBER --- " + str(i+1) + ' out of ' + str(args.runs) + ' total.')
    print("-----------------------------------------------------")
    os.system(command)

print("Time taken to do batch runs = ", time.time() - start)
