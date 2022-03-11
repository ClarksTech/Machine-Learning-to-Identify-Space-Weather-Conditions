# include the required libraries
import netCDF4 as nc                        # dataset is in netCDF format
import matplotlib.pyplot as plt             # for graphing data to validate its presence 
from pathlib import Path                    # to iterate over all files in folder
from datetime import datetime, timedelta    # convert GPS time to UTC time

#####################################################################
################## Class to Hold TEC for each LEO ###################
#####################################################################
class tecData(object):
    def __init__(self,leo=None, prn=None, utcTime=None, tec=None):  # define class and parameters
        self.leo = leo                                              # refrenced to self. for access
        self.prn = prn              # refrenced to self. for access                                          
        self.utcTime = utcTime      # refrenced to self. for access
        self.tec = tec              # refrenced to self. for access

# empty list to store classes for each LEO and PRN
tecDataList = []

#####################################################################
####### Count Number of Files to be loaded for progress bar #########
#####################################################################
directoryPath = "C:\\Users\\crutt\\Documents\\University\\Final Year Project\\FYP_Data\\podTc2_postProc_2020_032"   # Directory path containing Data
paths = Path(directoryPath).glob('**/*.3430_nc')                                                                    # Path for all .3430_nc podTEC files

# Progres bar setup
numPaths = 0
# increment counter for every path
for path in paths:
    numPaths += 1
print("Number of paths: ", numPaths)    # print total number of files to be loaded

#####################################################################
#################### Open dataset and access TEC ####################
#####################################################################
directoryPath = "C:\\Users\\crutt\\Documents\\University\\Final Year Project\\FYP_Data\\podTc2_postProc_2020_032"   # Directory path containing Data
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

    tecDataList.append(tecData(leoId, prnId, utcTime, tec)) # Add data extracted to class in data list

# sort list by LEO ID, and then by PRN ID
tecDataList.sort(key=lambda l: (l.leo, l.prn, l.utcTime[0]))

# plot time vs TEC
for data in tecDataList:
    plt.plot(data.utcTime, data.tec)                    # plot time vs TEC
    plt.ylabel("TEC along LEO-GPS link (TECU)")         # label y axis
    plt.xlabel(f"UTC Time of Measurement on {data.utcTime[0].year}/{data.utcTime[0].month}/{data.utcTime[0].day}")  # label x axis
    #plt.title(f"TEC plot for PRN ID: {data.leo} and LEO ID: {data.prn}")                                            # title with PRN and LEO ID
    plt.title("TEC plot for LEO 1-6 PRN 1-32 for one day")          # title 
plt.show()

# plot time vs TEC for LEO 1 PRN 1
for data in tecDataList:
    if data.leo == 1 and data.prn == 1:
        plt.plot(data.utcTime, data.tec)                    # plot time vs TEC

plt.ylabel("TEC along LEO-GPS link (TECU)")                 # label y axis
plt.xlabel(f"UTC Time of Measurement on {data.utcTime[0].year}/{data.utcTime[0].month}/{data.utcTime[0].day}")  # label x axis
plt.title("TEC plot for LEO 1 PRN 1 for one day")           # title 
plt.show()
