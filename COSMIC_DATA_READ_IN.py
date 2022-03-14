# include the required libraries
import netCDF4 as nc                        # dataset is in netCDF format
import matplotlib.pyplot as plt             # for graphing data to validate its presence 
from pathlib import Path                    # to iterate over all files in folder
from datetime import datetime, timedelta    # convert GPS time to UTC time
import pyproj                               # convert ECF to LLA

#####################################################################
################## Class to Hold TEC for each LEO ###################
#####################################################################
class tecData(object):
    def __init__(self,leo=None, prn=None, utcTime=None, tec=None, x=None, y=None, z=None, lat=None, lon=None, alt=None):  # define class and parameters
        self.leo = leo              # refrenced to self. for access to LEO
        self.prn = prn              # refrenced to self. for access to PRN                                        
        self.utcTime = utcTime      # refrenced to self. for access to UTC
        self.tec = tec              # refrenced to self. for access to TEC
        self.x = x                  # refrenced to self. for access to ECF X
        self.y = y                  # refrenced to self. for access to ECF Y
        self.z = z                  # refrenced to self. for access to ECF Z
        self.lat = lat              # refrenced to self. for access to latitude
        self.lon = lon              # refrenced to self. for access to longitude
        self.alt = alt              # refrenced to self. for access to altitude

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

        # Obtain ECF coordinate of each measurement point
        ecfX = dataset['x_LEO'][:]  # x coordinate
        ecfY = dataset['y_LEO'][:]  # y coordinate
        ecfZ = dataset['z_LEO'][:]  # z coordinate

        # convert ECEF to Lat Long Alt
        lat = []    # empty containers for lat
        lon = []    # empty containers for lon
        alt = []    # empty container for alt

        # convert every measurement
        for pos in range(len(ecfX)):
            x = ecfX[pos]*1000  # convert from km to m
            y = ecfY[pos]*1000  # convert from km to m
            z = ecfZ[pos]*1000  # convert from km to m

            # pyproj for conversion from ECF to LLA WGS84 in degrees
            transformer = pyproj.Transformer.from_crs(
                {"proj":'geocent', "ellps":'WGS84', "datum":'WGS84'},
                {"proj":'latlong', "ellps":'WGS84', "datum":'WGS84'}  
            )
            lon1, lat1, alt1 = transformer.transform(x, y, z, radians=False)   # transform to desired format
            lat.append(lat1)    # append to lat list
            lon.append(lon1)    # append to lon list
            alt.append(alt1)    # append to alt list

        tecDataList.append(tecData(leo=leoId, prn=prnId, utcTime=utcTime, tec=tec, x=ecfX, y=ecfY, z=ecfZ, lat=lat, lon=lon, alt=alt)) # Add data extracted to class in data list

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

# plot time vs TEC
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