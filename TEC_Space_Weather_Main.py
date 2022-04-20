# include required files
import Import_Cosmic_Data as Data
import Display_Cosmic_Data as Display
import PreProcess_Cosmic_Data as PrePro
import Processed_Cosmic_Data as Pros
import urllib.request
import tarfile
import os

#####################################################################
####################### Main Program Script #########################
#####################################################################
print("Starting Program...")

#####################################################################
################### Download the COSMIC 2 Data ######################
#####################################################################
# Check if path is empty and Files need downloading:
path = '../FYP_Data'        # path of the directory 
dir = os.listdir(path)      # Getting the list of directories
  
# Checking if the list is empty or not and download any required files
if len(dir) < 366:
    print("Directory Empty - Files Need Downloading")
    print("Downloading the Data Files...")
    start = len(dir) + 32
    # Download whole of 2020 data files
    for day in range(start, 367, 1):
        # progress bar
        progress = ((day-32)/(367-32)) * 100
        print("Progress of Data Download: %.2f" %progress, "%",end='\r')

        url = f'https://data.cosmic.ucar.edu/gnss-ro/cosmic2/postProc/level1b/2020/{day:03d}/podTc2_postProc_2020_{day:03d}.tar.gz' # url to download with variable day
        downloaded_filename = f'../FYP_Data/podTc2_postProc_2020_{day:03d}.tar.gz'                                                  # name and location of downloaded file
        urllib.request.urlretrieve(url, downloaded_filename)                                                                        # curl to download the file

        # Extract the downloaded file
        fname = f'../FYP_Data/podTc2_postProc_2020_{day:03d}.tar.gz'        # name of the file to be extracted
        if fname.endswith("tar.gz"):                                        # so long as ends in correct format perform the extraction
            tar = tarfile.open(fname, "r:gz")                               # open the tar.gz file
            tar.extractall(f'../FYP_Data/podTc2_postProc_2020_{day:03d}')   # extract all to a new folder of same name
            tar.close()                                                     # close file
        os.remove(f'../FYP_Data/podTc2_postProc_2020_{day:03d}.tar.gz')     # delete non-extracted version of the file
    print("Progress of Data Download: 100% - Data Files Downloaded and Extracted!")
else:
    print("Directory Populated - No Files Need Downloading")                # if files exist in data folder then no need to download

#####################################################################
## Generate all CSV files containing Pixel Data for the year 2020 ###
#####################################################################
for day in range(32, 367, 1):
    # progress bar
    progress = ((day-32)/(367-32)) * 100
    print("Progress of CSV Export: %.2f" %progress, "%",end='\r')

    #####################################################################
    #################### Import the COSMIC 2 Data #######################
    #####################################################################
    # directory where data is held
    directoryPath = "C:\\Users\\crutt\\Documents\\University\\Final Year Project\\FYP_Data\\podTc2_postProc_2020_{day:03d}"   # Directory path containing Data

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

print("Progress of CSV Export: 100% - All CSV files with Pixel Data produced for 2020!")

## Display Proccessed TEC Delta on world map per hour
#Pros.displayProcessedTecDeltaWorldMapPerHr(processedTecDataList)

#####################################################################
################### Display Pre Processing Data #####################
#####################################################################

## Display Smooth and non-smooth vs Lat (smooth = 8 hour 30 for LEO 1 PRN 1, noisy = )
#PrePro.displayTecDiffVsLatSpecific(tecDataList)

## Display each measurement distances to validate geometry and intersect point seclection
#PrePro.displayIntersectDist(tecDataList)

## Display intersect sor specific satellites vs lat
#while(1):
#    PrePro.displayIntersectsVsLatSpecific(tecDataList)

## Display Delta at P2 on world map per hour
#PrePro.displayTecDeltaWorldMapAtP2PerHr(tecDataList)

## Display Intersect Lat vs Delta
#PrePro.displayIntersectsVsLat(tecDataList)

## Display Delta at P2 on world map
#PrePro.displayTecDeltaWorldMapAtP2(tecDataList)

## Display the Delta vs time
#PrePro.displayDeltaVsUtc(tecDataList)

## Display the Delta vs time specific
#PrePro.displayDeltaVsUtcSpecific(tecDataList)

## Display the Delta on world map
#PrePro.displayTecDeltaWorldMap(tecDataList)

#####################################################################
############# Display Raw Data Before Pre Processing ################
#####################################################################

## Display the TEC Diff vs elevation
#Display.displayTecDiffVsElevation(tecDataList)

## Display the TEC vs elevation
#Display.displayTecVsElevation(tecDataList)

## Display TEC Diff vs UTC time
#Display.displayTecDiffVsUtc(tecDataList)

## Display TEC Diff vs UTC time specific
#Display.displayTecDiffVsUtcSpecific(tecDataList)

## Display TEC Diff measurements on world map
#Display.displayTecDiffWorldMap(tecDataList)

## Display TEC measurements on world map
#Display.displayTecWorldMap(tecDataList)

## Display TEC vs UTC time
#Display.displayTecVsUtc(tecDataList)

## Display TEC vs UTC time for specific PRN and LEO ID
#Display.displayTecVsUtcSpecific(tecDataList)
