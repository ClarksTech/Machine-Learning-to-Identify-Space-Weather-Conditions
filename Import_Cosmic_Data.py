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
    def __init__(self,leo=None, prn=None, utcTime=None, tec=None, tecDiff=None, lat=None, lon=None):  # define class and parameters
        self.leo = leo              # refrenced to self. for access to LEO
        self.prn = prn              # refrenced to self. for access to PRN                                        
        self.utcTime = utcTime      # refrenced to self. for access to UTC
        self.tec = tec              # refrenced to self. for access to TEC
        self.tecDiff = tecDiff      # refrenced to self. for access to TEC Diff
        self.lat = lat              # refrenced to self. for access to latitude
        self.lon = lon              # refrenced to self. for access to longitude

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
    paths = Path(directoryPath).glob('**/*.3430_nc')                                                                    # Path for all .3430_nc podTEC files

    # repeat for all files in directory to show variation
    progressCount = 0
    for path in paths:

        # Print Progress
        print("Progress of Data Import: ", progressCount, "/", numPaths, end='\r')
        progressCount += 1

        # Access the data and obtain TEC and measurement time
        dataset = nc.Dataset(path)              # Access the dataset using netCDF4 library tools
        tec = dataset['TEC'][:]                 # store the entire TEC data in variable TEC
        measurementTime = dataset['time'][:]    # store entire time data in variable

        # convert GPS time to UTC time
        utcTime = []                    # initialise array to hold utcTime
        for time in measurementTime:    # convert every measurement
            utcTime.append(datetime(1980, 1, 6) + timedelta(seconds=time - (37 - 19)))  # GPS and UTS initialised 1980,1,6. Add time delta acounting for leapseconds

        # Identify the LEO and PRN satellites used for measurements
        leoId = dataset.__dict__['leo_id']          # Store LEO ID
        prnId = dataset.__dict__['prn_id']          # Store PRN ID

        # get LEO satellite ECEF coordinate converting to metres
        leoX = np.array(dataset['x_LEO'][:]) * 1000     # store the entire TEC data in variable TEC
        leoY = np.array(dataset['y_LEO'][:]) * 1000     # store the entire TEC data in variable TEC
        leoZ = np.array(dataset['z_LEO'][:]) * 1000     # store the entire TEC data in variable TEC

        # convert to LLA
        lat, lon, alt = pm.ecef2geodetic(leoX, leoY, leoZ, ell=None, deg=True)

        # Calculate the TEC difference between measurements
        tempTecArr = np.array(tec)          # create temp array to avoid altering TEC array
        tecDiff = np.diff(tempTecArr)       # find the diff between consecutive values of TEC
        tecDiff = np.append(tecDiff, [0])   # to ensure remains same length as time arrays

        tecDataList.append(tecData(leo=leoId, prn=prnId, utcTime=utcTime, tec=tec, tecDiff=tecDiff, lat=lat, lon=lon)) # Add data extracted to class in data list

    print("Data Import Complete - Now Sorting Data")

    # sort list by LEO ID, and then by PRN ID
    tecDataList.sort(key=lambda l: (l.leo, l.prn, l.utcTime[0]))
    
    print("Data Sort Complete")

    return(tecDataList)             # return the list of class objects






