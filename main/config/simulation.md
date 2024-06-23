# simulation.json
Path: `/config/simulation.json`

This file describes the paramaters inputted into the models as a part of the simulation

Used in `simulator.py`

## File Structure

```json
{
    "profileName": {
        "scenarioName": "string",
        "solarCapacity": float,
        "turbineName": string,
        "turbineCount": int,
        "meanTurbineDirection": int,
        "turbineDirectionRange": int,
        "useRealClimateVar": boolean,
        "variables": {
            "dayOfTheYear": float OR dict,
            "temperature": float OR dict,
            "irradiance": float OR dict,
            "pressure": float OR dict,
            "rainfall": float OR dict,
            "windspeed": float OR dict,
            "windangle": float OR dict
        }
    }
}
```

## Variables
### profileName
Replace this with the name of the profile, as it will appear in the selector at the start of the model trainer

`string`

### scenarioName
The name of the scenario. Dictates the name of the data file after it is exported. 

`string`

### solarCapacity
The overall solar capacity (in KwH) for all of Australia

`float`

### turbineName
The name of the .csv file that contains the generation curve for the wind turbine model

`string`

### turbineCount
The number of turbines in the simulated wind farm

`int`

### meanTurbineDirection
The middle direction a turbine will face. The possible range of turbine directions is between $\text{meanTurbineDirection} - \frac{1}{2}\times \text{turbineDirectionRange}$ and $\text{meanTurbineDirection} + \frac{1}{2}\times \text{turbineDirectionRange}$. Where 0 is north, 90 is East and so on. 

`float`

### turbineDirectionRange
The range of directions a turbine will face. The central value of this range is given by `meanTurbineDirection`.

`float`

### useRealClimateVar
Whether to use the values in `data/processed/climate` or the ones specific by the user

### variables
Inside of variables is the paramaters of the model. Each parameter can eiteher have a number, or a dict. If it is a number, the simulator will simply apply this value to every instance it is run. However, if a dict is supplied, it must be of the below format:

```json
{"min": int, "max": int, "step": int}
```

This means the simulation will start at the min value, and test every value up to the max value, incrasing by the step value each time. 

> If you have selected useRealClimateVar, then the variables must instead be "startDate" and "endDate", which will specify the range of dates used as inputs for the simulation. 