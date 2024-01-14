import numpy as np
import matplotlib.pyplot as plt

class ValueMap:
    def __init__(self, gridSize, southWestPos, cellSize, noDataVal):
        self.gridSize = gridSize
        self.southWestPos = southWestPos
        self.cellSize = cellSize
        self.noDataVal = noDataVal
        
        self.gridData = np.empty((gridSize[0], gridSize[1]))
    
    def setGridData(self, gridData):
        self.gridData = gridData
    
    def determineValue(self, lattitude, longitude):
        yIndex = self.gridData.shape[0] -  int(abs(lattitude - self.southWestPos[0]) / self.cellSize)
        xIndex = int(abs(longitude - self.southWestPos[1]) / self.cellSize)
        if yIndex > 0:
            yIndex = yIndex - 1
        if xIndex > 0:
            xIndex = xIndex - 1

        return self.gridData[yIndex][xIndex]
    
    def plot(self, colormap='jet'):
        plt.imshow(self.gridData, cmap=colormap, interpolation='nearest')
        plt.colorbar()
        plt.show()

    def writeToFile(self, filePath):
        with open(filePath, "w+", encoding='utf-8') as outputFile:
            header = [
                f"nrows {self.gridData.shape[0]}",
                f"ncols {self.gridData.shape[1]}",
                f"cellsize {self.cellSize}",
                f"nodata_value {self.noDataVal}",
                f"SOUTHWEST LONGITUDE {self.southWestPos[1]}",
                f"SOUTHWEST LATITUDE {self.southWestPos[0]}"
            ]

            outputFile.writelines([string + '\n' for string in header])

            coordData = []
            rowIndex = 0
            for row in self.gridData:
                thisRow = ""
                for itemIndex, item in enumerate(row):
                    thisRow = thisRow + str(item)
                    if(itemIndex + 1 != len(row)):
                        thisRow = thisRow + " "
                    
                thisRow = thisRow + "\n"
                coordData.append(thisRow)

                rowIndex +=1 
                if(rowIndex % 100 == 0):
                    print(f"Writing line {rowIndex}/{self.gridData.shape[0]}")

            outputFile.writelines(coordData)
