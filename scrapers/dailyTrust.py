import scrapekit
import dataset
from BeautifulSoup import BeautifulSoup
from urlparse import urljoin
import lxml 
from datetime import datetime
import time

name = 'dailytrust'
base_url = 'http://www.dailytrust.com.ng'
scraper = scrapekit.Scraper('get_urls_dailytrust')


@scraper.task
def scrape_index(url):
    db = dataset.connect('sqlite:///./../database/db.sqlite')
    db_stories_table = db['stories']
    db_stories_data_table = db['story_data']

    doc = scraper.get(url).html()
    soup = BeautifulSoup(lxml.html.tostring(doc))

    next = soup.find('li', {"class":"pagination-next"})
    if next is not None:
        try:
            next_link = base_url+next.contents[0]['href']
            print next_link
            scrape_index.queue(next_link)
        except:
            pass

        stories = soup.findAll('td', {"class":"list-title"})
        for story in stories:
            story_url = base_url+ str(story.contents[1]['href'])
            
            exists = db_stories_table.find_one(url=story_url)
            if exists is not None:
                break


            insert_data = {"website":name, "url": story_url}
            print(insert_data)
            db_stories_table.insert(insert_data)
            db.commit() 

            doc = scraper.get(story_url).html()
            soup = BeautifulSoup(lxml.html.tostring(doc))

            tag_text = ""
            no_of_comments = -1
            pubDate = datetime.strptime( "9999-01-01" , "%Y-%m-%d")

            try:
                title_ref = soup.find('div', {"class":"item-page"})
                title = unicode(BeautifulSoup(title_ref.contents[1].getText(),  convertEntities=BeautifulSoup.HTML_ENTITIES)) 

                pubDate_ref = soup.find('time')['datetime']
                pubDate = datetime.strptime( str(pubDate_ref[0:10]), "%Y-%m-%d")
                tag_text = "Health"

                # disqus_url="http://disqus.com/embed/comments/?base=default&disqus_version=f87655a9&f=daily-trust&t_i=07b9e8d8b8_id34431&t_u="+str(story_url)
                # disqus_doc = scraper.get(disqus_url).html()                
                # disqus_soup = BeautifulSoup(lxml.html.tostring(disqus_doc))
                # print disqus_soup                
                # comments_ref = disqus_soup.find('span', {"class":'comment-count'}).contents[0].getText()
                # print comments_ref
                # tag_text = "Health"                
                # no_of_comments = (comments_ref.split(" "))[0]

            except:
                pass

            insert_stories_data = {"story_url": story_url, "title":title,"no_comments": int(no_of_comments),"tags":tag_text,  'published_on':pubDate, "status_initial":1}
            print str(insert_stories_data)
            db_stories_data_table.insert(insert_stories_data)
            db.commit() 
scrape_index.run('http://www.dailytrust.com.ng/daily/health')
