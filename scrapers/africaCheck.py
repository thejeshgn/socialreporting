import scrapekit
import dataset
from BeautifulSoup import BeautifulSoup
from urlparse import urljoin
import lxml 

name = 'africacheck'
scraper = scrapekit.Scraper('get_urls_africacheck')
db = dataset.connect('sqlite:////home/thej/Documents/code/socialreporting/database/db.sqlite')
db_stories_table = db['stories']
db_stories_data_table = db['story_data']


@scraper.task
def scrape_index(url):
	doc = scraper.get(url).html()
	soup = BeautifulSoup(lxml.html.tostring(doc))

	next = soup.find('a', {"class":"next page-numbers"})	
	if next is not None:
		next_link = next['href']
	 	#scrape_index.queue(next_link)

	lead_story = soup.find('article', {"class":"secondary_article report lead"})	 	
	if lead_story is not None:
		url = str(lead_story.contents[0].contents[0]['href'])
		insert_data = {"website":name, "url": url}
 		db_stories_table. insert(insert_data)
 		insert_stories_data = {"story_url": url}

 		db_stories_data_table.insert(insert_stories_data)

 	following_stories = soup.findAll('article', {"class":"secondary_article report nonlead"})
 	for story in following_stories:
 		url = str(story.contents[0].contents[1]['href'])
 		insert_data = {"website":name, "url": url}
 		db_stories_table. insert(insert_data)
 		insert_stories_data = {"story_url": url}
 		db_stories_data_table.insert(insert_stories_data)

	db.commit() 

scrape_index.run('http://africacheck.org/latest-reports/')