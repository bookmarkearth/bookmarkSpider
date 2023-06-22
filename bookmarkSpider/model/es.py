
from elasticsearch_dsl import Document, Date, Nested,InnerDoc,Keyword, Text,Long
from scrapy.utils.project import get_project_settings  # 导入seetings配置
from elasticsearch_dsl import connections

##读取配置文件
settings = get_project_settings()  # 获取settings配置，设置需要的信息
index = settings['ELASTICSEARCH_INDEX']
shards = settings['NUMBER_OF_SHARDS']
hosts = settings['ELASTICSEARCH_HOSTS']
client=connections.create_connection(hosts=hosts, timeout=60)

class Tag(InnerDoc):

    name = Keyword()
    content = Text()

#elasticsearch table create
class Searchtemplate(Document):

    id = Keyword()

    title = Text(analyzer='snowball', fields={'raw': Keyword()}) #raw 前缀
    keywords= Text(analyzer='snowball') #关键词，先分词后索引
    description = Text(analyzer='snowball') #描述

    body = Nested(Tag) #重要内容，进行存储

    url = Keyword()#链接
    size = Long()#大小
    host=Keyword() #域名
    bookmark_id=Long() #书签id
    folder_id=Long() #folder id
    referer = Keyword() #来源

    create_at = Long() #创建时间,Long 形式存储
    update_at= Long() #更新时间，Long 形式存储

    #index
    class Index:
        name = index
        settings = {
            "number_of_shards": shards,
            'refresh_interval': "30s",
        }

    def add_body(self, name, content):
        self.body.append(Tag(name=name, content=content))

if __name__ == "__main__":
    Searchtemplate.init()
