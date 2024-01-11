import rasterio
import rasterio.features
import rasterio.warp
from pyproj import Transformer


with rasterio.open('./data/populationDensity.tif') as dataset:
    bottomRight = dataset.transform * (dataset.width, dataset.height)
    topLeft = dataset.transform * (0, 0)
    southWestCoords = [topLeft[0], bottomRight[1]]
    print(dataset.crs)
    print(topLeft)
    print(bottomRight)


    transformer = Transformer.from_crs("EPSG:3577", "EPSG:4326")
    southWestPost = transformer.transform(southWestCoords[0], southWestCoords[1])

    print(southWestPost)
    print(southWestCoords)