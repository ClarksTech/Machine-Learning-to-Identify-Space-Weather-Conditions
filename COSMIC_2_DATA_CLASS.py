# include the required libraries
import netCDF4 as nc                        # dataset is in netCDF format
import matplotlib.pyplot as plt             # for graphing data to validate its presence 
from pathlib import Path                    # to iterate over all files in folder
from datetime import datetime, timedelta

from sympy import timed    # to convert GPS to UTC time

#####################################################################
#################### Open dataset and access TEC ####################
#####################################################################
directoryPath = "C:\\Users\\crutt\\Documents\\University\\Final Year Project\\FYP_Data\\podTc2_postProc_2020_032"   # Directory path containing Data
paths = Path(directoryPath).glob('**/*.3430_nc')                                                                    # Path for all .3430_nc podTEC files

leoIdArr = []
prnIdArr = []

# repeat for all files in directory to show variation
for path in paths:
    dataset = nc.Dataset(path)  # Access the dataset using netCDF4 library tools
    print(dataset)                  # printing dataset to display all available fields to verify correct podTEC format
    print(dataset['TEC'])           # print TEC variable to verify the TEC data format
    TEC = dataset['TEC'][:]         # store the entire TEC data in variable TEC
    print(TEC)                      # Print variable TEC to confirm data transfer
    print(dataset['time'])                  # print time variable to verify time format
    measurementTime = dataset['time'][:]    # store entire time data in variable
    print(measurementTime)                  # print variable to confirm data transfer

    # convert GPS time to UTC time
    utcTime = []                    # initialise array to hold utcTime
    for time in measurementTime:    # convert every measurement
        utcTime.append(datetime(1980, 1, 6) + timedelta(seconds=time - (37 - 19)))  # GPS and UTS initialised 1980,1,6. Add time delta acounting for leapseconds

    # Identify the LEO and PRN satellites used for measurements
    print(dataset.__dict__['leo_id'])           # print LEO ID
    print(dataset.__dict__['prn_id'])           # print PRN ID
    leoId = dataset.__dict__['leo_id']          # Store LEO ID
    prnId = dataset.__dict__['prn_id']          # Store PRN ID
    leoIdArr.append(dataset.__dict__['leo_id'])          # Store LEO ID
    prnIdArr.append(dataset.__dict__['prn_id'])          # Store PRN ID

    ####################### Plot TEC against Time #######################
    plt.plot(utcTime, TEC)                                              # plot GPS measurement time on x axis, TEC on y axis
    plt.ylabel("TEC along LEO-GPS link (TECU)")                         # label y axis
    plt.xlabel(f"UTC Time of Measurement on {utcTime[0].year}/{utcTime[0].month}/{utcTime[0].day}") # label x axis
    plt.title(f"TEC plot for PRN ID: {leoId} and LEO ID: {prnId}")      # title with PRN and LEO ID
    plt.show()  