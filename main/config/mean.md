# Mean.json
This file controls the values used in both the normalization of the density data, and the use of these values in determining the geographic mean. 

Used in `mean.py`

## File structure
The file is structured to include multiple different profiles, as shown below. The list of points creates a polygon, and all coordinates within that polygon will be considered by the normaliaztion and mean calculations. To close the polygon, a line is drawn from the final point to the first point. 

```
{
    "profileName": {
        "isbounding": boolean
        "coords" : [
            [Lat1, Lon1],
            [Lat2, Lon2],
            [Lat3, Lon3],
            [Lat4, Lon4]
        ]
    }
}
```

### profileName
This can be replaced by any `string`, and is the name of the profile. 

### isbounding
If set to true, the written value will be an average of all the cells within a boundin box defined by `coords`. If set to false, the output will be the raw value at the first coordinate specified in `coords`

### Lat
The latitude of a point. It must be a `float`


### Lon
The Longitude of a point. It must be a `float`