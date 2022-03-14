# include the required libraries
import netCDF4 as nc                        # dataset is in netCDF format
import matplotlib.pyplot as plt             # for graphing data to validate its presence 
from pathlib import Path                    # to iterate over all files in folder
from datetime import datetime, timedelta    # convert GPS time to UTC time
from mpl_toolkits.basemap import Basemap    # Map for plotting global data
import numpy as np


#####################################################################
################## Class to Hold TEC for each LEO ###################
#####################################################################
class tecData(object):
    def __init__(self,leo=None, prn=None, utcTime=None, tec=None, lat=None, lon=None):  # define class and parameters
        self.leo = leo              # refrenced to self. for access to LEO
        self.prn = prn              # refrenced to self. for access to PRN                                        
        self.utcTime = utcTime      # refrenced to self. for access to UTC
        self.tec = tec              # refrenced to self. for access to TEC
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
    print("Number of paths: ", numPaths)    # print total number of files to be loaded
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
        print("Progress of Data Import: ", progressCount, "/", numPaths)
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

        # Calculate Lat and Lon of each measurement
        lat = []    # empty array to store lat 
        lon = []    # empty array to store lon

        # get all required fields from PodTec data to extrapolate lat and lon at given time
        latStart = dataset.__dict__['lat_start']        # start latitude for measurement set   
        lonStart = dataset.__dict__['lon_start']        # start longitude for measurement set          
        latStop = dataset.__dict__['lat_stop']          # stop latitude for measurement set     
        lonStop = dataset.__dict__['lon_stop']          # stop longitude for measurement set 
        timeStart = dataset.__dict__['start_time']      # start time (GPS) for measurement set 
        timeStop = dataset.__dict__['stop_time']        # stop time (GPS) for measurement set 

        # calculate difference between start and stop lat, lon, time
        timeDiff = timeStop - timeStart     # time diff from start to end
        latDiff = latStop - latStart        # lat diff from start to end
        lonDiff = lonStop - lonStart        # lon diff from start to end

        # for every measurement point determine percentage through arc and apply corrective measurement to lat and lon
        for time in measurementTime:
            measurementTimeDiff = time - timeStart                          # difference of measurement time from start time
            extrapolatedLatDiff = (measurementTimeDiff/timeDiff)*latDiff    # percentage through arc*lat diff to give proposed lat movement
            extrapolatedLonDiff = (measurementTimeDiff/timeDiff)*lonDiff    # percentage through arc*lon diff to give proposed lon movement
            extrapolatedLat = latStart + extrapolatedLatDiff                # measurement extrapolated lat by adding proposed diff to start
            extrapolatedLon = lonStart + extrapolatedLonDiff                # measurement extrapolated lon by adding proposed diff to start
            lat.append(extrapolatedLat)                                     # Add final lat to array
            lon.append(extrapolatedLon)                                     # Add final lon to array

        tecDataList.append(tecData(leo=leoId, prn=prnId, utcTime=utcTime, tec=tec, lat=lat, lon=lon)) # Add data extracted to class in data list

    print("Data Import Complete - Now Sorting Data")
    # sort list by LEO ID, and then by PRN ID
    tecDataList.sort(key=lambda l: (l.leo, l.prn, l.utcTime[0]))
    print("Data Sort Complete")
    return(tecDataList)

#####################################################################
################## Display the Extracted Datasets ###################
#####################################################################

############################### MAIN ################################
directoryPath = "C:\\Users\\crutt\\Documents\\University\\Final Year Project\\FYP_Data\\podTc2_postProc_2020_032"   # Directory path containing Data

# Determine number of files to be imported
numberOfFiles = getNumFiles(directoryPath)

# Import files to Class list for easy data access
tecDataList = importDataToClassList(directoryPath, numberOfFiles)

print("Drawing World Map of TEC")
map = Basemap()
map.drawcoastlines()
map.drawparallels(np.arange(-90,90,30),labels=[1,1,0,1], fontsize=8)
map.drawmeridians(np.arange(-180,180,30),labels=[1,1,0,1], rotation=45, fontsize=8)
for data in tecDataList:
    map.scatter(data.lon, data.lat, latlon=True, c=data.tec, s=10, cmap='Reds', alpha=0.2)
plt.colorbar(label='TECU')
plt.clim(0,600) 
plt.xlabel('Longitude', labelpad=40, fontsize=8)
plt.ylabel('Latitude', labelpad=40, fontsize=8) 
plt.title('COSMIC 2 TEC plot on global map for one day', fontsize=8) 
plt.show()



# plot time vs TEC
print("Plotting TEC vs Time")
for data in tecDataList:
    plt.plot(data.utcTime, data.tec)                            # plot time vs TEC
    plt.ylabel("TEC along LEO-GPS link (TECU)")                 # label y axis
    plt.xlabel(f"UTC Time of Measurement on {data.utcTime[0].year}/{data.utcTime[0].month}/{data.utcTime[0].day}")  # label x axis
    plt.title("TEC plot for LEO 1-6 PRN 1-32 for one day")      # title 
plt.show()

# plot time vs TEC for specific LEO and PRN ID
print("Enter LEO ID to display: ")  # prompt user to enter LEO ID
displayLeo = int(input())           # capture LEO ID
print("Enter PRN ID to display: ")  # prompt user to enter PRN ID
displayPrn = int(input())           # prompt user to enter PRN ID

# search list and only plot if is specified LEO and PRN ID
for data in tecDataList:
    if data.leo == displayLeo and data.prn == displayPrn:   # only LEO and PRN ID 
        plt.plot(data.utcTime, data.tec)                    # plot time vs TEC

plt.ylabel("TEC along LEO-GPS link (TECU)")                 # label y axis
plt.xlabel(f"UTC Time of Measurement on {data.utcTime[0].year}/{data.utcTime[0].month}/{data.utcTime[0].day}")  # label x axis
plt.title(f"TEC plot for LEO {displayLeo} PRN {displayPrn} for one day")       # title 
plt.show()