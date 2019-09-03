# Isostatic-land-revealing-in-Finland

## Introduction
In this use case example we will calculate the yearly revealing of dry land due to isostacy in Finland. 


## Data

- [2m Elevation model][1] by National Land Survey of Finland. Data available in Taito.
- [10m Elevation model][2] by National Land Survey of Finland. Data available in Taito.
- TM35 map sheet division by the National Land Survey of Finland. Data available in Taito
- Sea areas of the [Topographic Database][3] by the National Land Survey of Finland. Data available in Taito
- Isostacy point data based on the NKG2016LU_lev landuplift data by the Nordic Geodetic Comission. Data available HERE

## Scripts used
- Resample_wanted_km10_to_2m_taito.py Searches the wanted 10m elevation models and resamples them to 2meter resolution.
- utm25_2m_masker_taito.py Masks the resampled 10m elevation models with the intersecting sea polygons. 
- dryland_calculator5_taito.py Calculates the revealed dry land between given years.
- result_gatherer.py Goes throught the result files and visualizes the results.


[1]:https://www.maanmittauslaitos.fi/en/maps-and-spatial-data/expert-users/product-descriptions/elevation-model-2-m
[2]:https://www.maanmittauslaitos.fi/en/maps-and-spatial-data/expert-users/product-descriptions/elevation-model-10-m
[3]:https://www.maanmittauslaitos.fi/en/maps-and-spatial-data/expert-users/product-descriptions/topographic-database
