import scrapekit
import dataset
from BeautifulSoup import BeautifulSoup
from urlparse import urljoin
import lxml 
import json

scraper = scrapekit.Scraper('story_data_shared_count')


@scraper.task
def add_to_scraper():
	db = dataset.connect('sqlite:////home/thej/Documents/code/socialreporting/database/db.sqlite')
	db_stories_table = db['stories']
	db_stories_data_table = db['story_data']

	stroies_to_update = db_stories_data_table.find(status_social=0)
	for story in stroies_to_update:
		get_shared_count.queue(story['story_url'])
	db.commit()

@scraper.task
def get_shared_count(url):
	db = dataset.connect('sqlite:////home/thej/Documents/code/socialreporting/database/db.sqlite')
	db_stories_table = db['stories']
	db_stories_data_table = db['story_data']	
	api_url='https://free.sharedcount.com?url='+str(url)+"&apikey=ded16b5b2a0280a41c929f5ac006e90c12205341"
	data = scraper.get(api_url).json()
	stroies_to_update = db_stories_data_table.find_one(status_social=0, story_url=url)
	db_id = stroies_to_update['id']
	print db_id
	db.commit() 
	if db_id is not None:
		update_data = {"id":db_id, "count_stumbleupon":data['StumbleUpon'] , "count_reddit" :data['Reddit'], "count_delicious":data['Delicious'] , \
		"count_googleplusone":data['GooglePlusOne'] , "count_twitter":data['Twitter'] , "count_pinterest":data['Pinterest'] , "count_linkedIn":data['LinkedIn'] ,\
		"count_fb_commentsbox" :data['Facebook']['commentsbox_count'], "count_fb_click"  :data['Facebook']['click_count'], "count_fb_total"  :data['Facebook']['total_count'], "count_fb_comment" :data['Facebook']['comment_count'] ,\
		"count_fb_like"  :data['Facebook']['like_count'], "count_fb_share" :data['Facebook']['share_count'] , "status_social":1 }
		db_stories_data_table.update(update_data,['id'])
		db.commit() 


if __name__ == '__main__':
	#get_shared_count.run()
	add_to_scraper.queue().wait()