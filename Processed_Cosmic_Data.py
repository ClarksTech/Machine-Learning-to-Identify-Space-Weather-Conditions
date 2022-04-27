# Import Libraries
import numpy as np
from mpl_toolkits.basemap import Basemap    # Map for plotting global data
import matplotlib.pyplot as plt             # for plotting delta
import statistics as stat                   # for calculating standard deviation of pixels
import pandas as pd

#####################################################################
############ Class to Hold Processed TEC for each LEO ###############
#####################################################################
class processedTecData(object):
    def __init__(self, tec=None, tecDiff=None, tecDelta=None, lat=None, lon=None, utcTime=None):  # define class and parameters

        self.tec = tec                  # refrenced to self. for access to tec
        self.tecDiff = tecDiff          # refrenced to self. for access to tecDiff
        self.tecDelta = tecDelta        # refrenced to self. for access to tecDelta
        self.lat = lat                  # refrenced to self. for access to lat
        self.lon = lon                  # refrenced to self. for access to lon
        self.utcTime = utcTime          # refrenced to self. for access to utcTime

#####################################################################
###### Algorithm to determine the P1 or P2 occultation point ########
#####################################################################
def occultationPointAlgorithm(initialLinkP1, initialLinkP2, finalLinkP1, finalLinkP2):
    # 20 degrees decided as equatorial area 
    # Get absolutes
    initialLinkP1Lat = abs(initialLinkP1)
    initialLinkP2Lat = abs(initialLinkP2)
    finalLinkP1Lat = abs(finalLinkP1)
    finalLinkP2Lat = abs(finalLinkP2)

    # Only P1 in equatorial
    if initialLinkP1Lat <= 20 or finalLinkP1Lat <= 20:
        if initialLinkP2Lat > 20 and finalLinkP2Lat > 20:
            occultationPoint = 1

    # Only P2 in equatorial
    if initialLinkP2Lat <= 20 or finalLinkP2Lat <= 20:
        if initialLinkP1Lat > 20 and finalLinkP1Lat > 20:
            occultationPoint = 2

    # Both in equatorial use that with the furthest point closer to 0
    if (initialLinkP2Lat <= 20 or finalLinkP2Lat <= 20) and (initialLinkP1Lat <= 20 or finalLinkP1Lat <= 20):
        
        # find largest lat of P1 link
        if initialLinkP1Lat >= finalLinkP1Lat:
            largestP1Lat = initialLinkP1Lat
        else:
            largestP1Lat = finalLinkP1Lat

        # find smallest lat of P2 link
        if initialLinkP2Lat >= finalLinkP2Lat:
            largestP2Lat = initialLinkP2Lat
        else:
            largestP2Lat = finalLinkP2Lat

        # determine if smallest lat belongs to P1 or P2
        if largestP1Lat <= largestP2Lat:
            occultationPoint = 1
        else:
            occultationPoint = 2

    # None in Equatorial use P2 point as is cloeser to LEO satellite and inline with groud based
    if initialLinkP2Lat > 20 and finalLinkP2Lat > 20 and initialLinkP1Lat > 20 and finalLinkP1Lat > 20:
        occultationPoint = 2
    
    return(occultationPoint)

#####################################################################
############ Function to Populate processed TEC Class ###############
#####################################################################
def importProcessedDataToClassList(tecDataList):
    print("Loading Processed Data into Object...")

    # Empty list to store days worth of data
    processedTecDataList = []

    # Add to new object class completing algorithm to produce assigned lat and lon
    for x in range(len(tecDataList)):
        validFlag = 0
        tec = []
        tecDiff = []
        tecDelta = []
        lat = []
        lon = []
        utcTime = []
        latP1 = []
        lonP1 = []
        latP2 = []
        lonP2 = []
        # Check if every point is valid - only valid if P1 and P2 exist
        for i in range(len(tecDataList[x].xP1)):

            # is valid only if value of P1 is not NaN
            if np.isnan(tecDataList[x].xP1[i]) == False:

                # Append the valid datapoints to the temporary arrays
                tec.append(tecDataList[x].tec[i])
                tecDiff.append(tecDataList[x].tecDiff[i])
                tecDelta.append(tecDataList[x].delta[i])
                utcTime.append(tecDataList[x].utcTime[i])
                latP1.append(tecDataList[x].latP1[i])
                lonP1.append(tecDataList[x].lonP1[i])
                latP2.append(tecDataList[x].latP2[i])
                lonP2.append(tecDataList[x].lonP2[i])
                validFlag = 1   # set flag to indicate valid points found                   

        # perform operations on valid points only if flag set
        if validFlag == 1:
            # lat and lon algorithm to produce correct lat and lon
            occultationPoint = occultationPointAlgorithm(latP1[0], latP2[0], latP1[-1], latP2[-1])

            # Depending on algorithms returned occultation point populate lat and lon with P1 or P2 values
            if occultationPoint == 1:   # 1 returned for P1
                lat = latP1
                lon = lonP1
            if occultationPoint == 2:   # 2 returned for P2
                lat = latP2
                lon = lonP2
        
            processedTecDataList.append(processedTecData(tec=tec, tecDiff=tecDiff, tecDelta=tecDelta, lat=lat, lon=lon, utcTime=utcTime))   # Populate Object and add to array of objects
    print("Processed Data Loaded into Object Successfully!")
    return(processedTecDataList)

#####################################################################
### Function to display processed TEC Delta on World Map Per Hour ###
#####################################################################
def displayProcessedTecDeltaWorldMapPerHr(processedTecDataList):
    for hour in range(0, 24):
        print(f"Drawing World Map of Processed Delta at Hour {hour}...")
        map = Basemap()                                                                             # Using basemap as basis for world map
        map.drawcoastlines()                                                                        # Only add the costal lines to the map for visual refrence
        map.drawparallels(np.arange(-90,90,30),labels=[1,1,0,1], fontsize=8)                        # Add Longitude lines and degree labels
        map.drawmeridians(np.arange(-180,180,30),labels=[1,1,0,1], rotation=45, fontsize=8)         # Add latitude lines and degree labels

        # repeat for every TEC measurement for entire day
        for data in processedTecDataList:
            lon = []
            lat = []
            delta = []
            for i in range(len(data.utcTime)):
                if data.utcTime[i].hour == hour:
                    lon.append(data.lon[i])
                    lat.append(data.lat[i])
                    delta.append(data.tecDelta[i])
            map.scatter(lon, lat, latlon=True, c=delta, s=10, cmap='RdBu_r', alpha=0.2)                # Plot as a scatter where shade of red depends on TEC Diff value
        plt.colorbar(label='TECU per Second')                                                                   # Add coloutbar key for TECu Shades of red
        plt.clim(-5,5)                                                                                          # Key from 0 to 1000 (max TEC Diff measurement ~+-50)
        plt.xlabel('Longitude', labelpad=40, fontsize=8)                                                        # Add x axis label
        plt.ylabel('Latitude', labelpad=40, fontsize=8)                                                         # Add y axis label
        plt.title(f'Processed COSMIC 2 TEC Delta plot on global map on {data.utcTime[0].year}/{data.utcTime[0].month}/{data.utcTime[0].day} Hour:{hour}', fontsize=8)  # Add title
        plt.show()
    return()

#####################################################################
##### Function to populate processed TEC Delta pixels per hour ######
#####################################################################
def populateProcessedTecDeltaPixelPerHr(processedTecDataList, hour):
    # lists to store the specific hours data
    lon = []
    lat = []
    delta = []
    # repeat for every TEC measurement for entire day
    for data in processedTecDataList:
        for i in range(len(data.utcTime)):
            if data.utcTime[i].hour == hour:
                lon.append(data.lon[i])
                lat.append(data.lat[i])
                delta.append(data.tecDelta[i])
    # create empty 2D list of lists to store pixel standard deviation
    processedDataPixelArray = []
    for i in range(4):
        processedDataPixelArray.append([])
    y = 3
    # itterate through all pixels in lat and lon 20 degree steps
    for latStart in range(-40, 40, 20):
        for lonStart in range(-180, 180, 20):
            pixel = []  # empty list to store all values of delta TEC in the current pixel
            # Only add to current pixel list if the point satisfies the location conditions
            for i in range(len(delta)):
                if (lat[i] >= latStart) and (lat[i] < (latStart+20)) and (lon[i] >= lonStart) and (lon[i] < (lonStart+20)):
                    pixel.append(delta[i])
            # calculate standard deviation for entire pixel
            if not pixel:
                # empty list Standard Deviation set to None
                processedDataPixelArray[y].append(None)
            else:
                # not empty list calculate standard deviation and add to list of lists
                standarDeviationOfPixel = stat.pstdev(pixel)
                processedDataPixelArray[y].append(standarDeviationOfPixel)
        y -= 1  # decrement row counter

    return(processedDataPixelArray) # return populated list of lists for the hours standard deviation of delta TEC

#####################################################################
######### Function to save TEC delta Pixels per Hr as CSV ###########
#####################################################################
def saveProcessedTecDeltaPixelPerHr(processedTecDataList, savePath):
    # Generate and Store Pixel Array as CSV for each hour of the day
    for hour in range(0, 24, 1):
        progress = hour/23 * 100
        print("Progress of Conversion to Pixel CSV files: %.2f" %progress, "%",end='\r')
        processedDataPixelArray = populateProcessedTecDeltaPixelPerHr(processedTecDataList, hour)  # get list of lists with pixel array data
        pixelArray = np.array(processedDataPixelArray)                                                  # convert to numpy array for easier manipulation
        # store as CSV file so can be accessed by ML model easiy and generation only needed once
        pd.DataFrame(pixelArray).to_csv(f'{savePath}{processedTecDataList[0].utcTime[0].year}_{processedTecDataList[0].utcTime[0].month}_{processedTecDataList[0].utcTime[0].day}_{hour}.csv', index=False)
    print("Progress of Conversion to Pixel CSV files: 100 % - CSV Export Complete")
    return()