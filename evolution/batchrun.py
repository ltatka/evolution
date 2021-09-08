import os
import time
from datetime import date
from datetime import datetime
import argparse
import multiprocessing


parser = argparse.ArgumentParser()
parser.add_argument("--runs", default=10, type=int, help="Change the number of evolution trials")
parser.add_argument("--newConfigFile", default=None, type=str, help="Use a different configuration file")
parser.add_argument("--probabilities", default=None, nargs=4,  type=float, help="Set random network reaction probabilities")
parser.add_argument("--numGenerations", default=None, type=int, help="Set the max number of generations")
parser.add_argument("--multiprocess", default="True", type=str, help="Enable or disable multiprocessing")

def toBool(args):
    multiprocess = args.multiprocess.upper()
    if multiprocess.startswith("T"):
        return True
    else:
        return False

def parseProbabilities(probabilities):
    probString = ''
    for p in probabilities:
        probString += str(p) + ' '
    return probString

def runEvolution(args):
    command = 'python ./evolve.py'
    if args.newConfigFile:
        command += f' --newConfigFile {args.newConfigFile}'
    if args.numGenerations:
        command += f' --numGenerations {str(args.numGenerations)}'
    if args.probabilities:
        command += f' --probabilities {parseProbabilities(args.probabilities)}'

    today = date.today()
    now = datetime.now()
    start = time.time()

    #If not multiprocessing, enable printing and loop through batches
    if not toBool(args):
        print("Batch set up for " + str(args.runs) + " runs")
        print("Run Started on: ", today.strftime("%b-%d-%Y"))
        print("at time: ", now.strftime("%H:%M:%S"), '\n')
        for i in range(args.runs):
            if not toBool(args):
                print("-----------------------------------------------------")
                print(" --- BATCH NUMBER --- " + str(i+1) + ' out of ' + str(args.runs) + ' total.')
                print("-----------------------------------------------------")
            os.system(command)
        print("Time taken to do batch runs = ", time.time() - start)
    # If multiprocessing, then we will loop through the entire function each time, so disable printing
    # and run the command once per function
    else:
        os.system(command)


if __name__=='__main__':
    args = parser.parse_args()

    # Multiprocess:
    if toBool(args):
        starttime = time.time()
        processes = []
        for i in range(args.runs):
            p = multiprocessing.Process(target=runEvolution, args=(args,))
            processes.append(p)
            p.start()
        for process in processes:
            process.join()

        print(f"Finished in {time.time()-starttime} seconds.")
    else:
        runEvolution(args)