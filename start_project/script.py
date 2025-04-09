import polars as pl
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import json
from io import StringIO
import pygwalker as pyg
import os

pl.Config.set_max_threads(4)


json_dir_path = './skillcorner-20250214/'

json_list = os.listdir(json_dir_path)


#loop through the json files and concat them into one big df

# creating an empty data frame to concat the json dataframes to
corr_df = pl.DataFrame()

#initializing a counter for code testing 
counter = 0 
for jsonf in json_list:

    counter += 1
    #if counter > 1:
    #    break

    json_path = f"{json_dir_path}{jsonf}"
    #print(json_path)

    #creating df of the current json file 
    json_df = pl.read_json(json_path)
    #print(json_df.head())

    if counter == 1:
        corr_df = json_df
    else:
        corr_df = pl.concat([corr_df, json_df], how="align_full")


corr_df.shape
#corr_df.head(2)

output_path = "json_output.csv"
corr_df.write_csv(output_path)