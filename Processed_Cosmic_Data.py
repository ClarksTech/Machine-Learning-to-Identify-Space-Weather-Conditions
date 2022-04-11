# Import Libraries
import numpy as np

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
    return()