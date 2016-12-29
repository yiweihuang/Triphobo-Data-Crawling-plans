# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TripdetailItem(scrapy.Item):
    # define the fields for your item here like:
    trip_start_time = scrapy.Field()
    trip_end_time = scrapy.Field()
    trip_path_city = scrapy.Field()
    trip_path_detail = scrapy.Field()
    pass
