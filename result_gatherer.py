# -*- coding: utf-8 -*-
"""
Created on Tue Jul  9 14:36:20 2019

@author: Administrator
"""
import geopandas as gpd
import pandas as pd
import os
from statistics import mean 
from statistics import median
from statistics import stdev
import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

#directory of the result files
resdir =r'filepath of the result directory'

#empty dataframe for the results
dataAll = pd.DataFrame()

#loop through the files, if the file is a .txt file and isn't empty, it will be appended to the dataframe.
# if the file is empty, the loop prints out the filename
for subdir, dirs, files in os.walk(resdir): 
    for filename in files:
        if filename.endswith(".txt"):
            filepath = os.path.join(subdir,filename)
            if os.stat(filepath).st_size > 0:
                result = pd.read_csv(filepath, sep= ',', header=None)
                dataAll = dataAll.append(result, ignore_index=True)
            else:
                print(filepath)
                continue
        else:
            continue

#rename column after the yearly intervals
dataAll = dataAll.rename(columns={0: "200_250", 1: "250_300", 2:'300_350',3:'350_400',4:'400_450',5:'450_500',6:'500_550',7:'550_600',8:'600_650',9:'650_700',10:'ID' })

dataAll['sum'] = dataAll.sum(axis=1)                

#drop areas with mines and 0 result
dataAll = dataAll[dataAll.ID != 'L4111F']
dataAll = dataAll[dataAll.ID != 'L4114B']
dataAll = dataAll[dataAll.ID != 'Q4143H']
dataAll = dataAll[dataAll.ID != 'Q4321B']
dataAll = dataAll[dataAll.ID != 'M3332A']                
dataAll = dataAll[dataAll['sum'] != 0.000000]


# funktion for best fit line
x0 = np.array([1, 1])
xdata = np.array([250, 300, 350, 400, 450, 500, 550, 600, 650, 700])

def func(x, a, b):
    return a + b*x

################# PLOTTING ######################


#make a subset excluding the ID of the map grid
data = dataAll[['200_250','250_300','300_350','350_400','400_450','450_500','500_550','550_600','600_650','650_700']]

#empty lists
sumlist = []
yearly =[]

# calculate the sums of each time period by 50 year intervals and yearly. Add the results in the right list
for column in data.columns:
    columnsum = data[column].sum()
    sumlist.append(columnsum)
    yearlyrise = (data[column].sum())/50
    yearly.append(yearlyrise)

# variable for the x-axle tickmarks
objects = data.columns

#best fit line
params, params_covariance = curve_fit(func,xdata,sumlist,x0)

#plot the 50 year interval rise
plt.bar(data.columns,sumlist, align='center', alpha=0.5)
plt.plot(data.columns, func(xdata, params[0], params[1]), 'r--', label='fit: 2019 = %5.3f, slope = %5.3f' % tuple(params))
plt.xticks(objects, fontsize=7)
plt.xlabel('Years ago')
plt.ylabel('New dry land in 50 years (km2)')
plt.title('The appearance of dry land in Finland presented in 50 year intervals')
plt.legend()
plt.show()

#best fit line
params, params_covariance = curve_fit(func,xdata,yearly,x0)

# plot the yearly rise averages
plt.bar(data.columns,yearly, align='center', alpha=0.5)
plt.plot(data.columns, func(xdata, params[0], params[1]), 'r--', label='fit: Year 2019 = %5.3f, slope = %5.3f' % tuple(params))
plt.xticks(objects, fontsize=7)
plt.xlabel('Years ago')
plt.ylabel('New dry land in a year (km2)')
plt.title('The yearly appearance of dry land in Finland during 50 year intervals')
plt.legend()
plt.show()

# print some statistics
print('Yearly rise mean:', mean(yearly))
print('Yearly rise median:', median(yearly))
print('Yearly rise max:', max(yearly))
print('Yearly rise min:', min(yearly))
print('Yearly rise stdev:', stdev(yearly))


############ Export as shapefile ############


#directory of the utm10 shapefile
griddir = r'filepath of the utm 10 grid'

# read in utm10 shapefile
utm= gpd.read_file(griddir)

# combine the dataframes based on the ID
newdf = pd.merge(left=dataAll,right=utm, left_on='ID', right_on='LEHTITUNNU')

newGdf = gpd.GeoDataFrame(newdf, crs = utm.crs , geometry = newdf.geometry)

#save as shapefile
out_shp= r'filepath\results.shp'
newGdf.to_file(out_shp, driver='ESRI Shapefile')
print('shapefile saved')