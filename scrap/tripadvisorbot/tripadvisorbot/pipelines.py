# -*- coding: utf-8 -*- 

from scrapy.exceptions import DropItem

class FilterWordsPipeline(object):
	"""A pipeline for filtering out items which contain certain words in their
	description"""

	def process_item(self, item, spider):
		return item;

import pymongo

from scrapy.conf import settings
#from scrapy import log
import logging

class MongoDBPipeline(object):

    def __init__(self):
      try:
        connection = pymongo.MongoClient(
            settings['MONGODB_SERVER'],
            settings['MONGODB_PORT']
        )
        db = connection[settings['MONGODB_DB']]
        self.collection = db[settings['MONGODB_COLLECTION']]
        result = self.collection.delete_many({})

      except Exception as e:
        logging.log(logging.CRITICAL, "No connect to MongoDB database! " + str(e))

    def process_item(self, item, spider):
      try:
        for data in item:
            if not data:
                raise DropItem("Missing data!")
        self.collection.insert(dict(item))
        #log.msg("Restaurant added to MongoDB database!", level=log.DEBUG, spider=spider)
        logging.log(logging.INFO, "Restaurant added to MongoDB database!")
      except Exception as e:
        logging.log(logging.ERROR, "No restaurant added to MongoDB database! " + str(e))
      return item

