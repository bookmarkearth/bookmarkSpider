# coding=utf-8
'''
Created on 2022-3-27

@author: www.bookmarkearth.com
'''

from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess

if __name__ == '__main__':

    setting = get_project_settings()
    process = CrawlerProcess(setting)

    ##创建表格
    # Searchtemplate.init()

    didntWorkSpider = ['broken_link']
    for spider_name in process.spiders.list():
        print(spider_name)
        if spider_name in didntWorkSpider:
            continue
        print("Running spider %s" % (spider_name))
        process.crawl(spider_name)
    process.start()
