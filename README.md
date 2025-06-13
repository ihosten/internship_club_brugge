# internship_club_brugge

## Inwerkdag
This directory contains data and notebooks of my first few days at the internship.
Where I focused on getting familiar with python

## Start Project 
**analysis.ipynb**    
**data_normalization.ipynb**  
**exploratory_analysis.ipynb**  
**benchmarking.ipynb**
- Combines Skillcorner match data with statsbomb competition information and in house quality scores
- Normalizes data to 90 minutes
- Calculates statistical metrics per competition and position
- Writes the statistical data to 2 seperate excel formats
- Stores processed data in a single parquet file

**position_benchmarking_script.py**  
Contains the same content as _ _benchmarking.ipynb_ _ but is a single script

**statistical_testing_competitions.ipynb**  
**clustering_competitions.ipynb**  
Extracts metrics from a parquet file and clusters similar competitions
- Clusters created based on 2 metrics using K-means from Scikit-Learn
- Optimal cluster number is detrmined using silhoutte score (limit set to 6)
- Results are written to an Excel file

**analysis.ipynb**  
**visualisation.ipynb**  

## Positional data 