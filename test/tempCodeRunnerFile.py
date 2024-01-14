    # bottomRight = dataset.transform * (dataset.width, dataset.height)
    # topLeft = dataset.transform * (0, 0)
    # southWestCoords = [abs(topLeft[0]), abs(bottomRight[1])]

    # x_res, y_res = dataset.res
    # pixel_height_meters = y_res
    # row, col = dataset.height // 2, dataset.width // 2 # get the center pixel
    # x, y = dataset.xy(row, col) # get the spatial coordinates of the center pixel
    # latitude = y # get the latitude of the center pixel
    # R = 6378137 # radius of the earth in meters
    # pixel_height_degrees = abs(pixel_height_meters * 360 / (2 * math.pi * R * math.cos(math.radians(latitude))))
    # print(pixel_height_degrees)