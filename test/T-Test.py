import numpy as np
import scipy.stats as stats

rawData = [[] for _ in range(4)]
dType = "WIND"
with open(f"./data/Seasonal {dType}.csv", "r") as dataFile:
    for line in dataFile.readlines():
        for valIndex, val in enumerate(line.split(",")):
            rawData[valIndex].append(float(val.replace(",", "")))

dataArr= np.empty((len(rawData[0]), 4))

for i in range(4):
    for valIndex, val in enumerate(rawData[i-1]):
        dataArr[valIndex][i-1] = val

seasons = ["summer", "autumn", "winter", "spring"]

for aIndex, aItem in enumerate(seasons):
    for bIndex, bItem in enumerate(seasons):
        if aIndex != bIndex:
            group1 = dataArr[:, aIndex]
            group2 = dataArr[:, bIndex]
            
            tVal = stats.ttest_rel(group1, group2)
            print(f"For {aItem}-{bItem}: {tVal.pvalue}")