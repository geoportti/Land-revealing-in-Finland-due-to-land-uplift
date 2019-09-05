<img src="https://github.com/geoportti/Logos/blob/master/geoportti_logo_300px.png">

# Isostatic-land-revealing-in-Finland

## Introduction
In this use case example we will calculate the yearly revealing of dry land due to isostasy in Finland. 
 
## Data

- [2m Elevation model][1] by National Land Survey of Finland. Data available in Taito.
- [10m Elevation model][2] by National Land Survey of Finland. Data available in Taito.
- [UTM map sheet division][9] by the National Land Survey of Finland. Data available in the [File service of open data][10]. The needed   UTM_10 grid is stored for you in [data][11] folder. 
- Sea areas of the [Topographic Database][3] by the National Land Survey of Finland. Data available in Taito
- [Isostasy point data][11] based on the NKG2016LU_lev land uplift data by the Nordic Geodetic Comission. The point data available in     data folder is allready cropped to cover only the coastal areas of Finland. Read more about the data [here][8].

## Workflow

### 1. Prepare the 10m elevation data

Script used :  [10mDem_masker_resampler.py][7]

Because the 2m elevation model is not available everywhere in Finland, we need to use 10m elevation model at some areas. To make sure that we have the data when needed, we will prepare it in advance. 

Run the script 10mDem_masker_resampler.py. At the first phase the script will go through the directory of 10m dem files, mask the sea areas to value 0 with the intersecting sea area polygons. The masking to 0 is essential because the water areas of the laser scanning data include a lot of errors. Negative values are also converted to 0. The masked file is saved if it fills the following criteria:

- We are only interested in dem files with minimum value less than 7.3. Higher dem files would have no changes in them. The value is based   on the calculated maximum of land uplift in 700 years. 
```pythonscript
  (700yr x 9,34mm) + ((1890yr-(2019yr-700yr)) x 1mm) = 7109mm* 
```
  Where 9.34mm is the maximum value of yearly land uplift at the study area. Also the 1mm addition to land uplift values after year 1890   is taken into account (Ekman). Safety marginal of 0.2m was added to the result.

- We are also only interested in dem files that have dry land in them. This is why the max value of the file has to be over 0m. 

In the second phase the masked 10m dem files are resampled to 2m resolution. The 10m dem needs to be resampled to 2m resolution so we can make calculations between other layers. After resampling the files are renamed and saved as .tif files.   


### 2. Run the calculator

Script used: [dryland_calculator.py][5] , [calculator_batch][6]

#### Principals

You can run the dryland_calculator using the calculator_batch file in Taito. The script is designed so that it runs in 14 parallel jobs. The jobs are separated with the first stage of UTM map sheet division. This way we will also limit the search to the coastal areas of Finland. The used map sheets are: S4, R4, Q3, Q4, P3, N3, M3, L2, L3, L4, L5, K2, K3, K4.

The actual calculation of the land revealing is done in the UTM10 map division level, which means 6km x 6km grid squares that are named for example ”L5124E”. This is because the 2m dem is stored in files named and defined after this level of division. 

The calculator goes through a file containing the ID ("LEHTITUNNU") and the geometry of UTM10 grid cells. Whenever a corresponding 2m dem file is found, it is masked and filtered just like 10m dem files previously. If a corresponding 2m dem file cannot be found, the calculator opens the already resampled and masked 10m dem file and uses that in the calculations instead of the 2m dem.

Before we can begin the calculations we also need a 2m resolution raster layer of the isostasy data. The isostasy raster is created on the fly with each iteration only to the area corresponding the dem file by using linear interpolation. 

#### Calculations

##### Paleotopography of different time periods

The first phase of the calculations between the dem layer and the isostasy layer is to define the paleotopography for every time period. 
In this example we use 10 time periods between every 50 years from 200bp. to 700bp. The paleotopography can be calculated by multiplying the isostasy layer with the number of years and then extracting the isostasy layer form the present day dem file. Before extraction the isostasy values were converted to meters. The change in the speed of isostasy after 1890 was also taken into account. The ten paleotopography layers for each grid ID were calculated as following:
```pythonscript
 dem_year = dem - ((isostasylayer*year)+(year-(year-(2019-1890)))/1000)
 ```
 ##### Sea level differences between consecutive paleotopographies
 
 In the next phase we want to calculate the difference in pixels that have values greater than 0 between consecutive paleotopographies. This way we can establish how many pixels were revealed during the 50 year time interval. When we multiply the difference with 4 and divide the result with 1000000, we will get the amount of revealed land in square kilometers. The calculations were done for all the 10 time intervals as following:
 ```pythonscript
 change = (4*((0 < dem_year1).sum()-(0 < dem_year2).sum()))/1000000
 ```
The 10 resulting values are saved in text file with the grid cell id. 

### 3. Gather the results at your local computer

Script used: [result_gatherer.py][4]

Because all the results are stored in separate text files, we need to gather them together. Result gatherer will go through all the text files in the directory and gather the data into one table.

After the results are gathered it is relatively easy to plot the results for example as bar plots:

<img src="https://github.com/geoportti/Isostatic-land-revealing-in-Finland/blob/master/Images/Yearly_revealing.png">


You can also export an shapefile merging the utm10 grid with the data you just created. This way you can visualize maps for example in QGIS or ArcMap:

<img src="https://github.com/geoportti/Isostatic-land-revealing-in-Finland/blob/master/Images/reveal_sum_small2.png">



When using the scripts or CSC.s computation services, please cite the oGIIR project: "We made use of geospatial data/instructions/computing resources provided by the Open Geospatial Information Infrastructure for Research (oGIIR, urn:nbn:fi:research-infras-2016072513) funded by the Academy of Finland."

Authored by Akseli Toikka and the Department of Geoinformatics and Cartography at FGI

#todo
- kirjoita intro
- testaa resampler batch

[1]:https://www.maanmittauslaitos.fi/en/maps-and-spatial-data/expert-users/product-descriptions/elevation-model-2-m
[2]:https://www.maanmittauslaitos.fi/en/maps-and-spatial-data/expert-users/product-descriptions/elevation-model-10-m
[3]:https://www.maanmittauslaitos.fi/en/maps-and-spatial-data/expert-users/product-descriptions/topographic-database
[4]:https://github.com/geoportti/Isostatic-land-revealing-in-Finland/blob/master/result_gatherer.py
[5]:https://github.com/geoportti/Isostatic-land-revealing-in-Finland/blob/master/dryland_calculator.py
[6]:https://github.com/geoportti/Isostatic-land-revealing-in-Finland/blob/master/calculator_batch
[7]:https://github.com/geoportti/Isostatic-land-revealing-in-Finland/blob/master/10mDem_masker_resampler.py
[8]:https://link.springer.com/article/10.1007/s00190-019-01280-8
[9]:https://www.maanmittauslaitos.fi/sites/maanmittauslaitos.fi/files/old/UTM_lehtijakopdf.pdf
[10]:https://tiedostopalvelu.maanmittauslaitos.fi/tp/kartta
[11]:https://github.com/geoportti/Isostatic-land-revealing-in-Finland/tree/master/data
