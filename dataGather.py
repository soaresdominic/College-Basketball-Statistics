from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
from game import Game


def main():
	#getTeamWebsites()
	teamWebsiteList = loadTeamWebsites()
	#print(teamWebsiteList)
	teamScheduleList = loadGameLinks(teamWebsiteList)
	#saveGameLinks(teamScheduleList)
	gameLinks = openGameLinksFromFile()
	gameList = readGames(gameLinks)




def readGames(gameLinks):
	#Game("401083394")
	i = 0
	for gameID in gameLinks[4800:]:
		i+=1
		print(i)
		Game(gameID.split("\n")[0])
	return True



def openGameLinksFromFile():
	text_file = open("gameLinks.txt", "r")
	lines = text_file.readlines()
	text_file.close()
	return lines



def saveGameLinks(teamScheduleList):
	links = []
	i = 0
	for url in teamScheduleList:
		raw_html = simple_get(url)
		html = BeautifulSoup(raw_html, 'html.parser')
		for game in html.find_all("span", class_="ml4"):
			gameLink = game.find_all("a")[0]
			link = str(gameLink['href']).split("=")[1]
			if(link not in links):
				links.append(link)
		i += 1
		print(i)

	with open('gameLinks.txt', 'w') as f:
	    for l in links:
	        f.write("%s\n" % l)



'''
http://www.espn.com/mens-college-basketball/team/_/id/2250/gonzaga-bulldogs
http://www.espn.com/mens-college-basketball/team/schedule/_/id/2250
'''
def loadGameLinks(teamWebsiteList):
	teamScheduleList = []
	for teamWebsite in teamWebsiteList:
		scheduleText = "schedule/_/id/" + teamWebsite.split("id/")[1].split("/")[0]
		scheduleUrl = teamWebsite.split("_")[0] + scheduleText
		teamScheduleList.append(scheduleUrl)
	return teamScheduleList



def loadTeamWebsites():
	text_file = open("teamLinks.txt", "r")
	lines = text_file.readlines()
	text_file.close()
	return lines



def getTeamWebsites():
	teamWebsiteList = []
	url = "http://www.espn.com/mens-college-basketball/teams"
	raw_html = simple_get(url)
	html = BeautifulSoup(raw_html, 'html.parser')
	for team in html.find_all("section", class_="ContentList__Item"):
		if("TeamLinks flex items-center" in str(team)):
			teamLink = team.find_all("a")[0]
			teamLinkText = "http://www.espn.com" + str(teamLink['href'])
			teamWebsiteList.append(teamLinkText)

	for link in teamWebsiteList:
		print(link)




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







main()