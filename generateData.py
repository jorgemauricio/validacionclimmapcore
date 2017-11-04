#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 17 16:17:25 2017

@author: jorgemauricio
"""
#%% librerias
import pandas as pd
import os
import math
import numpy as np 

#%% Clear terminal
os.system('clear')

#%% Obtener todos los archivos en data
filesList = [x for x in os.listdir('data') if x.endswith('.csv')]

#%% generate info for AGS
for i in filesList:
	print('***** Processing Ags: {}'.format(i))
	fileTitle = 'data/{}'.format(i)
	date, ext = i.split(".")
	tYear, tMonth, tDay = date.split("-")
	temporalData = pd.read_csv(fileTitle)
	temporalData = temporalData.filter(['Long', 'Lat', 'Rain', 'Hr', 'Tpro'], axis=1)
	temporalData = temporalData.loc[temporalData['Long'] > -103.09]
	temporalData = temporalData.loc[temporalData['Long'] < -101.62]
	temporalData = temporalData.loc[temporalData['Lat'] > 21.54]
	temporalData = temporalData.loc[temporalData['Lat'] < 22.58]
	temporalData['Year'] = int(tYear)
	temporalData['Month'] = int(tMonth)
	temporalData['Day'] = int(tDay)
	processingFileTitle = 'ags/{}'.format(i)
	temporalData.to_csv(processingFileTitle, index=False)

for i in filesList:
	print('***** Processing Sonora: {}'.format(i))
	fileTitle = 'data/{}'.format(i)
	date, ext = i.split(".")
	tYear, tMonth, tDay = date.split("-")
	temporalData = pd.read_csv(fileTitle)
	temporalData = temporalData.filter(['Long', 'Lat', 'Rain', 'Hr', 'Tpro'], axis=1)
	temporalData = temporalData.loc[temporalData['Long'] > -115.61]
	temporalData = temporalData.loc[temporalData['Long'] < -107.57]
	temporalData = temporalData.loc[temporalData['Lat'] > 25.70]
	temporalData = temporalData.loc[temporalData['Lat'] < 33.02]
	temporalData['Year'] = int(tYear)
	temporalData['Month'] = int(tMonth)
	temporalData['Day'] = int(tDay)
	processingFileTitle = 'sonora/{}'.format(i)
	temporalData.to_csv(processingFileTitle, index=False)

#%% Processing Ags
print('***** Processing Weather Stations from Aguascalientes \n')

#%% Read data
agsWeatherStations = pd.read_csv('dataStations/aguascalientes_2017.csv')

#%% Drop NA values from the rows
agsWeatherStations = agsWeatherStations.dropna()

#%% Final data base structure
dataBaseStructure = "Station,Type,State,Lat,Long,Year,Month,Day,Rain,Hr,Tpro" + "\n"
dataBaseStructuretTest =  "Station,State,Lat,Long,Year,Month,Day,Rain,Hr,Tpro,RainWRF,HrWRF,TproWRF" + "\n"

#%% iterate ags
for index, row in agsWeatherStations.iterrows():
	
	# generate title for csv file from the WRF
	monthTitle = "{}".format(int(row['Month']))
	dayTitle = "{}".format(int(row['Day']))

	if len(monthTitle) == 1:
		monthTitle = "0" + monthTitle

	if len(dayTitle) == 1:
		dayTitle = "0" + dayTitle

	print('***** Processing file of Ags: {}-{}-{}'.format(int(row['Year']),monthTitle,dayTitle))
	temporalFileTitle = 'ags/{}-{}-{}.csv'.format(int(row['Year']),monthTitle,dayTitle)
	dataWRF = pd.read_csv(temporalFileTitle)
	#%% generate np arrays
	Lat = np.array(dataWRF['Lat'])
	Long = np.array(dataWRF['Long'])
	Year = np.array(dataWRF['Year'])
	Month = np.array(dataWRF['Month'])
	Day = np.array(dataWRF['Day'])
	Rain = np.array(dataWRF['Rain'])
	Hr = np.array(dataWRF['Hr'])
	Tpro = np.array(dataWRF['Tpro'])

	# Point to evaluate
	pointLat = row['Lat']
	pointLong = row['Long']
	pointNumber = row['Number']
	pointYear = row['Year']
	pointMonth = row['Month']
	pointDay = row['Day']
	pointRain = row['Rain']
	pointHr = row['Hr']
	pointTpro = row['Tpro']
	# distances
	d1 = 0.0
	d2 = 0.0
	d3 = 0.0
	pointIndex1 = 0.0
	pointIndex2 = 0.0
	pointIndex3 = 0.0

	# Select the 3 points to interpolate
	for i in range(len(Lat)):
		distanceBetweenPoints = 0.0
		differenceX = pointLong - Long[i]
		differenceY = pointLat - Lat[i]
		sumDifferenceXY = pow(differenceX, 2.0) + pow(differenceY, 2.0)
		distanceBetweenPoints = math.sqrt(sumDifferenceXY)
		if i == 0:
			d1 = distanceBetweenPoints
			pointIndex1 = i
			d2 = distanceBetweenPoints
			pointIndex2 = i
			d3 = distanceBetweenPoints
			pointIndex3 = i
		if distanceBetweenPoints < d1:
			d3 = d2
			pointIndex3 = pointIndex2
			d2 = d1
			pointIndex2 = pointIndex1
			d1 = distanceBetweenPoints
			pointIndex1 = i
		if distanceBetweenPoints > d1 and distanceBetweenPoints < d2:
			d3 = d2
			pointIndex3 = pointIndex2
			d2 = distanceBetweenPoints
			pointIndex2 = i
		if distanceBetweenPoints > d2 and distanceBetweenPoints < d3:
			d3 = distanceBetweenPoints
			pointIndex3 = i

	# Interpolate data
	k = 2.0
	w1 = 0.0
	w2 = 0.0
	w3 = 0.0
	zTpro = 0.0
	zRain = 0.0
	zHr = 0.0

	inverseSum = pow((1 / d1),k) + pow((1 / d2),k) + pow((1 / d3),k)
	w1 = 1 / pow(d1,k) / inverseSum
	w2 = 1 / pow(d2,k) / inverseSum
	w3 = 1 / pow(d3,k) / inverseSum

	zTpro = (w1 * Tpro[pointIndex1]) + (w2 * Tpro[pointIndex2]) + (w3 * Tpro[pointIndex3])
	zRain = (w1 * Rain[pointIndex1]) + (w2 * Rain[pointIndex2]) + (w3 * Rain[pointIndex3])
	zHr = (w1 * Hr[pointIndex1]) + (w2 * Hr[pointIndex2]) + (w3 * Hr[pointIndex3])
	# structure 1
	dataBaseStructure += '{},{},{},{},{},{},{},{},{},{},{}\n'.format(pointNumber, 'Station', 'AGS', pointLat, pointLat, pointYear, pointMonth, pointDay, pointRain, pointHr, pointTpro)
	dataBaseStructure += '{},{},{},{},{},{},{},{},{},{},{}\n'.format(pointNumber, 'WRF', 'AGS', pointLat, pointLat, pointYear, pointMonth, pointDay, zRain, zHr, zTpro)

	# structure 2
	dataBaseStructuretTest += '{},{},{},{},{},{},{},{},{},{},{},{},{}\n'.format(pointNumber, 'AGS', pointLat, pointLat, pointYear, pointMonth, pointDay, pointRain, pointHr, pointTpro, zRain, zHr, zTpro)

#%% Save to csv data 1
fileName = 'dataFromAguascalientes.csv'
textFile = open(fileName, "w")
textFile.write(dataBaseStructure)
textFile.close()

#%% Save to csv data 1
fileName = 'dataFromAguascalientestTest.csv'
textFile = open(fileName, "w")
textFile.write(dataBaseStructuretTest)
textFile.close()

#%% Processing Ags
print('***** Processing Weather Stations from Sonora \n')

#%% Read data
sonoraWeatherStations = pd.read_csv('dataStations/sonora_2017.csv')

#%% Drop NA values from the rows
sonoraWeatherStations = sonoraWeatherStations.dropna()

#%% Final data base structure
dataBaseStructure = "Station,Type,State,Lat,Long,Year,Month,Day,Rain,Hr,Tpro" + "\n"
dataBaseStructuretTest =  "Station,State,Lat,Long,Year,Month,Day,Rain,Hr,Tpro,RainWRF,HrWRF,TproWRF" + "\n"

#%% iterate ags
for index, row in sonoraWeatherStations.iterrows():
	
	# generate title for csv file from the WRF
	monthTitle = "{}".format(int(row['Month']))
	dayTitle = "{}".format(int(row['Day']))

	if len(monthTitle) == 1:
		monthTitle = "0" + monthTitle

	if len(dayTitle) == 1:
		dayTitle = "0" + dayTitle

	print('***** Processing file of Sonora: {}-{}-{}'.format(int(row['Year']),monthTitle,dayTitle))
	temporalFileTitle = 'sonora/{}-{}-{}.csv'.format(int(row['Year']),monthTitle,dayTitle)
	dataWRF = pd.read_csv(temporalFileTitle)
	#%% generate np arrays
	Lat = np.array(dataWRF['Lat'])
	Long = np.array(dataWRF['Long'])
	Year = np.array(dataWRF['Year'])
	Month = np.array(dataWRF['Month'])
	Day = np.array(dataWRF['Day'])
	Rain = np.array(dataWRF['Rain'])
	Hr = np.array(dataWRF['Hr'])
	Tpro = np.array(dataWRF['Tpro'])

	# Point to evaluate
	pointLat = row['Lat']
	pointLong = row['Long']
	pointNumber = row['Number']
	pointYear = row['Year']
	pointMonth = row['Month']
	pointDay = row['Day']
	pointRain = row['Rain']
	pointHr = row['Hr']
	pointTpro = row['Tpro']
	# distances
	d1 = 0.0
	d2 = 0.0
	d3 = 0.0
	pointIndex1 = 0.0
	pointIndex2 = 0.0
	pointIndex3 = 0.0

	# Select the 3 points to interpolate
	for i in range(len(Lat)):
		distanceBetweenPoints = 0.0
		differenceX = pointLong - Long[i]
		differenceY = pointLat - Lat[i]
		sumDifferenceXY = pow(differenceX, 2.0) + pow(differenceY, 2.0)
		distanceBetweenPoints = math.sqrt(sumDifferenceXY)
		if i == 0:
			d1 = distanceBetweenPoints
			pointIndex1 = i
			d2 = distanceBetweenPoints
			pointIndex2 = i
			d3 = distanceBetweenPoints
			pointIndex3 = i
		if distanceBetweenPoints < d1:
			d3 = d2
			pointIndex3 = pointIndex2
			d2 = d1
			pointIndex2 = pointIndex1
			d1 = distanceBetweenPoints
			pointIndex1 = i
		if distanceBetweenPoints > d1 and distanceBetweenPoints < d2:
			d3 = d2
			pointIndex3 = pointIndex2
			d2 = distanceBetweenPoints
			pointIndex2 = i
		if distanceBetweenPoints > d2 and distanceBetweenPoints < d3:
			d3 = distanceBetweenPoints
			pointIndex3 = i

	# Interpolate data
	k = 2.0
	w1 = 0.0
	w2 = 0.0
	w3 = 0.0
	zTpro = 0.0
	zRain = 0.0
	zHr = 0.0

	inverseSum = pow((1 / d1),k) + pow((1 / d2),k) + pow((1 / d3),k)
	w1 = 1 / pow(d1,k) / inverseSum
	w2 = 1 / pow(d2,k) / inverseSum
	w3 = 1 / pow(d3,k) / inverseSum

	zTpro = (w1 * Tpro[pointIndex1]) + (w2 * Tpro[pointIndex2]) + (w3 * Tpro[pointIndex3])
	zRain = (w1 * Rain[pointIndex1]) + (w2 * Rain[pointIndex2]) + (w3 * Rain[pointIndex3])
	zHr = (w1 * Hr[pointIndex1]) + (w2 * Hr[pointIndex2]) + (w3 * Hr[pointIndex3])
	# structure 1
	dataBaseStructure += '{},{},{},{},{},{},{},{},{},{},{}\n'.format(pointNumber, 'Station', 'SON', pointLat, pointLat, pointYear, pointMonth, pointDay, pointRain, pointHr, pointTpro)
	dataBaseStructure += '{},{},{},{},{},{},{},{},{},{},{}\n'.format(pointNumber, 'WRF', 'SON', pointLat, pointLat, pointYear, pointMonth, pointDay, zRain, zHr, zTpro)

	# structure 2
	dataBaseStructuretTest += '{},{},{},{},{},{},{},{},{},{},{},{},{}\n'.format(pointNumber, 'SON', pointLat, pointLat, pointYear, pointMonth, pointDay, pointRain, pointHr, pointTpro, zRain, zHr, zTpro)

#%% Save to csv data 1
fileName = 'dataFromSonora.csv'
textFile = open(fileName, "w")
textFile.write(dataBaseStructure)
textFile.close()

#%% Save to csv data 1
fileName = 'dataFromSonoratTest.csv'
textFile = open(fileName, "w")
textFile.write(dataBaseStructuretTest)
textFile.close()