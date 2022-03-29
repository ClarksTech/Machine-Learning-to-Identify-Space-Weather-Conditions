# include the required libraries
import netCDF4 as nc                        # dataset is in netCDF format
from pathlib import Path                    # to iterate over all files in folder
from datetime import datetime, timedelta    # convert GPS time to UTC time
import numpy as np                          # to find TEC DIFF
import pymap3d as pm

#####################################################################
################## Class to Hold TEC for each LEO ###################
#####################################################################
class tecData(object):
    def __init__(self,leo=None, prn=None, antId=None, utcTime=None, tec=None, tecDiff=None, lat=None, lon=None, elev=None):  # define class and parameters
        self.leo = leo              # refrenced to self. for access to LEO
        self.prn = prn              # refrenced to self. for access to PRN  
        self.antId = antId          # refrenced to self. for access to antenna ID                              
        self.utcTime = utcTime      # refrenced to self. for access to UTC
        self.tec = tec              # refrenced to self. for access to TEC
        self.tecDiff = tecDiff      # refrenced to self. for access to TEC Diff
        self.lat = lat              # refrenced to self. for access to latitude
        self.lon = lon              # refrenced to self. for access to longitude
        self.elev = elev            # refrenced to self. for access to elevation angle

#####################################################################
####### Count Number of Files to be loaded for progress bar #########
#####################################################################
def getNumFiles(directoryPath):
    paths = Path(directoryPath).glob('**/*.3430_nc')                                                                    # Path for all .3430_nc podTEC files
    # Progres bar setup
    numPaths = 0
    # increment counter for every path
    for path in paths:
        numPaths += 1
    print("Number of Data Files to Import: ", numPaths)    # print total number of files to be loaded
    return (numPaths)

#####################################################################
#################### Open dataset and access TEC ####################
#####################################################################
def importDataToClassList(directoryPath, numPaths):
    # empty list to store classes for each LEO and PRN
    tecDataList = []
    paths = Path(directoryPath).glob('**/*.3430_nc')    # Path for all .3430_nc podTEC files

    # repeat for all files in directory to show variation
    progressCount = 0
    for path in paths:

        # Print Progress
        progress = progressCount/numPaths * 100
        print("Progress of Data Import: %.2f" %progress, "%",end='\r')
        progressCount += 1

        # Access the data and obtain TEC and measurement time
        dataset = nc.Dataset(path)                      # Access the dataset using netCDF4 library tools
        tecTemp = np.array(dataset['TEC'][:])               # store the entire TEC data in variable TEC
        measurementTimeTemp = np.array(dataset['time'][:])  # store entire time data in variable

        # Identify the LEO and PRN satellites used for measurements
        leoId = dataset.__dict__['leo_id']          # Store LEO ID
        prnId = dataset.__dict__['prn_id']          # Store PRN ID
        antennaId = dataset.__dict__['antenna_id']  # Store Antenna ID

        # get LEO satellite ECEF coordinate converting to metres
        leoX = np.array(dataset['x_LEO'][:]) * 1000     # store the entire TEC data in variable TEC
        leoY = np.array(dataset['y_LEO'][:]) * 1000     # store the entire TEC data in variable TEC
        leoZ = np.array(dataset['z_LEO'][:]) * 1000     # store the entire TEC data in variable TEC

        # convert to LLA
        latTemp, lonTemp, alt = pm.ecef2geodetic(leoX, leoY, leoZ, ell=None, deg=True)

        # get and store LEO - GPS link elevation angle
        elevationTemp = np.array(dataset['elevation'][:])

        # Only keep values for elevations at or below 0 degrees
        tec = []                # empty array to hold values of correct elevation
        measurementTime = []    # empty array to hold values of correct elevation  
        lat = []                # empty array to hold values of correct elevation
        lon = []                # empty array to hold values of correct elevation
        elevation = []          # empty array to hold values of correct elevation
        negativeFlag = 0        # flag to determine if negative exists in measurement set

        # Loop over all datapoints and add to final arrya if is of negative elevation
        for i in range(len(elevationTemp)):
            if elevationTemp[i] <= 0:
                elevation.append(elevationTemp[i])
                tec.append(tecTemp[i])
                measurementTime.append(measurementTimeTemp[i])
                lat.append(latTemp[i])
                lon.append(lonTemp[i])
                negativeFlag = 1        # set negative flag to 1 to acknowledge are negatives

        # only perform further conversions and add to array of objects if negatives exist
        if negativeFlag == 1:
            # convert GPS time to UTC time
            utcTime = []                    # initialise array to hold utcTime
            for time in measurementTime:    # convert every measurement
                utcTime.append(datetime(1980, 1, 6) + timedelta(seconds=time - (37 - 19)))  # GPS and UTS initialised 1980,1,6. Add time delta acounting for leapseconds

            # Calculate the TEC difference between measurements
            tempTecArr = np.array(tec)      # create temp array to avoid altering TEC array
            tecDiff = []                    # create empty array to hold the tec differences
            # repeat for all tec values excluding last as is no next value to difference off
            for i in range(len(tempTecArr)-1):
                timeDif = measurementTime[i+1]-measurementTime[i]   # calculated time difference between TEC measurements
                tecDif = tempTecArr[i+1]-tempTecArr[i]              # calculate TEC difference between measuremnts
                tecDifferenceSecond = tecDif/timeDif                # calculate diff as change in TEC over change in time so is TECu per Second
                tecDiff.append(tecDifferenceSecond)                 # append to empty container
            tecDiff.append(0)                                       # assign 0 to last value as no next value to difference off

            tecDataList.append(tecData(leo=leoId, prn=prnId, antId=antennaId, utcTime=utcTime, tec=tec, tecDiff=tecDiff, lat=lat, lon=lon, elev=elevation)) # Add data extracted to class in data list

    print("Progress of Data import: 100 % - Import Complete")

    return(tecDataList)             # return the list of class objects






