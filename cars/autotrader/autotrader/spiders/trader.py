import scrapy
import json
from datetime import datetime

class TraderSpider(scrapy.Spider):
    name = 'trader'
    allowed_domains = ['autotrader.com']

    custom_settings = {
        'FEED_URI': 'trader.json',
        'FEED_FORMAT': 'json'
    }


    def start_requests(self):
        url = 'https://www.autotrader.com/cars-for-sale/dayton-oh-45424?dma=&sellerTypes=p&searchRadius=100&location=&startYear=2011&endYear=2020&marketExtension=include&isNewSearch=false&showAccelerateBanner=false&sortBy=relevance&numRecords=100&firstRecord=0'
        yield scrapy.Request(url, callback=self.flip_pages)


    def flip_pages(self, response):
        adTotal = int(response.css('.results-text-container::text').extract_first().split()[-2])
        if adTotal%100==0:
            pagesTotal=adTotal//100
        else:
            pagesTotal = (adTotal//100)+1
        
        flipPageUrl = response.url
        yield scrapy.Request(flipPageUrl, dont_filter=True)
        for i in range(1, pagesTotal):
            flipPageUrl = flipPageUrl.replace('firstRecord={}'.format((i-1)*100), 'firstRecord={}'.format(i*100))
            yield scrapy.Request(flipPageUrl)


 
    def parse(self, response):
        selected = response.xpath('//script[contains(.,"window.__BONNET_DATA__")]/text()').extract_first()
        myselected='{'+selected[24:]
        mydict=json.loads(myselected)
        mycars=mydict['initialState']['inventory']

        for key in mycars:
            owner = mycars[key].setdefault('ownerName','')
            if owner!='Private Seller':
                continue
            try:
                id = mycars[key]['id']
                brand = mycars[key]['make']
                model = mycars[key]['model']
                notes = mycars[key].setdefault('trim','')
                price = mycars[key]['pricingDetail']['salePrice']
                km = mycars[key]['specifications']['mileage']['value']
                proDate = mycars[key]['year']
                url = mycars[key]['website']            
            except:
                continue
            yield {
                'id':id,
                'brand':brand,
                'model':model,
                'notes':notes,
                'prince':price,
                'km':km,
                'proDate':proDate,
                'url':url,
                'adDate':datetime.strftime(datetime.today(),'%Y-%m-%d')
            }

