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
from sklearn.preprocessing import StandardScaler, normalize

#####################################################################
################# Import COSMIC 2 CSV file Data #####################
#####################################################################
def loadCSVData(directoryPath):
    print('Loading CSV File Data...')
    cosmic2CSVDataArray = []                        # list to store all ML data inputs
    paths = Path(directoryPath).glob('**/*.csv')    # Path for all .csv files

    # must load every CSV file
    for path in paths:
        df = pd.read_csv(path)                  # read the CSV file in as a pandas data frame
        numpydf = df.to_numpy()                 # convert data frame to numpy array
        csvData1D = numpydf.flatten(order='C')  # convert to 1D array for correct dimension to ML model input
        csvData1D = np.nan_to_num(csvData1D)    # convert nan to 0s to make valid for ML model
        cosmic2CSVDataArray.append(csvData1D)   # append numpy array to running list of ML input data

    print('All CSV Files Successfully Loaded - Data Ready For ML Model!')
    return(cosmic2CSVDataArray) # return list of all input arrays for ML model

#####################################################################
####################### Train GMM ML model ##########################
#####################################################################
def trainGMM(inputArrayAsList):
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