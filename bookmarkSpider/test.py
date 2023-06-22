#coding=utf-8
'''
Created on 2022-3-31

@author: www.bookmarkearth.com
'''

from scrapy import cmdline
from model.es import Searchtemplate

if __name__ == '__main__':

    ##创建表格
    #Searchtemplate.init()

    cmdline.execute('scrapy crawl  main_spider'.split())
