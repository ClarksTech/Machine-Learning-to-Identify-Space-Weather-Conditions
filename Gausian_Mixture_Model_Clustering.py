# include required files
from cgi import test
import csv
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
            gmm = GaussianMixture(n_components=clusters). fit(cosmic2MlInputArrayPCA)                       # initialise the GMM model
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
def predictHourWithGMM(inputArrayAsList):
    print('Loading Data Into ML Model...')
    inputArray = np.array(inputArrayAsList)
    GMM = GaussianMixture(n_components=3, random_state=0).fit(inputArray)
    testPredict = inputArray[0].reshape(1, -1)
    print(GMM.predict_proba(testPredict))

    # Standardize data
    scaler = StandardScaler() 
    scaled_inputArray = scaler.fit_transform(inputArray) 
  
    # Normalizing the Data 
    normalized_inputArray = normalize(scaled_inputArray) 


    normalized_inputArray = pd.DataFrame(normalized_inputArray)
    pca = PCA(n_components=2)
    X_principal = pca.fit_transform(normalized_inputArray)

    # Determine amount of variance explained by components
    print("Total Variance Explained: ", np.sum(pca.explained_variance_ratio_))

    # Plot the explained variance
    plt.plot(pca.explained_variance_ratio_)
    plt.title('Variance Explained by Extracted Componenents')
    plt.ylabel('Variance')
    plt.xlabel('Principal Components')
    plt.show()


    X_principal = pd.DataFrame(X_principal)
    X_principal.columns = ['P1', 'P2']

    X_principal.head(2)
    print(X_principal)

    gmm = GaussianMixture(n_components=3)
    gmm.fit(X_principal)
    print(gmm.means_)

    plt.scatter(X_principal['P1'], X_principal['P2'], c = GaussianMixture(n_components=3).fit_predict(X_principal), cmap=plt.cm.winter, alpha=0.6)
    plt.show()

    n_clusters=np.arange(2, 8)
    sils=[]
    sils_err=[]
    iterations=20
    for n in n_clusters:
        tmp_sil=[]
        for _ in range(iterations):
            gmm=GaussianMixture(n, n_init=2).fit(X_principal) 
            labels=gmm.predict(X_principal)
            sil=metrics.silhouette_score(X_principal, labels, metric='euclidean')
            tmp_sil.append(sil)
        val=np.mean(SelBest(np.array(tmp_sil), int(iterations/5)))
        err=np.std(tmp_sil)
        sils.append(val)
        sils_err.append(err)

    plt.errorbar(n_clusters, sils, yerr=sils_err)
    plt.title("Silhouette Scores", fontsize=20)
    plt.xticks(n_clusters)
    plt.xlabel("N. of clusters")
    plt.ylabel("Score")
    plt.show()

    return()


def SelBest(arr:list, X:int)->list:
    '''
    returns the set of X configurations with shorter distance
    '''
    dx=np.argsort(arr)[:X]
    return arr[dx]
