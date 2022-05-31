import numpy as np
from scipy.integrate import solve_ivp
import modTeUtils as tu
from numba import jit
from configLoader import loadConfiguration
import readObjData

UNIUNI = tu.TReactionType.UniUni
UNIBI = tu.TReactionType.UniBi
BIUNI = tu.TReactionType.BiUni
BIBI = tu.TReactionType.BiBi

integrators = ['radu', 'BDF', 'LSODA']
currentModel = 0


def runCvodeSimulation(model, timeEnd, numberOfPoints, initialConditions):
    global currentModel
    currentModel = model
    model.cvode.setModel(cvodeModel)
    y0 = np.zeros(model.numFloats + model.numBoundary)
    for i in range(model.numFloats + model.numBoundary):
        y0[i] = initialConditions[i]

    neq = model.numFloats + model.numBoundary
    model.cvode.initialize(neq, y0)

    m = model.cvode.simulate(0, timeEnd, numberOfPoints)
    return m[:, 0], m[:, 1:]


def runSimulation(model, timeEnd, numberOfPoints, initialConditions):
    try:
        y = np.zeros(model.numFloats + model.numBoundary)
        t = np.linspace(0, timeEnd, numberOfPoints)
        for i in range(model.numFloats + model.numBoundary):
            y[i] = initialConditions[i]

        tt = np.linspace(0, timeEnd, numberOfPoints)
        sol1 = solve_ivp(getdydt, [0, timeEnd], y, t_eval=tt,
                         method='BDF', rtol=1e-6, atol=1e-12, args=(model,))
        return sol1.t, np.transpose(sol1.y)
    except Exception as err:
        print("Error in run simulation: ", err)
        raise


def computeFitnessOfIndividual(model, initialConditions):
    # Run eval to get next time step and next values for y
    global objFunctionData
    numberOfPoints = objFunctionData.numberOfPoints
    timeEnd = objFunctionData.timeEnd
    try:
        t, y = runCvodeSimulation(model, timeEnd, numberOfPoints, initialConditions)

        nFloats = model.numFloats
        # compute fitness with respect to each node
        deviation = np.zeros(nFloats)  # Size = number of floats
        smallestDeviation = 1E18
        for j in range(nFloats):  # loop all nFloats
            deviation[j] = 0;
            for i in range(numberOfPoints - 1):
                deviation[j] = deviation[j] + (y[i, j] - objFunctionData.outputData[i]) ** 2

            if smallestDeviation > deviation[j]:
                smallestDeviation = deviation[j]
    except Exception as err:
        # Assign high fitness
        model.fitness = 1E17
        return 1E17

    model.fitness = smallestDeviation
    return smallestDeviation


def readObjectiveFunction():
    result = readObjData.ObjectiveFunctionData()
    f = open("objectivefunction.txt", "r")

    astr = f.readline()  # Dump the first comment line

    astr = f.readline()
    aList = astr.split()
    result.timeStart = float(aList[1])

    astr = f.readline();
    aList = astr.split();
    result.timeEnd = float(aList[1])

    astr = f.readline()
    aList = astr.split()
    result.numberOfPoints = int(aList[1])

    for i in range(result.numberOfPoints):
        result.outputData.append(float(f.readline()))
    f.close()
    return result


def euler(y, t, model, h):
    dydt = getdydt(y, t, model)
    n = len(y)
    ynew = np.zeros(n)
    for i in range(n):
        ynew[i] = y[i] + h * dydt[i]
    return ynew


@jit(nopython=True)
def computeRates(dydt, y, reactionType, rateConstant, reactant1, reactant2, product1, product2):
    if reactionType == UNIUNI:
        rate = y[reactant1] * rateConstant
        dydt[reactant1] -= rate
        dydt[product1] += rate
        return
    if reactionType == BIUNI:
        rate = y[reactant1] * y[reactant2] * rateConstant
        dydt[reactant1] -= rate
        dydt[reactant2] -= rate
        dydt[product1] += rate
        return
    if reactionType == UNIBI:
        rate = y[reactant1] * rateConstant
        dydt[reactant1] -= rate
        dydt[product1] += rate
        dydt[product2] += rate
        return
    if reactionType == BIBI:
        rate = y[reactant1] * y[reactant2] * rateConstant
        dydt[reactant1] -= rate
        dydt[reactant2] -= rate
        dydt[product1] += rate
        dydt[product2] += rate


def getdydt2(t, y, model):
    nFloats = model.numFloats
    nBoundary = model.numBoundary
    reactions = model.reactions
    nReactions = len(model.reactions)
    dydt = np.zeros(nFloats + nBoundary)
    for i in range(nReactions):
        reaction = reactions[i]
        computeRates(dydt, y,
                     reaction.reactionType,
                     reaction.rateConstant,
                     reaction.reactant1,
                     reaction.reactant2,
                     reaction.product1,
                     reaction.product2)

    # zero all the boundary dydts
    dydt[nFloats:] = 0
    return dydt
    # except Exception as err:
    #    print ("ERROR in getdydt-----------------------------")
    #    print (err)


# @jit(nopython=True)
def computedydt(y, reactant, rateConstant):
    return y[reactant] * rateConstant


@jit(nopython=True)
def getdydt(t, y, nFloats, nBoundary, reactions):
    nReactions = len(reactions)
    dydt = np.zeros(nFloats + nBoundary)
    for i in range(nReactions):
        reaction = reactions[i]  # +1 to jump over number of reactions entry
        if reaction.reactionType == UNIUNI:
            reactant1 = reaction.reactant1
            product1 = reaction.product1
            rateConstant = reaction.rateConstant
            rate = computedydt(y, reactant1, rateConstant)
            rate = y[reactant1] * rateConstant
            dydt[reactant1] -= rate
            dydt[product1] += rate

        elif reaction.reactionType == UNIBI:
            reactant1 = reaction.reactant1
            product1 = reaction.product1
            product2 = reaction.product2
            rateConstant = reaction.rateConstant
            rate = y[reactant1] * rateConstant
            dydt[reactant1] -= rate
            dydt[product1] += rate
            dydt[product2] += rate

        elif reaction.reactionType == BIUNI:
            reactant1 = reaction.reactant1
            reactant2 = reaction.reactant2
            product1 = reaction.product1
            rateConstant = reaction.rateConstant
            rate = y[reactant1] * y[reactant2] * rateConstant
            dydt[reactant1] -= rate
            dydt[reactant2] -= rate
            dydt[product1] += rate

        elif reaction.reactionType == BIBI:
            reactant1 = reaction.reactant1
            reactant2 = reaction.reactant2
            product1 = reaction.product1
            product2 = reaction.product2
            rateConstant = reaction.rateConstant
            rate = y[reactant1] * y[reactant2] * rateConstant
            dydt[reactant1] -= rate
            dydt[reactant2] -= rate
            dydt[product1] += rate
            dydt[product2] += rate

    # zero all the boundary dydts
    dydt[nFloats:] = 0
    return dydt


def cvodeModel(t, y, ydot, user_data):
    global currentModel
    total = currentModel.numFloats + currentModel.numBoundary
    yarray = currentModel.cvode.getVectorArray(y)
    ynumpy = np.zeros(total)
    for i in range(total):
        ynumpy[i] = yarray[i]

    dydt = getdydt2(t, ynumpy, currentModel)

    for i in range(currentModel.numFloats + currentModel.numBoundary):
        currentModel.cvode.setVectorValue(ydot, i, dydt[i])
    return 0


global objFunctionData
objFunctionData = readObjectiveFunction()
