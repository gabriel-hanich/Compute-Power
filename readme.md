# Compute Power
Project Compute Power aims to use computational techniques to predict electricity consumption and demand based upon short term weather conditions. 

> Note that this repo comes with a years worth of .GRID data. More data can be downloaded using `main/downloader.py`, but this is to be done by the user

## Structure of the Repo
### Test
This is a test folder for me to mess around in 

### Main
This is the main folder

# Workflow
If you intend on actually using the code, everything you need is in the `./main` folder. The files in the root directory are tools that rely on the functions and classes provided in `./main/func`. The workflow operates as follows:

1. Relevant `.json` files are updated
2. Data is downloaded using `downloader.py`
3. Mean scores are calculated using `mean.py`

The data that can be downloaded measures:
- Irradiance (MJ/m^2)
- Temperature (C)
- Pressure (hPa)
- Rainfall (mm)


## .JSON File adjustments
Inside of `main/config` is a number of `.json` files with associated `.md` files that explain what each of the JSON parameters do. Every file is broken up into multiple different profiles, allowing multiple different config settings to be tested. 

## Data Downloading
`downloader.py` downloads meterological data from BOM in the form of `.GRID` files. These files are 2D arrays holding the given climatic variable corresponding with the given latitude and longitude. `downloader.py` can be configured to download any combination of the 4 studied variables, over any time period, with different frequencies. It can be configured to only download missing data or override existing stored data to redownload files.

The output from this download is dumped into `./main/data/[CLIMATE VARIABLE]/[DATE].grid`. Each file is a map showing the distribution of the given climatic variable across Australia for the given date. 

## Mean Calculation
Each of the seperate `.GRID` files can then be averaged and combined into one `.csv` file by `mean.py`. Mean.py can be configured to isolate the conditions of a specific lat/lon coordinate, or take an average of all coordinates within the bounding box. If this is done, this average is weighted according to the population density determined by `./main/data/density/compressedDensity.grid`.  