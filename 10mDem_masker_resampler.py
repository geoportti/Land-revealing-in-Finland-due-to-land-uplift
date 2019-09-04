#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 15 13:39:27 2019

@author: toikkaak


This script finds wanted 10m elevation model files, masks them with sea polygons,
resamples them to 2m resolution and finally saves them as .tif files. 

"""

import os
import rasterio
from rasterio.enums import Resampling
from rasterio.transform import from_origin
import fiona
from rasterio.mask import mask

#directory of the 10m dem files
directory =r'/wrk/project_ogiir-csc/mml/dem10m/2015'
#directory of the sea polygons
seafp = r'/wrk/project_ogiir-csc/mml/maastotietokanta/2019/gpkg/MTK-vakavesi_19-01-23.gpkg'

#filepaths for the output in your own work directory
outdir1 = r'filepath for masked demfiles'
outdir2 = r'filepath for resampled demfiles'

#list of the coastal map areas
maplist = ['S4','R4','Q3','Q4','P3','N3','M3','L2','L3','L4','L5','K2','K3','K4']

'''
The first loop goes through the directory of the 10m dem files and opens 
only the ones with the starting characters metioned in the maplist. After this the areas 
intersecting with sea polygons are masked to value 0. If the masked demfile min value 
is below 7.3m and the max value is over 0, the masked dem is stored in the outdir1 folder.
More about rasterio mask function: https://rasterio.readthedocs.io/en/stable/topics/masking-by-shapefile.html
'''

#loop through the km 10 files in directory
for subdir, dirs, files in os.walk(directory): 
    for filename in files:
            if filename.endswith(".tif") and filename[0:2] in maplist:
                filepath = os.path.join(subdir,filename)
                # open the Dem and mask it with sea areas
                with rasterio.open(filepath) as demdata:
                    bounds = demdata.bounds
                    with fiona.open(seafp, layer='meri') as sea:
                        hits = sea.items(bbox=(bounds.left,bounds.bottom,bounds.right,bounds.top))
                        items = [i for i in hits]
    
                    if len(items) > 0:
                        geoms = [item[1]['geometry'] for item in items]
                        demarr, out_transform = mask(demdata,geoms, invert=True)
                    else:
                        demarr = demdata.read()
                        demarr[demarr < 0] = 0
                    # If after masking the min value of the DEM file is below 7.3m and max over 10 add the ID in the list
                    if demarr.min() <= 7.3 and demarr.max() > 0:
                        #km10list.append(filename[0:5])
                        #print(filename)
                        out_meta = demdata.meta.copy()
                        outname = os.path.join(outdir1,'{}_masked.tif'.format(filename[0:5]))
                        with rasterio.open(outname,"w", **out_meta) as dest:
                            dest.write(demarr)
                        print('masked',filename,'saved')
                    else: 
                        continue
                    
                    

'''
The second loop goes through the masked 10m dems and resamples them to 2m resolution. 
You can read more about the resampling at https://rasterio.readthedocs.io/en/stable/topics/resampling.html
After resampling the new file is named after the orginal 10m elevation model
and saved as .tif file in outdir2. 
'''
# loop through the files again
for filename in os.listdir(outdir1):
    #construct the filepath
    filepath = os.path.join(outdir1,filename)
    # read the demfile and resample it to 2m resolution
    with rasterio.open(filepath) as dataset:
            data = dataset.read(out_shape=(dataset.count, dataset.height * 5, dataset.width * 5),resampling=Resampling.bilinear)
            bounds = dataset.bounds
            west = bounds[0]
            north = bounds[3]
            out_transform = from_origin(west, north, 2, 2) 
            out_meta = dataset.meta.copy()
    
    #update the metafile of the output 
    out_meta.update({"driver": "GTiff",
                     "height": data.shape[1],
                     "width": data.shape[2],
                     "count": data.shape[0],
                     "crs": dataset.crs,
                     "transform": out_transform})

    #save the resampled dem file
    outname = os.path.join(outdir2,'{}_2m_masked.tif'.format(filename[0:5]))
    with rasterio.open(outname,"w", **out_meta) as dest:
            dest.write(data)
    print('resampled',filename,'saved')


