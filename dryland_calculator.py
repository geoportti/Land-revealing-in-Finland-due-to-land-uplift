# -*- coding: utf-8 -*-
"""
Created on Mon Jul  8 14:14:46 2019

@author: Administrator


This script calculates the amount of revealed land in a utm10 map grid cells (6km x 6km)
of Finnish coastall areas during ten 50 year intervals between 200 and 700 pb.

Copyright. Akseli Toikka and Ville Mäkinen, Finnish Geospatial Research Institute
           Department of Geoinformatics and Cartography.

"""
import pandas as pd
import geopandas as gpd
import os
import rasterio
from rasterio.mask import mask
from rasterio.windows import from_bounds
import fiona
from scipy import interpolate
import numpy as np
import sys

####### filepaths ########

#directory of the dem files
rootdir =r'/wrk/project_ogiir-csc/mml/dem2m/2008_latest'
rootdir2 =r'directory of the resampled 10m dem files'

#filepath of the sea areas
seafp = r'/wrk/project_ogiir-csc/mml/maastotietokanta/2019/gpkg/MTK-vakavesi_19-01-23.gpkg'

#isostacy points filepath
pointsfp = r'filepath of the isostacy point data'

#UTM_10 grid fp
gridfp = r'filepath of the utm 10 grid file'

#result filepath
resultpath = r'filepath of your result folder'


###### function for isostacy layer interpolation #######
points = gpd.read_file(pointsfp)

#pisteiden x ja y koordinaatit
points['x'] = points['geometry'].x
points['y'] = points['geometry'].y

x = points['x'].values
y = points['y'].values
z = points['movement'].values

coords = np.empty((len(x),2))
coords[:,0] = x
coords[:,1] = y

####### calculations #######

#read in the utm10 grid
utm= gpd.read_file(gridfp) 

#create a list of the coastline map sheet names
maplist = ['S4','R4','Q3','Q4','P3','N3','M3','L2','L3','L4','L5','K2','K3','K4']

#pick one item in the maplist at the time
myMap = maplist[int(sys.argv[1])]


#loop through the utm10 polygons
for index, row in utm.iterrows():
    #is the polygon on the coastline?
    if row['LEHTITUNNU'][0:2] == myMap:
        # construct filepath of the dem file 
        filepath = os.path.join(rootdir + '/{}/{}/{}.tif'.format(row.LEHTITUNNU[0:2],row.LEHTITUNNU[0:3],row.LEHTITUNNU)) 
        # can the filepath be found in the demfile km2 demfile location.
        if os.path.isfile(filepath):
            # open the demfile and mask it with the intersecting sea polygons
            with rasterio.open(filepath) as demdata:
                bounds = demdata.bounds
                with fiona.open(seafp, layer='meri') as sea:
                    hits = sea.items(bbox=(bounds[0],bounds[1],bounds[2],bounds[3]))
                    items = [i for i in hits]
                if len(items) > 0:
                    geoms = [item[1]['geometry'] for item in items]
                    demarr, out_transform = mask(demdata,geoms, invert=True)
                else:
                    demarr = demdata.read()
                demarr[demarr < 0] = 0
                # If after masking the min value of the km2 file is below 7.3m and the max calue above 0 continue
                if demarr.min() <= 7.3 and demarr.max() > 0:
                    # use the bounds of the DEM file to create a grid and interpolate the isostacy data to it
                    print(row.LEHTITUNNU, 'in km2')
                    xnew = np.arange(bounds[0], bounds[2], 2)
                    ynew = np.arange(bounds[1], bounds[3], 2)    
                    #use linear interpolation to create the isostacy raster layer
                    grid_x, grid_y = np.mgrid[xnew[0]:xnew[-1]:3000j,ynew[0]:ynew[-1]:3000j]
                    isoarr = interpolate.griddata(coords,z,(grid_x, grid_y),method='linear')
                    
                    #dictionary to save the arrays of different years
                    yeararrays =dict()
                    #list of years (200 = 200 years before present)
                    yearlist = [200,250,300,350,400,450,500,550,600,650,700]
                    
                    #loop through the list and calculate the paleotopography for each year by subtracting the amount of isostacy from the dem.
                    for year in yearlist:
                        yeararrays[year] = demarr-(((isoarr*year)+(year-(2019-1890)))/1000)
                        
                    # call the results from the dictionary
                    dem200 =yeararrays.get(200)
                    dem250=yeararrays.get(250)
                    dem300=yeararrays.get(300)
                    dem350=yeararrays.get(350)
                    dem400=yeararrays.get(400)
                    dem450=yeararrays.get(450)
                    dem500=yeararrays.get(500)
                    dem550=yeararrays.get(550)
                    dem600=yeararrays.get(600)
                    dem650=yeararrays.get(650)
                    dem700=yeararrays.get(700)
                    
                    #calculate the change in pixels above the sealevel in 50 year intervals. Multiply the pixels with their m2 size and divide with 1000000 to get the km2 change in 50 years
                    change200_250 = (4*((0 < dem200).sum()-(0 < dem250).sum()))/1000000
                    change250_300 = (4*((0 < dem250).sum()-(0 < dem300).sum()))/1000000
                    change300_350 = (4*((0 < dem300).sum()-(0 < dem350).sum()))/1000000
                    change350_400 = (4*((0 < dem350).sum()-(0 < dem400).sum()))/1000000
                    change400_450 = (4*((0 < dem400).sum()-(0 < dem450).sum()))/1000000
                    change450_500 = (4*((0 < dem450).sum()-(0 < dem500).sum()))/1000000
                    change500_550 = (4*((0 < dem500).sum()-(0 < dem550).sum()))/1000000
                    change550_600 = (4*((0 < dem550).sum()-(0 < dem600).sum()))/1000000
                    change600_650 = (4*((0 < dem600).sum()-(0 < dem650).sum()))/1000000
                    change650_700 = (4*((0 < dem650).sum()-(0 < dem700).sum()))/1000000
                    
                    #resultname from the row ID
                    resultname = row.LEHTITUNNU
                    
                    #save the changes in a list
                    changelist = [[change200_250,change250_300,change300_350,change350_400,change400_450,change450_500,change500_550,change550_600,change600_650,change650_700,resultname]]
                  
                    #create seperate df of the list
                    list_df = pd.DataFrame(changelist)
                    
                    #save the resulting dataframes in the results folder and create a folderstructure for storing the result .txt files
                    level1 = os.path.join(resultpath,resultname[0:2])
                    level2 = os.path.join(level1,resultname[0:3])
                        
                    #Create directions if they dont exist
                    if not os.path.exists(level1):
                        os.mkdir(level1)
                    if not os.path.exists(level2):
                        os.mkdir(level2)
                    # name the resulting file after the row ID 
                    name = os.path.join(level2,'{}.txt'.format(resultname))
                    if not os.path.exists(name):
                        list_df.to_csv(name, index=False, header=False)
                    
                    print('result saved')
                    
                else:
                    continue
        # if the filepath cannot be found in the km2 filelocation        
        else:
            # loop through the folder of allready resampled and masked km10 files
            for filename in os.listdir(rootdir2):
                # check to open the right km10 file
                if filename.endswith(".tif") and filename[0:5] == row.LEHTITUNNU[0:5]:
                    #construct filepath
                    filepath = os.path.join(rootdir2,filename)
                    #read the bounds of the grid polygon
                    bounds = row.geometry.bounds
                    west = round(bounds[0])
                    south = round(bounds[1])
                    east = round(bounds[2])
                    north = round(bounds[3])
                    #open the folder connection
                    with rasterio.open(filepath) as demdata:
                        #use the transform of the orginal demfile
                        transform = demdata.transform
                        #construct a window bounding box from the bounds
                        window = from_bounds(west,south,east,north,transform,width = 3000,height = 3000)
                        #read the dem data using the window 
                        demarr = demdata.read(1,window=window)
                        #negative values to 0.(areas outside Finland borders are negative)
                        demarr[demarr < 0] = 0
                        # If after masking the min value of the DEM file is below 7.3m continue
                        if demarr.min() <= 7.3 and demarr.max() > 0:
                            # use the bounds of the DEM file to create a grid and interpolate the isostacy data to it
                            print(row.LEHTITUNNU, 'in km10', window)
                            xnew = np.arange(west, east, 2)
                            ynew = np.arange(south, north, 2)     
                            # use linear interpolation to create a isostacy raster
                            grid_x, grid_y = np.mgrid[xnew[0]:xnew[-1]:3000j,ynew[0]:ynew[-1]:3000j]
                            isoarr = interpolate.griddata(coords,z,(grid_x, grid_y),method='linear')
                            
                            #dictionary to save the arrays of different years
                            yeararrays =dict()
                            #list of years (200 = 200 years before present)
                            yearlist = [200,250,300,350,400,450,500,550,600,650,700]
                            
                            #loop through the list and calculate the paleotopography for each year by subtracting the amount of isostacy from the dem.
                            for year in yearlist:
                                yeararrays[year] = demarr-(((isoarr*year)+(year-(2019-1890)))/1000)
                            
                            # call the results from the dictionary
                            dem200 =yeararrays.get(200)
                            dem250=yeararrays.get(250)
                            dem300=yeararrays.get(300)
                            dem350=yeararrays.get(350)
                            dem400=yeararrays.get(400)
                            dem450=yeararrays.get(450)
                            dem500=yeararrays.get(500)
                            dem550=yeararrays.get(550)
                            dem600=yeararrays.get(600)
                            dem650=yeararrays.get(650)
                            dem700=yeararrays.get(700)
                            
                           #calculate the change in pixels above the sealevel in 50 year intervals. Multiply the pixels with their m2 size and divide with 1000000 to get the km2 change in 50 years
                            change200_250 = (4*((0 < dem200).sum()-(0 < dem250).sum()))/1000000
                            change250_300 = (4*((0 < dem250).sum()-(0 < dem300).sum()))/1000000
                            change300_350 = (4*((0 < dem300).sum()-(0 < dem350).sum()))/1000000
                            change350_400 = (4*((0 < dem350).sum()-(0 < dem400).sum()))/1000000
                            change400_450 = (4*((0 < dem400).sum()-(0 < dem450).sum()))/1000000
                            change450_500 = (4*((0 < dem450).sum()-(0 < dem500).sum()))/1000000
                            change500_550 = (4*((0 < dem500).sum()-(0 < dem550).sum()))/1000000
                            change550_600 = (4*((0 < dem550).sum()-(0 < dem600).sum()))/1000000
                            change600_650 = (4*((0 < dem600).sum()-(0 < dem650).sum()))/1000000
                            change650_700 = (4*((0 < dem650).sum()-(0 < dem700).sum()))/1000000
                            
                            #resultname grid ID
                            resultname = row.LEHTITUNNU
                            
                            #save the changes in a list
                            changelist = [[change200_250,change250_300,change300_350,change350_400,change400_450,change450_500,change500_550,change550_600,change600_650,change650_700,resultname]]
                            
                            #create seperate df of the list
                            list_df = pd.DataFrame(changelist)
                            
                            #save the resulting dataframes in the results folder and create a folderstructure for storing the result .txt files
                            level1 = os.path.join(resultpath,resultname[0:2])
                            level2 = os.path.join(level1,resultname[0:3])
                                
                            # Create directions if they dont exist
                            if not os.path.exists(level1):
                                os.mkdir(level1)
                            if not os.path.exists(level2):
                                os.mkdir(level2)
                            
                            name = os.path.join(level2,'{}.txt'.format(resultname))
                            if not os.path.exists(name):
                                list_df.to_csv(name, index=False, header=False)
                            
                            print('result saved')
                        else:
                            continue
                
                else:
                    continue
    else:
        continue
