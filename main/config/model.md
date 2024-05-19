# model.json
Path: `/config/download.json`

The file describes thow the SVR models for demand and solar production will be trained

Used in `modelTrainer.py`, `simulator.py`

## File Structure

```json
{
    "profileName": {
        "doGammaTuning": boolean,
        "doCValTuning": boolean,
        "models" : [
            {
                "modelType": "demand",
                "kernel": string,
                "cVal": float,
                "gammaVal": float,
                "testValCount": integer,
                "doDataDump": boolean
            }
        ]
    }
}
```

## Variables
### profileName
Replace this with the name of the profile, as it will appear in the selector at the start of the model trainer

#### doGammaTuning
Whether or not to test a bunch of different gamma values

> Note, this feature is currently not supported, and will be added later if I can find the time

`bolean`

### doCValTuning
Whether or not to test a bunch of different C-values

> Note, this feature is currently not supported, and will be added later if I can find the time

`bolean`

### models
Models contains a list of dictionaries, where each item describes one specific model that will be trained by the code. The file trains all of these models one after the other.

`list of dicts`

#### modelType
Replaced this with the type of model that needs to be made. Can either be `demand` or `solar`. 

`string`

#### kernel
The SVR kernel that will be used to create the model. Can either be `rbf`, `linear` or `poly`.

`string`

#### cVal
The C value that will be used by the model.

`float`

#### gammaVal
The Gamma value that will be used by the model.

`float`

#### testValCount
The number of values that will be used to evaluate the model's performance. Note that the model will NOT be trained on these values, so having a value that is too high will limit model performance.

`integer`

#### doDataDump
Whether to dump all of the data at the end. The code will always save the models, however this flag dictates if the climate and predicted values will be included as well in a seperate .csv file. 

`boolean`


