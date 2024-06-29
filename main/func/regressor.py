import numpy as np
from scipy.interpolate import interp1d
import math

class SVRregressor:
    def __init__(self, type, svr, scalerX, scalerY) -> None:
        self.regressorType = type
        self.svr = svr
        self.scalerX = scalerX
        self.scalerY = scalerY
        
            
        
    def predict(self, datePoint):

        if type(datePoint) != list:
            datePoint = [datePoint]

        a = np.empty((len(datePoint), 5))
        for dateIndex, date in enumerate(datePoint):
            a[dateIndex] = [
            date.dayoftheyear,
            date.temperature,
            date.irradiance,
            date.pressure,
            date.rainfall,
        ]
        transformedVal = self.scalerX.transform(a)
        predictedVal = self.svr.predict(transformedVal)
        val = self.scalerY.inverse_transform(predictedVal.reshape(1, -1))
        return val
    
class TurbineRegressor:
    def __init__(self, name, curveData, turbineAngle) -> None:
        self.name = name
        self.curveData = curveData
        self.turbineAngle = turbineAngle
        self.linearRegressor = interp1d(curveData[:,0], curveData[:,1])

    def predictOutput(self, windspeed, windangle, turbinesYaw):
        if turbinesYaw:
            return self.linearRegressor(windspeed)
        
        # If the turbines aren't rott
        angleDiff = (self.turbineAngle - windangle + 180 + 360) % 360 - 180

        # print(f"{windangle}, {self.}")

        if abs(angleDiff) < 90:
            windComp = windspeed * math.cos(angleDiff * (2*math.pi/180))
        else:
            windComp = 0

        if windComp < 0:
            windComp = 0

        return self.linearRegressor(windComp)
