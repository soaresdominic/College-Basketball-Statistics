import pandas as pd
import numpy as np
import os
import datetime
import time as tm
import pickle
import csv


def main():
	#PlayByPlays = readPlayByPlays()
	#DetailedPlayByPlays = readDetailedPlayByPlays()
	#saveDetailedPlayByPlays(DetailedPlayByPlays)
	DetailedPlayByPlays = loadDetailedPlayByPlays()

	schoolDunkDiff = analyzeDunksTotalDunks(DetailedPlayByPlays)
	#schoolDunkDiff = analyzeDunks(DetailedPlayByPlays)
	#print(schoolDunkDiff)

	writeDunksToFile(schoolDunkDiff)
	#dunkDiffList = getDunkDiff(schoolDunkDiff)

	"""
	playerClutchDictionary = analyzePlays(PlayByPlays)
	print(jbP)
	print(jbN)
	print(playerClutchDictionary)
	"""



def getDunkDiff(dunkDict):
	dunkList = []
	for school, gameList in dunkDict.items():
		tmplist = []
		tmplist.append(school)
		diff = 0
		for game in gameList:
			diff += game[2]
		tmplist.append(diff)
		dunkList.append(tmplist)
	dunkList.sort(key=lambda x: x[1])
	print(dunkList)
	return dunkList




def writeDunksToFile(dunks):
	with open('./playerdunks.csv', 'w') as csv_file:
		writer = csv.writer(csv_file)
		for key, value in dunks.items():
			writer.writerow([key, value])




#{"March 11, 2019 Gonzaga at UCLA playbyplay": dataframe, ...}
#{"player": dunks, "player": dunks,...}
def analyzeDunksTotalDunks(DetailedPlayByPlays):
	playerDunks = {}
	i = 0
	for title, playbyplay in DetailedPlayByPlays.items():
		print(i)
		i+=1;
		dunks = 0
		for index, row in playbyplay.iterrows():
			if(row["ACTION"] == "Dunk"):
				if(row["PLAYER"] in playerDunks):
					playerDunks[row["PLAYER"]] = playerDunks[row["PLAYER"]] + 1
				else:
					playerDunks[row["PLAYER"]] = 1
	return playerDunks






#i want a graph that has date at bottom, dot for W-L record
#{"March 11, 2019 Gonzaga at UCLA playbyplay": dataframe, ...}
#{"Gonzaga: [["W", November 10, 2018", 10], [["L", December 11, 2018", 26]], ...}
def analyzeDunks(DetailedPlayByPlays):
	schoolDunks = {}
	i = 0
	for title, playbyplay in DetailedPlayByPlays.items():
		print(i)
		i+=1;
		homeDunks = 0
		awayDunks = 0
		awayteam = ' '.join(title.split(" ")[3:]).split(" at ")[0]
		hometeam = ' '.join(title.split(" ")[3:]).split(" at ")[1].split(" playbyplay")[0]
		for index, row in playbyplay.iterrows():
			if(row["ACTION"] == "Dunk"):
				if(row["TEAM"] == hometeam):
					homeDunks += 1
				elif(row["TEAM"] == awayteam):
					awayDunks += 1
				else:
					print(row["TEAM"], hometeam, awayteam)
					print("team name match error!")

		homeDunkDiff = homeDunks - awayDunks
		awayDunkDiff = awayDunks - homeDunks

		homeResult = None
		awayResult = None
		#winner = playbyplay.iloc[-1, playbyplay.columns.get_loc("TEAM")]
		#print(playbyplay)
		#print(playbyplay.iloc[-1])

		if(playbyplay.iloc[-1]["AWAYSCORE"] < playbyplay.iloc[-1]["HOMESCORE"]):
			winner = hometeam
		else:
			winner = awayteam

		#print("winner " + winner, "hometeam " + hometeam, "awayteam " + awayteam)
		if(winner == hometeam):
			homeResult = "W"
			awayResult = "L"
		elif(winner == awayteam):
			homeResult = "L"
			awayResult = "W"

		date = ' '.join(title.split(" ")[:3])
		
		if(hometeam not in schoolDunks):
			schoolDunks[hometeam] = [[homeResult, date, homeDunkDiff]]
		else:
			currlist = schoolDunks[hometeam]
			currlist.append([homeResult, date, homeDunkDiff])
			schoolDunks[hometeam] = currlist

		if(awayteam not in schoolDunks):
			schoolDunks[awayteam] = [[awayResult, date, awayDunkDiff]]
		else:
			currlist = schoolDunks[awayteam]
			currlist.append([awayResult, date, awayDunkDiff])
			schoolDunks[awayteam] = currlist
	return schoolDunks




def readDetailedPlayByPlays():
	PlayByPlays = {}
	for filename in os.listdir("playbyplay/"):
		filename = os.fsdecode(filename)
		print(filename)
		df = pd.read_csv("playbyplay/" + filename, header=0, encoding = "ISO-8859-1")
		PlayByPlays[filename] = df
	#pickle.dump(PlayByPlays, open( "playbyplay/pbps.p", "wb" ))
	return PlayByPlays


def saveDetailedPlayByPlays(pbp):
	pickle.dump(pbp, open("./pbps.p", "wb"))
	print("Dictionary of dataframes saved")


def loadDetailedPlayByPlays():
	dic = pickle.load(open("./pbps.p", "rb"))
	print("Dictionary of dataframes loaded")
	return dic


def analyzePlays(PlayByPlays):
	playerCD = {}
	player = None
	clutch = None
	i = 0
	for playbyplay in PlayByPlays:
		playbyplay = playbyplay[int(len(playbyplay) / 3):]  #take only last third of game
		i += 1
		print(i)
		for index, row in playbyplay.iterrows():
			player, clutch = getClutch(row)
			if(player is None or clutch is None):
				continue
			else:
				if(player not in playerCD):
					playerCD[player] = clutch
				else:
					playerCD[player] = playerCD[player] + clutch
				#print(playerCD)
	playerCD = sorted(playerCD.items(), key=lambda kv: kv[1])
	playerCD.reverse()
	return playerCD


jbP = []
jbN = []
CDjP = []
CDjN = []




def getClutch(row):
	player = row['PLAYER']
	clutch = 0
	time = tm.strptime(row['TIME'], '%M:%S')
	time = datetime.timedelta(minutes=time.tm_min,seconds=time.tm_sec).total_seconds()
	#print(time)
	if(time < 180):
		if(time == 0):
			time = 1
		action = row['ACTION']
		if(action == "Free Throw" or action == "Layup"):
			clutch = 5
			clutch *= 10/time
			scoreDif = abs(row['HOMESCORE'] - row['AWAYSCORE'])
			if(scoreDif == 0):
				scoreDif = 1
			clutch *= 1/scoreDif
		elif(action == "Jumper" or action == "Three Point Jumper"):
			clutch = 10
			clutch *= 10/time
			scoreDif = abs(row['HOMESCORE'] - row['AWAYSCORE'])
			if(scoreDif == 0):
				scoreDif = 1
			clutch *= 1/scoreDif
		elif(action == "Turnover"):
			clutch = -10
			clutch *= 10/time
			scoreDif = abs(row['HOMESCORE'] - row['AWAYSCORE'])
			if(scoreDif == 0):
				scoreDif = 1
			clutch *= 1/scoreDif
		elif(action == "Steal"):
			clutch = 10
			clutch *= 10/time
			scoreDif = abs(row['HOMESCORE'] - row['AWAYSCORE'])
			if(scoreDif == 0):
				scoreDif = 1
			clutch *= 1/scoreDif
		elif(action == "Block"):
			clutch = 5
			clutch *= 10/time
			scoreDif = abs(row['HOMESCORE'] - row['AWAYSCORE'])
			if(scoreDif == 0):
				scoreDif = 1
			clutch *= 1/scoreDif
		elif(action == "Missed Free Throw" or action == "Missed Layup"):
			clutch = -10
			clutch *= 10/time
			scoreDif = abs(row['HOMESCORE'] - row['AWAYSCORE'])
			if(scoreDif == 0):
				scoreDif = 1
			clutch *= 1/scoreDif
		elif(action == "Missed Jumper" or action == "Missed Three Point Jumper"):
			clutch = -5
			clutch *= 10/time
			scoreDif = abs(row['HOMESCORE'] - row['AWAYSCORE'])
			if(scoreDif == 0):
				scoreDif = 1
			clutch *= 1/scoreDif

		

		#debug
		if(player == "Sterling Taplin"):
			if(clutch > 0):
				jbP.append((action, clutch))
			if(clutch <= 0):
				jbN.append((action, clutch))


	return player, clutch



def readPlayByPlays():
	PlayByPlays = []
	for filename in os.listdir("playbyplay/"):
		filename = os.fsdecode(filename)
		#print(filename)
		df = pd.read_csv("playbyplay/" + filename, header=0)
		PlayByPlays.append(df)
	return PlayByPlays




main()