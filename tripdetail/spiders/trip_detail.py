# -*- coding: utf-8 -*-
import sys
import os
import json
import scrapy
import pandas as pd
from scrapy.selector import Selector
from scrapy.http import HtmlResponse
from tripdetail.items import TripdetailItem
from scrapy.http import Request,FormRequest

if len(sys.argv) < 4:
    print('Usage: scrapy crawl trip_detail -o tripdetail_dataset/[name].csv')
    sys.exit()
else:
    csv_name = sys.argv[3]

class TripDetailSpider(scrapy.Spider):
    name = "trip_detail"
    start_urls = []
    allowed_domains = ["triphobo.com"]
    file_name = csv_name.split('/')[1]
    read_path = 'dataset/' + file_name
    df = pd.read_csv(read_path)
    for url in df['url']:
        start_urls.append(url)

    def parse(self, response):
        itinerary_id = response.css('section').xpath('@data-itinerary-id').extract()
        author_id = response.css('small').xpath('@data-author-id').extract()
        loadDayOnView = 'https://www.triphobo.com/itinerary/loadDayOnView/' + str(itinerary_id[0])
        select_option = response.xpath('//select[contains(@id, "js_day_dropdown")]//option//text()').extract()
        limit = select_option[-1].split(' ')[-1]
        trip_start_time = response.xpath('//span[contains(@itemprop, "startTime")]//text()').extract()
        trip_end_time = response.xpath('//span[contains(@itemprop, "endTime")]//text()').extract()
        start_city = response.xpath('//ul[contains(@id, "js_city_container")]//li[contains(@class, "start-city-name")]//span//text()').extract()
        transit_city = response.xpath('//ul[contains(@id, "js_city_container")]//li[contains(@class, "transit-city")]//span//text()').extract()
        trip_path_detail = start_city + transit_city
        trip_path_city = trip_path_detail

        yield FormRequest(loadDayOnView, method='POST', formdata={'start': '0', 'limit': limit}, callback = self.parseTriphobo, meta = {'author_id':author_id, 'trip_start_time':trip_start_time, 'trip_end_time':trip_end_time})

    def parseTriphobo(self, response):
        item = TripdetailItem()
        plan_json = json.loads(response.text)
        stay_days = len(plan_json['itinerary_day_html'])
        temparr_city = []
        temparr = []
        for i in range(1, stay_days+1, 1):
            location = plan_json['itinerary_day_cities'][str(i)]
            if len(location) is not 0:
                if len(list(location.values())) > 1:
                    location_name = []
                    for plane in list(location.values()):
                        location_name.append(plane['name'])
                else:
                    location_name = list(location.values())[0]['name']
            elif len(location) is 0:
                location_name = ' '
            plan_detail = Selector(text = plan_json['itinerary_day_html'][str(i)])
            content = plan_detail.xpath('//div[contains(@class, "step-2-attraction-details")]//h4//text()').extract()
            content = [x for x in content if '\n' not in x and 'Additional time available for you to plan.' not in x]
            temparr_city.append(location_name)
            temparr.append(content)
        item['author_id'] = response.meta['author_id']
        item['trip_start_time'] = response.meta['trip_start_time']
        item['trip_end_time'] = response.meta['trip_end_time']
        item['trip_path_city'] = temparr_city
        item['trip_path_detail'] = temparr
        yield item
