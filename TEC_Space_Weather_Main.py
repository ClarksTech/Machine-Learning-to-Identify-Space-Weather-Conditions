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

# Display TEC measurements on world map
Display.displayTecWorldMap(tecDataList)

# Display TEC vs UTC time
Display.displayTecVsUtc(tecDataList)

# Display TEC vs UTC time for specific PRN and LEO ID
Display.displayTecVsUtcSpecific(tecDataList)