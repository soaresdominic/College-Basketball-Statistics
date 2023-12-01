import pandas as pd
import numpy as np
import os
import datetime
import time as tm
import pickle
import csv
import math


def main():
	#PlayByPlays = readPlayByPlays()
	#DetailedPlayByPlays = readDetailedPlayByPlays()
	#saveDetailedPlayByPlays(DetailedPlayByPlays)
	DetailedPlayByPlays = loadDetailedPlayByPlays()

	#schoolDunkDiff = analyzeDunksTotalDunks(DetailedPlayByPlays)
	schoolDunkDiff = analyzeDunks(DetailedPlayByPlays)
	#print(schoolDunkDiff)
	writeDToFile(schoolDunkDiff)

	
	#writeDunksToFile(schoolDunkDiff)
	#dunkDiffList = getDunkDiff(schoolDunkDiff)

	"""
	playerClutchDictionary = analyzePlays(DetailedPlayByPlays)
	print(playerClutchDictionary)
	writeClutchToFile(playerClutchDictionary)
	print(AJpos, AJneg, DEpos, DEneg)
	saveLists()
	"""

	
	#streakList = analyzeStreaks(DetailedPlayByPlays)
	#print(streakList)
	#writeStreakList(streakList)
	
	#streaks = loadStreaks()
	#findStreaks(streaks)



def writeDToFile(dunks):
	with open('./schooldunkstotal.csv', 'w') as csv_file:
		writer = csv.writer(csv_file)
		for school, games in dunks.items():
			dunkdiff = 0
			for game in games:
				dunkdiff += game[2]
			writer.writerow([school, dunkdiff])



def loadDunks():
	df = pd.read_csv("playerdunksrest.csv", header=0, encoding = "ISO-8859-1")
	return df

def loadDunksOrig():
	df = pd.read_csv("playerdunks.csv", header=0, encoding = "ISO-8859-1")
	return df


def addDunks(newdunks, olddunks):
	l = []
	for index, row in olddunks.iterrows():
		player = row["PLAYER"]
		dunks = row["DUNKS"]
		for index, row1 in newdunks.iterrows():
			if(row1["PLAYER"] == player):
				dunks += row1["DUNKS"]
		l.append([player, dunks])
	print(l)
	return l




def findStreaks(df):
	d = []
	for index, row in df.iterrows():  #for each player
		dt = []
		dt.append(row['PLAYER'])
		strkVal = 0
		for i in range(1,11):  #for each attribute
			'''
			firstleft = int(row[str(i)].split("/")[0])
			firstright = int(row[str(i)].split("/")[1])
			secondleft = int(row[str(i-1)].split("/")[0])
			secondright = int(row[str(i-1)].split("/")[1])
			if(firstright > 20 and secondright > 20):
				#if(firstleft / firstright != secondleft / secondright):
					dt.append(str(row["PLAYER"]) + " Shot " + str(i) + " " + str(firstleft / firstright) + ", Shot " + str(i-1) + " " + str(secondleft / secondright))
					#dt.append(firstleft / firstright)
					dt.append(((firstleft / firstright) - (secondleft / secondright))*100)
					#print(row["PLAYER"], " Shot " + str(i) + " ", firstleft / firstright, ", Shot " + str(i-1) + " ", secondleft / secondright)
					d.append(dt)
			'''
			if(int(row[str(0)].split("/")[1]) >= 100):
				firstleft = int(row[str(i)].split("/")[0])
				firstright = int(row[str(i)].split("/")[1])
				secondleft = int(row[str(0)].split("/")[0])
				secondright = int(row[str(0)].split("/")[1])
				if(firstright > 10 and secondright > 10):
					strkVal += (((firstleft / firstright) - (secondleft / secondright))*100)
		dt.append(strkVal)
		d.append(dt)
	d.sort(key=lambda x: x[1])
	with open('./temp.csv', 'w') as csv_file:
		writer = csv.writer(csv_file)
		for item in d:
			writer.writerow(item)



#streakList = [[team - player, made/missed on first shot or after a miss, made/missed after 1 made, after 2 made,...,after 10],...]
#ex. {"Gonzaga - zach norvell": ["40/90", "30/40",...], ...}
def writeStreakList(streaks):
	with open('./playerstreaksall.csv', 'w') as csv_file:
		writer = csv.writer(csv_file)
		for player, l in streaks.items():
			writer.writerow([player, l])


def analyzeStreaks(PlayByPlays):
	streaks = {}
	i = 1
	tmp = 0
	for title, playbyplay in PlayByPlays.items():  #for each game
		per = int((i/len(PlayByPlays.items()))*100)
		if(tmp != per):
			print(int((i/len(PlayByPlays.items()))*100), "%", end='\r')
			tmp = per
		i += 1
		#print(i)

		#iterate through a game and create mini version of streaklist
		streaksMini = {}
		currPlayerStreak = {}
		for index, row in playbyplay.iterrows():  #for each action in game
			action = row["ACTION"]
			if(action == "Missed Jumper" or action == "Missed Three Point Jumper" or action == "Jumper" or action == "Three Point Jumper" or action == "Layup" or action == "Missed Layup"):
				team = row["TEAM"]
				player = row["PLAYER"]
				key = team + " - " + player
				if(key not in streaksMini):  #if player is not already in the dictionary
					if("Missed" in action):
						streaksMini[key] = ["0/1"] + ["0/0"] * 10
						currPlayerStreak[key] = 0
					else:
						streaksMini[key] = ["1/1"] + ["0/0"] * 10
						currPlayerStreak[key] = 1
				else:  #player is in dictionary
					currStreak = currPlayerStreak[key]
					if(currStreak > 10):
						print(currStreak)
					top = int(streaksMini[key][currStreak].split("/")[0])
					bottom = int(streaksMini[key][currStreak].split("/")[1]) 
					if("Missed" in action):
						#add 1 to bottom of the currStreak # made/missed
						bottom = bottom + 1
						currPlayerStreak[key] = 0
					else:  #made shot
						#add 1 to both top and bottom
						top = top + 1
						bottom = bottom + 1
						currPlayerStreak[key] = currStreak + 1
						if(currPlayerStreak[key] > 10):  #just never go over 10 (change for longer streaks)
							currPlayerStreak[key] = 10
					streaksMini[key][currStreak] = str(top) + "/" + str(bottom)



		#add values from streaksMini to streaks
		#{"Gonzaga - zach norvell": ["40/90", "30/40",...], ...}
		#{"Gonzaga - zach norvell": ["20/50", "10/20",...], ...}
		#{"Gonzaga - zach norvell": ["60/140", "40/60",...], ...}
		for player, strkList in streaksMini.items():  #for player and list in game dictionary
			if(player not in streaks):  #if player isnt in main dictionary
				streaks[player] = strkList
			else:  #player is in main dictionary
				mainList = streaks[player]
				for j in range(len(strkList)):  #for "x/x" in game list for this player
					mainTop = int(mainList[j].split("/")[0])
					mainBot = int(mainList[j].split("/")[1])
					gameTop = int(strkList[j].split("/")[0])
					gameBot = int(strkList[j].split("/")[1])
					mainTop = mainTop + gameTop
					mainBot = mainBot + gameBot
					mainList[j] = str(mainTop) + "/" + str(mainBot)
				streaks[player] = mainList
						
	return streaks



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




def writeClutchToFile(clutchList):
	with open('./playerclutch.csv', 'w') as csv_file:
		writer = csv.writer(csv_file)
		for tup in clutchList:
			writer.writerow(tup)




def writeDunksToFile(dunks):
	with open('./playerdunksrest.csv', 'w') as csv_file:
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
			schoolDunks[hometeam] = [[homeResult, date, homeDunks]]
		else:
			currlist = schoolDunks[hometeam]
			currlist.append([homeResult, date, homeDunks])
			schoolDunks[hometeam] = currlist

		if(awayteam not in schoolDunks):
			schoolDunks[awayteam] = [[awayResult, date, awayDunks]]
		else:
			currlist = schoolDunks[awayteam]
			currlist.append([awayResult, date, awayDunks])
			schoolDunks[awayteam] = currlist
	return schoolDunks




def readDetailedPlayByPlays():
	PlayByPlays = {}
	for filename in os.listdir("playbyplay/"):
		filename = os.fsdecode(filename)
		print(filename)
		df = pd.read_csv("playbyplay/" + filename, header=0, encoding = "ISO-8859-1")
		df = df.drop_duplicates(subset=None, keep="first", inplace=False)
		PlayByPlays[filename] = df
	#pickle.dump(PlayByPlays, open( "playbyplay/pbps.p", "wb" ))
	return PlayByPlays



def loadStreaks():
	df = pd.read_csv("analysis/playerstreaks.csv", header=0, encoding = "ISO-8859-1")
	return df



def saveDetailedPlayByPlays(pbp):
	pickle.dump(pbp, open("./pbps.p", "wb"))
	print("Dictionary of dataframes saved")


def loadDetailedPlayByPlays():
	dic = pickle.load(open("./pbps.p", "rb"))
	#dic = dic.head(x)
	print("Dictionary of dataframes loaded")
	return dic


def analyzePlays(PlayByPlays):
	playerCD = {}
	player = None
	clutch = None
	i = 1
	tmp = 0
	for title, playbyplay in PlayByPlays.items():
		playbyplay = playbyplay[int(len(playbyplay) / 3):]  #take only last third of game

		per = int((i/len(PlayByPlays.items()))*100)
		if(tmp != per):
			print(int((i/len(PlayByPlays.items()))*100), "%", end='\r')
			tmp = per
		i += 1

		secondHalf = False
		for index, row in playbyplay.iterrows():
			if(row["TIME"] == "0:00"):
				secondHalf = True
			if(not secondHalf):
				continue

			player, clutch = getClutch(title, row)
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


"""
What is clutch? Clutch is defined as how well a player performs at the end of a game. During The 
last three minutes of a game, positive actions increase a player's clutch number, and negative
actions decrease a player's clutch number. Variables that change the degree of clutch include
whether the player's team is winning or losing and by how many points, how much time is left 
in the game, and the type of action. Each variable is given a certain weight depending on the 
importance the player's action is to winning the game for their team.

Multipliers for time left are given to actions based on the number of possessions left,
which is 30 seconds a posession taking the ceiling. Ex. 2min 30sec left, 160sec/30sec = 5.3 -> 6
6 possessions left = 1x
5 possessions left = 2x
...
1 posession left = 6x
Ex. made jumper (5), 5 poss. left (2) = 5*2 = 10
    made jumper (5), 2 poss. left (5) = 5*5 = 25

Multipliers for score difference are given to actions based on how close the score is,
which is based on possessions and thefeore multiples of 3 for 3 point shots.
11-9pts = 1x
8-6pts = 2x
5-3pts = 3x
2-0pts = 4x
Ex. made jumper (5), 7 pt game (2) = 5*2 = 10
    made jumper (5), 1 pt game (4) = 5*4 = 20

Multiplier for currently winning or losing is 1x for winning and 1.5x for losing.

Out of reach multiplier determines whether the losing team has no chance of winning.
multipliers are given as follows:
0-10 seconds >3 points  = 0
0-30 seconds 4-5 points = .5
			 6-8 points = .25
			 >8 points  = 0
30-1min		 7-8 points = .5
			 9-11 points= .25
			 >11 points = 0

Base clutch numbers for actions are as follows:
Made Free Throw, Layup, Block = 5
Steal = 7
Made Jumper = 10
Made Three Point Jumper = 12
Missed Jumper, Missed Three Point Jumper = -7 
Missed Free Throw, Missed Layup = -10
Turnover = -12

"""
def getClutch(title, row):
	player = row['PLAYER']
	clutch = None
	time = tm.strptime(row['TIME'], '%M:%S')
	time = datetime.timedelta(minutes=time.tm_min,seconds=time.tm_sec).total_seconds()
	#print(time)
	if(time < 180):  #only last 3 minutes
		scoreDif = abs(row['HOMESCORE'] - row['AWAYSCORE'])
		if(scoreDif <= 11):  #only close games
			if(time == 0):  #divide by zero error
				time = 1
			action = row['ACTION']
			if(action == "Free Throw" or action == "Layup" or action == "Block"):
				clutch = 5
			elif(action == "Steal"):
				clutch = 7
			elif(action == "Jumper"):
				clutch = 10
			elif(action == "Three Point Jumper"):
				clutch = 12
			elif(action == "Missed Jumper" or action == "Missed Three Point Jumper"):
				clutch = -7
			elif(action == "Missed Free Throw" or action == "Missed Layup"):
				clutch = -10
			elif(action == "Turnover"):
				clutch = -12
			else:
				return player, clutch

			scoreDif = abs(row['HOMESCORE'] - row['AWAYSCORE'])
			if(scoreDif <= 2):
				clutch *= 4
			elif(scoreDif <= 5):
				clutch *= 3
			elif(scoreDif <= 8):
				clutch *= 2
			elif(scoreDif <= 11):
				clutch *= 1

			possLeft = math.ceil(time/30)
			if(possLeft == 6):
				clutch *= 1
			elif(possLeft == 5):
				clutch *= 2
			elif(possLeft == 4):
				clutch *= 3
			elif(possLeft == 3):
				clutch *= 4
			elif(possLeft == 2):
				clutch *= 5
			elif(possLeft == 1):
				clutch *= 6

			if(time <= 10 and scoreDif > 3):
				clutch = 0
			elif(time <= 30 and (scoreDif >= 4 and scoreDif <= 5)):
				clutch = int(clutch*.5)
			elif(time <= 30 and (scoreDif >= 6 and scoreDif <= 8)):
				clutch = int(clutch*.25)
			elif(time <= 30 and scoreDif >= 9):
				clutch = 0
			elif(time <= 60 and (scoreDif >= 7 and scoreDif <= 8)):
				clutch = int(clutch*.5)
			elif(time <= 60 and (scoreDif >= 9 and scoreDif <= 11)):
				clutch = int(clutch*.25) 
			elif(time <= 60 and scoreDif >= 12):
				clutch = 0

			awayteam = ' '.join(title.split(" ")[3:]).split(" at ")[0]
			hometeam = ' '.join(title.split(" ")[3:]).split(" at ")[1].split(" playbyplay")[0]
			homeWinning = False
			awayWinning = False
			if(row['HOMESCORE'] > row['AWAYSCORE']):
				homeWinning = True
			else:
				awayWinning = True
			if(row['TEAM'] == hometeam and awayWinning):
				clutch = int(clutch * 1.5)
			elif(row['TEAM'] == awayteam and homeWinning):
				clutch = int(clutch * 1.5)


			if(player == "Lamar Stevens"):
				if(clutch >= 0):
					DEpos.append([row.tolist(),clutch])
				else:
					DEneg.append([row.tolist(),clutch])
			elif(player == "Jordan Davis"):
				if(clutch >= 0):
					AJpos.append([row.tolist(),clutch])
				else:
					AJneg.append([row.tolist(),clutch])
			elif(player == "Grant Williams"):
				if(clutch >= 0):
					GWpos.append([row.tolist(),clutch])
				else:
					GWneg.append([row.tolist(),clutch])

		
	return player, clutch


AJpos = []
AJneg = []
DEpos = []
DEneg = []
GWpos = []
GWneg = []

def saveLists():
	with open('./indivclutch.csv', 'w') as csv_file:
		writer = csv.writer(csv_file)
		for ls in AJpos:
			writer.writerow(ls)
		for ls in AJneg:
			writer.writerow(ls)
		for ls in DEpos:
			writer.writerow(ls)
		for ls in DEneg:
			writer.writerow(ls)
		for ls in GWpos:
			writer.writerow(ls)
		for ls in GWneg:
			writer.writerow(ls)


def readPlayByPlays():
	PlayByPlays = []
	for filename in os.listdir("playbyplay/"):
		filename = os.fsdecode(filename)
		#print(filename)
		df = pd.read_csv("playbyplay/" + filename, header=0)
		PlayByPlays.append(df)
	return PlayByPlays




main()