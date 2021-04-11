import scrapy
from datetime import datetime

class ScoutSpider(scrapy.Spider):
    name = 'scout'
    allowed_domains = ['autoscout24.de']
    custom_settings = {
        'FEED_URI': 'scout.json',
        'FEED_FORMAT': 'json' }

    def start_requests(self):
        cars=['audi', 'bmw', 'mercedes-benz', 'volkswagen', 'ford', 'opel', 'toyota', 'renault', 'fiat', 'porsche']
        myurl='https://www.autoscout24.de/lst/{}/dortmund?desc=1&size=20&zip=Dortmund&custtype=P&adage=14&page=1&fc=5&fregfrom=2008&cy=D&gear=A%2CS&ac=0&lon=7.4708&zipr=150&offer=U&sort=age&lat=51.50805&ustate=N%2CU&atype=C'
        for car in cars:
            url=myurl.format(car)
            yield scrapy.Request(url,meta={'brand':car},callback=self.flip_pages)

    def flip_pages(self,response):
        adTotal=response.xpath('//as24-tracking [contains(@as24-tracking-value, "search_numberOfArticles")]/@as24-tracking-value').extract_first().split()[1]
        adTotal=int(adTotal.translate(str.maketrans  ('','',':"\'{}')))

        if adTotal%20==0:
            pagesTotal=adTotal//20
        else:
            pagesTotal=adTotal//20+1

        flipPageUrl=response.url
        yield scrapy.Request(flipPageUrl,meta={'brand':response.meta['brand']} ,dont_filter=True)
        for i in range(1,pagesTotal):
            flipPageUrl=flipPageUrl.replace  ('page={}'.format(i), 'page={}'.format(i+1))
            yield scrapy.Request(flipPageUrl,meta={'brand':response.meta['brand']})



    def parse(self, response):
        containerDivs=response.xpath('.//div[@class="cldt-summary-full-item-main"]')
        for eachCar in containerDivs:
            id=eachCar.xpath('.//@data-articleid').extract_first()
            model=eachCar.xpath('.//div[@class="cldt-summary-title"]/h2[1]/text()').extract_first()
            notes=eachCar.xpath('.//div[@class="cldt-summary-title"]/h2[2]/text()').extract_first()

            price=eachCar.xpath('.//span[@data-item-name="price"]/text()').extract_first()
            price=price.strip().translate(str.maketrans('','','€,.- '))

            km=eachCar.xpath('.//ul[@data-item-name="vehicle-details"]/li[1]/text()').extract_first()
            km=km.strip().translate(str.maketrans('','','km .'))

            proDate=eachCar.xpath('.//ul[@data-item-name="vehicle-details"]/li[2]/text()').extract_first()
            proDate=proDate.strip().split('/')[1]

            url=eachCar.xpath('.//span[@data-fed-detail-page-url]/@data-fed-detail-page-url').extract_first()

            yield {'id':id,
                'model':model,
                'brand':response.meta['brand'],
                'notes':notes if notes!=None else '',
                'price':price,
                'km':km,
                'proDate':proDate,
                'url':url,
                'adDate':datetime.strftime(datetime.today(),'%Y-%m-%d')}
