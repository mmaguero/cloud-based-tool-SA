import re
import time
import scrapy

from scrapy.spiders import Spider
from scrapy.selector import Selector
from scrapy.http.request import Request

from tripadvisorbot.items import *
from tripadvisorbot.spiders.crawlerhelper import *
from datetime import datetime

# Constants.
# Max reviews pages to crawl.
# Reviews collected are around: 5 * MAX_REVIEWS_PAGES
MAX_REVIEWS_PAGES = 1000
# Max search result pages
MAX_SEARCH_RESULT_PAGES = 100

SEPARATOR = "=============================================================" + \
            "==================="

# this is update to 19/10/2017, and is possible you need edit the XPath route
class TripAdvisorRestaurantBaseSpider(Spider):
	name = "tripadvisor-restaurant"

	allowed_domains = ["tripadvisor.com"]
	base_uri = "https://www.tripadvisor.com"
	'''
        start_urls = [
		base_uri + "/Restaurants-g1044828-Province_of_Granada_Andalucia.html", #restaurants
                           "/Restaurants-g1044828-zfg11776-Province_of_Granada_Andalucia.html", #bar & pubs
                           "/Restaurants-g1044828-zfg9909-Province_of_Granada_Andalucia.html", #desserts
                           "/Restaurants-g1044828-zfg9901-Province_of_Granada_Andalucia.html", #bakeries
                           "/Restaurants-g1044828-zfg9900-Province_of_Granada_Andalucia.html", #coffee & tea
	]
        '''
        def start_requests(self):
              yield scrapy.Request(self.base_uri + '/Restaurants-g1044828-Province_of_Granada_Andalucia.html', self.parse)
              yield scrapy.Request(self.base_uri + '/Restaurants-g1044828-zfg11776-Province_of_Granada_Andalucia.html', self.parse)
              yield scrapy.Request(self.base_uri + '/Restaurants-g1044828-zfg9909-Province_of_Granada_Andalucia.html', self.parse)
              yield scrapy.Request(self.base_uri + '/Restaurants-g1044828-zfg9901-Province_of_Granada_Andalucia.html', self.parse)
              yield scrapy.Request(self.base_uri + '/Restaurants-g1044828-zfg9900-Province_of_Granada_Andalucia.html', self.parse)

	# Entry point for BaseSpider.
	# Page type: /RestaurantSearch
	def parse(self, response):
		tripadvisor_items = []
		counter_page = response.meta.get('counter_page', 0)

		sel = Selector(response)
		snode_restaurants = sel.xpath('//div[@id="EATERY_SEARCH_RESULTS"]/div[starts-with(@class, "listing")]')
                
		if (counter_page >= MAX_SEARCH_RESULT_PAGES or snode_restaurants is None):
			return
		counter_page += 1

		# Build item index.
		for i, snode_restaurant in enumerate(snode_restaurants):

			try:
				tripadvisor_item = TripAdvisorItem()
                                

                                tripadvisor_item['datetime'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                                tripadvisor_item['origin'] = self.allowed_domains[0]

				tripadvisor_item['url'] = self.base_uri + clean_parsed_string(get_parsed_string(snode_restaurant, 'div[starts-with(@class, "ui_column")]/div[starts-with(@class, "ui_column")]/div/a[@class="property_title"]/@href'))
                                
				tripadvisor_item['name'] = clean_parsed_string(get_parsed_string(snode_restaurant, 'div[starts-with(@class, "ui_column")]/div[starts-with(@class, "ui_column")]/div/a[@class="property_title"]/text()'))

				# Cleaning string and taking only the first part before whitespace.
				snode_restaurant_item_avg_stars = clean_parsed_string(get_parsed_string(snode_restaurant, './/div[starts-with(@class,"rating")]/span/@alt'))
                                if snode_restaurant_item_avg_stars:
                                      if snode_restaurant_item_avg_stars.count(" "):
                                           tripadvisor_item['avg_stars'] = snode_restaurant_item_avg_stars.split(' ')[0]
                                      else:
                                           tripadvisor_item['avg_stars'] = 0
 
                                page_url = response.urljoin(tripadvisor_item['url'])
                                print(SEPARATOR + "\n" + str(i) + "/" + str(counter_page) + page_url + "\n" + SEPARATOR)
				# Populate reviews and address for current item.
                                yield scrapy.Request(url=page_url, meta={'tripadvisor_item': tripadvisor_item}, callback=self.parse_search_page)

				tripadvisor_items.append(tripadvisor_item)
			except Exception as e: 
                                print("\n _ERROR IN SCRAP_ \n" + str(e))
				pass

		# Find the next page link if available and go on.
		next_page_url = clean_parsed_string(get_parsed_string(sel, '//a[starts-with(@class, "nav next rndBtn")]/@href'))
		if next_page_url and len(next_page_url) > 0:
                        page_url = response.urljoin(self.base_uri + next_page_url)
                        print(SEPARATOR + "\n" + "NEXT REVIEW" + page_url + "\n" + SEPARATOR)
		        yield Request(url=page_url, meta={'tripadvisor_item': tripadvisor_item, 'counter_page' : counter_page}, callback=self.parse)


	# Populate reviews and address in item index for a single item.
	# Page type: /Restaurant_Review
	def parse_search_page(self, response): 
		tripadvisor_item = response.meta['tripadvisor_item']
		sel = Selector(response)

		# TripAdvisor address for item.
		snode_address = sel.xpath('//ul[@class="detailsContent"]')
		tripadvisor_address_item = TripAdvisorAddressItem()

		tripadvisor_address_item['street'] = clean_parsed_string(get_parsed_string(snode_address, 'li/div/span/span[@class="format_address"]/span[@class="street-address"]/text()'))

		snode_address_locality = clean_parsed_string(get_parsed_string(snode_address, 'li/div/span/span[@class="format_address"]/span[@class="locality"]/text()'))
		if snode_address_locality:
			if snode_address_locality.count(" "):

				tripadvisor_address_item['postal_code'] = "".join([x for x in snode_address_locality if x.isdigit()]).replace(",", "").strip()

				tripadvisor_address_item['locality'] = "".join([x for x in snode_address_locality if not x.isdigit()]).replace(",", "").strip()

			else:
				tripadvisor_address_item['locality'] = snode_address_locality.replace(",", "")

				tripadvisor_address_item['country'] = clean_parsed_string(get_parsed_string(snode_address, 'li/div/span/span[@class="format_address"]/span[@class="country-name"]/text()'))

		tripadvisor_item['address'] = tripadvisor_address_item

		tripadvisor_item['reviews'] = []

		# The default page contains the reviews but the reviews are shrink and need to click 'More' to view the complete content.
		# An alternate way is to click one of the reviews in the page to open the expanded reviews display page.
		# We're using this last solution to avoid AJAX here.
		expanded_review_url = clean_parsed_string(get_parsed_string(sel, '//div[contains(@class, "basic_review")]//a[starts-with(@id, "rn")]/@href'))
		if expanded_review_url:
                       page_url = response.urljoin(self.base_uri + expanded_review_url)
                       print(SEPARATOR + "\n" + "FIRST REVIEW" + page_url + "\n" + SEPARATOR)
		       yield Request(url=page_url, meta={'tripadvisor_item': tripadvisor_item, 'counter_page_review' : 0}, callback=self.parse_fetch_review)


	# If the page is not a basic review page, we can proceed with parsing the expanded reviews.
	# Page type: /ShowUserReviews
	def parse_fetch_review(self, response):
		tripadvisor_item = response.meta['tripadvisor_item']
		sel = Selector(response)

		counter_page_review = response.meta['counter_page_review']

		# Limit max reviews pages to crawl.
		if counter_page_review < MAX_REVIEWS_PAGES:
			counter_page_review += 1

			# TripAdvisor reviews for item.
			snode_reviews = sel.xpath('//div[@class="ui_column is-9"]/div[@class="innerBubble"]/div[@class="wrap"]')
                        if snode_reviews is None:
                                return

			# Reviews for item.
			for i, snode_review in enumerate(snode_reviews):
				tripadvisor_review_item = TripAdvisorReviewItem()

				tripadvisor_review_item['title'] = clean_parsed_string(get_parsed_string(snode_review, 'div[contains(@class, "quote")]/a/span/text()'))
                                if tripadvisor_review_item['title'] is not None:
                                    print(SEPARATOR + "\n" + str(i) + "/" + str(counter_page_review) + tripadvisor_review_item['title'] + "\n" + SEPARATOR)

				# Review item description is a list of strings.
				# Strings in list are generated parsing user intentional newline. DOM: <br>
				tripadvisor_review_item['description'] = get_parsed_string_multiple(snode_review, 'div/div[@class="entry"]/p/text()')

				# Cleaning string and taking only the first part before whitespace.
				snode_review_item_stars = clean_parsed_string(get_parsed_string(snode_review, 'div[@class="rating reviewItemInline"]/span[starts-with(@class, "ui_bubble_rating")]/@class'))
				if snode_review_item_stars:
					snode_review_item_stars = snode_review_item_stars.split(' ')[1].split('_')[1]
					tripadvisor_review_item['stars'] = int(snode_review_item_stars)/10

				snode_review_item_date = clean_parsed_string(get_parsed_string(snode_review, 'div[@class="rating reviewItemInline"]/span[contains(@class, "ratingDate")]/@title'))
				if snode_review_item_date:
					#snode_review_item_date = re.sub(r'Reviewed ', '', snode_review_item_date, flags=re.IGNORECASE)
					snode_review_item_date = time.strptime(snode_review_item_date, '%B %d, %Y') if snode_review_item_date else datetime.now().strftime('%Y-%m-%d')
					tripadvisor_review_item['date'] = time.strftime('%Y-%m-%d', snode_review_item_date) if snode_review_item_date else datetime.now().strftime('%Y-%m-%d')
                                else:
                                        tripadvisor_review_item['date'] = datetime.now().strftime('%Y-%m-%d')

				snode_review_item_user = clean_parsed_string(get_parsed_string(snode_review, 'div/div[starts-with(@class, "helpful")]/span/span[@class="helpful_text"]/span[@class="thankUser"]/text()'))
				if snode_review_item_user:
					tripadvisor_review_item['user'] = re.sub(r'Thank ', '', snode_review_item_user, flags=re.IGNORECASE)

				tripadvisor_item['reviews'].append(tripadvisor_review_item)

			# Find the next page link if available and go on.
			next_page_url = clean_parsed_string(get_parsed_string(sel, '//a[starts-with(@class, "nav next rndBtn")]/@href'))
			if next_page_url and len(next_page_url) > 0:
                               page_url = response.urljoin(self.base_uri + next_page_url)
                               print(SEPARATOR + "\n" + "NEXT REVIEW" + page_url + "\n" + SEPARATOR)
			       yield Request(url=page_url, meta={'tripadvisor_item': tripadvisor_item, 'counter_page_review' : counter_page_review}, callback=self.parse_fetch_review)
			else:
			       yield tripadvisor_item

		# Limitatore numero di pagine di review da passare. Totale review circa 5*N.
		else:
			yield tripadvisor_item

