#coding=utf-8
'''
Created on 2022-3-31

@author: www.bookmarkearth.com
'''

from scrapy import cmdline

if __name__ == '__main__':

    cmdline.execute('scrapy crawl  main_spider'.split())
