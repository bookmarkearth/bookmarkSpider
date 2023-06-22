
from w3lib.url import url_query_cleaner
from scrapy.utils.request import request_fingerprint

import scrapy.dupefilters
from bookmarkSpider.model.local_redis import RedisHelper

class RedisDupeFilter(scrapy.dupefilters.BaseDupeFilter):

    def __init__(self):
        self.helper = RedisHelper()

    def my_request_fingerprint(self, request):
        url=url_query_cleaner(request.url,["spm"],remove=True)
        new_request = request.replace(url=url)
        r=request_fingerprint(new_request)
        return r

    def request_seen(self, request):
        added = self.helper.sadd("url_seen",self.my_request_fingerprint(request))
        return added == 0