import numpy as np
import matplotlib.pyplot as plt
import matplotlib.path as mplPath

class ValueMap:
    def __init__(self, gridSize, southWestPos, cellSize, noDataVal, units):
        # Initialize data
        self.gridSize = gridSize
        self.southWestPos = southWestPos
        self.cellSize = cellSize
        self.noDataVal = noDataVal
        self.units = units

        # Create an empty NP array that will store the GRID data
        self.gridData = np.empty((gridSize[0], gridSize[1]))
    
    def setGridData(self, gridData):
        # Load the grid data
        self.gridData = gridData
    
    def determineValue(self, lattitude, longitude):
        # Determine the value at a specific latitude and longitude 
        xIndex, yIndex = self.getCoord(lattitude, longitude)

        return self.gridData[yIndex][xIndex]
    
    def getCoord(self, lattitude, longitude):
        # Convert a latitude and longitude into array indexes
        yIndex = self.gridData.shape[0] -  int(abs(lattitude - self.southWestPos[0]) / self.cellSize)
        xIndex = int(abs(longitude - self.southWestPos[1]) / self.cellSize)
        if yIndex > 0:
            yIndex = yIndex - 1
        if xIndex > 0:
            xIndex = xIndex - 1
        return [xIndex, yIndex]
    
    def getLatLon(self, xIndex, yIndex):
        # Convert a specific array index into a lat/lon coordinate
        lat, lon = -1,-1

        lat = self.southWestPos[0] - ((self.gridSize[0] - yIndex) * self.cellSize)
        lon = self.southWestPos[1] + (xIndex * self.cellSize)

        return [lat,lon]

    def getInternalCoords(self, boundingIndexes):
        # Returns a list of all the indexes in the array that are within a given bounding box
        coords = []
        polyPath = mplPath.Path(boundingIndexes)
        for rowIndex in range(self.gridData.shape[0]):
            for columnIndex in range(self.gridData.shape[1]):
                if(polyPath.contains_point([columnIndex, rowIndex])):
                    coords.append([rowIndex, columnIndex])
        return coords


    def plot(self, colormap='jet', path="", title="", dpi=300):
        # Plot the data as a heatmap
        plt.clf()
        plt.imshow(self.gridData, cmap=colormap, interpolation='nearest')
        plt.colorbar()
        plt.title(title)
        if path=="":
            plt.show()
        else:
            plt.savefig(path, dpi=dpi)

    def writeToFile(self, filePath):
        # Write the grid data to a file
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
