# internship_club_brugge  
A summary of the notebooks created during the internships
The headers represent the folders containing all work per project
The bold subheaders represent specific notebooks 

## Inwerkdag
This directory contains data and notebooks of my first few days at the internship.
Where I focused on getting familiar with python

## Start Project 
**exploratory_analysis.ipynb**  
Contianing code of the initial data exploration  
Investigates correlations between metrics

**benchmarking.ipynb**
- Combines Skillcorner match data with statsbomb competition information and in house quality scores
- Normalizes data to 90 minutes
- Calculates statistical metrics for for physical match data per competition and position
- Writes the statistical data to 2 seperate excel formats
- Stores processed data in a single parquet file

**position_benchmarking_script.py**  
Contains the same content as _ _benchmarking.ipynb_ _ but is a single script

**statistical_testing_competitions.ipynb**  
Identifying competitions that have similar demands
- Compares competitions based on a selected match metrics
- Attempts to find statistically significant differences using Tukey HSD post hoc analysis
- Results are written to 2 Excel files, one file compares the competitions on a general level, the second file compares the competitions per position.

**clustering_competitions.ipynb**  
Identifying competitions that have similar demands
- Clusters created based on 2 metrics using K-means from Scikit-Learn
- Optimal cluster number is detrmined using silhoutte score (limit set to 6)
- Results are written to an Excel file

**visualisation.ipynb**  
Notebook containing Dash app
- Compares competion and position demands
- Clusters competitions

## Positional data 