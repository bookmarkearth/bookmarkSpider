import os
from datetime import datetime

BOT_NAME = 'bookmarkSpider'

#任务列表
#JOB_DIR='e:/job/bookmark'

SPIDER_MODULES = ['bookmarkSpider.spiders']
NEWSPIDER_MODULE = 'bookmarkSpider.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

##线程
PRODUCER_THREAD=6
CONSUMER_THREAD=12

# 允许重定向
MEDIA_ALLOW_REDIRECTS =False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 128

#the max size for the reactor thread pool of the spider. Its default size is 10.
CONCURRENT_REQUESTS_PER_DOMAIN = 128

##同时处理的item数量
CONCURRENT_ITEMS=64

#增大dns线程池
REACTOR_THREADPOOL_MAXSIZE = 64

# DNS in-memory cache
DNSCACHE_SIZE=30000

##DNS##超时时间
DNS_TIMEOUT=20

#CONCURRENT_REQUESTS_PER_IP = 256

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

##禁止重试
RETRY_ENABLED = False

##重定向
REDIRECT_ENABLED=False
REDIRECT_MAX_TIMES=0

##允许处理301
#HTTPERROR_ALLOWED_CODES = [301]

##减小下载超时
DOWNLOAD_TIMEOUT=3

##下载延时##
DOWNLOAD_DELAY = 2

AJAXCRAWL_ENABLED = True

###############log#############
# 目录
LOG_DIR='e:/log/bookmark/'
# 级别
_LEVEL = 'DEBUG'
#LOG_LEVEL = 'WARNING'
LOG_LEVEL = 'INFO'

today = datetime.now()
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

LOG_FILE = LOG_DIR+"scrapy_{}_{}_{}.log".format(today.year, today.month, today.day)
############log end#################

##优先队列
SCHEDULER_PRIORITY_QUEUE = 'scrapy.pqueues.DownloaderAwarePriorityQueue'

# ##最大深度
DEPTH_LIMIT = 1
##优先级为正数时，随着深度越大，优先级越低
DEPTH_PRIORITY = 1
SCHEDULER_DISK_QUEUE = 'scrapy.squeues.PickleFifoDiskQueue'
SCHEDULER_MEMORY_QUEUE = 'scrapy.squeues.FifoMemoryQueue'

##dupefilter
DUPEFILTER_CLASS = 'bookmarkSpider.service.dupe_filter.RedisDupeFilter'

ITEM_PIPELINES = {
     'bookmarkSpider.pipelines.CompleteItemPipeline': 10,
     'bookmarkSpider.pipelines.FilterWordsPipeline': 20,
     #'bookmarkSpider.pipelines.ElasticsearchPipeline':30,
     'bookmarkSpider.pipelines.MogoPipeline':40,
}

#内存debug
MEMDEBUG_ENABLED=True

#邮件通知
MEMDEBUG_NOTIFY = ['yours@163.com']

#限制内存使用512M最大
MEMUSAGE_LIMIT_MB = 512

DOWNLOADER_MIDDLEWARES = {
   'bookmarkSpider.middlewares.FilterResponses': 20,
   'bookmarkSpider.middlewares.MyUserAgentMiddleware': 10,
   'bookmarkSpider.middlewares.FilterRequest': 1,
   #'bookmarkSpider.middlewares.BookmarkspiderDownloaderMiddleware': 100,
}

USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
MY_USER_AGENT = [
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
    "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
    "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
    "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
    "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
    "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/2.0 Safari/536.11",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; LBBROWSER)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E; LBBROWSER)",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 LBBROWSER",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; QQBrowser/7.0.3698.400)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SV1; QQDownload 732; .NET4.0C; .NET4.0E; 360SE)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1",
    "Mozilla/5.0 (iPad; U; CPU OS 4_2_1 like Mac OS X; zh-cn) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8C148 Safari/6533.18.5",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b13pre) Gecko/20110307 Firefox/4.0b13pre",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:16.0) Gecko/20100101 Firefox/16.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
    "Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
]

#Mysql数据库的配置信息
MYSQL_HOST = '127.0.0.1'
MYSQL_DBNAME = 'bookmarkchina'         #数据库名字，请修改
MYSQL_USER = 'root'             #数据库账号，请修改
MYSQL_PASSWD = 'root'         #数据库密码，请修改
MYSQL_PORT = 3306               #数据库端口，在dbhelper中使用

#ELASTICSEARCH配置信息
#http://username:password@elasticsearch.com
ELASTICSEARCH_HOSTS = ['http://101.37.160.126:9200']
ELASTICSEARCH_INDEX = 'bookmarkearth_index'
NUMBER_OF_SHARDS = 1

##mongo
MONGODB_HOST = "127.0.0.1"
MONGODB_PORT = 27017
MONGODB_USERNAME = 'root'
MONGODB_PASSWORD='root'
MONGODB_SOURCE="admin"
MONGODB_DBNAME = "bookmarkearth"

##table
MONGO_TABLE_PAGE="page"
MONGO_TABLE_HOST="host"
MONGO_TABLE_LAST_RECORD="last_record"
MONGO_TABLE_URL_CACHE="url_cache"
MONGO_TABLE_REFERER="referer"
MONGO_TABLE_COUNT_RECORD="count_record"

##redis
REDIS_SERVER_HOST="127.0.0.1"
REDIS_SERVER_PORT=6379
REDIS_SERVER_PASSWORD="123456"
