import scrapy
from scrapy.crawler import CrawlerProcess
from bs4 import BeautifulSoup

class Character(scrapy.Item):
    name = scrapy.Field()
    specials = scrapy.Field()
    game = scrapy.Field()
    description = scrapy.Field()

class URLSpider(scrapy.spiders.CrawlSpider):
    name = "smash"
    start_urls = ["https://www.ssbwiki.com/Super_Smash_Bros._for_Wii_U"]

    def parse(self, response):
                                # all tables with @class   # 1st appearance  # all 'a' tags from that node
        veterans = response.xpath('//table[@class="wikitable"][1]//a')

                                # continue from last selection  # all href variables
        veturls = veterans.xpath('.//@href').extract()
        veturls = [('https://www.ssbwiki.com' + v) for v in sorted(set(veturls)) if '(SSB4)' in v]
        for v in veturls:
            yield scrapy.Request(v, callback=self.parse_char)

    def parse_char(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        char = Character()

        char['name'] = soup.find('h1', {'id':'firstHeading'}).text[:-7]
        char['game'] = soup.find('table', {'class':'infobox bordered'}).findAll('tr')[2].findAll('td')[1].text.strip('\n')
        char['description'] = soup.p.text
        moves = soup.find('span', {'id':'Moveset'}).find_parent('h2').find_next_sibling('table',{'class':'wikitable'})

        char['specials'] = []
        for num in [-13, -10, -7, -4]:
            move = moves.findAll('tr')[num].findAll('td')[1]
            char['specials'].append(move.text)


        yield char

process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
    'FEED_FORMAT': 'csv',
    'FEED_URI': 'smash_characters.csv'
})

process.crawl(URLSpider)
process.start()