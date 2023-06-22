# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class Page(Item):

    ##主键，唯一的
    id = Field()

    ##书签信息
    bookmark_id=Field()
    folder_id=Field()

    ##基本信息
    cookie=Field()
    depth = Field() #深度

    ##统计信息
    referer = Field() #来源url
    referer_md5=Field() #来源url的md5
    referer_no=Field() #来源次数
    linked_num=Field() #这个页面被指向的次数

    #协议
    protocol=Field() #https 或者 http
    url = Field()#链接
    host=Field()
    host_md5=Field()#group
    title = Field()
    size = Field()
    keywords= Field() #关键词
    description = Field() #描述

    ##body
    body = Field()

    ##统计
    collect_times=Field() #在书签文件夹中出现次数
    uid=Field() #来自哪个链接

    ##是否索引
    has_index=Field()
    white=Field() #0为干净 1为存在违规，-1为删除
    robots=Field() #0不遵守，1遵守
    official=Field() #0不是网 1疑似，2大概率是
    domain=Field()

    ##时间
    create_at=Field()
    update_at=Field()
    delete_at=Field() #删除时间

    def __repr__(self):
         """only print out attr1 after exiting the Pipeline"""
         return repr({"bookmark_id":self['bookmark_id'],"title": self['title'],"url":self['url'],"uid":self['uid']})



