import scrapekit
import dataset
from BeautifulSoup import BeautifulSoup
from urlparse import urljoin
import lxml 

scraper = scrapekit.Scraper('story_data_shared_count')
db = dataset.connect('sqlite:///./../database/db.sqlite')
db_stories_table = db['stories']
db_stories_data_table = db['story_data']

@scraper.task
def create_scrape_index(website):
	all_stories_from_website = db_stories_table.find(website=website)
	all_insert_data = []
	for story in all_stories_from_website:
		insert_data = {"status_initial":0, "status_social": 0, "story_url":story['url']}
		all_insert_data.append(insert_data)
	db.commit()
	db_stories_data_table.insert_many(all_insert_data)
	db.commit()

create_scrape_index('africacheck')