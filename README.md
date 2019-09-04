# Isostatic-land-revealing-in-Finland

## Introduction
In this use case example we will calculate the yearly revealing of dry land due to isostacy in Finland. 

## 
## Data

- [2m Elevation model][1] by National Land Survey of Finland. Data available in Taito.
- [10m Elevation model][2] by National Land Survey of Finland. Data available in Taito.
- TM35 map sheet division by the National Land Survey of Finland. Data available in Taito
- Sea areas of the [Topographic Database][3] by the National Land Survey of Finland. Data available in Taito
- Isostacy point data based on the NKG2016LU_lev landuplift data by the Nordic Geodetic Comission. Data available HERE

## Scripts used
- 10mDem_masker_resampler.py 10m dem data preparation.
- dryland_calculator5_taito.py Calculates the revealed dry land between given years.
- result_gatherer.py Goes throught the result files and visualizes the results.

## Workflow

### 1. Prepare the 10m elevation data

Because the 2m elevation model is not available everywhere in Finland, we need to use 10m elevation model at some areas. To make sure that we have the data when needed, we will prepare it in advance. 

Run the script 10mDem_masker_resampler.py. At the first phase the script will go through the directory of 10m dem files, mask the sea areas to value 0 with the intersecting sea area polygons. The masking to 0 is essentiall because the water areas of the laser scanning data include a lot of errors. Negative values are also converted to 0. The masked file is saved if it fills the following criteria:

- We are only intersted in dem files with minimum value less than 7.3. Higher demfiles would have no changes in them. The value is based   on the calculated maximum of land uplift in 700 years. 

  (700yr x 9,34mm) + ((1890yr-(2019yr-700yr)) x 1mm) = 7109mm 

  Where 9.34mm is the maximum value of yearly land uplif at the study area. Also the 1mm addition to land uplift values after year 1890   is taken into account (Ekman). Safety marginal of 0.2m was added to the result.

- We are also only interested in dem files that have dry land in them. This is why the max value of the file has to be over 0m. 


In the second phase the masked 10m dem files are resampled to 2m resolution. The 10m dem needs to be resampled to 2m resolution so we can make calculations between other layers. After resampling the files are renamed and saved as .tif files.   


### 2. Run the calculations

### 3. Gather the results at your local computer







[1]:https://www.maanmittauslaitos.fi/en/maps-and-spatial-data/expert-users/product-descriptions/elevation-model-2-m
[2]:https://www.maanmittauslaitos.fi/en/maps-and-spatial-data/expert-users/product-descriptions/elevation-model-10-m
[3]:https://www.maanmittauslaitos.fi/en/maps-and-spatial-data/expert-users/product-descriptions/topographic-database
