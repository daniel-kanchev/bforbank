import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from bforbank.items import Article


class BforbankSpider(scrapy.Spider):
    name = 'bforbank'
    start_urls = ['https://www.bforbank.com/mag.html']

    def parse(self, response):
        links = response.xpath('//div[@class="nav m-ep-tabs new-v"]/ul/li/a/@href')[1:-1]
        yield from response.follow_all(links, self.parse_category)

    def parse_category(self, response):
        links = response.xpath('//a[text()="Lire la suite"]/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//a[@class="pagerLink nextLink"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse_category)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//p[@class="date"]/text()').get()
        if date:
            date = date.strip()

        content = response.xpath('//div[@itemprop="articleBody"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
