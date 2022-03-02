#include the required libraries
import netCDF4 as nc                # dataset is in netCDF format
import matplotlib.pyplot as plt     # for graphing data to validate its presence 
from pathlib import Path            # to iterate over all files in folder

#####################################################################
#################### Open dataset and access TEC ####################
#####################################################################
directoryPath = "C:\\Users\\crutt\\Documents\\University\\Final Year Project\\FYP_Data\\podTc2_postProc_2020_032"   # Directory path containing Data
paths = Path(directoryPath).glob('**/*.3430_nc')                                                                    # Path for all .3430_nc podTEC files

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

    ####################### Plot TEC against Time #######################
    plt.plot(measurementTime, TEC)                      # plot GPS measurement time on x axis, TEC on y axis
    plt.ylabel("TEC along LEO-GPS link (TECU)")         # label y axis
    plt.xlabel("Time of GPS measurement (GPS Second)")  # label x axis
    plt.show()                                          # display the plot



