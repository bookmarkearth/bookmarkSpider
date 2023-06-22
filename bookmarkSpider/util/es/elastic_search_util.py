#coding=utf-8
'''
Created on 2022-3-27

@author: www.bookmarkearth.com
'''
from elasticsearch import helpers


class ElasticSearchUtil:

    @classmethod
    def InsertDocument(cls, using, index, body, id=None):
        '''
        插入一条数据body到指定的index，可指定Id,若不指定,会自动生成
        '''
        return using.index(index=index, body=body, id=id)

    @classmethod
    def bulkUpdate(cls, using, index, body):
        '''
        批量插入更新指定index、id对应的数据
        '''
        action = [{"_op_type": "update",
                   "_index": index,
                   "_type": "_doc",
                   "_id": str(i.get("keyword_id")) + str(i.get("de")),
                   "doc": i,
                   "doc_as_upsert": True} for i in body]
        return helpers.bulk(using, action, index=index)

    @classmethod
    def deleteDocByQuery(cls, using, index, query):
        '''
        删除idnex下符合条件query的所有数据
        :return:
        '''
        return using.delete_by_query(index=index, body=query, conflicts="proceed", request_timeout=100)

    @classmethod
    def deleteDocByDeCount(cls, using, index, keyword_id, de_count):
        '''
        删除idnex下符合条件query的所有数据
        :return:
        '''
        query = {
            "query": {
                "bool": {
                    "filter": [{
                        "term": {"keyword_id": keyword_id},
                    },
                        {"range": {
                            "de": {"gte": de_count}
                        }
                        }
                    ]
                }
            }
        }

        return using.delete_by_query(index=index, body=query, conflicts="proceed", request_timeout=100)

    @classmethod
    def searchDoc(cls, using, index=None, query=None):
        '''
        查找index下所有符合条件的数据
        '''
        return using.search(index=index, body=query, request_timeout=300)

    @classmethod
    def getDocById(cls, using, index, id):
        '''
        获取指定index、id对应的数据
        '''
        return using.get(index=index, id=id)

    @classmethod
    def updateDocById(cls, using, index, id, body=None):
        '''
        更新id所对应的数据
        '''
        return using.update(index=index, id=id, body=body)

    @classmethod
    def updateDocByQuery(cls, using, index, query):
        '''
        批量更新 符合该条件的批量更改hint字段
        query：
        '''
        return using.update_by_query(index=index, body=query, request_timeout=60)

    @classmethod
    def insertBulk(cls, using, index, body=None):
        '''
        批量插入doc
        '''
        return using.bulk(index=index, body=body, request_timeout=60)