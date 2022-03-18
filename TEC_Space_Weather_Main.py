# include required files
import Import_Cosmic_Data as Data
import Display_Cosmic_Data as Display


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

# debug large TEC variations in 1s
print("identifying large TEC DIFF...")
for data in tecDataList:
    for tDiff in data.tecDiff:
        if abs(tDiff) > 20:
            print("Large TEC diff of ", tDiff, " LEO ID: ", data.leo, " PRN ID: ", data.prn, " Time: ", data.utcTime)

while(1):
    # Display TEC vs UTC time for specific PRN and LEO ID
    Display.displayTecVsUtcSpecific(tecDataList)

# Display TEC Diff vs UTC time
Display.displayTecDiffVsUtc(tecDataList)

# Display TEC Diff measurements on world map
Display.displayTecDiffWorldMap(tecDataList)

# Display TEC measurements on world map
Display.displayTecWorldMap(tecDataList)

# Display TEC vs UTC time
Display.displayTecVsUtc(tecDataList)

# Display TEC vs UTC time for specific PRN and LEO ID
Display.displayTecVsUtcSpecific(tecDataList)

