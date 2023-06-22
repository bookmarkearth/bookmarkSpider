#coding=utf-8
'''
Created on 2022-3-27

@author: www.bookmarkearth.com
'''

from urllib.parse import urlparse
from tldextract import tldextract
from .langconv import Converter

# 转换繁体到简体
def cht_to_chs(line):
    line = Converter('zh-hans').convert(line)
    line.encode('utf-8')
    return line

# 转换简体到繁体
def chs_to_cht(line):
    line = Converter('zh-hant').convert(line)
    line.encode('utf-8')
    return line

def url_split(url):

    try:
        uri = urlparse(url)
        ext = tldextract.extract(url)
        return {
            "scheme": uri.scheme,
            "suffix": ext.suffix,
            "domain": ext.domain,
            "subdomain": ext.subdomain,
        }
    except Exception as e:
        print ("parse errro %s ", e)
    return None

