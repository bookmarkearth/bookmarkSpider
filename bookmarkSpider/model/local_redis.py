# coding=utf-8
'''
Created on 2022-3-27

@author: www.bookmarkearth.com
'''

import redis
from scrapy.utils.project import get_project_settings

class RedisHelper():

    def __init__(self):

        settings = get_project_settings()  # 获取settings配置，设置需要的信息
        self.server = redis.Redis(
            host=settings['REDIS_SERVER_HOST'],
            port=settings['REDIS_SERVER_PORT'],
            password=settings['REDIS_SERVER_PASSWORD']
        )

    # 插入数据
    def sadd(self,key,value):
        return self.server.sadd(key,value)

    def smembers(self,key):
        return self.server.smembers(key)

    def dels(self,name):
        self.server.delete(name)

    def set(self,key,value):
        self.server.set(key,value)

    def get(self,key):
        return self.server.get(key)

    def lrange(self,key,start,end):
        return self.server.lrange(key,start,end)

    def lpush(self,key,value):
        self.server.lpush(key,value)

'''测试'''
class TestMongoHelper():
   pass
   #helper = RedisHelper()
   #helper.sadd("test","我是你妈")