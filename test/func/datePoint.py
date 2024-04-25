class datePoint:
    def __init__(self, date, temperature=-1, irradiance=-1, pressure=-1, rainfall=-1, windspeed=-1, windangle=-1, energyData={}) -> None:
        self.date = date
        self.temperature = temperature
        self.irradiance = irradiance
        self.pressure = pressure
        self.rainfall = rainfall
        self.windspeed = windspeed
        self.windangle = windangle
        self.energyData = energyData

        self.dayoftheyear = date.timetuple().tm_yday

    def getDateStr(self):
        return self.date.strftime("%d/%m/%Y")
    
    def printClimateOverview(self):
            linelength = 35
            divider = "#"*5
            print(f"\n{divider} ↓ {self.getDateStr()} Climate ↓ {divider}")
            print(f"{'Windspeed (ms^-1)':<{linelength}} |   {round(self.windspeed, 3)}")
            print(f"{'Wind Angle(deg)':<{linelength}} |   {round(self.windangle, 3)}")
            print(f"{'Temperature (C)':<{linelength}} |   {round(self.temperature, 3)}")
            print(f"{'Irradiance (MJ/m^2)':<{linelength}} |   {round(self.irradiance, 3)}")
            print(f"{'Pressure (hPa)':<{linelength}} |   {round(self.pressure, 3)}")
            print(f"{'Rainfall (mm)':<{linelength}} |   {round(self.rainfall, 3)}")
            print(f"{divider} ↑ {self.getDateStr()} Climate ↑ {divider}\n")

    def printGridOverview(self):
        linelength = 55
        divider = "#"*5
        try:
            print(f"\n{divider} ↓ {self.getDateStr()} Energy ↓ {divider}")
            print(f"{'Total Demand (GWh)':<{linelength}} |   {round(self.energyData['au.nem.nsw1.demand.energy (GWh)'], 3)}")
            print(f"{'Energy Generated from Black Coal (GWh)':<{linelength}} |   {round(self.energyData['au.nem.nsw1.fuel_tech.coal_black.energy (GWh)'], 3)}")
            print(f"{'Energy Generated from Hydro (GWh)':<{linelength}} |   {round(self.energyData['au.nem.nsw1.fuel_tech.hydro.energy (GWh)'], 3)}")
            print(f"{'Energy Generated from Rooftop Solar (GWh)':<{linelength}} |   {round(self.energyData['au.nem.nsw1.fuel_tech.solar_rooftop.energy (GWh)'], 3)}")
            print(f"{'Energy Generated from Solar Utilities (GWh)':<{linelength}} |   {round(self.energyData['au.nem.nsw1.fuel_tech.solar_utility.energy (GWh)'], 3)}")
            print(f"{'Energy Generated from Wind (GWh)':<{linelength}} |   {round(self.energyData['au.nem.nsw1.fuel_tech.wind.energy (GWh)'], 3)}")
            print(f"{'Energy Imported (GWh)':<{linelength}} |   {round(self.energyData['au.nem.nsw1.fuel_tech.imports.energy (GWh)'], 3)}")
            print(f"{'Energy Exported (GWh)':<{linelength}} |   {round(self.energyData['au.nem.nsw1.fuel_tech.exports.energy (GWh)'], 3)}")
            print(f"\n{divider} ↑ {self.getDateStr()} Energy ↑ {divider}")
            
        except ValueError:
             print("SOME OR ALL OF THE REQUIRED ENERGY GRID VALUES ARE NOT PRESENT FOR THIS DAY")