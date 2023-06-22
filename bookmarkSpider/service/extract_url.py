# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


from bookmarkSpider.model.mysql import MysqlHelper

class SqlFactory():

    def __init__(self):
        self.dbHelper = MysqlHelper()
        self.conn = None
        self.curr = None
        self.connect_db()

    def connect_db(self):
        self.conn = self.dbHelper.connectDatabase()
        self.curr = self.conn.cursor()

    def close_db(self):
        self.conn.close()

    def active_database(self):
        self.dbHelper.live_db(self.curr)  # 激活数据库，所以用了for循环


    def get_page_data(self, start, limit):
        sql = 'select * from `bookmarks_entity` limit ' + str(start) + ',' + str(limit)
        self.dbHelper.select(sql, self.curr)
        results = self.curr.fetchall()
        return results

    def get_total_num(self):
        total = 0
        sql = 'select count(*) from `bookmarks_entity`'
        self.dbHelper.select(sql, self.curr)
        results = self.curr.fetchall()
        for r in results:
            total = r[0]
        return total

    ##解析所有书签
    def select_all_bookmark(self):
        start=0
        limit=30
        total = self.get_total_num()
        while start<=total:
            results=self.get_page_data(start,limit)
            for r in results:
                yield r
            start=start+limit

    def select_all_dirty(self):
        list=[]
        sql = 'select name from `forbidden_words`'
        self.dbHelper.select(sql, self.curr)
        results = self.curr.fetchall()
        for r in results:
            list.append(r[0])
        return list

    ##查找最大id
    def select_max_bookmark_id(self):
        max_id=0
        sql = 'select max(id) from bookmarks_entity'
        self.dbHelper.select(sql, self.curr)
        results = self.curr.fetchall()
        for r in results:
            max_id = r[0]
        return max_id

    # 读取书签的搜索文件夹
    def select_all_folder(self,bookmarkId):
        sql = 'select bf.* from bookmark_folder bf where bf.bookmark_id=' + str(bookmarkId)
        self.dbHelper.select(sql, self.curr)
        results = self.curr.fetchall()
        return results

    ##读取文件夹
    def select_folder_content(self,folderId):

        sql = 'select u.id,u.name,u.url from folder_content fc left join urls u on u.id=fc.url_id where fc.folder_id=' + str(folderId)
        self.dbHelper.select(sql, self.curr)
        results = self.curr.fetchall()
        return results

    ##读取文件夹
    def select_collect_times_num(self,uid):
        total = 0
        sql = 'select count(*) from folder_content where url_id='+str(uid)
        self.dbHelper.select(sql, self.curr)
        results = self.curr.fetchall()
        for r in results:
            total = r[0]
        return total

    def select_uid_by_urlmd5(self,urlmd5):
        sql = "select id from urls where url_md5='"+urlmd5+"'"
        self.dbHelper.select(sql, self.curr)
        results = self.curr.fetchall()
        for r in results:
            return r[0]
        return None

    def live_db(self):
        self.curr.execute('select id from `bookmark_folder` limit 1')






