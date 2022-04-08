# include required libraries
import matplotlib.pyplot as plt             # for plotting delta
import numpy as np                          # for manipulating moving averages
from mpl_toolkits.basemap import Basemap    # Map for plotting global data
import pymap3d as pm                        # for LLA conversion

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
########## Function to obtain delta between MA and tec Diff #########
#####################################################################
def calculateDelta(tecDataList):
    print("Calculating Delta between Moving Averages and TEC Diff...")
    # repeat for every TEC Diff measurement for entire day
    for data in tecDataList:
        arrayOne = np.array(data.tecDiff)               # array to be subtracted from is the tecDiff
        arrayTwo = np.array(data.movingAv)              # array being subtracted is the moving average
        deltaArray = np.subtract(arrayOne, arrayTwo)    # subtract arrays to find the difference
        delta = list(deltaArray)                        # convert back to list
        data.delta = delta                              # assign to object
    print("Delta's Calculated Successfully")
    return()

#####################################################################
########### Function to obtain P1, P2, and TP coordinates ###########
#####################################################################
def calculateIntersects(tecDataList):
    print("Calculating P1, P2, and TP coordinates...")
    # repeat for every TEC Diff measurement for entire day
    for data in tecDataList:
        # Arrays to be returned to object
        xP1 = []
        yP1 = []
        zP1 = []
        xP2 = []
        yP2 = []
        zP2 = []
        xTp = []
        yTp = []
        zTp = []
        for i in range(len(data.xLeo)):
            # initialise the coordinates as single arrays for easy manipulation
            leoCoordinate = [data.xLeo[i], data.yLeo[i], data.zLeo[i]]
            gpsCoordinate = [data.xGps[i], data.yGps[i], data.zGps[i]]
            earthCoordinate = [0, 0, 0]

            # Generate required intermediate vectors and scalars
            leoGpsVector = [leoCoordinate[0]-gpsCoordinate[0], leoCoordinate[1]-gpsCoordinate[1], leoCoordinate[2]-gpsCoordinate[2]]            # ray direction vector
            leoGpsVectorNormalised = leoGpsVector/ np.sqrt(leoGpsVector[0]**2 + leoGpsVector[1]**2 + leoGpsVector[2]**2)                        # normalised ray vector                                                          # ray direction vector normalised
            gpsEarthVector = [earthCoordinate[0]-gpsCoordinate[0], earthCoordinate[1]-gpsCoordinate[1], earthCoordinate[2]-gpsCoordinate[2]]    # vector from GPS satellite to earth centre
            tca = np.dot(gpsEarthVector, leoGpsVectorNormalised)                        # tca is distance to TP point along ray path
            d = np.sqrt((np.dot(gpsEarthVector, gpsEarthVector) - np.dot(tca, tca)))    # d is distance from centre of earth to ray path (orthodonal)
            thc = np.sqrt(((6371000+350000)**2)-d**2)                                   # thc is distance between TP point and P1 along ray path
            t0 = tca - thc                                      # scalar on ray path for P1
            t1 = tca + thc                                      # scalar on ray path for P2

            # Generate final P1, P2, and Tp coordinated
            p1 = gpsCoordinate + t0*leoGpsVectorNormalised      # first intersect coordinates
            p2 = gpsCoordinate + t1*leoGpsVectorNormalised      # second intersect coordinates
            tp = gpsCoordinate + tca*leoGpsVectorNormalised     # TP point coordinates

            # append to arrays
            xP1.append(p1[0])
            yP1.append(p1[1])
            zP1.append(p1[2])
            xP2.append(p2[0])
            yP2.append(p2[1])
            zP2.append(p2[2])
            xTp.append(tp[0])
            yTp.append(tp[1])
            zTp.append(tp[2])
        
        # Store back in object
        data.xP1 = xP1
        data.yP1 = yP1
        data.zP1 = zP1
        data.xP2 = xP2
        data.yP2 = yP2
        data.zP2 = zP2
        data.xTp = xTp
        data.yTp = yTp
        data.zTp = zTp

    print("Coordinates's Calculated Successfully")
    return()

#####################################################################
########### Function to obtain P1, P2, and TP lat and lon ###########
#####################################################################
def calculateIntersecsLatLon(tecDataList):
    print("Calculating P1, P2, and TP Lat and Lon...")
    # repeat for every TEC Diff measurement for entire day
    for data in tecDataList:

        # setup as numpy arrays for single manipulations
        xP1 = np.array(data.xP1)
        yP1 = np.array(data.yP1)
        zP1 = np.array(data.zP1)
        xP2 = np.array(data.xP2)
        yP2 = np.array(data.yP2)
        zP2 = np.array(data.zP2)
        xTp = np.array(data.xTp)
        yTp = np.array(data.yTp)
        zTp = np.array(data.zTp)

        # convert to LLA
        latP1, lonP1, altP1 = pm.ecef2geodetic(xP1, yP1, zP1, ell=None, deg=True)
        # convert to LLA
        latP2, lonP2, altP2 = pm.ecef2geodetic(xP2, yP2, zP2, ell=None, deg=True)
        # convert to LLA
        latTp, lonTp, altTp = pm.ecef2geodetic(xTp, yTp, zTp, ell=None, deg=True)

        # store back in object
        data.latP1 = latP1
        data.lonP1 = lonP1
        data.latP2 = latP2
        data.lonP2 = lonP2
        data.latTp = latTp
        data.lonTp = lonTp

    print("Lat and Lons Calculated Successfully")
    return()

#####################################################################
############# Function to display lat vs P1, P2, and TP #############
#####################################################################
def displayIntersectsVsLat(tecDataList):
    print("Plotting intersects vs lat...")
    # Plot delta vs P1 lat
    for data in tecDataList:
        plt.plot(data.latP1, data.delta)                                                        # plot delta vs P1 Lat
        plt.ylabel("Delta between TEC Diff and Moving Average (TECU per Second)")               # label y axis
        plt.xlabel("lat")                                                                       # label x axis
        plt.title(f"Delta vs P1 Lat for LEO 1-6 PRN 1-32 on {data.utcTime[0].year}/{data.utcTime[0].month}/{data.utcTime[0].day}")  # title 
    plt.show()
        # Plot delta vs P2 lat
    for data in tecDataList:
        plt.plot(data.latP2, data.delta)                                                        # plot delta vs P2 Lat
        plt.ylabel("Delta between TEC Diff and Moving Average (TECU per Second)")               # label y axis
        plt.xlabel("lat")                                                                       # label x axis
        plt.title(f"Delta vs P2 Lat for LEO 1-6 PRN 1-32 on {data.utcTime[0].year}/{data.utcTime[0].month}/{data.utcTime[0].day}")  # title 
    plt.show()
        # Plot delta vs Tp lat
    for data in tecDataList:
        plt.plot(data.latTp, data.delta)                                                        # plot delta vs Tp Lat
        plt.ylabel("Delta between TEC Diff and Moving Average (TECU per Second)")               # label y axis
        plt.xlabel("lat")                                                                       # label x axis
        plt.title(f"Delta vs TP Lat for LEO 1-6 PRN 1-32 on {data.utcTime[0].year}/{data.utcTime[0].month}/{data.utcTime[0].day}")  # title 
    plt.show()
    return()

#####################################################################
#### Function to display lat vs P1, P2, and TP specific LEO PRN #####
#####################################################################
def displayIntersectsVsLatSpecific(tecDataList):
    print("Plotting intersects vs lat for specific links...")
    # Get specific LEO and PRN ID
    print("Enter LEO ID to display: ")      # prompt user to enter LEO ID
    displayLeo = int(input())               # capture LEO ID
    print("Enter PRN ID to display: ")      # prompt user to enter PRN ID
    displayPrn = int(input())               # prompt user to enter PRN ID
    # Plot delta vs P1 lat
    for data in tecDataList:
        if data.leo == displayLeo and data.prn == displayPrn:   # only LEO and PRN ID for given antenna to avoid double readings
            plt.plot(data.latP1, data.delta)                                                        # plot delta vs P1 Lat
            plt.ylabel("Delta between TEC Diff and Moving Average (TECU per Second)")               # label y axis
            plt.xlabel("lat")                                                                       # label x axis
            plt.title(f"Delta vs P1 Lat for LEO {displayLeo} PRN {displayPrn} on {data.utcTime[0].year}/{data.utcTime[0].month}/{data.utcTime[0].day}")  # title 
    plt.show()
        # Plot delta vs P2 lat
    for data in tecDataList:
        if data.leo == displayLeo and data.prn == displayPrn:   # only LEO and PRN ID for given antenna to avoid double readings
            plt.plot(data.latP2, data.delta)                                                        # plot delta vs P2 Lat
            plt.ylabel("Delta between TEC Diff and Moving Average (TECU per Second)")               # label y axis
            plt.xlabel("lat")                                                                       # label x axis
            plt.title(f"Delta vs P2 Lat for LEO {displayLeo} PRN {displayPrn} on {data.utcTime[0].year}/{data.utcTime[0].month}/{data.utcTime[0].day}")  # title 
    plt.show()
        # Plot delta vs Tp lat
    for data in tecDataList:
        if data.leo == displayLeo and data.prn == displayPrn:   # only LEO and PRN ID for given antenna to avoid double readings
            plt.plot(data.latTp, data.delta)                                                        # plot delta vs Tp Lat
            plt.ylabel("Delta between TEC Diff and Moving Average (TECU per Second)")               # label y axis
            plt.xlabel("lat")                                                                       # label x axis
            plt.title(f"Delta vs TP Lat for LEO {displayLeo} PRN {displayPrn} on {data.utcTime[0].year}/{data.utcTime[0].month}/{data.utcTime[0].day}")  # title 
    plt.show()
    return()

#####################################################################
## Function to display distance between intersect points P1, P2, TP #
#####################################################################
def displayIntersectDist(tecDataList):
    print("Plotting intersect distances for specific links...")
    # Get specific LEO and PRN ID
    print("Enter LEO ID to display: ")      # prompt user to enter LEO ID
    displayLeo = int(input())               # capture LEO ID
    print("Enter PRN ID to display: ")      # prompt user to enter PRN ID
    displayPrn = int(input())               # prompt user to enter PRN ID
    # Plot delta vs P1 lat
    for data in tecDataList:
        if data.leo == displayLeo and data.prn == displayPrn:   # only LEO and PRN ID
            for x in range(len(data.xLeo)):
                print("Press enter:")
                nan = input()
                leoP1Dist = np.sqrt((data.xLeo[x]-data.xGps[x])**2 + (data.yLeo[x]-data.yGps[x])**2 + (data.zLeo[x]-data.zGps[x])**2)
                print(f"Leo to P1: {leoP1Dist}")
                p1TpDist = np.sqrt((data.xP1[x]-data.xTp[x])**2 + (data.yP1[x]-data.yTp[x])**2 + (data.zP1[x]-data.zTp[x])**2)
                print(f"P1 to TP: {p1TpDist}")
                tpP2Dist = np.sqrt((data.xTp[x]-data.xP2[x])**2 + (data.yTp[x]-data.yP2[x])**2 + (data.zTp[x]-data.zP2[x])**2)
                print(f"Tp to P2: {tpP2Dist}")
                p1P2Dist = np.sqrt((data.xP1[x]-data.xP2[x])**2 + (data.yP1[x]-data.yP2[x])**2 + (data.zP1[x]-data.zP2[x])**2)
                print(F"P1 to P2: {p1P2Dist}")
                LeoP2Dist = np.sqrt((data.xLeo[x]-data.xP2[x])**2 + (data.yLeo[x]-data.yP2[x])**2 + (data.zLeo[x]-data.zP2[x])**2)
                print(f"Leo to P2: {LeoP2Dist}")
    return()

#####################################################################
############## Function to display Delta vs UTC time ################
#####################################################################
def displayDeltaVsUtc(tecDataList):
    # plot time vs TEC
    print("Plotting Delta vs Time...")
    for data in tecDataList:
        plt.plot(data.utcTime, data.delta)                                                      # plot time vs TEC
        plt.ylabel("Delta between TEC Diff and Moving Average (TECU per Second)")               # label y axis
        plt.xlabel("UTC Time of Measurement")                                                   # label x axis
        plt.title(f"Delta vs Time for LEO 1-6 PRN 1-32 on {data.utcTime[0].year}/{data.utcTime[0].month}/{data.utcTime[0].day}")  # title 
    plt.show()
    return()

#####################################################################
########## Function to display specific Delta vs UTC time ###########
#####################################################################
def displayDeltaVsUtcSpecific(tecDataList):
    print("Plotting specific Delta vs Time...")
    # plot time vs TEC for specific LEO and PRN ID
    print("Enter LEO ID to display: ")      # prompt user to enter LEO ID
    displayLeo = int(input())               # capture LEO ID
    print("Enter PRN ID to display: ")      # prompt user to enter PRN ID
    displayPrn = int(input())               # prompt user to enter PRN ID

    # search list and only plot if is specified LEO and PRN ID
    for data in tecDataList:
        if data.leo == displayLeo and data.prn == displayPrn:   # only LEO and PRN ID
            plt.plot(data.utcTime, data.delta)                  # plot time vs TEC

    plt.ylabel("Delta between TEC Diff and Moving Average (TECU per Second")    # label y axis
    plt.xlabel("UTC Time of Measurement")                                       # label x axis
    plt.title(f"Delta vs Time for LEO {displayLeo} PRN {displayPrn} on {data.utcTime[0].year}/{data.utcTime[0].month}/{data.utcTime[0].day}")    # title 
    plt.show()
    return()

#####################################################################
########### Function to display TEC Delta on World Map ##############
#####################################################################
def displayTecDeltaWorldMap(tecDataList):
    print("Drawing World Map of Delta...")
    map = Basemap()                                                                             # Using basemap as basis for world map
    map.drawcoastlines()                                                                        # Only add the costal lines to the map for visual refrence
    map.drawparallels(np.arange(-90,90,30),labels=[1,1,0,1], fontsize=8)                        # Add Longitude lines and degree labels
    map.drawmeridians(np.arange(-180,180,30),labels=[1,1,0,1], rotation=45, fontsize=8)         # Add latitude lines and degree labels

    # repeat for every TEC measurement for entire day
    for data in tecDataList:
        map.scatter(data.lon, data.lat, latlon=True, c=data.delta, s=10, cmap='RdBu_r', alpha=0.2)          # Plot as a scatter where shade of red depends on TEC Diff value
    plt.colorbar(label='TECU per Second')                                                                   # Add coloutbar key for TECu Shades of red
    plt.clim(-5,5)                                                                                          # Key from 0 to 1000 (max TEC Diff measurement ~+-50)
    plt.xlabel('Longitude', labelpad=40, fontsize=8)                                                        # Add x axis label
    plt.ylabel('Latitude', labelpad=40, fontsize=8)                                                         # Add y axis label
    plt.title(f'COSMIC 2 TEC Delta plot on global map on {data.utcTime[0].year}/{data.utcTime[0].month}/{data.utcTime[0].day}', fontsize=8)  # Add title
    plt.show()
    return()

#####################################################################
###### Function to display TEC Delta on World Map at P2 point #######
#####################################################################
def displayTecDeltaWorldMapAtP2(tecDataList):
    print("Drawing World Map of Delta at P2...")
    map = Basemap()                                                                             # Using basemap as basis for world map
    map.drawcoastlines()                                                                        # Only add the costal lines to the map for visual refrence
    map.drawparallels(np.arange(-90,90,30),labels=[1,1,0,1], fontsize=8)                        # Add Longitude lines and degree labels
    map.drawmeridians(np.arange(-180,180,30),labels=[1,1,0,1], rotation=45, fontsize=8)         # Add latitude lines and degree labels

    # repeat for every TEC measurement for entire day
    for data in tecDataList:
        map.scatter(data.lonP2, data.latP2, latlon=True, c=data.delta, s=10, cmap='RdBu_r', alpha=0.2)      # Plot as a scatter where shade of red depends on TEC Diff value
    plt.colorbar(label='TECU per Second')                                                                   # Add coloutbar key for TECu Shades of red
    plt.clim(-5,5)                                                                                          # Key from 0 to 1000 (max TEC Diff measurement ~+-50)
    plt.xlabel('Longitude', labelpad=40, fontsize=8)                                                        # Add x axis label
    plt.ylabel('Latitude', labelpad=40, fontsize=8)                                                         # Add y axis label
    plt.title(f'COSMIC 2 TEC Delta plot on global map at P2 point on {data.utcTime[0].year}/{data.utcTime[0].month}/{data.utcTime[0].day}', fontsize=8)  # Add title
    plt.show()
    return()

#####################################################################
## Function to display TEC Delta on World Map at P2 point Per Hour ##
#####################################################################
def displayTecDeltaWorldMapAtP2PerHr(tecDataList):
    for hour in range(0, 24):
        print(f"Drawing World Map of Delta at Hour {hour}...")
        map = Basemap()                                                                             # Using basemap as basis for world map
        map.drawcoastlines()                                                                        # Only add the costal lines to the map for visual refrence
        map.drawparallels(np.arange(-90,90,30),labels=[1,1,0,1], fontsize=8)                        # Add Longitude lines and degree labels
        map.drawmeridians(np.arange(-180,180,30),labels=[1,1,0,1], rotation=45, fontsize=8)         # Add latitude lines and degree labels

        # repeat for every TEC measurement for entire day
        for data in tecDataList:
            lonP2 = []
            latP2 = []
            delta = []
            for i in range(len(data.utcTime)):
                if data.utcTime[i].hour == hour:
                    lonP2.append(data.lonP2[i])
                    latP2.append(data.latP2[i])
                    delta.append(data.delta[i])
            map.scatter(lonP2, latP2, latlon=True, c=delta, s=10, cmap='RdBu_r', alpha=0.2)                # Plot as a scatter where shade of red depends on TEC Diff value
        plt.colorbar(label='TECU per Second')                                                                   # Add coloutbar key for TECu Shades of red
        plt.clim(-5,5)                                                                                          # Key from 0 to 1000 (max TEC Diff measurement ~+-50)
        plt.xlabel('Longitude', labelpad=40, fontsize=8)                                                        # Add x axis label
        plt.ylabel('Latitude', labelpad=40, fontsize=8)                                                         # Add y axis label
        plt.title(f'COSMIC 2 TEC Delta plot on global map at P2 point on {data.utcTime[0].year}/{data.utcTime[0].month}/{data.utcTime[0].day} Hour:{hour}', fontsize=8)  # Add title
        plt.show()
    return()

