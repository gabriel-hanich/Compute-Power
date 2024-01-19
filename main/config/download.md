# Download.json
Path: `/config/download.json`

This file describes the nature, type and duration of the data downloaded by `BOMScraper.py`. Changing this file changes the start and end dates for the collection of the GRID data from BOM

> Note that all dates are to be in the format DD/MM/YYYY

## Variables
### startDate
The first date that will be downloaded

`date`

### endData
The last date that will be downloaded. All dates between `startDate` and `endDate` will be downloaded in accordance with the `frequency` paramater.

`date`

### frequency
The number of days in between downloaded dates. For example, if set to `2`, the downloader will download data for every second day, and if set to `1`, then it download for everyday's data.

`integer`

### overRideFiles
Whether to re-download a file if it has already been downloaded. If set to `true`, then the program will download grid data even if that file is already in the data folder. If set to `false`, then only non-existent files will be downloaded. 

### dataTypes
The different categories that will be downloaded. Can be any group of the following:

- `irradiance`
- `pressure`
- `rainfall`
- `temperature`

`list of strings`