# STEP 0: importing required packages
import polars as pl
import json
import os
import polars.selectors as cs
import xlsxwriter
import zipfile
import io

# STEP 1: Defining the path to the required files

# 1.1 json file containing skillcorner competition editions information
ce_json_path = "./data/skillcorner-competition-editions.json"
# 1.2 Directory containing json files with skillcorner position data
json_PosDir_path = "./data/skillcorner-20250214.zip"
# 1.3 csv containing statsbomb competition id and info (country & division)
sb_path = "./data/statsbomb-competition-levels.csv"
# 1.4 csv containing comparison of statsbomb and skillcorner id's / information
sb_sc_path = "./data/mapping-competition-seasons.csv"



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
#json_list = [
#    pl.read_json(os.path.join(json_PosDir_path, jsonf))
#    for jsonf in os.listdir(json_PosDir_path)
#]

json_list = []

with zipfile.ZipFile(json_PosDir_path, "r") as zip:
    for file_name in zip.namelist():
        if file_name.endswith(".json"):
            with zip.open(file_name) as f:
                json_bytes = f.read()
                json_buffer = io.BytesIO(json_bytes)
                df = pl.read_json(json_buffer)
                json_list.append(df)

json_df = pl.concat(json_list)

json_df = pl.concat(json_list)

# STEP 4: Combining the 2 DataFrames (ce & json_df) to store all data together
# join function keeps the "left_on" column name
df = json_df.join(ce, 
                  left_on = "competition_edition_id",
                  right_on = "id",
                  how = "left"
)

# STEP 5: 
# 5.1 Linking competition info (country & division) to skillcorner competition edition
sb = pl.read_csv(sb_path)
sb_sc = pl.read_csv(sb_sc_path)

sb_sc_joined = sb_sc.join(sb, 
        left_on="sb_competition_id",
        right_on="competition_id",
        how = "left"
        )

# 5.2 Extract columns containing skillcorner information
# competition country and national division information, sc_competition_id
# Concatenate region and division 
extracted_sb_sc = sb_sc_joined.select(
    ["sc_competition_season_id", 
     "competition_region_name",
     "competition_division_level"
    ]
).with_columns(
    pl.concat_str(
        [
            pl.col("competition_region_name"),
            pl.col("competition_division_level").cast(str),
        ],
        separator=" ",
    ).alias("competition_region_division")
).drop(
    ["competition_region_name", 
     "competition_division_level"
    ]
)

# STEP 6: Joining df with the extracted_sb_sc DataFrame into a datframe used
# for further processing
df = df.join(extracted_sb_sc,
             left_on="competition_edition_id",
             right_on="sc_competition_season_id",
             how = "left"
             )
# 6.1 Sorting DataFrame columns so related metrics are next to each other
df = df.select(sorted(df.columns))

# STEP 7: Performance metrics have to be normalized towards a 90 minute match
# based on the minutes played

# 7.1: Defining column names that do not have to be normalized
# Columns that do not contain numerical values can not be normalized
list2skip = df.select(~cs.numeric()).columns
# Hardcoding the numerical columns that do not have to be normalized
hardcoded = [
    'PSV-99',
    'competition_edition_id',
    'competition_id',
    'competition_id_right',
    'match_id',
    'player_id',
    'season_id_right',
    'season_id',
    'season_end_year',
    'season_start_year',
    'team_id'
]

for value in hardcoded: list2skip.append(value) 

# 7.2 hardcoding the time indicators
# Needed to correctly normalize each metric
time_indicators = {
    "OTIP 2": "Minutes OTIP 2",
    "OTIP 1": "Minutes OTIP 1",
    "TIP 2": "Minutes TIP 2",
    "TIP 1": "Minutes TIP 1",
    "OTIP": "Minutes OTIP",
    "TIP": "Minutes TIP",
    "2": "Minutes 2",
    "1": "Minutes 1"
}

# iterating over the columns to match them to the correct time / minute column
# normalizing the metrics for the time played
for coln in df.columns:
    if coln in list2skip:
        continue

    for pattern, indicator in time_indicators.items():
        if pattern in coln:
            divisor = indicator
            break
    else:
        divisor = "Minutes"

    df = df.with_columns(
        ((pl.col(coln) / pl.col(divisor))*90).alias(f"P90 {coln}")
    )

# sort the dataframe again 
df = df.select(sorted(df.columns))

# STEP 8: Creating Excell files showing benchmaarked data for the needed metrics

# 8.1 group the symmetrical positions by hardcoding
# symmetrical positions have to be shown in the same excell sheet 
mapping = {
    "RM": "RM|LM",
    "LM": "RM|LM",
    "RCB": "RCB|LCB",
    "LCB": "RCB|LCB",
    "RWB": "RWB|LWB",
    "LWB": "RWB|LWB",
    "RF": "RF|LF",
    "LF": "RF|LF",
    "RW": "RW|LW",
    "LW": "RW|LW",
    "DM": "DM",
    "AM": "AM",
    "CB": "CB",
    "CF": "CF"
}

df = df.with_columns(
    position_grouped = pl.col("position").replace_strict(mapping)
)

# 8.2 Hardcoding column names of the metrics wanted in the excells
# competition_region_division and position are fixed columns and should not be changed
df_subset = df.select([
    'competition_region_division', 
    'position_grouped',
    'P90 Distance',
    'P90 Running Distance',
    'P90 HSR Distance', 
    'P90 Sprinting Distance', 
    'PSV-99'
])
# The performance metrics are variable columns and can be modified
# depending on the wanted analysis
metrics = df_subset.drop([
    'competition_region_division', 
    'position_grouped'
]).columns

# 8.3 Hardcoding positions in the same order as the wanted excell sheet order
positions = ['CB', 'RCB|LCB', 'RWB|LWB', 'DM','RM|LM', 'AM', 'RW|LW', 'CF', 'RF|LF']

# 8.4 Create the 1st excell type
# store the statistical measures to loop through 
stats = {
    "Mean": pl.col(metrics).mean(),
    "Median": pl.col(metrics).median(),
    "Std": pl.col(metrics).std(),
    "Q25": pl.col(metrics).quantile(0.25),
    "Q75": pl.col(metrics).quantile(0.75),
}

with xlsxwriter.Workbook("match_benchmarks_stat_grouped.xlsx") as wb:

    #for position in tqdm(df_subset.select('position').unique('position').to_series().to_list()):
    for position in positions:
        result_list = []

        # determine the sample size per competition
        ss = (df_subset
            .filter(pl.col("position_grouped") == position)
            .group_by("competition_region_division")
            .agg([
                pl.col("competition_region_division").len().alias("Sample Size")])
        )

        # Filter for the specific position
        df_pos = df_subset.filter(pl.col("position_grouped") == position)

        for stat_name, stat_expr in stats.items():
            result = (
                df_pos
                .group_by("competition_region_division")
                .agg([stat_expr])
                .with_columns(pl.lit(stat_name).alias("Statistical Measure"))
            )
            result_list.append(result)

        # Combine all results in a dataframe to write to a position sheet of the excel
        df2write = pl.concat(result_list)
        #print(df2write)

        # put columns in the prefered order
        df2write = df2write.select([
            "competition_region_division",
            "Statistical Measure"]
            + metrics)

        df2write = ss.join(df2write, on="competition_region_division")

        df2write = df2write.rename({"competition_region_division":"Competition"})

        # write the dataframe to the excel
        df2write.write_excel(
            workbook=wb, 
            worksheet = position,
            autofit = True,
            float_precision = 1,
            freeze_panes = (1,0),
            header_format = {"bold": True}
        )
    
# 8.5 Create the 2nd excell type
with xlsxwriter.Workbook("match_benchmarks_stat_sep.xlsx") as wb:

    #for position in tqdm(df_subset.select('position').unique('position').to_series().to_list()):
    for position in positions:    
        result_list = []

        df_pos = df_subset.filter(pl.col("position_grouped") == position)
        df_pos = df_pos.filter(pl.col("competition_region_division").is_not_null())

        # determine the sample size per competition
        ss = (df_pos
            .filter(pl.col("position_grouped") == position)
            .group_by("competition_region_division")
            .agg([
                pl.col("competition_region_division").len().alias("Sample Size")])
        )
        result_list.append(ss)

        # Filter for this specific position
        for metric in metrics:
            result = (
                df_pos
                .filter(pl.col("position_grouped") == position)
                .group_by("competition_region_division")
                .agg(
                    [pl.col(metric).mean().alias(f"{metric} Mean")] +
                    [pl.col(metric).median().alias(f"{metric} Median")] + 
                    [pl.col(metric).std().alias(f"{metric}  Std")] + 
                    [pl.col(metric).quantile(0.25).alias(f"{metric} Q25")]+
                    [pl.col(metric).quantile(0.75).alias(f"{metric} Q75")]
                )
            )   

            result_list.append(result)

        # Combine all results in a dataframe to write to a position sheet of the excel
        df2write = pl.concat(result_list, how='align')

        df2write = df2write.rename({"competition_region_division":"Competition"})

        # write the dataframe to the excel
        df2write.write_excel(
            workbook=wb, 
            worksheet = position,
            autofit = True,
            float_precision = 1,
            freeze_panes = (1,0),
            header_format = {"bold": True}
        )
        
# STEP 9: Write the dataframe to a parquet file that will be used for visualisation
# entire dataframe written to the parquet file 
parquet4visual_path = "./data/parquet4visual.parquet"

df.write_parquet(parquet4visual_path)
