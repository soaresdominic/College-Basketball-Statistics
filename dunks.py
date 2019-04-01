from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup

#401082333

def main():
	dunks = {}
	dunksL = []
	for i in range(401082338, 401082348):
	#for i in range(401082001, 401087000):
		print(i)
		totalD = 0
		url = "http://www.espn.com/mens-college-basketball/playbyplay?gameId=" + str(i)
		raw_html = simple_get(url)

		if(raw_html is None):
			print("None")
			continue

		html = BeautifulSoup(raw_html, 'html.parser')
		title = html.title.string

		if("2018" in title):
			if("November" in title or "December" in title):
				for td in html.select('td'):
					if(td.has_attr("class")):
						if(td['class'][0] == 'game-details'):
							if("made Dunk" in td.text):
								totalD += 1
				print(totalD)
			else:
				continue
		elif("2019" in title):
			for td in html.select('td'):
				if(td.has_attr("class")):
					if(td['class'][0] == 'game-details'):
						if("made Dunk" in td.text):
							totalD += 1
			print(totalD)
		dunks[str(i)] = totalD
		dunksL.append(totalD)
	print(max(dunksL))
	#print(dunks[str(max(dunksL))])




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