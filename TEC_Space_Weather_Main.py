# include required files
import Import_Cosmic_Data as Data
import Display_Cosmic_Data as Display
import PreProcess_Cosmic_Data as PrePro

#####################################################################
####################### Main Program Script #########################
#####################################################################
print("Starting Program...")

# directory where data is held
directoryPath = "C:\\Users\\crutt\\Documents\\University\\Final Year Project\\FYP_Data\\podTc2_postProc_2020_032"   # Directory path containing Data

# Determine number of files to be imported
numberOfFiles = Data.getNumFiles(directoryPath)

# Import files to Class list for easy data access
tecDataList = Data.importDataToClassList(directoryPath, numberOfFiles)

## debug large TEC variations in 1s
#print("identifying large TEC DIFF...")
#for data in tecDataList:
#    for tDiff in data.tecDiff:
#        if abs(tDiff) > 20:
#            print("Large TEC diff of ", tDiff, " LEO ID: ", data.leo, " PRN ID: ", data.prn)

## Find out how many points populate a 30 deg by 30 deg square
#print("Calculating how many datapoints in 30 by 30 degree square...")
#count = 0
#for data in tecDataList:
#    for i in range(len(data.lat)):
#        if 0 <= data.lat[i] <= 15 and 0 <= data.lon[i] <= 15 :
#            count += 1
#print("Data Points in a 30 by 30 degree square = ", count)

# Generate moving averages test
PrePro.calculateMovingAverages(tecDataList)

# Generate difference between moving average and Tec Diff
PrePro.calculateMaTecDiffDiff(tecDataList)

# Display the Delta vs time
PrePro.displayDeltaVsUtc(tecDataList)

# Display the Delta vs time specific
PrePro.displayDeltaVsUtcSpecific(tecDataList)

# Display the Delta on world map
PrePro.displayTecDeltaWorldMap(tecDataList)

# Display the TEC Diff vs elevation
Display.displayTecDiffVsElevation(tecDataList)

# Display the TEC vs elevation
Display.displayTecVsElevation(tecDataList)

# Display TEC Diff vs UTC time
Display.displayTecDiffVsUtc(tecDataList)

# Display TEC Diff vs UTC time specific
Display.displayTecDiffVsUtcSpecific(tecDataList)

# Display TEC Diff measurements on world map
Display.displayTecDiffWorldMap(tecDataList)

# Display TEC measurements on world map
Display.displayTecWorldMap(tecDataList)

# Display TEC vs UTC time
Display.displayTecVsUtc(tecDataList)

# Display TEC vs UTC time for specific PRN and LEO ID
Display.displayTecVsUtcSpecific(tecDataList)

