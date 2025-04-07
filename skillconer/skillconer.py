
import polars as pl

df = pl.read_csv(
    "skillconer.csv", 
    has_header = True, 
    separator = ";", 
    quote_char = '"'
    )

#print(df.head(n=2))
#print(df.columns)
#rint(df.schema)

#team_ids = df['Team ID']
#print(team_ids.unique())
#print(unique_team_ids['Team_ID'])

#print(df['Competition'].unique())

print(df.describe())

print(df['Competition ID'].unique())