import copy
import os
from datetime import datetime
from queue import Queue

import scrapy
from scrapy.http import TextResponse
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule
from scrapy.utils.project import get_project_settings

from bookmarkSpider.model.local_redis import RedisHelper
from bookmarkSpider.model.mongo import MongoHelper
from bookmarkSpider.service.extract_url import SqlFactory
from bookmarkSpider.spiders.parser import Parser
from bookmarkSpider.util.common import get_md5, date_today
from bookmarkSpider.util.convert import url_split


class MainSpider(Parser):

    name = "main_spider"

    rules = [Rule(LinkExtractor(), callback='parse', follow=True)]

    custom_settings  = {
        # Put your debug settings here
    }

    @classmethod
    def update_settings(cls, settings):

        today = datetime.now()
        log_path=settings.get('LOG_DIR')

        if not os.path.exists(log_path):
            os.makedirs(log_path)

        log_file = log_path + "scrapy_{}_{}_{}.log".format(today.year, today.month, today.day)
        #print(log_file)

        ##更新##
        cls.custom_settings.update({'LOG_FILE':log_file})
        settings.setdict(cls.custom_settings or {}, priority='command')

    def __init__(self, *args, **kwarg):

        super(MainSpider, self).__init__()
        self.factory = SqlFactory()
        self.visited= set()
        self.mongoHelper = MongoHelper()
        self.request_queue=Queue()
        self.download_timeout=self.settings.get('DOWNLOAD_TIMEOUT')
        self.unique_mark="key_md5_fixed"
        self.update_settings(get_project_settings())#日志文件貌似只初始化一次，没法改变名字
        self.redisHelper = RedisHelper()
        self.count=0


    def _parms_host(self,parms):

        # 仅允许当前网站数据
        subdomain = parms['subdomain']
        if (subdomain != ''):
            subdomain = subdomain + "."

        host = subdomain + parms['domain'] + "." + parms['suffix']
        parms['host'] = host
        return parms

    def start_requests(self):

        while True:

            record = {}
            ball = self.factory.select_all_bookmark()
            record['key_md5']=get_md5(self.unique_mark)
            record=self.mongoHelper.query_by_key(record,self.mongoHelper.last_record,'key_md5')

            ##已经爬到了结尾处
            max_id=self.factory.select_max_bookmark_id()

            if record and max_id >= record['bookmark_id']:
                record['uid']=1
                record['bookmark_id']=1
                self.mongoHelper.upsert(record,self.mongoHelper.last_record,'key_md5')
                self.redisHelper.dels("url_seen")

            for b in ball:

                bookmarkId=b[0]
                if record and bookmarkId < record['bookmark_id']:
                    continue

                fall = self.factory.select_all_folder(bookmarkId)
                for f in fall:
                    folderId=f[0]
                    uall=self.factory.select_folder_content(folderId)
                    for u in uall:
                        uid = u[0]
                        url = u[2]
                        parms = url_split(url)

                        if parms is not None and "http" in parms['scheme']:

                            parms['bookmark_id']=bookmarkId
                            parms['folder_id']=folderId
                            parms['uid']=uid

                            if record and uid < record['uid']:
                                continue

                            parms['collect_times']=self.factory.select_collect_times_num(uid) #在书签文件夹中出现的次数
                            parms=self._parms_host(parms)

                            last_record = {}
                            last_record['bookmark_id'] = bookmarkId
                            last_record['uid']=uid
                            last_record['today']=date_today()
                            last_record['key_md5']=get_md5(self.unique_mark)

                            self.mongoHelper.upsert(last_record,self.mongoHelper.last_record,'key_md5')
                            self.request_queue.put((url, parms))  ##加入队列

                            #print('uid %s %s' %(uid,url))
                            while self.request_queue.qsize()>0:

                                url, parms = self.request_queue.get()

                                ##只对种子url做处理
                                if url.startswith("http://"):
                                    yield scrapy.Request(
                                        url,
                                        # dont_filter=True,
                                        meta={
                                            "parms": parms,
                                            "pro":"01",
                                            "depth": 0,
                                            #"download_timeout":2,
                                        },
                                        callback=self.parse,
                                        errback=self.errback
                                    )
                                else:
                                    yield scrapy.Request(
                                        url,
                                        # dont_filter=True,
                                        meta={
                                            "parms": parms,
                                            "depth": 0,
                                        },
                                        callback=self.parse,
                                        errback=self.errback
                                    )

    def parse(self,response):

        if not isinstance(response, TextResponse):
            yield None

        if response.status != 200:
            yield  None

        page = super(MainSpider, self)._get_item(response)
        if page:

            yield page

            # 直接返回，强制返回2层结果，节约硬盘

            depth = response.meta.get('depth')
            if depth and 0==depth:
                # copy, 防止再次请求没法释放内存
                meta = copy.deepcopy(response.meta)

                urllist = []
                for href in response.xpath('//a/@href').extract():
                    url = response.urljoin(href)
                    urllist.append(url)

                # copy 释放上层内存
                pg = copy.deepcopy(page)

                self.crawl_detail(pg, meta, urllist)

    def crawl_detail(self,page,meta,urllist):

        ##提取参数
        parms = meta.get('parms')
        bookmarkId = parms['bookmark_id']
        folderId = parms['folder_id']
        uid = parms['uid']
        id=page['id']
        robots=page['robots'] #0为不可以爬取、1为可以爬取

        if robots==1 and id not in self.visited: #如果robots==1，代表可以爬取

            self.visited.add(id)  # 访问过了
            if (len(self.visited) > 3000):
                self.visited.clear()

            ##提取页面链接
            for url in urllist:

                parms = url_split(url)
                domain = parms['domain'] + "." + parms['suffix']

                #print("href" + href)

                if parms is not None and "http" in parms['scheme'] and domain in url:

                    parms['bookmark_id'] = bookmarkId
                    parms['folder_id'] = folderId
                    parms['uid'] = uid

                    # 准备host
                    parms = self._parms_host(parms)
                    _uid = self.factory.select_uid_by_urlmd5(get_md5(url))
                    parms['collect_times'] = 0
                    if _uid:
                        parms['collect_times'] = self.factory.select_collect_times_num(_uid)  # 在书签文件夹中出现的次数

                    #print(url, parms)
                    yield scrapy.Request(
                        url,
                        # dont_filter=True,
                        meta={
                            "parms": parms,
                            "depth": 1,
                        },
                        callback=self.parse,
                        errback=self.errback
                    )


    def errback(self, err):

        # copy, 防止再次请求没法释放内存
        url = copy.deepcopy(err.request.url)

        error= {
            'url': url,
            'status': 'error_downloading_http_response',
            'message': str(err.value),
        }

        # copy, 防止再次请求没法释放内存
        meta = copy.deepcopy(err.request.meta)

        pro=meta.get('pro')
        if pro and "01" in pro and "timeout" in str(err.value):
            url=url.replace("http:","https:")
            parms = meta.get('parms')
            parms['scheme']="https"
            #print((url, parms))
            self.request_queue.put((url, parms))  ##加入队列

        return error
