# STEP 0: importing required packages
import polars as pl
import json
import os
import polars.selectors as cs

# STEP 1: Defining the path to the required csv file

# 1.1 json file containing skillcorner competition editions information 
ce_json_path = './skillcorner-competition-editions.json'
# 1.2  directory containing json files with skillcorner position data
json_PosDir_path = './skillcorner-20250214/'
# 1.3 

# STEP 2: Converting the competitions editions json to a usable DataFrame

# 2.1 Reading the competitions editions json
ce_df = pl.read_json(ce_json_path)

# 2.2 Unnesting the results column
ce_df = ce_df.select('results').explode('results').unnest('results')

# 2.2.1 Extracting name and id column in seperate DataFrame
ce_name_id = ce_df.select([pl.col('name'), pl.col('id'),])

# 2.2.2 Unnesting the competition column and storing it in a different DataFrame
ce_competition = ce_df.select('competition').unnest('competition')
# Renaming the DataFrame columns
ce_competition = ce_competition.rename({col: f"competition_{col}" for col in ce_competition.columns})

# 2.2.3 Unnesting the season column and storing it in a different DataFrame
ce_season = ce_df.select('season').unnest('season')
# Renaming the DataFrame columns
ce_season = ce_season.rename({col: f"season_{col}" for col in ce_season.columns})

# 2.2.4 Concattenating the seperate dataframes into a usable DataFrame 
# containing all competition edition information
ce = pl.concat([
    ce_name_id,
    ce_season,
    ce_competition
],
how = "horizontal",)

# STEP 3: Combining the json files with the position data into a usable dataframe
# Looping through the json files and concating them into one dataframe

json_list = [
    pl.read_json(os.path.join(json_PosDir_path, jsonf))
    for jsonf in os.listdir(json_PosDir_path)
]

json_df = pl.concat(json_list)

# STEP 4: Combining the 2 DataFrames (ce & json_df) to store all data together
# join function keeps the "left_on" column name
df = json_df.join(ce, 
                  left_on = "competition_edition_id",
                  right_on = "id"
)

