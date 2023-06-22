#coding=utf-8
'''
Created on 2022-3-27

@author: www.bookmarkearth.com
'''
import hashlib
import os
import platform
import time
import uuid
import cgi
import datetime
import re
from urllib import parse
import threading
import base64

from scrapy.linkextractors import IGNORED_EXTENSIONS
from bookmarkSpider.constant.constant import ignored_extensions_all

mutex = threading.RLock() #可重入锁

def get_unix_time(): #10b的长度
   
    temp= str(time.mktime(datetime.datetime.now().timetuple()))
    t=temp.replace('.','')
    now_time=t[0:13]
    return now_time

def escape_html(html):
    ss = cgi.escape(html) # s = '&amp; &lt; &gt;'
    return ss

def now_time():
    temp = time.time()
    x = time.localtime(float(temp))
    y = time.strftime("%Y-%m-%d %H:%M:%S",x) # get time now
    return y

def date_today():
    temp = time.time()
    x = time.localtime(float(temp))
    y = time.strftime("%Y-%m-%d", x)  # get date today
    return y

def filter_digit(s): 
    ss=re.findall(r"\d+\.?\d*",s)
    if ss:
        return ss[0]
    return 0

def get_dentification():
    return str(uuid.uuid1()).replace("-","",100000)

def get_name(name):
    
    where=name.rfind('/')
    if where!=-1:
        return name[where+1:len(name)]
    return "#"

def qs(url):
    query = parse.urlparse(url).query
    return dict([(k,v[0]) for k,v in parse.urlparse.parse_qs(query).items()])

def is_valid_date(strdate):  
    '''''判断是否是一个有效的日期字符串'''  
    try:  
        if ":" in strdate:  
            time.strptime(strdate, "%Y-%m-%d %H:%M:%S")  
        else:  
            time.strptime(strdate, "%Y-%m-%d")  
        return True  
    except:  
        return False 
    
def lock(): #加锁
    mutex.acquire()

def unlock(): #解锁
    mutex.release()
    
def base64_decode(a):
    return base64.decodestring(a)

def format_time(strdate): 
    
    #%a 星期，日月年 时间 +时区
    parse_time_format = '%a, %d %b %Y %H:%M:%S +0000'
    day_output_date_format = '%Y-%m-%d %H:%M:%S'
    t = time.strptime(strdate, parse_time_format)
    x=time.strftime(day_output_date_format, t)
    return x

def get_extension(name):
    
    where=name.rfind('.')
    if where!=-1:
        return name[where:len(name)]
    return "#"

def get_md5(s):

    if isinstance(s,str):
        s = s.encode("utf-8")
    m = hashlib.md5()
    m.update(s)
    return m.hexdigest()

def which_platform():
    sys_str = platform.system()
    return sys_str

def get_absolute_path():
    curPath = os.path.abspath(os.path.dirname(__file__))
    end=curPath.rfind("\bookmarkSpider\sbookmarkSpider")
    if which_platform()=="Linux":
        end=curPath.rfind("/bookmarkSpider/bookmarkSpider")
    return curPath[0:end]

def get_ignore_extensitons():
    for item in IGNORED_EXTENSIONS:
        ignored_extensions_all.append(item)
    return ignored_extensions_all

##换行
def get_rid_of_feed(str):
    return str.replace('\n', '').replace('\t', '').replace('\r', '')


def body2str(d):

    body=""
    for values in d.values():
        for items in values:
            for item in items.values():
                body+=item

    return body

def list2str(values):

    rs=""
    for item in values:
        rs += item
    return rs
