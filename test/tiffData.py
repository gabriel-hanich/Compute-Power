import rasterio
import rasterio.features
import rasterio.warp
from pyproj import Transformer
from valueMaps import ValueMap
import math

with rasterio.open('./data/populationDensity.tif') as dataset:
    # Calculate the position of the southwest position corner of the dataset
    bottomRight = dataset.transform * (dataset.width, dataset.height)
    topLeft = dataset.transform * (0, 0)
    southWestCoords = [abs(topLeft[0]), abs(bottomRight[1])]

    x_res, y_res = dataset.res
    pixel_height_meters = y_res
    row, col = dataset.height // 2, dataset.width // 2 # get the center pixel
    x, y = dataset.xy(row, col) # get the spatial coordinates of the center pixel
    latitude = y # get the latitude of the center pixel
    R = 6378137 # radius of the earth in meters
    pixel_height_degrees = abs(pixel_height_meters * 360 / (2 * math.pi * R * math.cos(math.radians(latitude))))
    print(pixel_height_degrees)

    print(dataset.crs)

    southWestPos = [85.96019432861101, 40.13997503559076]
    
    # Calculate the dimensions of the dataset
    gridSize = [dataset.width, dataset.height]

    # Process density data
    density = dataset.read(1)
    noDataVal = 0

    densityData = ValueMap(gridSize, southWestPos, pixel_height_degrees, noDataVal)
    densityData.setGridData(density)

# densityData.writeToFile("./data/density.grid")

densityData.plot()

-34.09425620948342, 150.8947018434003
-34.85727658279411, 151.41380581233346