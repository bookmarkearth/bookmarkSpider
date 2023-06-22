#coding=utf-8
'''
Created on 2022-3-27

@author: www.bookmarkearth.com
'''

import MySQLdb
from scrapy.utils.project import get_project_settings #导入seetings配置

class MysqlHelper():
    
    '''这个类也是读取settings中的配置，自行修改代码进行操作'''
    def __init__(self):
        self.settings=get_project_settings() #获取settings配置，设置需要的信息
        
        self.host=self.settings['MYSQL_HOST']
        self.port=self.settings['MYSQL_PORT']
        self.user=self.settings['MYSQL_USER']
        self.passwd=self.settings['MYSQL_PASSWD']
        self.db=self.settings['MYSQL_DBNAME']
    
    #连接到具体的数据库（settings中设置的MYSQL_DBNAME）
    def connectDatabase(self):
        conn=MySQLdb.connect(host=self.host, port=self.port, user=self.user, passwd=self.passwd,db=self.db,  charset='utf8') #要指定编码，否则中文可能乱码
        return conn   
    
    #创建数据库
    def createDatabase(self,cur):
        sql="create database if not exists "+self.db
        cur.execute(sql)#执行sql语句
    
    #创建表
    def createTable(self,sql,cur):
        cur.execute(sql)
        
    #插入数据
    def insert(self,sql,cur,*params):#注意这里params要加*,因为传递过来的是元组，*表示参数个数不定
        cur.execute(sql,params)
        
    def select(self,sql,cur):
        cur.execute(sql) 

    #更新数据
    def update(self,sql,cur,*params):
        cur.execute(sql,params)
        
    def commit(self,conn):
        conn.commit()#注意要commit
        
    def close(self,conn):
        conn.close()
    
    #删除数据
    def delete(self,sql,cur,*params):
        cur.execute(sql,params)
        
    def live_db(self,cur):
        cur.execute('select * from `crawl_classify` limit 1')
        
'''测试DBHelper的类'''
class TestDBHelper():
    def __init__(self):
        self.dbHelper=MysqlHelper()
        self.conn=self.dbHelper.connectDatabase()
        self.curr=self.conn.cursor()

    #测试创建数据库（settings配置文件中的MYSQL_DBNAME,直接修改settings配置文件即可）
    def testCreateDatebase(self):
        self.dbHelper.createDatabase(self.curr) 
        self.dbHelper.commit(self.conn)
        
    #测试创建表
    def testCreateTable(self):
        sql="create table testtable(id int primary key auto_increment,name varchar(50),url varchar(200))"
        self.dbHelper.createTable(sql,self.curr)
        self.dbHelper.commit(self.conn)
        
    #测试插入
    def testInsert(self):
        sql="insert into testtable(name,url) values(%s,%s)"
        params=("test","test")
        self.dbHelper.insert(sql,self.curr,*params) #  *表示拆分元组，调用insert（*params）会重组成元组
        self.dbHelper.commit(self.conn)
        
    def testUpdate(self):
        sql="update testtable set name=%s,url=%s where id=%s"
        params=("update","update","1")
        self.dbHelper.update(sql,self.curr,*params)
        self.dbHelper.commit(self.conn)
    
    def testDelete(self):
        sql="delete from testtable where id=%s"
        params=("1")
        self.dbHelper.delete(sql,self.curr,*params)
        self.dbHelper.commit(self.conn)
    
if __name__=="__main__":
    testDBHelper=TestDBHelper()
    #testDBHelper.testCreateDatebase()  #执行测试创建数据库
    testDBHelper.testCreateTable()     #执行测试创建表
    #testDBHelper.testInsert()          #执行测试插入数据
    #testDBHelper.testUpdate()          #执行测试更新数据
    #testDBHelper.testDelete()          #执行测试删除数据