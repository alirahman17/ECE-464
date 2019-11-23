# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class AmcItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # pass
    movie_name = scrapy.Field()
    theater_name = scrapy.Field()
    date = scrapy.Field()
    time = scrapy.Field()
    type = scrapy.Field()
