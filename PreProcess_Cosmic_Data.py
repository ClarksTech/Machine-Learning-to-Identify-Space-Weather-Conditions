# include required libraries
import matplotlib.pyplot as plt             # 
import numpy as np                          # 

#####################################################################
########### Function to obtain moving average of TEC Diff ###########
#####################################################################
def calculateMovingAverages(tecDataList):
    windowSize = 5
    # repeat for every TEC Diff measurement for entire day
    for data in tecDataList:
        if len(data.tecDiff) >= windowSize:
            movingAverages = [data.tecDiff[0], data.tecDiff[1]]
            i = 0
            while i < len(data.tecDiff) - windowSize + 1:
                windowVals = data.tecDiff[i : i + windowSize]
                windowAverage = sum(windowVals)/windowSize
                movingAverages.append(windowAverage)
                i += 1
            movingAverages.extend([data.tecDiff[-2], data.tecDiff[-1]])
            data.movingAv = movingAverages
            print(movingAverages)
        else:
            data.movingAv = data.tecDiff
    return()

#####################################################################
########## Function to obtain diff between MA and tec Diff ##########
#####################################################################
def calculateMaTecDiffDiff(tecDataList):
    # repeat for every TEC Diff measurement for entire day
    for data in tecDataList:
        arrayOne = np.array(data.tecDiff)
        arrayTwo = np.array(data.movingAv)
        deltaArray = np.subtract(arrayOne, arrayTwo)
        delta = list(deltaArray)
        data.tdMaDiff = delta
        print(delta)
    return()

#####################################################################
######### Function to display TEC diff to MA vs UTC time ############
#####################################################################
def displayDeltaVsUtc(tecDataList):
    # plot time vs TEC
    print("Plotting diff between Tec Diff and Moving Average vs Time")
    for data in tecDataList:
        plt.plot(data.utcTime, data.tdMaDiff)                       # plot time vs TEC
        plt.ylabel("Diff between TEC Diff and Moving Average (TECU per Second")                 # label y axis
        plt.xlabel("UTC Time of Measurement")                       # label x axis
        plt.title(f"Tec Diff and Moving Average vs Time for LEO 1-6 PRN 1-32 on {data.utcTime[0].year}/{data.utcTime[0].month}/{data.utcTime[0].day}")  # title 
    plt.show()
    return()
