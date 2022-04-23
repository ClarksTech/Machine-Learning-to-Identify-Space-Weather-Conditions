# include required files
from cgi import test
import csv
import pandas as pd                             # pandas to recover pandas data frames from csv files
import numpy as np                              # numpy for data manipulation to ML  model
from pathlib import Path                        # to iterate over all files in folder
from sklearn.mixture import GaussianMixture     # GMM macine learning model

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
    return()