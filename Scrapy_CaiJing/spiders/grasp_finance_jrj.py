"""
@Description :
@File        : grasp_finance_jrj
@Project     : Scrapy_CaiJing
@Time        : 2022/4/8 15:49
@Author      : LiHouJian
@Software    : PyCharm
@issue       :
@change      :
@reason      :
"""

import scrapy
from scrapy.utils import request
from Scrapy_CaiJing.items import ScrapyCaijingItem
from Scrapy_CaiJing import upload_file
from datetime import datetime


class GraspFinanceJrjSpider(scrapy.Spider):
    name = 'grasp_finance_jrj'
    allowed_domains = ['finance.jrj.com.cn']
    start_urls = ['https://finance.jrj.com.cn/list/industrynews-1.shtml/']
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"
    }

    def start_requests(self):
        for i in range(1, 6):
            url = f'http://finance.jrj.com.cn/list/industrynews-{i}.shtml'
            req = scrapy.Request(url, callback=self.parse, dont_filter=True)
            yield req

    def parse(self, response):
        url_list = response.xpath("//ul[@class='list2']/li/a/@href").extract()
        titles = response.xpath(
            "//ul[@class='list2']/li/a/text()").extract()
        pub_time_list = response.xpath(
            "//ul[@class='list2']/li/i/text()").extract()
        for i in range(len(url_list)):
            url = url_list[i]
            req = scrapy.Request(
                url, callback=self.parse_detail, dont_filter=True)
            news_id = request.request_fingerprint(req)
            title = titles[i]
            pub_time = pub_time_list[i]
            req.meta.update({"news_id": news_id})
            req.meta.update({"title": title})
            req.meta.update({"pub_time": pub_time})
            yield req
        # next_url = response.xpath("//div[@class='news-box']/ul[@class='pagination']/li[last()]/a/@href").extract()
        # if next_url:
        # yield scrapy.Request(url= next_url[-1], callback=self.parse,
        # dont_filter=True)

    def parse_detail(self, response):
        news_id = response.meta['news_id']
        title = response.meta['title']
        pub_time = response.meta['pub_time']
        source = response.xpath(
            "//p[@class='inftop']/span/i/a/text()").extract_first()
        content = ''.join(response.xpath(
            "//div[@class='texttit_m1']").extract())
        content_img = response.xpath(
            "//div[@class='texttit_m1']//img/@src").extract()
        if content_img:
            content_img_list = list()
            for index, value in enumerate(content_img):
                img_name = title + str(index)
                res = upload_file.send_file(value, img_name, self.headers)
                if res['msg'] == 'success':
                    content = content.replace(value, res['url'][0])
                    content_img_list.append(res['url'][0])
                else:
                    self.logger.info(f'内容图片 {value} 上传失败，返回数据：{res}')

            imgs = ','.join(content_img_list)
        else:
            imgs = None

        item = ScrapyCaijingItem()
        item['news_id'] = news_id
        item['category'] = '财经'
        item['content_url'] = response.url
        item['title'] = title
        item['issue_time'] = pub_time
        item['title_image'] = None
        item['information_source'] = '金融界'
        item['content'] = content
        item['source'] = source
        item['author'] = None
        item['images'] = imgs
        item['update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        item['cleaning_status'] = 0
        self.logger.info(item)
        yield item


if __name__ == '__main__':
    import scrapy.cmdline as cmd
    cmd.execute(['scrapy', 'crawl', 'grasp_finance_jrj'])
