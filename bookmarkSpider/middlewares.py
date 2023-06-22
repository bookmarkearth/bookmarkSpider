from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
import random

from scrapy.utils import log
from scrapy.utils.misc import arg_to_iter
from scrapy.utils.url import url_has_any_extension
from scrapy.exceptions import IgnoreRequest
import re

# useful for handling different item types with a single interface
from util.common import get_ignore_extensitons
class MyUserAgentMiddleware(UserAgentMiddleware):

    '''
    设置User-Agent
    '''

    def __init__(self, user_agent):
        self.user_agent = user_agent

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            user_agent=crawler.settings.get('MY_USER_AGENT')
        )

    def process_request(self, request, spider):
        agent = random.choice(self.user_agent)
        request.headers['User-Agent'] = agent

class FilterRequest(object):

    def __init__(self):
        self.deny_extensions = {'.' + e for e in arg_to_iter(get_ignore_extensitons())}

    def process_request(self, request, spider):

        url = request.url
        if url_has_any_extension(url,self.deny_extensions):
            print("%s extensions is not right" % (url))
            raise IgnoreRequest()

class FilterResponses(object):

    """Limit the HTTP response types that Scrapy dowloads."""
    def is_valid_response(self,type_whitelist, content_type_header):
        for type_regex in type_whitelist:
            if re.search(type_regex, content_type_header.decode()):
                return True
        return False

    def process_response(self, request, response, spider):
        """
        Only allow HTTP response types that that match the given list of
        filtering regexs
        """
        # to specify on a per-spider basis
        # type_whitelist = getattr(spider, "response_type_whitelist", None)
        type_whitelist = (r'text', )
        content_type_header = response.headers.get('content-type', None)
        if not content_type_header or not type_whitelist:
            return response

        if self.is_valid_response(type_whitelist, content_type_header):
            return response
        else:
            msg = "Ignoring request {}, content-type was not in whitelist".format(response.url)
            log.msg(msg, level=log.INFO)
            raise IgnoreRequest()