# include required libraries
from mpl_toolkits.basemap import Basemap    # Map for plotting global data
import numpy as np                          # numpy used for basemap plotting
import matplotlib.pyplot as plt             # for graphing data to validate its presence 

#####################################################################
############### Function to display TEC on World Map ################
#####################################################################
def displayTecWorldMap(tecDataList):
    print("Drawing World Map of TEC")
    map = Basemap()                                                                             # Using basemap as basis for world map
    map.drawcoastlines()                                                                        # Only add the costal lines to the map for visual refrence
    map.drawparallels(np.arange(-90,90,30),labels=[1,1,0,1], fontsize=8)                        # Add Longitude lines and degree labels
    map.drawmeridians(np.arange(-180,180,30),labels=[1,1,0,1], rotation=45, fontsize=8)         # Add latitude lines and degree labels

    # repeat for every TEC measurement for entire day
    for data in tecDataList:
        map.scatter(data.lon, data.lat, latlon=True, c=data.tec, s=10, cmap='Reds', alpha=0.2)  # Plot as a scatter where shade of red depends on TEC value
    plt.colorbar(label='TECU')                                                                  # Add coloutbar key for TECu Shades of red
    plt.clim(0,1000)                                                                            # Key from 0 to 1000 (max TECu measurement ~600)
    plt.xlabel('Longitude', labelpad=40, fontsize=8)                                            # Add x axis label
    plt.ylabel('Latitude', labelpad=40, fontsize=8)                                             # Add y axis label
    plt.title('COSMIC 2 TEC plot on global map for one day', fontsize=8)                        # Add title
    plt.show()
    return()

#####################################################################
############ Function to display TEC Diff on World Map ##############
#####################################################################
def displayTecDiffWorldMap(tecDataList):
    print("Drawing World Map of TEC Diff")
    map = Basemap()                                                                             # Using basemap as basis for world map
    map.drawcoastlines()                                                                        # Only add the costal lines to the map for visual refrence
    map.drawparallels(np.arange(-90,90,30),labels=[1,1,0,1], fontsize=8)                        # Add Longitude lines and degree labels
    map.drawmeridians(np.arange(-180,180,30),labels=[1,1,0,1], rotation=45, fontsize=8)         # Add latitude lines and degree labels

    # repeat for every TEC measurement for entire day
    for data in tecDataList:
        map.scatter(data.lon, data.lat, latlon=True, c=data.tecDiff, s=10, cmap='RdBu_r', alpha=0.2)  # Plot as a scatter where shade of red depends on TEC Diff value
    plt.colorbar(label='TECU Diff')                                                                 # Add coloutbar key for TECu Shades of red
    plt.clim(-60,60)                                                                                # Key from 0 to 1000 (max TEC Diff measurement ~+-50)
    plt.xlabel('Longitude', labelpad=40, fontsize=8)                                                # Add x axis label
    plt.ylabel('Latitude', labelpad=40, fontsize=8)                                                 # Add y axis label
    plt.title('COSMIC 2 TEC Diff plot on global map for one day', fontsize=8)                       # Add title
    plt.show()
    return()

#####################################################################
############### Function to display TEC vs UTC time #################
#####################################################################
def displayTecVsUtc(tecDataList):
    # plot time vs TEC
    print("Plotting TEC vs Time")
    for data in tecDataList:
        plt.plot(data.utcTime, data.tec)                            # plot time vs TEC
        plt.ylabel("TEC along LEO-GPS link (TECU)")                 # label y axis
        plt.xlabel(f"UTC Time of Measurement on {data.utcTime[0].year}/{data.utcTime[0].month}/{data.utcTime[0].day}")  # label x axis
        plt.title("TEC plot for LEO 1-6 PRN 1-32 for one day")      # title 
    plt.show()
    return()

#####################################################################
############ Function to display TEC Diff vs UTC time ###############
#####################################################################
def displayTecDiffVsUtc(tecDataList):
    # plot time vs TEC
    print("Plotting TEC Diff vs Time")
    for data in tecDataList:
        plt.plot(data.utcTime, data.tecDiff)                        # plot time vs TEC
        plt.ylabel("TEC Diff along LEO-GPS link (TECU)")            # label y axis
        plt.xlabel(f"UTC Time of Measurement on {data.utcTime[0].year}/{data.utcTime[0].month}/{data.utcTime[0].day}")  # label x axis
        plt.title("TEC Diff plot for LEO 1-6 PRN 1-32 for one day")      # title 
    plt.show()
    return()

#####################################################################
######### Function to display TEC vs UTC time (specific) ############
#####################################################################
def displayTecVsUtcSpecific(tecDataList):
    # plot time vs TEC for specific LEO and PRN ID
    print("Enter LEO ID to display: ")  # prompt user to enter LEO ID
    displayLeo = int(input())           # capture LEO ID
    print("Enter PRN ID to display: ")  # prompt user to enter PRN ID
    displayPrn = int(input())           # prompt user to enter PRN ID

    # search list and only plot if is specified LEO and PRN ID
    for data in tecDataList:
        if data.leo == displayLeo and data.prn == displayPrn:   # only LEO and PRN ID 
            plt.plot(data.utcTime, data.tec)                    # plot time vs TEC

    plt.ylabel("TEC along LEO-GPS link (TECU)")                                                                     # label y axis
    plt.xlabel(f"UTC Time of Measurement on {data.utcTime[0].year}/{data.utcTime[0].month}/{data.utcTime[0].day}")  # label x axis
    plt.title(f"TEC plot for LEO {displayLeo} PRN {displayPrn} for one day")                                        # title 
    plt.show()
    return()

