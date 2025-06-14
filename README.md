# internship_club_brugge  
A summary of the notebooks created during the internships
The headers represent the folders containing all work per project
The bold subheaders represent specific notebooks 

## Inwerkdag
This directory contains data and notebooks of my first few days at the internship.
Where I focused on getting familiar with python

## Competition Comparison 
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
The aim of this directory was to process Secondspectrum optical tracking data from matches using various methods

**floodlight_functions.ipynb**  
Contains modified/optimized versions of the functions of the Python Floodlight module

**floodlight2parquet.ipynb**  
Extracts meeaningfull data from the Secondspectrum json files using Floodlight functions
- X-Y coordinates per frame dataframe
- Distance moved per frame dataframe
- Moving velocity per frame dataframe
- Using slight changes acceleration dataframe can also be determined
- Dataframes are written to seperate parquet files to avoid unescessary repetitio, of the heavy Floodlight functions

**NumberOfRuns.ipynb**  
Calculates the total distance ran above or between certain speed tresholds per player using the Floodlight distance and velocity dataframes

**velocity_distance.ipynb**  
Calculates the number of runs above or between certain speed tresholds per player using the Floodlight velocity dataframe

**ChangesOfDirection.ipynb**  
Calculates the number of direction changes per player
- Contains 3 different calculation methods
- Reilly, B., Morgan, O., Czanner, G., & Robinson, M. A. (2021). Automated Classification of Changes of Direction in Soccer Using Inertial Measurement Units. Sensors, 21(14), 4625. https://doi.org/10.3390/s21144625 
- Merks, B., Frencken, W., Otter, A. R., & Brink, M. (2021). Quantifying change of direction load using positional data from small-sided games in soccer. Science and Medicine in Football, 6. https://doi.org/10.1080/24733938.2021.1912382 
- Kai, T., Hirai, S., Anbe, Y., & Takai, Y. (2021). A new approach to quantify angles and time of changes-of-direction during soccer matches. PLoS One, 16(5), e0251292. https://doi.org/10.1371/journal.pone.0251292 

**ChangesOfDirection_PossessionStatus.ipynb**  
Calculates the number of direction changes per player both in and out ball possession
