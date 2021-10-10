# Scrapy settings for dirbot project
BOT_NAME = 'tripadvisorbot'
#BOT_VERSION = '1.1'
# For version '1.0', go to https://github.com/magic890/tripadvisor-scraper

SPIDER_MODULES = ['tripadvisorbot.spiders']
NEWSPIDER_MODULE = 'tripadvisorbot.spiders'

DEFAULT_ITEM_CLASS = 'tripadvisorbot.items.TripAdvisorItem'
#USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)

ITEM_PIPELINES = {'tripadvisorbot.pipelines.MongoDBPipeline': 300, }

#MONGODB_SERVER = "localhost"
MONGODB_SERVER = "restaurant_db"
MONGODB_PORT = 27017
MONGODB_DB = "sadb"
MONGODB_COLLECTION = "restaurant"

#USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36'

# Obey robots.txt rules
#ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 1

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 0.01

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#    'User-Agent': USER_AGENT,
#    'Connection': 'Keep-Alive',
#    'Accept-Encoding': 'gzip, deflate',
#    'Accept-Language': 'en-US,*',
#}
