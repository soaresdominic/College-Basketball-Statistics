#game
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import csv

class Game:
	'''
	teams = {}   #{id: team name, id: team name}
	homeTeam = None
	awayTeam = None
	date = None
	boxscore = None
	plays = []
	'''

	def __init__(self, gameID):
		self.teams = {}   #{id: team name, id: team name}
		self.homeTeam = None
		self.awayTeam = None
		self.date = None
		self.boxscore = None
		self.plays = []
		url = "http://www.espn.com/mens-college-basketball/game?gameId="
		url = url + str(gameID)
		raw_html = simple_get(url)
		html = BeautifulSoup(raw_html, 'html.parser')
		try:
			self.setTeamNames(html)
		except Exception as e:
			return
		finally:
			pass
		self.setTeamNames(html)
		self.setTeams(html)
		self.setDate(html)
		#self.createPlays(gameID)
		#self.printGameObject()
		#self.writeGameToFile()
		#self.createBoxscore(gameID)
		#self.printBoxObject()
		#self.writeBoxToFile()


	def writeBoxToFile(self):
		filename = "boxscores/" + self.date + " " + self.awayTeam + " at " + self.homeTeam + " boxscore" + ".csv"
		with open(filename, "w") as csv_file:
			writer = csv.writer(csv_file, delimiter=',')
			line = []
			line.append("NAME")
			line.append("MIN") 
			line.append("FG")
			line.append("PT")	
			line.append("FT")	
			line.append("OREB")	
			line.append("DREB")	
			line.append("REB")	
			line.append("AST")	
			line.append("STL")	
			line.append("BLK")	
			line.append("TO")	
			line.append("PF")	
			line.append("PTS")
			writer.writerow(line)
			for player in self.boxscore.players:
				line = []
				line.append(player.NAME)
				line.append(player.MIN)
				line.append(player.FG)
				line.append(player.PT)
				line.append(player.FT)
				line.append(player.OREB)
				line.append(player.DREB)
				line.append(player.REB)
				line.append(player.AST)
				line.append(player.STL)
				line.append(player.BLK)
				line.append(player.TO)
				line.append(player.PF)
				line.append(player.PTS)
				writer.writerow(line)



	def writeGameToFile(self):
		filename =  "playbyplay/" + self.date + " " + self.awayTeam + " at " + self.homeTeam + " playbyplay" + ".csv"
		with open(filename, "w") as csv_file:
			writer = csv.writer(csv_file, delimiter=',')
			line = []
			line.append("TIME")
			line.append("TEAM") 
			line.append("PLAYER")
			line.append("ACTION")	
			line.append("AWAYSCORE")	
			line.append("HOMESCORE")
			writer.writerow(line)
			for play in self.plays:
				line = []
				line.append(play.time)
				line.append(play.team)
				line.append(play.player)
				line.append(play.action)
				line.append(play.awayScore)
				line.append(play.homeScore)
				writer.writerow(line)


	def printBoxObject(self):
		for player in self.boxscore.players:
			player.printBox()


	def printGameObject(self):
		print(self.date)
		print(self.awayTeam + " at " + self.homeTeam)
		for play in self.plays:
			print(play.time, play.team, play.player, play.action, play.awayScore, play.homeScore)


	def setTeams(self, html):
		awayDiv = html.find_all("div", class_="team-info-logo")[0]
		homeDiv = html.find_all("div", class_="team-info-logo")[1]
		awayImg = html.find_all("img", class_="team-logo")[0]
		homeImg = html.find_all("img", class_="team-logo")[1]
		awayTxt = awayImg['src']
		homeTxt = homeImg['src']
		awayID = awayTxt.split("/")[-1].split(".")[0]
		homeID = homeTxt.split("/")[-1].split(".")[0]
		self.teams[awayID] = self.awayTeam
		self.teams[homeID] = self.homeTeam



	def setDate(self, html):
		title = html.title.string
		self.date = title.split(" - ")[2]



	def setTeamNames(self, html):
		self.awayTeam = html.find_all("span", class_="long-name")[0].get_text()
		self.homeTeam = html.find_all("span", class_="long-name")[1].get_text()



	def createBoxscore(self, gameID):
		url = "http://www.espn.com/mens-college-basketball/boxscore?gameId="
		url = url + str(gameID)
		self.boxscore = Box(url)



	def createPlays(self, gameID):
		url = "http://www.espn.com/mens-college-basketball/playbyplay?gameId="
		url = url + str(gameID)
		raw_html = simple_get(url)
		html = BeautifulSoup(raw_html, 'html.parser')
		containers = html.find_all("li", class_="accordion-item")
		for container in containers:
			for p in container.find_all("tr"):
				if(p.find("td") is not None):
					time = p.find("td", class_="time-stamp").get_text()
					homeScore = p.find("td", class_="combined-score").get_text().split(" - ")[1]
					awayScore = p.find("td", class_="combined-score").get_text().split(" - ")[0]
					player, action = self.getPlayerAndAction(p)
					team = self.getTeam(p)
					tmpPlay = play(time, team, player, action, homeScore, awayScore)
					self.plays.append(tmpPlay)




	def getPlayerAndAction(self, p):
		detailsText = p.find("td", class_="game-details").get_text()
		player = "None"
		action = "None"
		if("Foul" in detailsText):  #if its a foul play
			action = "Foul"
			if("Flagrant" not in detailsText):
				text = detailsText.split("Foul on ")[1]
				player = text[:-1]
			else:
				player = "FlagrantFoul"
		elif("Turnover" in detailsText):
			action = "Turnover"
			player = detailsText.split(" Turnover")[0]
		elif("Steal" in detailsText):
			action = "Steal"
			player = detailsText.split(" Steal")[0]
		elif("Block" in detailsText):
			action = "Block"
			player = detailsText.split(" Block")[0]	

		elif("made Free Throw" in detailsText):
			action = "Free Throw"
			player = detailsText.split(" made ")[0]
		elif("made Layup" in detailsText):
			action = "Layup"
			player = detailsText.split(" made ")[0]
		elif("made Jumper" in detailsText):
			action = "Jumper"
			player = detailsText.split(" made ")[0]
		elif("made Three Point Jumper" in detailsText):
			action = "Three Point Jumper"
			player = detailsText.split(" made ")[0]
		elif("made Dunk" in detailsText):
			action = "Dunk"
			player = detailsText.split(" made ")[0]

		elif("Defensive Rebound" in detailsText):
			action = "Defensive Rebound"
			player = detailsText.split(" Defensive Rebound")[0]
		elif("Team Rebound" in detailsText):
			action = "Team Rebound"
			player = "None"
		elif("Offensive Rebound" in detailsText):
			action = "Offensive Rebound"
			player = detailsText.split(" Offensive Rebound")[0]

		elif("missed Free Throw" in detailsText):
			action = "Missed Free Throw"
			player = detailsText.split(" missed ")[0]
		elif("missed Layup" in detailsText):
			action = "Missed Layup"
			player = detailsText.split(" missed ")[0]
		elif("missed Jumper" in detailsText):
			action = "Missed Jumper"
			player = detailsText.split(" missed ")[0]
		elif("missed Three Point Jumper" in detailsText):
			action = "Missed Three Point Jumper"
			player = detailsText.split(" missed ")[0]
		elif("missed Dunk" in detailsText):
			action = "Missed Dunk"
			player = detailsText.split(" missed ")[0]

		return player, action



	#https://a.espncdn.com/combiner/i?img=/i/teamlogos/ncaa/500/2294.png&h=100&w=100
	def getTeam(self, p):
		logo = p.find("td", class_="logo")
		if(logo.find("img") is None):
			return "<D1"
		logoSrcText = logo.find("img")['src']
		teamID = logoSrcText.split("/")[-1].split(".")[0]
		return self.teams[teamID]







class play:
	'''
	time = None
	team = None
	player = None
	action = None
	homeScore = None
	awayScore = None
	'''


	def __init__(self, time, team, player, action, homeScore, awayScore):
		self.time = time
		self.team = team
		self.player = player
		self.action = action
		self.homeScore = homeScore
		self.awayScore = awayScore





class Box:
	'''
	players = []
	'''

	def __init__(self, url):
		self.players = []
		raw_html = simple_get(url)
		html = BeautifulSoup(raw_html, 'html.parser')
		container = html.find("div", id="gamepackage-boxscore-module")
		for tbody in html.find_all("div", id="gamepackage-boxscore-module"):  #for each section
			for tr in tbody.find_all("tr"):  #for each player
				if(not(tr.has_attr("class"))):
					name = None
					MIN = None 
					FG = None
					PT = None	
					FT = None	
					OREB = None	
					DREB = None	
					REB = None	
					AST = None	
					STL = None	
					BLK = None	
					TO = None	
					PF = None	
					PTS = None
					for td in tr.find_all("td"):
						if(td["class"][0] == "min"):
							MIN = td.get_text()
						elif(td["class"][0] == "fg"):
							FG = td.get_text()
						elif(td["class"][0] == "3pt"):
							PT = td.get_text()
						elif(td["class"][0] == "ft"):
							FT = td.get_text()
						elif(td["class"][0] == "oreb"):
							OREB = td.get_text()
						elif(td["class"][0] == "dreb"):
							DREB = td.get_text()
						elif(td["class"][0] == "reb"):
							REB = td.get_text()
						elif(td["class"][0] == "ast"):
							AST = td.get_text()
						elif(td["class"][0] == "stl"):
							STL = td.get_text()
						elif(td["class"][0] == "blk"):
							BLK = td.get_text()
						elif(td["class"][0] == "to"):
							TO = td.get_text()
						elif(td["class"][0] == "pf"):
							PF = td.get_text()
						elif(td["class"][0] == "pts"):
							PTS = td.get_text()
						elif(td["class"][0] == "name"):
							name = td.find("a")["href"].split("/")[-2]
					if(name is not None):
						self.players.append(player(name, MIN, FG, PT, FT, OREB, DREB, REB, AST, STL, BLK, TO, PF, PTS))
					


	def getPlayerName(self, url):
		raw_html = simple_get(url)
		html = BeautifulSoup(raw_html, 'html.parser')
		playername = html.title.string.split(" Stats")[0]
		return playername



class player():
	'''
	NAME = None
	MIN = None 
	FG = None
	PT = None	
	FT = None	
	OREB = None	
	DREB = None	
	REB = None	
	AST = None	
	STL = None	
	BLK = None	
	TO = None	
	PF = None	
	PTS = None
	'''


	def __init__(self, name, MIN, fg, pt, ft, oreb, dreb, reb, ast, stl, blk, to, pf, pts):
		self.NAME = name
		self.MIN = MIN
		self.FG = fg
		self.PT = pt
		self.FT = ft
		self.OREB = oreb
		self.DREB = dreb
		self.REB = reb
		self.AST = ast
		self.STL = stl
		self.BLK = blk
		self.TO = to
		self.PF = pf
		self.PTS = pts


	def printBox(self):
		print(self.NAME, self.MIN, self.FG, self.PT, self.FT, self.OREB, self.DREB,
			self.REB, self.AST, self.STL, self.BLK, self.TO, self.PF, self.PTS)




def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200 
            and content_type is not None 
            and content_type.find('html') > -1)


def log_error(e):
    """
    It is always a good idea to log errors. 
    This function just prints them, but you can
    make it do anything.
    """
    print(e)
