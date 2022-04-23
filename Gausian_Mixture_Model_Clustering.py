# include required files
import pandas as pd
import numpy as np

#####################################################################
################# Import COSMIC 2 CSV file Data #####################
#####################################################################
df = pd.read_csv('../FYP_pixelArrayCSV/2020_2_1_0.csv')
numpydf = df.to_numpy()
print('')