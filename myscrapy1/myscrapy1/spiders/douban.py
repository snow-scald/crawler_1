import scrapy
from myscrapy1.items import Myscrapy1Item
import os


headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36 Edg/103.0.1264.49'}
count=1

class DoubanSpider(scrapy.Spider):
    name = 'douban'
    allowed_domains = ['book.douban.com']
    start_urls = ['https://book.douban.com/subject/26912767/']

    def parse(self, response):
        global count
        page=response.selector.xpath('//span [@property="v:itemreviewed"]/text()')
        item=Myscrapy1Item()
        item['bookname']=page.extract()[0]
        count=count+1
        print("count=")
        print(count)
        yield item

        if count>10:
            return
        nexts=response.selector.xpath('//div[@class="content clearfix"]//dl[@class=""]//dt//a/@href')
        for i in nexts.extract():
            yield scrapy.Request(url=i,callback=self.parse)

        
