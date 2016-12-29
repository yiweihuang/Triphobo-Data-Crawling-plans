# -*- coding: utf-8 -*-
import sys
import json
import scrapy
from scrapy.selector import Selector
from scrapy.http import HtmlResponse
from tripdetail.items import TripdetailItem
from scrapy.http import Request,FormRequest

class TripDetailSpider(scrapy.Spider):
    name = "trip_detail"
    start_urls = []
    allowed_domains = ["triphobo.com"]
    start_urls = ['https://www.triphobo.com/tripplans/europe-itinerary-3-weeks']

    def parse(self, response):
        itinerary_id = response.css('section').xpath('@data-itinerary-id').extract()
        loadDayOnView = 'https://www.triphobo.com/itinerary/loadDayOnView/' + str(itinerary_id[0])
        select_option = response.xpath('//select[contains(@id, "js_day_dropdown")]//option//text()').extract()
        limit = select_option[-1].split(' ')[-1]
        trip_start_time = response.xpath('//span[contains(@itemprop, "startTime")]//text()').extract()
        trip_end_time = response.xpath('//span[contains(@itemprop, "endTime")]//text()').extract()
        start_city = response.xpath('//ul[contains(@id, "js_city_container")]//li[contains(@class, "start-city-name")]//span//text()').extract()
        transit_city = response.xpath('//ul[contains(@id, "js_city_container")]//li[contains(@class, "transit-city")]//span//text()').extract()
        trip_path_detail = start_city + transit_city
        trip_path_city = trip_path_detail

        yield FormRequest(loadDayOnView, method='POST', formdata={'start': '0', 'limit': limit}, callback = self.parseTriphobo, meta = {'trip_start_time':trip_start_time, 'trip_end_time':trip_end_time, 'trip_path_city':trip_path_city})

    def parseTriphobo(self, response):
        item = TripdetailItem()
        plan_json = json.loads(response.text)
        stay_days = len(plan_json['itinerary_day_html'])
        temparr = []
        for i in range(1, stay_days+1, 1):
            plan_detail = Selector(text = plan_json['itinerary_day_html'][str(i)])
            content = plan_detail.xpath('//div[contains(@class, "step-2-attraction-details")]//h4//text()').extract()
            content = [x for x in content if '\n' not in x and 'Additional time available for you to plan.' not in x]
            temparr.append(content)
        item['trip_start_time'] = response.meta['trip_start_time']
        item['trip_end_time'] = response.meta['trip_end_time']
        item['trip_path_city'] = response.meta['trip_path_city']
        item['trip_path_detail'] = temparr
        yield item
