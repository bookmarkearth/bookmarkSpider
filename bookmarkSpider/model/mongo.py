# coding=utf-8
'''
Created on 2018-3-27

@author: www.bookmarkearth.com
'''

# 导入seetings配置
import pymongo
from bson import ObjectId
from scrapy.utils.project import get_project_settings

class MongoHelper():

    def __init__(self):

        settings = get_project_settings()  # 获取settings配置，设置需要的信息
        #print(settings['MONGODB_HOST'],settings['MONGODB_PORT'],settings['MONGODB_USERNAME'],settings['MONGODB_PASSWORD'],settings['MONGODB_SOURCE'])
        self.client = pymongo.MongoClient(
            host=settings['MONGODB_HOST'],
            port=settings['MONGODB_PORT'],
            username=settings['MONGODB_USERNAME'],
            password=settings['MONGODB_PASSWORD'],
            authSource=settings['MONGODB_SOURCE']
        )
        self.db = self.client[settings['MONGODB_DBNAME']]  # 获得数据库的句柄

        ##page table##
        self.page = self.db[settings['MONGO_TABLE_PAGE']]
        indexs = self.page.index_information()
        if "id_1" not in indexs:
            self.page.create_index([('id', pymongo.ASCENDING)],unique=True)
        if "bookmark_id_1" not in indexs:
            self.page.create_index([('bookmark_id', pymongo.ASCENDING)])
        if "folder_id_1" not in indexs:
            self.page.create_index([('folder_id', pymongo.ASCENDING)])
        if "uid_1" not in indexs:
            self.page.create_index([('uid', pymongo.ASCENDING)])
        if "collect_times_1" not in indexs:
            self.page.create_index([('collect_times', pymongo.ASCENDING)])
        if "has_index_1" not in indexs:
            self.page.create_index([('has_index', pymongo.ASCENDING)])
        if "white_1" not in indexs:
            self.page.create_index([('white', pymongo.ASCENDING)])
        if "domain_1" not in indexs:
            self.page.create_index([('domain', pymongo.ASCENDING)])


        ##host table##
        self.host = self.db[settings['MONGO_TABLE_HOST']]
        indexs = self.host.index_information()
        if "host_md5_1" not in indexs:
            self.host.create_index([('host_md5', pymongo.ASCENDING)], unique=True)

        ##last record table##
        self.last_record = self.db[settings['MONGO_TABLE_LAST_RECORD']]
        indexs = self.last_record.index_information()
        if "today_md5_1" not in indexs:
            self.last_record.create_index([('today_md5', pymongo.ASCENDING)], unique=True)

        ##url cache table##
        self.url_cache = self.db[settings['MONGO_TABLE_URL_CACHE']]

        ##referer table###
        self.referer = self.db[settings['MONGO_TABLE_REFERER']]
        indexs = self.referer.index_information()
        if "id_1_referer_md5_1" not in indexs:
            self.referer.create_index([('id',pymongo.ASCENDING),('referer_md5', pymongo.ASCENDING)],unique=True)
        if "id_1" not in indexs:
            self.referer.create_index([('id',pymongo.ASCENDING)])

        ##count_record##
        self.count_record = self.db[settings['MONGO_TABLE_COUNT_RECORD']]

    # 插入数据
    def insert_one(self, data,handler):
        handler.insert_one(data)

    def upsert(self,data,handler,key):
        handler.replace_one({key: data[key]}, data, upsert=True)

    def upsert_bind(self,data,handler,key1,key2):
        handler.replace_one({key1: data[key1],key2:data[key2]}, data, upsert=True)

    def count(self,condition,handler):
        count=handler.count_documents(condition)
        return count

    def query_limit(self,handler,num):
        for data in handler.find().limit(num):
            yield data

    def query_by_page(self,condition,data,handler,start,num):
        return handler.find(condition,data).skip(start).limit(num)

    def delete_one(self,handler,id):
        handler.delete_one({'_id': ObjectId(id)})

    def delete_batch(self,handler,ids):
        handler.delete_many({'_id': { '$in': ids}})

    def update_batch(self,handler,ids,data):
        handler.update_many({'_id': { '$in': ids}},{"$set": data})

    def query_by_key(self,data,handler,key):
        return handler.find_one({key: data[key]})

    def find_value(self,data,handler,key,field):
        result = handler.find_one({key: data[key]},{'_id':0,field:1})
        return result

'''测试'''
class TestMongoHelper():
   pass