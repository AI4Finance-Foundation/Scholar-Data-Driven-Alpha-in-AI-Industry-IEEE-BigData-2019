# -*- coding: utf-8 -*-
import scrapy
import time
import random

class UsPatentSpider(scrapy.Spider):
    name = 'us_patent'
    allowed_domains = ['uspto.gov']
    keywords = ["Artificial Intelligence"]
    companies = ["Google"]
    start_urls = ['http://uspto.gov/']

    # additional settings
    FEED_URI = 'C:/Users/Yunzhe Fang/Documents/Python/smart_beta_patent_data/test.csv'
    FEED_FORMAT = 'CSV'

    def start_requests(self):
        for company in self.companies:
            for keyword in self.keywords:
                url = "http://patft.uspto.gov/netacgi/nph-Parser?Sect1=PTO2&Sect2=HITOFF&u=%2Fnetahtml%2FPTO%2Fsearch-adv.htm&r=0&f=S&l=50&d=PTXT&p={}&S1=(%22{}%22+AND+{}.ASNM.)&Page=Next".format("1",keyword.replace(" ","+"), company.replace(" ","+"))
                yield scrapy.Request(
                url,
                self.parse_patent_urls,
                meta = {"company":company,
                "keyword":keyword,
                "page":1})

    def parse_patent_urls(self, response):
        meta = response.meta
        patent_number_and_title = response.xpath("//td[@valign='top']/a/text()").extract()
        patent_url = response.xpath("//td[@valign='top']/a/@href").extract()
        if len(patent_number_and_title)%2 == 0 and len(patent_number_and_title) == len(patent_url):
            for i in range(0,int(len(patent_number_and_title)/2)):
                meta['patent_number'] = patent_number_and_title[2*i].replace(",","").strip()
                meta['patent_name'] = patent_number_and_title[2*i + 1].strip()
                yield scrapy.Request(
                response.urljoin(patent_url[2*i]),
                self.parse_patent_data,
                meta = meta
                )

        #next page
        next_page = response.xpath("//img[@alt='[NEXT_LIST]']")
        if len(next_page) > 0:
            meta['page'] = meta['page'] + 1
            url2 = "http://patft.uspto.gov/netacgi/nph-Parser?Sect1=PTO2&Sect2=HITOFF&u=%2Fnetahtml%2FPTO%2Fsearch-adv.htm&r=0&f=S&l=50&d=PTXT&p={}&S1=(%22{}%22+AND+{}.ASNM.)&Page=Next".format(str(meta["page"]),meta["keyword"].replace(" ","+"), meta["company"].replace(" ","+"))
            yield scrapy.Request(
            url2,
            callback = self.parse_patent_urls,
            meta = meta
            )

    def parse_patent_data(self, response):
        meta = response.meta
        retry = False
        try:
            date = response.xpath("//td[@align='right']/b/text()").extract()[1].strip()
        except:
            retry = True
        if not retry:
            abstract = "".join([x.strip().replace("\n","") for x in response.xpath("//p/text()").extract()])
            patent_detail = response.xpath("//td[@align='left' and @width='90%']/b/text()").extract()[-3:]
            family_id = patent_detail[0].strip()
            application_number = patent_detail[1].strip()
            filed_date = patent_detail[2].strip()
            CPC_class_code = response.xpath("//td[@valign='top' and @align='right' and @width='70%']/text()").extract()[1].strip().replace("&nbsp"," ")
            item = {
            "company" : meta['company'],
            "keyword" : meta['keyword'],
            "patent_number" : meta["patent_number"],
            "application_number" : application_number,
            "patent_name" : meta["patent_name"],
            "date" : date,
            "filed_date" : filed_date,
            "family_id" : family_id,
            "CPC_class_code" : CPC_class_code,
            "abstract" : abstract,
            "url" : response.url
            }
            yield item
        else:
            time.sleep(20)
            print("retry:" + response.url)
            yield scrapy.Request(
            response.url,
            self.parse_patent_data,
            meta = meta,
            dont_filter = True
            )
