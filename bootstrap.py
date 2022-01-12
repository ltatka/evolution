import pandas as pd
import random
import numpy as np

# oscdf = pd.read_csv("/home/hellsbells/Desktop/equalProbNOAC.csv")
# controldf = pd.read_csv("/home/hellsbells/Desktop/equalProbAC.csv")

oscdf = pd.read_csv("/home/hellsbells/Desktop/equalProbNOAC.csv")
controldf = oscdf.loc[oscdf['Autocatalysis Present']==0]
oscdf = oscdf.loc[oscdf['Autocatalysis Present']==1]

uniuni = list(oscdf["Uni-Uni"]/oscdf['Total']) + list(controldf["Uni-Uni"]/controldf['Total'])
biuni = list(oscdf["Bi-Uni"]/oscdf['Total']) + list(controldf["Bi-Uni"]/controldf['Total'])
unibi = list(oscdf["Uni-Bi"]/oscdf['Total']) + list(controldf["Uni-Bi"]/controldf['Total'])
bibi = list(oscdf["Bi-Bi"]/oscdf['Total']) + list(controldf["Bi-Bi"]/controldf['Total'])

s= list(oscdf["Total"]) + list(controldf["Total"])

trueDifUniUni = np.abs(np.mean(list(oscdf["Uni-Uni"]/oscdf['Total']))-np.mean(list(controldf["Uni-Uni"]/controldf['Total'])))
print(trueDifUniUni)
trueDifUnibi = np.abs(np.mean(list(oscdf["Uni-Bi"]/oscdf['Total']))-np.mean(list(controldf["Uni-Bi"]/controldf['Total'])))
print(trueDifUnibi)
trueDifBiUni = np.abs(np.mean(list(oscdf["Bi-Uni"]/oscdf['Total']))-np.mean(list(controldf["Bi-Uni"]/controldf['Total'])))
print(trueDifBiUni)
trueDifBiBi = np.abs(np.mean(list(oscdf["Bi-Bi"]/oscdf['Total']))-np.mean(list(controldf["Bi-Bi"]/controldf['Total'])))
print(trueDifBiBi)

truedifsize = np.abs(np.mean(list(oscdf["Total"])) - np.mean(list(controldf["Total"])))

idx = list(range(len(uniuni)))

difUniUni = []
difUnibi = []
difBiuni = []
difBibi = []
difSize = []

for i in range(1000):
    controlIdx = random.sample(idx, len(controldf))
    treatmentId = [x for x in idx if x not in controlIdx]

    controlUniUni = []
    controlUnibi = []
    controlBiuni = []
    controlBibi = []
    controlSize = []

    tUniUni = []
    tUnibi = []
    tBiuni = []
    tBibi = []
    tSize = []

    for i in controlIdx:
        controlUniUni.append(uniuni[i])
        controlUnibi.append(unibi[i])
        controlBiuni.append(biuni[i])
        controlBibi.append(bibi[i])
        controlSize.append(s[i])
    for i in treatmentId:
        tUniUni.append(uniuni[i])
        tUnibi.append(unibi[i])
        tBiuni.append(biuni[i])
        tBibi.append(bibi[i])
        tSize.append(s[i])
    difUniUni.append(int(abs(np.mean(controlUniUni) - np.mean(tUniUni)) > trueDifUniUni))
    if abs(np.mean(controlUniUni) - np.mean(tUniUni)) > trueDifUniUni:
        print(f"found a bigger uniuni diff {abs(np.mean(controlUniUni) - np.mean(tUniUni))}")
    difUnibi.append(int(abs(np.mean(controlUnibi) - np.mean(tUnibi)) > trueDifUnibi))
    if abs(np.mean(controlUnibi) - np.mean(tUnibi)) > trueDifUnibi:
        print(f"bigger unibi diff: {abs(np.mean(controlUnibi) - np.mean(tUnibi))}")
    difBiuni.append(int(abs(np.mean(controlBiuni) - np.mean(tBiuni)) > trueDifBiUni))
    if abs(np.mean(controlBiuni) - np.mean(tBiuni)) > trueDifBiUni:
        print(f"bigger biunidiff {abs(np.mean(controlBiuni) - np.mean(tBiuni))}")

    difBibi.append(int(abs(np.mean(controlBibi) - np.mean(tBibi)) > trueDifBiBi))
    if abs(np.mean(controlBibi) - np.mean(tBibi)) > trueDifBiBi:
        print(f"bigger bi bi diff {abs(np.mean(controlBibi) - np.mean(tBibi))}")
    difSize.append(int(abs(np.mean(controlSize) - np.mean(tSize)) > truedifsize))
    if abs(np.mean(controlSize) - np.mean(tSize)) > truedifsize:
        print(f" bigger size dif {abs(np.mean(controlSize) - np.mean(tSize)) > truedifsize}")

print(np.mean(difUniUni))
print(np.mean(difUnibi))
print(np.mean(difBiuni))
print(np.mean(difBibi))
print(np.mean(difSize))


