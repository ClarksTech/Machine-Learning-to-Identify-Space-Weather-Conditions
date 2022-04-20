# include required files
import Import_Cosmic_Data as Data
import Display_Cosmic_Data as Display
import PreProcess_Cosmic_Data as PrePro
import Processed_Cosmic_Data as Pros

#####################################################################
####################### Main Program Script #########################
#####################################################################
print("Starting Program...")

#####################################################################
#################### Import the COSMIC 2 Data #######################
#####################################################################
# directory where data is held
directoryPath = "C:\\Users\\crutt\\Documents\\University\\Final Year Project\\FYP_Data\\podTc2_postProc_2020_032"   # Directory path containing Data

# Determine number of files to be imported
numberOfFiles = Data.getNumFiles(directoryPath)

# Import files to Class list for easy data access
tecDataList = Data.importDataToClassList(directoryPath, numberOfFiles)

#####################################################################
################# Perform Pre Processing on Data ####################
#####################################################################

# Generate moving averages test
PrePro.calculateMovingAverages(tecDataList)

# Generate difference between moving average and Tec Diff
PrePro.calculateDelta(tecDataList)

# Generate Intersection coordinates
PrePro.calculateIntersects(tecDataList)

# Generate Intersection Lat and Lons
PrePro.calculateIntersecsLatLon(tecDataList)

#####################################################################
################### Store Final Processed Data ######################
#####################################################################

# Function to run lat lon algorithm and store final data values
processedTecDataList = Pros.importProcessedDataToClassList(tecDataList)

# Generate and Store Pixel Array as CSV for each hour of the day
Pros.saveProcessedTecDeltaPixelPerHr(processedTecDataList)

# Display Proccessed TEC Delta on world map per hour
Pros.displayProcessedTecDeltaWorldMapPerHr(processedTecDataList)

#####################################################################
################### Display Pre Processing Data #####################
#####################################################################

# Display Smooth and non-smooth vs Lat (smooth = 8 hour 30 for LEO 1 PRN 1, noisy = )
PrePro.displayTecDiffVsLatSpecific(tecDataList)

# Display each measurement distances to validate geometry and intersect point seclection
PrePro.displayIntersectDist(tecDataList)

# Display intersect sor specific satellites vs lat
while(1):
    PrePro.displayIntersectsVsLatSpecific(tecDataList)

# Display Delta at P2 on world map per hour
PrePro.displayTecDeltaWorldMapAtP2PerHr(tecDataList)

# Display Intersect Lat vs Delta
PrePro.displayIntersectsVsLat(tecDataList)

# Display Delta at P2 on world map
PrePro.displayTecDeltaWorldMapAtP2(tecDataList)

# Display the Delta vs time
PrePro.displayDeltaVsUtc(tecDataList)

# Display the Delta vs time specific
PrePro.displayDeltaVsUtcSpecific(tecDataList)

# Display the Delta on world map
PrePro.displayTecDeltaWorldMap(tecDataList)

#####################################################################
############# Display Raw Data Before Pre Processing ################
#####################################################################

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
