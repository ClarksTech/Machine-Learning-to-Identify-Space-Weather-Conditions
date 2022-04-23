# include required files
import pandas as pd         # pandas to recover pandas data frames from csv files
import numpy as np          # numpy for data manipulation to ML  model
from pathlib import Path    # to iterate over all files in folder

#####################################################################
################# Import COSMIC 2 CSV file Data #####################
#####################################################################
def loadCSVData(directoryPath):
    cosmic2CSVDataArray = []                        # list to store all ML data inputs
    paths = Path(directoryPath).glob('**/*.csv')    # Path for all .csv files

    # must load every CSV file
    for path in paths:
        df = pd.read_csv(path)              # read the CSV file in as a pandas data frame
        numpydf = df.to_numpy()             # convert data frame to numpy array
        cosmic2CSVDataArray.append(numpydf) # append numpy array to running list of ML input data

    return(cosmic2CSVDataArray) # return list of all input arrays for ML model