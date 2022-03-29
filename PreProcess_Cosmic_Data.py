# include required libraries
import matplotlib.pyplot as plt             # for plotting delta
import numpy as np                          # for manipulating moving averages
from mpl_toolkits.basemap import Basemap    # Map for plotting global data

#####################################################################
########### Function to obtain moving average of TEC Diff ###########
#####################################################################
def calculateMovingAverages(tecDataList):
    print("Calculating Moving Averages...")
    windowSize = 5  # chosen as 5*7.5 = 37.5 km distance average = around 6 measurements per average EPB size of 230km
    # repeat for every TEC Diff measurement for entire day
    for data in tecDataList:
        if len(data.tecDiff) >= windowSize:                         # only find moving average if enough datapoints exist (i.e. window size)
            movingAverages = [data.tecDiff[0], data.tecDiff[1]]     # first two points cant be calculated so pass through tecDiff
            i = 0
            while i < len(data.tecDiff) - windowSize + 1:           # repeat until window cannot slide anymore on the array
                windowVals = data.tecDiff[i : i + windowSize]       # access the valuses in current window position
                windowAverage = sum(windowVals)/windowSize          # average window values
                movingAverages.append(windowAverage)                # add average to the array of moving averages
                i += 1
            movingAverages.extend([data.tecDiff[-2], data.tecDiff[-1]]) # last two points cannot be calculated so pass through tecDiff
            data.movingAv = movingAverages                              # assign the array to the object
        else:
            data.movingAv = data.tecDiff                            # if there were not enough data points just pass through the tecDiff
    print("Moving Average's Calculated Successfully")
    return()

#####################################################################
########## Function to obtain diff between MA and tec Diff ##########
#####################################################################
def calculateMaTecDiffDiff(tecDataList):
    print("Calculating Delta between Moving Averages and TEC Diff...")
    # repeat for every TEC Diff measurement for entire day
    for data in tecDataList:
        arrayOne = np.array(data.tecDiff)               # array to be subtracted from is the tecDiff
        arrayTwo = np.array(data.movingAv)              # array being subtracted is the moving average
        deltaArray = np.subtract(arrayOne, arrayTwo)    # subtract arrays to find the difference
        delta = list(deltaArray)                        # convert back to list
        data.tdMaDiff = delta                           # assign to object
    print("Delta's Calculated Successfully")
    return()

#####################################################################
######### Function to display TEC diff to MA vs UTC time ############
#####################################################################
def displayDeltaVsUtc(tecDataList):
    # plot time vs TEC
    print("Plotting diff between Tec Diff and Moving Average vs Time...")
    for data in tecDataList:
        plt.plot(data.utcTime, data.tdMaDiff)                                                   # plot time vs TEC
        plt.ylabel("Diff between TEC Diff and Moving Average (TECU per Second")                 # label y axis
        plt.xlabel("UTC Time of Measurement")                                                   # label x axis
        plt.title(f"Tec Diff and Moving Average vs Time for LEO 1-6 PRN 1-32 on {data.utcTime[0].year}/{data.utcTime[0].month}/{data.utcTime[0].day}")  # title 
    plt.show()
    return()

#####################################################################
##### Function to display specific TEC diff to MA vs UTC time #######
#####################################################################
def displayDeltaVsUtcSpecific(tecDataList):
    print("Plotting specific diff between Tec Diff and Moving Average vs Time...")
    # plot time vs TEC for specific LEO and PRN ID
    print("Enter LEO ID to display: ")      # prompt user to enter LEO ID
    displayLeo = int(input())               # capture LEO ID
    print("Enter PRN ID to display: ")      # prompt user to enter PRN ID
    displayPrn = int(input())               # prompt user to enter PRN ID

    # search list and only plot if is specified LEO and PRN ID
    for data in tecDataList:
        if data.leo == displayLeo and data.prn == displayPrn:   # only LEO and PRN ID for given antenna to avoid double readings
            plt.plot(data.utcTime, data.tdMaDiff)               # plot time vs TEC

    plt.ylabel("Diff between TEC Diff and Moving Average (TECU per Second")                 # label y axis
    plt.xlabel("UTC Time of Measurement")                                                   # label x axis
    plt.title(f"Tec Diff and Moving Average vs Time for LEO {displayLeo} PRN {displayPrn} on {data.utcTime[0].year}/{data.utcTime[0].month}/{data.utcTime[0].day}")    # title 
    plt.show()
    return()

#####################################################################
########### Function to display TEC Delta on World Map ##############
#####################################################################
def displayTecDeltaWorldMap(tecDataList):
    print("Drawing World Map of TEC Delta...")
    map = Basemap()                                                                             # Using basemap as basis for world map
    map.drawcoastlines()                                                                        # Only add the costal lines to the map for visual refrence
    map.drawparallels(np.arange(-90,90,30),labels=[1,1,0,1], fontsize=8)                        # Add Longitude lines and degree labels
    map.drawmeridians(np.arange(-180,180,30),labels=[1,1,0,1], rotation=45, fontsize=8)         # Add latitude lines and degree labels

    # repeat for every TEC measurement for entire day
    for data in tecDataList:
        map.scatter(data.lon, data.lat, latlon=True, c=data.tdMaDiff, s=10, cmap='RdBu_r', alpha=0.2)       # Plot as a scatter where shade of red depends on TEC Diff value
    plt.colorbar(label='TECU per Second')                                                                   # Add coloutbar key for TECu Shades of red
    plt.clim(-5,5)                                                                                          # Key from 0 to 1000 (max TEC Diff measurement ~+-50)
    plt.xlabel('Longitude', labelpad=40, fontsize=8)                                                        # Add x axis label
    plt.ylabel('Latitude', labelpad=40, fontsize=8)                                                         # Add y axis label
    plt.title(f'COSMIC 2 TEC Delta plot on global map on {data.utcTime[0].year}/{data.utcTime[0].month}/{data.utcTime[0].day}', fontsize=8)  # Add title
    plt.show()
    return()

