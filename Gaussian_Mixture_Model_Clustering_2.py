# include required files
import pandas as pd                             # pandas to recover pandas data frames from csv files
import numpy as np                              # numpy for data manipulation to ML  model
from pathlib import Path                        # to iterate over all files in folder
from sklearn.mixture import GaussianMixture     # GMM macine learning model
import matplotlib.pyplot as plt                 # for plotting 
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn import metrics
from sklearn.preprocessing import MinMaxScaler, StandardScaler, normalize
from sklearn.impute import SimpleImputer
from yellowbrick.cluster import SilhouetteVisualizer
from datetime import datetime, date
import os
import urllib.request                           # import library to web scrape the data download
import tarfile                                  # import library to unzip the data
import Import_Cosmic_Data as Data               # import the data script to get data
import PreProcess_Cosmic_Data as PrePro         # import the pre-processing script to process data
import Processed_Cosmic_Data as Pros            # import the processed data script to produce CSV files


#####################################################################
################# Import COSMIC 2 CSV file Data #####################
#####################################################################
def loadCSVData(directoryPath):
    print('Loading CSV File Data...')
    cosmic2CSVDataArray = []                        # list to store all ML data inputs
    paths = Path(directoryPath).glob('**/*.csv')    # Path for all .csv files

    # must load every CSV file
    for path in paths:
        df = pd.read_csv(path)  # read the CSV file in as a pandas data frame
        
        # replace any missing NaN values with a 0 as 0 is insignificant to the data
        imputer = SimpleImputer(strategy='constant')    # use constant replacement default 0
        imputer.fit(df)                                 # fit to the array 
        reconstructedDf = imputer.transform(df)         # replace with zeros, and store back in same variable
        csvData1D = reconstructedDf.flatten(order='C')  # convert to 1D array for correct dimension to ML model input
        for x in range(len(csvData1D)):
            cosmic2CSVDataArray.append(csvData1D[x])           # append numpy array to running list of ML input data

    print('All CSV Files Successfully Loaded - Data Ready For ML Model!')
    return(cosmic2CSVDataArray) # return list of all input arrays for ML model

#####################################################################
#################### Perform PCA on CSV Data ########################
#####################################################################
def dataPCA(cosmic2MlInputArrayList, numPCAComponents):
    # Convert to correct shape of input i.e. 2 dimensions
    cosmic2MlInputArray = np.array(cosmic2MlInputArrayList)

    # Normlise the input array so that PCA may be carried out in an unbiased way
    minMaxScaler = MinMaxScaler()
    cosmic2MlInputArrayNormalised = minMaxScaler.fit_transform(cosmic2MlInputArray) # Apply normalisation scaler

    # Perform PCA 
    pca = PCA(n_components=numPCAComponents)    # 72 dimentions to start with to see variance
    pca.fit(cosmic2MlInputArrayNormalised)      # fit to normalised array

    # Determine amount of variance explained by components
    print("Total Variance Explained: ", np.sum(pca.explained_variance_ratio_))

    # Plot the explained variance so educated decision may be made for number of components
    plt.plot(pca.explained_variance_ratio_)
    plt.title('Variance Explained by Extracted Componenents')
    plt.ylabel('Variance')
    plt.xlabel('Principal Components')
    plt.show()

    # Extract the principle components and return back in array
    cosmic2MlInputArrayPCA = pca.fit_transform(cosmic2MlInputArrayNormalised)

    return(cosmic2MlInputArrayPCA)  # Return the array in desired number of principle components

#####################################################################
############### Determine Best Number of Clusters ###################
#####################################################################
def dataOptimalClusterNumber(cosmic2MlInputArrayPCA):
    cosmic2MlInputArrayPCA = np.array(cosmic2MlInputArrayPCA).reshape(-1, 1)
    numberOfClusters = np.arange(2,8)
    # Empty lists to hold silhouette score and error bars
    silhouettes = []
    silhouetteErrors = []
    # repeat for 2 to 8 clusters
    for clusters in numberOfClusters:
        temporarySilhouetteHolder = []
        # repeat for 10 itterations of each cluster size given random initialisation
        for iteration in range(10):
            # create GMM instance for different number of clusters
            gmm = GaussianMixture(n_components=clusters).fit(cosmic2MlInputArrayPCA)                       # initialise the GMM model
            predictions = gmm.predict(cosmic2MlInputArrayPCA)                                               # predict for each value its cluster membership
            silhouette = metrics.silhouette_score(cosmic2MlInputArrayPCA, predictions, metric='euclidean')  # obtain silhouette score for the predictions
            temporarySilhouetteHolder.append(silhouette)                # store temporerily each itteration                                                 
        meanSilhouette = np.mean(np.array(temporarySilhouetteHolder))   # obtain the mean silhouette score from the 10 itterations as the result
        error = np.std(temporarySilhouetteHolder)                       # determin the error for each cluster size 
        silhouettes.append(meanSilhouette)          # append back to list
        silhouetteErrors.append(error)              # append back to list

    # Plot the silhouette score figure
    plt.errorbar(numberOfClusters, silhouettes, yerr=silhouetteErrors)  # Plot with error bars
    plt.title("Silhouette Scores", fontsize=20)                         # plot title
    plt.xticks(numberOfClusters)                                        # tick at each cluster point
    plt.xlabel("Number of clusters")                                    # x axis label
    plt.ylabel("Silhouette Score")                                      # y axis label
    plt.show()                                                          # show plot

    # plot visualisation of proposed clusters in 2 dimensions PC0 and PC1
    plt.scatter(cosmic2MlInputArrayPCA[:,0], cosmic2MlInputArrayPCA[:,1], c = GaussianMixture(n_components=2).fit_predict(cosmic2MlInputArrayPCA), cmap=plt.cm.winter, alpha=0.6)
    plt.title("Visualisation of two clusters in first two PCA dimensions", fontsize=20)
    plt.xlabel("PCA 0")
    plt.ylabel("PCA 1")
    plt.show()
        
    return()

#####################################################################
##################### Predict Specific Hour #########################
#####################################################################
def predictHourWithGMM(year, day, month, hour, cosmic2MlInputArrayPCA):
    print(f'Generating Predictions for year:{year}, month:{month}, day:{day}, hour:{hour}')
    
    # Get day of year for required Data download
    dayOfYear = date(year, month, day).timetuple().tm_yday

    # Check if years CSV files already exist
    if os.path.isfile(f'../FYP_pixelArrayCSV/{year}_{month}_{day}_{hour}.csv') == FALSE:
        print('CSV file for predicted day does not exist - needs generating...')

        # If CSV does not exist check if data from that day is already downloaded, if not - download
        if os.path.isfile(f'../FYP_Data/podTc2_postProc_{year}_{dayOfYear}') == False:
            print('Data for predicted day does not exist - needs downloading...')

            # Download the File
            url = f'https://data.cosmic.ucar.edu/gnss-ro/cosmic2/postProc/level1b/2020/{day:03d}/podTc2_postProc_2020_{day:03d}.tar.gz' # url to download with variable day
            downloaded_filename = f'../FYP_Data/podTc2_postProc_{year}_{day:03d}.tar.gz'                                                  # name and location of downloaded file
            urllib.request.urlretrieve(url, downloaded_filename)                                                                        # curl to download the file

            # Extract the downloaded file
            fname = f'../FYP_Data/podTc2_postProc_{year}_{day:03d}.tar.gz'        # name of the file to be extracted
            if fname.endswith("tar.gz"):                                        # so long as ends in correct format perform the extraction
                tar = tarfile.open(fname, "r:gz")                               # open the tar.gz file
                tar.extractall(f'../FYP_Data/podTc2_postProc_{year}_{day:03d}')   # extract all to a new folder of same name
                tar.close()                                                     # close file
            os.remove(f'../FYP_Data/podTc2_postProc_{year}_{day:03d}.tar.gz')     # delete non-extracted version of the file
        else:
            print('Data for predicted day does exist!')

        # Generate CSV file for day
        #####################################################################
        #################### Import the COSMIC 2 Data #######################
        #####################################################################
        # directory where data is held
        directoryPath = f'../FYP_Data/podTc2_postProc_{year}_{day:03d}'   # Directory path containing Data

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
    else:
        print('CSV file for predicted day does exist!')
    
    #####################################################################
    ################### Load in CSV for prediction ######################
    #####################################################################
    print('Loading CSV File for prediction...')
    # Load in all CSV data
    cosmic2MlInputArray = loadCSVData('../FYP_pixelArrayCSV')
    # append specific prediction
    df = pd.read_csv(f'../FYP_pixelArrayCSV/{year}_{month}_{day}_{hour}.csv')  # read the CSV file in as a pandas data frame
    # replace any missing NaN values with a 0 as 0 is insignificant to the data
    imputer = SimpleImputer(strategy='constant')    # use constant replacement default 0
    imputer.fit(df)                                 # fit to the array 
    reconstructedDf = imputer.transform(df)         # replace with zeros, and store back in same variable
    csvData1D = reconstructedDf.flatten(order='C')  # convert to 1D array for correct dimension to ML model input
    cosmic2MlInputArray.append(csvData1D)           # append numpy array to running list of ML input data

    # perform PCA on all CSV to obtain only 51 dimensions
    cosmic2MlInputArrayPCA = dataPCA(cosmic2MlInputArray, 51)

    # create GMM instance for prediction
    gmm = GaussianMixture(n_components=2).fit(cosmic2MlInputArrayPCA)
    testPredict = cosmic2MlInputArrayPCA[-1].reshape(1, -1)
    predictionProbs = gmm.predict_proba(testPredict)
    print(f'Prediction probability of belonging to each cluster: {predictionProbs}')
    
    return()


