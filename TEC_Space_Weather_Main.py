# include required files
import Import_Cosmic_Data as Data               # import the data script to get data
import Display_Cosmic_Data as Display           # import the display script to allow display of results
import PreProcess_Cosmic_Data as PrePro         # import the pre-processing script to process data
import Processed_Cosmic_Data as Pros            # import the processed data script to produce CSV files
import Gaussian_Mixture_Model_Clustering as GMM  # import the machine learning script
import Gaussian_Mixture_Model_Clustering_2 as GMM2  # import the machine learning script
import urllib.request                           # import library to web scrape the data download
import tarfile                                  # import library to unzip the data
import os                                       # import library to allow deletion of files

#####################################################################
####################### Main Program Script #########################
#####################################################################
print("Starting Program...")
print("Warning - Requires 200GB Space available...")

#####################################################################
################### Download the COSMIC 2 Data ######################
#####################################################################

# Check if CSV folder is populated, if so no further action needed pre ML model
csvPath = '../FYP_pixelArrayCSV'    # directory Path
csvDir = os.listdir(csvPath)        # list of all directories in path (0 if is empty)

# check if CSV path is empty
if len(csvDir) == 0:
    # If is empty need to produce CSV files
    print('CSV files not found - Need Producing!')
    
    # Check if data path is empty and Files need downloading:
    dataPath = '../FYP_Data'        # path of the directory 
    dataDir = os.listdir(dataPath)      # Getting the list of directories

    # Checking if the data file list is empty or not and download any required files
    if len(dataDir) < (366 - 32):
        print("Data Directory Empty - Files Need Downloading")
        print("Downloading the Data Files...")
        start = len(dataDir) + 32
        # Download whole of 2020 data files
        for day in range(32, 367, 1):
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
        print("Data Directory Populated - No Files Need Downloading")                # if files exist in data folder then no need to download

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
        directoryPath = f'../FYP_Data/podTc2_postProc_2020_{day:03d}'   # Directory path containing Data

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
        Pros.saveProcessedTecDeltaPixelPerHr(processedTecDataList, '../FYP_pixelArrayCSV/')

    print("Progress of CSV Export: 100% - All CSV files with Pixel Data produced for 2020!")

else:
    print('CSV Files Exist - No Need To Produce')

#####################################################################
################# Load all CSV files for ML input ###################
#####################################################################

##################### BIAGIO VERSION TEST ###########################


cosmic2MlInputArray = GMM2.loadCSVData('../FYP_pixelArrayCSV')
GMM2.clusterInPixel(cosmic2MlInputArray)


cosmic2MlInputArrayPCA = GMM2.dataPCA(cosmic2MlInputArray, 72)
GMM2.dataOptimalClusterNumber(cosmic2MlInputArrayPCA)



cosmic2MlInputArray = GMM.loadCSVData('../FYP_pixelArrayCSV')

cosmic2MlInputArrayPCA = GMM.dataPCA(cosmic2MlInputArray, 72)

GMM.dataOptimalClusterNumber(cosmic2MlInputArrayPCA)

while(1):
    year = int(input("Enter Year: "))
    month = int(input("Enter Month: "))
    day = int(input("Enter Day: "))
    hour = int(input("Enter Hour: "))
    GMM.predictHourWithGMM(year, day, month, hour, cosmic2MlInputArrayPCA)







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
