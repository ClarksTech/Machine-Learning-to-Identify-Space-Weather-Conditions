# include required files
from pickle import FALSE
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
from mpl_toolkits.basemap import Basemap        # Map for plotting global data


#####################################################################
################# Import COSMIC 2 CSV file Data #####################
#####################################################################
def loadCSVData(directoryPath):
    print('Loading CSV File Data...')
    cosmic2CSVDataArray = []                        # list to store all ML data inputs
    paths = Path(directoryPath).glob('**/*.csv')    # Path for all .csv files
    
    # Determine number of files to be imported
    numPaths = Data.getNumFiles(directoryPath, '**/*.csv')

    progressCount = 0
    # must load every CSV file
    for path in paths:
        # Print Progress
        progress = progressCount/numPaths * 100
        print("Progress of CSV Data Import: %.2f" %progress, "%",end='\r')
        progressCount += 1

        df = pd.read_csv(path)  # read the CSV file in as a pandas data frame
        
        # replace any missing NaN values with a 0 as 0 is insignificant to the data
        imputer = SimpleImputer(strategy='constant')    # use constant replacement default 0
        imputer.fit(df)                                 # fit to the array 
        reconstructedDf = imputer.transform(df)         # replace with zeros, and store back in same variable
        csvData1D = reconstructedDf.flatten(order='C')  # convert to 1D array for correct dimension to ML model input

        # retain only highest 5 pixel values to prevent coverage pattern being most dominant feature
        nMax = 5
        index = np.argsort(csvData1D)[:-nMax]
        csvData1D[index] = 0

        cosmic2CSVDataArray.append(csvData1D)           # append numpy array to running list of ML input data

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
    print('Determining Optimal Cluster Number with Silhouette Score...')
    numberOfClusters = np.arange(2,8)
    # Empty lists to hold silhouette score and error bars
    silhouettes = []
    silhouetteErrors = []
    # repeat for 2 to 8 clusters
    progressCount = 0
    for clusters in numberOfClusters:
        temporarySilhouetteHolder = []
        # repeat for 10 itterations of each cluster size given random initialisation
        for iteration in range(20):
            # Print Progress
            progress = progressCount/140 * 100
            print("Progress of Silhouette Score: %.2f" %progress, "%",end='\r')
            progressCount += 1
            # create GMM instance for different number of clusters
            gmm = GaussianMixture(n_components=clusters).fit(cosmic2MlInputArrayPCA)                       # initialise the GMM model
            predictions = gmm.predict(cosmic2MlInputArrayPCA)                                               # predict for each value its cluster membership
            silhouette = metrics.silhouette_score(cosmic2MlInputArrayPCA, predictions, metric='euclidean')  # obtain silhouette score for the predictions
            temporarySilhouetteHolder.append(silhouette)                # store temporerily each itteration                                                 
        meanSilhouette = np.mean(np.array(temporarySilhouetteHolder))   # obtain the mean silhouette score from the 10 itterations as the result
        error = np.std(temporarySilhouetteHolder)                       # determin the error for each cluster size 
        silhouettes.append(meanSilhouette)          # append back to list
        silhouetteErrors.append(error)              # append back to list

    print('Silhouette Score Successfully Generated Plotting results and Optimal Cluster Visualisation!')

    # Plot the silhouette score figure
    plt.errorbar(numberOfClusters, silhouettes, yerr=silhouetteErrors)  # Plot with error bars
    plt.title("Silhouette Scores", fontsize=20)                         # plot title
    plt.xticks(numberOfClusters)                                        # tick at each cluster point
    plt.xlabel("Number of clusters")                                    # x axis label
    plt.ylabel("Silhouette Score")                                      # y axis label
    plt.show()                                                          # show plot

    # PCA for visualisation
    cosmic2MlInputArrayPCA = dataPCA(cosmic2MlInputArrayPCA, 2)

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
def predictHourWithGMM(year, day, month, hour):
    print(f'Generating Predictions for year:{year}, month:{month}, day:{day}, hour:{hour}...')
    
    # Get day of year for required Data download
    dayOfYear = date(year, month, day).timetuple().tm_yday

    # Check if years CSV files already exist
    if os.path.isfile(f'../FYP_pixelArrayCSV/{year}_{month}_{day}_{hour}.csv') == False:
        print('CSV file for predicted day does not exist - needs generating...')

        # If CSV does not exist check if data from that day is already downloaded, if not - download
        if os.path.isfile(f'../FYP_Data/podTc2_postProc_{year}_{dayOfYear:03d}') == False:
            print('Data for predicted day does not exist - needs downloading...')
            downloadFlag = 1

            # Download the File
            url = f'https://data.cosmic.ucar.edu/gnss-ro/cosmic2/nrt/level1b/{year}/{dayOfYear:03d}/podTc2_nrt_{year}_{dayOfYear:03d}.tar.gz'   # url to download with variable day
            downloaded_filename = f'../FYP_Data/podTc2_nrt_{year}_{dayOfYear:03d}.tar.gz'                                                       # name and location of downloaded file
            urllib.request.urlretrieve(url, downloaded_filename)                                                                                # curl to download the file

            # Extract the downloaded file
            fname = f'../FYP_Data/podTc2_nrt_{year}_{dayOfYear:03d}.tar.gz'             # name of the file to be extracted
            if fname.endswith("tar.gz"):                                                # so long as ends in correct format perform the extraction
                tar = tarfile.open(fname, "r:gz")                                       # open the tar.gz file
                tar.extractall(f'../FYP_Data/podTc2_postProc_{year}_{dayOfYear:03d}')   # extract all to a new folder of same name
                tar.close()                                                             # close file
            os.remove(f'../FYP_Data/podTc2_nrt_{year}_{dayOfYear:03d}.tar.gz')          # delete non-extracted version of the file
            print('Data Downloaded Succesfully!')
        else:
            print('Data for predicted day does exist!')
            downloadFlag = 0

        # Generate CSV file for day
        #####################################################################
        #################### Import the COSMIC 2 Data #######################
        #####################################################################
        # directory where data is held
        directoryPath = f'../FYP_Data/podTc2_postProc_{year}_{dayOfYear:03d}'   # Directory path containing Data

        # extension depends on year
        if year == 2020 and downloadFlag == 0:
            extension = '**/*.3430_nc'
        else:
            extension = '**/*.0001_nc'

        # Determine number of files to be imported
        numberOfFiles = Data.getNumFiles(directoryPath, extension)

        # Import files to Class list for easy data access
        tecDataList = Data.importDataToClassList(directoryPath, numberOfFiles, extension)

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

    # retain only highest 5 pixel values to prevent coverage pattern being most dominant feature
    nMax = 5
    index = np.argsort(csvData1D)[:-nMax]
    csvData1D[index] = 0
    cosmic2MlInputArray.append(csvData1D)           # append numpy array to running list of ML input data

    # create GMM instance for prediction
    gmm = GaussianMixture(n_components=2).fit(cosmic2MlInputArray)   # fit to the training Data
    testPredict = cosmic2MlInputArray[-1].reshape(1, -1)             # Reshape the prediction array to correct dimensions
    predictionProbs = gmm.predict_proba(testPredict)                 # Predict probability of membership to each cluster

    print(f'Prediction probability of belonging to each cluster: {predictionProbs}')

    # Display Heat Map with Cluster Prediction
    map = Basemap(llcrnrlon=-180,llcrnrlat=-40,urcrnrlon=180,urcrnrlat=40)                      # Using basemap as basis for world map
    map.drawcoastlines()                                                                        # Only add the costal lines to the map for visual refrence
    map.drawparallels(np.arange(-90,90,30),labels=[1,1,0,1], fontsize=8)                        # Add Longitude lines and degree labels
    map.drawmeridians(np.arange(-180,180,30),labels=[1,1,0,1], rotation=45, fontsize=8)         # Add latitude lines and degree labels
    map.imshow(reconstructedDf, cmap='hot', interpolation='nearest')                            # Plot the Heatmap                 
    plt.title("Heatmap of standard deviation distribution on world map", fontsize=20)           # plot title
    plt.show()
    
    return()

#####################################################################
############ Determine number of class in each pixel ################
#####################################################################
def clusterInPixel(cosmic2MlInputArray):
    print('Determining Coverage Pattern Globally of Each Cluster...')
    gmm = GaussianMixture(n_components=2).fit(cosmic2MlInputArray)  # initialise the GMM model
    predictions = gmm.predict(cosmic2MlInputArray)                  # predict for each standard deviation array its cluster membership

    # Zero Histograms to track which pixels belong to which cluster to validate meaningfullness of clusters
    cluster0 = [0]*72
    cluster1 = [0]*72

    # Increment Histograms
    for x in range(len(cosmic2MlInputArray)):
        for i in range(len(cosmic2MlInputArray[x])):
            if cosmic2MlInputArray[x][i] != 0:          # If the array value is non-zero i.e. if top 5 largest in array
                if predictions[x] == 0:                 # if predicted class 0 increment coresponding pixel in class 0 histogram
                    cluster0[i] +=1
                else:                                   # otherwise it belongs to class 1 so increment class 1 histogram bin
                    cluster1[i] +=1

    # convert histogram lists to numpy arrays so they may be easily manipulated
    cluster0 = np.array(cluster0)
    cluster1 = np.array(cluster1)

    # print the total number of values in each histogram to see cluster membership values
    print(f'Total number of datapoints in cluster 0: {np.sum(cluster0)}')
    print(f'Total number of datapoints in cluster 1: {np.sum(cluster1)}')

    # reshape to origional CSV pixel 2D shape
    cluster0 = np.reshape(cluster0, (4, 18))
    cluster1 = np.reshape(cluster1, (4, 18))

    # Display histogram pixel values on Global heat map to visualise cluster meaning
    map = Basemap(llcrnrlon=-180,llcrnrlat=-40,urcrnrlon=180,urcrnrlat=40)                      # Using basemap as basis for world map
    map.drawcoastlines()                                                                        # Only add the costal lines to the map for visual refrence
    map.drawparallels(np.arange(-90,90,30),labels=[1,1,0,1], fontsize=8)                        # Add Longitude lines and degree labels
    map.drawmeridians(np.arange(-180,180,30),labels=[1,1,0,1], rotation=45, fontsize=8)         # Add latitude lines and degree labels
    map.imshow(cluster0, cmap='hot', interpolation='nearest')                                   # Plot the Heatmap                 
    plt.title("Heatmap of Cluster 0 distribution on world map", fontsize=20)                    # plot title
    plt.show()

    map = Basemap(llcrnrlon=-180,llcrnrlat=-40,urcrnrlon=180,urcrnrlat=40)                      # Using basemap as basis for world map
    map.drawcoastlines()                                                                        # Only add the costal lines to the map for visual refrence
    map.drawparallels(np.arange(-90,90,30),labels=[1,1,0,1], fontsize=8)                        # Add Longitude lines and degree labels
    map.drawmeridians(np.arange(-180,180,30),labels=[1,1,0,1], rotation=45, fontsize=8)         # Add latitude lines and degree labels
    map.imshow(cluster1, cmap='hot', interpolation='nearest')                                   # Plot the Heatmap
    plt.title("Heatmap of Cluster 1 distribution on world map", fontsize=20)                    # plot title
    plt.show()
    
    return()

