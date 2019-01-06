# -*- coding: utf-8 -*-
import scrapy
import urllib
import pandas as pd
import json

class PaperSpider(scrapy.Spider):
    name = 'paper'
    allowed_domains = ['microsoft.com']
    url_AfN = "https://api.labs.cognitive.microsoft.com/academic/v1.0/interpret?"
    url_search = "https://api.labs.cognitive.microsoft.com/academic/v1.0/evaluate?"
    company_list = list(pd.read_csv("C:/Users/Yunzhe Fang/Desktop/company_list.csv")['company_list'])

    # Headers
    headers = {'Ocp-Apim-Subscription-Key': '9e022e160c234bc185661399320e68b8',}

    def start_requests(self):
        for company in self.company_list:
            params = urllib.parse.urlencode({
                # Request parameters
                'query': company,
                'complete': '0',
                'count': '1',
                'offset': '0',
                'timeout': '3600',
                'model': 'latest'
            })
            url = self.url_AfN + params
            yield scrapy.Request(url = url,
                headers = self.headers,
                callback = self.parse_company_name,
                meta = {"company_name":company})

    def parse_company_name(self, response):
        meta = response.meta
        company_result = json.loads(response.text)['interpretations']
        if len(company_result) != 0:
            company_query_name = company_result[0]['rules'][0]['output']['value'].split("=='")[-1].split("')")[0]
            params_dict = {
                'expr': "And(Ty='0',Composite(AA.AfN='{company}'))".format(company = company_query_name),
                'count': 1000,
                'offset': 0,
                'orderby': 'D',
                'attributes': 'Id,Ti,Pt,Y,D,CC,ECC,AA.AuN,AA.AuId,AA.AfN,AA.AfId,AA.S,F.FN,F.FId,J.JN,J.JId,C.CN,C.CId,W',
            }
            params = urllib.parse.urlencode(params_dict)
            url = self.url_search + params
            meta['params_dict'] = params_dict
            meta['company_query_name'] = company_query_name
            yield scrapy.Request(url = url,
            headers = self.headers,
            callback = self.parse_search_results,
            meta = meta)

    def parse_search_results(self, response):
        meta = response.meta
        search_results = json.loads(response.text)['entities']
        paper_type_dict = {'3':'Conference publications','1':'Journal publications','2':'Patents','5':'Books','0':'Articles'}
        for search_result in search_results:
            try:
                paper_type = paper_type_dict[search_result['Pt']]
            except:
                paper_type = "Others"
            if 'J' in search_result:
                J_or_C_name = search_result['J']['JN']
                J_or_C_id = search_result['J']['JId']
            elif 'C' in search_result:
                J_or_C_name = search_result['C']['CN']
                J_or_C_id = search_result['C']['CId']
            else:
                J_or_C_name = ""
                J_or_C_id = ""
            if "F" in search_result:
                Fields_of_study = search_result['F']
            else:
                Fields_of_study = []
            item = {
            'company' : meta['company_name'],
            'company_query_name' : meta['company_query_name'],
            'id' : search_result["Id"],
            'title' : search_result["Ti"],
            'paper_type' : paper_type,
            'paper_year' : search_result['Y'],
            'paper_date' : search_result['D'],
            'citation' : search_result['CC'],
            'citation_estimated' : search_result['ECC'],
            'Authors' : search_result['AA'],
            'Fields_of_study' : Fields_of_study,
            "J_or_C_name" : J_or_C_name,
            "J_or_C_id" : J_or_C_id,
            "keywords" : search_result['W'],
            'logprob' : search_result['logprob']
            }
            yield item
        if len(search_results) == 1000:
            meta['params_dict']['offset'] += 1000
            params = urllib.parse.urlencode(meta['params_dict'])
            url = self.url_search + params
            yield scrapy.Request(url = url,
            headers = self.headers,
            callback = self.parse_search_results,
            meta = meta)
