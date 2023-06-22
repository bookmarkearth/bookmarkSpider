import zlib

import requests
from lxml import html
from scrapy.http import HtmlResponse
from scrapy.spiders import CrawlSpider
from scrapy.linkextractors import LinkExtractor
from scrapy.utils.project import get_project_settings

from bookmarkSpider.constant.constant import tag_list, property_list, domain_postfix
from bookmarkSpider.util.common import get_md5, get_rid_of_feed, get_unix_time
from bookmarkSpider.items import Page
from protego import Protego

class Parser(CrawlSpider):

    def __init__(self, *args, **kwarg):
       #print(super(Parser, self).parse())
       self.official_list=domain_postfix.split("|")
       self.icp=['ICP','公网安备','Copyright','经营许可证','公安','备案']
       self.settings = get_project_settings()  # 获取settings配置，设置需要的信息
       self.robotstxt_obey = self.settings.get('ROBOTSTXT_OBEY')
       self.download_timeout = self.settings.get('DOWNLOAD_TIMEOUT')
       self.link_extractor = LinkExtractor()

    def url_robot_judge(self, parms,url):

        if self.robotstxt_obey:
            return 1

        robotstxt=self.alalysis_robots(parms)
        try:
            r = requests.get(robotstxt,timeout=self.download_timeout)  # 获得robot文件
            rp = Protego.parse(r.text)
            yes=rp.can_fetch(url, "mybot")
            #print("url is %s, robotstxt is %s, result is %s" %(url,robotstxt,yes))
            if not yes:
                return 0
        except Exception as e:
            print ("Parse robots.txt error %s" %(e))
        return 1

    def alalysis_robots(self,parms):

        host = parms['domain'] + "." + parms['suffix']
        subdomain=parms['subdomain']
        if subdomain:
            subdomain=subdomain+"."

        robotstxt = parms['scheme'] + "://" + subdomain + host + "/robots.txt"
        return robotstxt

    def _get_item(self, response):

        parms=response.meta.get("parms")
        bookmarkId=parms['bookmark_id']
        folderId = parms['folder_id']
        folderIn=parms['collect_times']
        uid=parms['uid']
        host = parms['host']
        url=response.url
        domain=parms['domain'] + "." + parms['suffix']
        #print(domain)

        #协议
        protocol='http'
        if url.startswith('https'):
            protocol = 'https'

        url=url.replace(protocol+"://","")
        id=get_md5(url) #md5值唯一标识

        item = Page(
            url=url,
            id=id, #唯一主键
            host=host,
            host_md5=get_md5(host),
            size=len(response.body),
            bookmark_id=bookmarkId,
            folder_id=folderId,
            collect_times=folderIn,
            uid=uid,
            depth=response.meta.get('depth'),
            robots=self.url_robot_judge(parms,url),
            update_at=get_unix_time(),
            create_at = get_unix_time(),
            protocol=protocol,
            delete_at=0,
            domain=domain
        )

        #referer
        item["referer"]=None
        item["referer_md5"]=None

        referer=response.request.headers.get('Referer')
        if referer:
            referer=referer.decode()
            item["referer"] = referer
            item["referer_md5"]=get_md5(referer.replace("https://","").replace("http://","")) #去除协议头的md5值

            #print(item["referer"], item["referer_md5"])

        item['has_index']=0
        item['white']=0

        self._set_title(item, response)
        #self._set_new_cookies(item, response)
        self._set_body(item,response)
        self._set_keywords(item, response)
        self._set_description(item, response)
        self._set_official(item,response,host)

        #print(item)
        return item

    def _set_official(self,page,response,host):

        page['official']=0
        url=response.url
        url=url.replace("https://","").replace("http://","").rstrip('/')

        for x in self.official_list:
            if x in url and ("www."+str(host).strip() == url or host.strip() == url):
                page['official']=1
                for y in self.icp:
                    if y in str(page['body']):
                        page['official']=2

    def _set_title(self, page, response):

        page['title']=None
        title = response.xpath("//title/text()").extract()
        if title:
            page['title'] = get_rid_of_feed(title[0].strip())

    def _set_keywords(self, page, response):

        page['keywords'] = []

        keywords = response.xpath('//meta[contains(@name,"keywords")]/@content').extract()
        if keywords:
            list=[]
            for keyword in keywords:
                if keyword.strip():
                    list.append(get_rid_of_feed(keyword.strip()))

            if list:
                page['keywords'] = list

    def _set_description(self, page, response):

        page['description'] = []

        keywords = response.xpath('//meta[contains(@name,"description")]/@content').extract()
        if keywords:
            list = []
            for keyword in keywords:
                if keyword.strip():
                    list.append(get_rid_of_feed(keyword.strip()))
            if list:
                page['description'] = list

    def _set_body(self, page, response):

        page['body']={}
        final_dict={}
        for mark in tag_list:

            mark_path = "//" + mark['t']
            tags = response.xpath(mark_path).extract()

            list_container = []
            for tag in tags:

                tag=html.fromstring(tag)#convert
                item={} #提取不同的标签

                for pr in property_list:

                    pt=pr['t']
                    ele=pt
                    if "text" not in pt:
                        pt="//@"+pt #解析属性
                    else:
                        pt="//"+pt+"()"

                    values=tag.xpath(pt)
                    if values:
                        hit=values[0].strip()
                        hit=get_rid_of_feed(hit)
                        if hit:
                            ##减少消耗，尽量短###
                            if ele=='title':
                                ele='tt'
                            else:
                                ele=ele[0:1]
                            item[ele] =hit

                if item and item not in list_container:
                    list_container.append(item)

            if list_container:
                final_dict[mark['t']] = list_container

        if final_dict:
            page['body']=final_dict


    def _extract_requests(self, response):
        links=[]
        if isinstance(response, HtmlResponse):
            links = self.link_extractor.extract_links(response)
        return links

    def _set_new_cookies(self, page, response):

        page['newcookies'] = []
        cookies = []

        for cookie in [x.split(b';', 1)[0] for x in
                       response.headers.getlist('Set-Cookie')]:
            if cookie not in self.cookies_seen:
                self.cookies_seen.add(cookie)
                cookies.append(cookie)
        if cookies:
            page['newcookies'] = cookies

