import scrapekit
import dataset
from BeautifulSoup import BeautifulSoup
from urlparse import urljoin
import lxml 
from datetime import datetime

name = 'africacheck'
scraper = scrapekit.Scraper('get_urls_africacheck')


@scraper.task
def scrape_index(url):
	db = dataset.connect('sqlite:////home/thej/Documents/code/socialreporting/database/db.sqlite')
	db_stories_table = db['stories']
	db_stories_data_table = db['story_data']

	doc = scraper.get(url).html()
	soup = BeautifulSoup(lxml.html.tostring(doc))

	next = soup.find('a', {"class":"next page-numbers"})	
	if next is not None:
		next_link = next['href']
	 	scrape_index.queue(next_link)

	lead_story = soup.find('article', {"class":"secondary_article report lead"})	 	
	if lead_story is not None:
		url = str(lead_story.contents[0].contents[0]['href'])
		insert_data = {"website":name, "url": url}
 		db_stories_table. insert(insert_data)
		db.commit() 

 		tag_text = ""
 		title = ""
 		no_of_comments = 0
 		pubDate = datetime.strptime( "9999-01-01" , "%Y-%m-%d")
 		try:
			title = lead_story.contents[0].contents[0].getText()
			base = lead_story.contents[2].contents[3].contents
			pubDate = datetime.strptime( str(base[3].contents[0]['datetime'][0:10]), "%Y-%m-%d")
			comments = lead_story.contents[2].contents[3].contents[5].contents[0].getText()
			tags = lead_story.contents[2].contents[3].contents[7].contents

			for tag in tags:
				tag_text = tag_text+"||"+tag.getText()

			
			if comments == "Be the first to comment":
				no_of_comments = 0
			else:
				no_of_comments = (comments.split(""))[0]
		except:
			pass

 		insert_stories_data = {"story_url": url, "title":title,"no_comments": int(no_of_comments),"tags":tag_text,  'published_on':pubDate, "status_initial":1}
 		print str(insert_stories_data)
 		db_stories_data_table.insert(insert_stories_data)
		db.commit() 


 	following_stories = soup.findAll('article', {"class":"secondary_article report nonlead"})
 	for story in following_stories:
 		url = str(story.contents[0].contents[1]['href'])
 		insert_data = {"website":name, "url": url}
 		db_stories_table. insert(insert_data)
		db.commit() 

 		tag_text = ""
 		title = ""
 		no_of_comments = 0
 		pubDate =  datetime.strptime( "9999-01-01" , "%Y-%m-%d")
 		try:
	 		base = story.contents[0].contents[3].contents
	 		title = unicode(BeautifulSoup(base[1].getText(),  convertEntities=BeautifulSoup.HTML_ENTITIES))

	 		pubDate =  datetime.strptime( str(base[5].contents[0]['datetime'][0:10]) , "%Y-%m-%d")

	 		comments = base[7] .getText()
	 		if comments == "Be the first to comment":
				no_of_comments = 0
			else:
				no_of_comments = (comments.split(" "))[0]
	 		
	 		tag_text = ""
	 		if len(base) > 9:
		 		tags =  base[9]
				for tag in tags:
					tag_text = tag_text+"||"+tag.getText()
		except:
			pass

 		insert_stories_data = {"story_url": url, "title":title,"no_comments":no_of_comments,"tags":tag_text, 'published_on':pubDate, "status_initial":1}
 		db_stories_data_table.insert(insert_stories_data)
 		db.commit() 


#scrape_index.run('http://africacheck.org/latest-reports/')
scrape_index.run('http://africacheck.org/latest-reports/page/12/')
