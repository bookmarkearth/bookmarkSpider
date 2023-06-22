import time

from numpy import long
from scrapy.exceptions import DropItem

##敏感词过滤
from scrapy.utils.project import get_project_settings

from model.mongo import MongoHelper
from service.algorithm.simhash_algorithms import SimhashAlgorithmService
from service.extract_url import SqlFactory
from util.common import body2str, list2str
from constant.constant import property_list, tag_list
from model.es import Searchtemplate, client, Tag
from util.convert import chs_to_cht
from util.es.elastic_search_util import ElasticSearchUtil

settings = get_project_settings()  # 获取settings配置，设置需要的信息
index = settings['ELASTICSEARCH_INDEX']
init_es=False

class CompleteItemPipeline(object):

    def process_item(self, item, spider):
        if 'body' not in item.keys() or 'title' not in item.keys():
            raise DropItem("Illegal item %s" % item)
        else:
            return item

class FilterWordsPipeline(object):

    def __init__(self):

        self.special_words = ['av', 'sm','发展','方法','流出','华人','地点','乐趣','杏','69','91','qq群','gv','理想','气氛','进入']
        self.dirty_words = "嫂子|QQ群|微信群|伦理|母牛|sev|帅同|美足|虎逼|淫奸|男体|男色|真炮|淫妹妹|性之助|伪娘|变性|狼盟 |屁屁|女優|素人|小澤|幼齒|手淫|性虎|蒼井空|1024|淫荡|1000giri|水蜜桃妹妹|房中术|淫幕|蝌蚪|羞涩|1030社區|艳居|性福|G点|虐爱|性奴|凤雅楼|蓝恋|女奴|SM|恋足|调教|母狗|欲望|阴茎|狼友|性吧|性论坛|Pussy|Cunt|Exempt|无遮|H剧|SILK LABO|铃木|网页发布|网址更新|淫語|凌辱|色中色|性交|彼女|情欲|最新网址|女优|情情爱爱|爱色|小姐|华人|Ｓ７Ｃ８．ＣＯＭ|A漫|禁漫|大尺度|虐待|2048|萝莉|草榴|H漫|gv|美腿|金瓶梅|轮理|色站|胴体|暴力|黄书|Gay|上车|Sex|boy|suck|搜同|断茎|Twink|最新地址|xHamster|東京熱|脱裤|番号|Yellow|撸|XNXX|桃花|杏|露出|成人|女郎|老司机|会所|傻逼|会所|美腿|丝袜|熟女|人体|艳照门|porn|H漫|奸淫|無碼|狼桥梦遗|嫂子|无码|撸|淫奸|泷泽萝|推川悠里|爱爱|三级|快播|福利片|情色|同志|援交|干炮|约炮|拔插|同人|AV成人|A片|成人影片|vpn|找小姐|ladyboy|一夜情|成人|AV社区|偷窥|街拍|性癖|操逼|宅男|男人网站|榴图床|爆乳|激情小说|成人论坛|成人漫畫|成人影片|成人电影|性爱|色情|看av|恋臀|福利漫画|福利导航|翻墙"

        # put all words in lowercase
        self.words_to_filter = self.dirty_words.split("|")
        self.factory = SqlFactory()
        #self.words_to_filter=self.words_to_filter+self.factory.select_all_dirty()
        self.filter = SimhashAlgorithmService()
        #self.mongoHelper = MongoHelper()

        for word in self.words_to_filter:
            for s in self.special_words:
                if s==word.lower():
                    self.words_to_filter.remove(word)

        #print(self.words_to_filter)
        '''
            d=""
            for x in self.words_to_filter:
               if x not in d and len(x)>1:
                    d=d+x+"|"
            print(d)
        '''

    def process_item(self, item, spider):

        if not item:
            raise DropItem("Empty result: %s" % item)

        tstr = ""
        bstr = ""
        if item['title']:
            tstr=str(item['title'])
            bstr += tstr
        bstr = bstr + list2str(item['keywords']) + list2str(item['description']) + body2str(item['body'])

        if "Permanently" in tstr or "301 Moved" in tstr:
            raise DropItem("Useless website: 301 Moved Permanently")

        max=4 #脏词出现了5个以上，则违规
        container=set()
        for word in self.words_to_filter:
            if word in bstr \
            or  word.lower() in bstr \
            or chs_to_cht(word) in bstr:
                container.add(word.lower())
                if len(container) >= max:
                    item['white'] = 1 #标志内容存在违规

                    ##数据##
                    #ss="("
                    #for s in list(container):
                    #    ss+=s+","
                    #ss+=")"
                    #print(ss)
                    #self.mongoHelper.insert_one({'ss': ss}, self.mongoHelper.count_record)

                    raise DropItem("Illegal website found") #直接丢弃，这样减少硬盘消耗
                    break

        ##开始重复内容过滤###
        if self.filter.analysis_item(bstr):
            raise DropItem("Content duplicates")  #repeat

        return item

##ES pipeLine
class ElasticsearchPipeline(object):
    # 将数据写入到ES中

    def process_item(self,item,spider):

        if not item:
            raise DropItem("Empty result: %s" % item)

        # 将item转换为ES的数据
        template = Searchtemplate()
        id=item['id']

        template.id=id #主键
        template.title=item['title']
        template.keywords="".join(item['keywords'])
        template.description="".join(item['description'])
        template.url=item['url']
        template.size=long(item['size'])
        template.host=item['host']
        template.bookmark_id=long(item['bookmark_id'])
        template.folder_id=long(item['folder_id'])
        template.referer=item['referer']
        template.create_at=long(int(round(time.time() * 1000)))
        template.update_at=long(int(round(time.time() * 1000)))
        template.meta.id=id

        #处理body
        body_dict=self._get_body(template,item['body'])
        for k in body_dict.keys():
            template.add_body(name=k,content=body_dict[k])

        #print (template.body)

        body = {'doc': template, 'doc_as_upsert': True}
        ElasticSearchUtil.updateDocById(using=client,index=index,id=id,body=body)

        return item

    def _get_body(self,template,body):

        # body 处理
        list=[]

        for k in body.keys():
            value = body[k]
            # print(k)
            filter = set()
            for v in value:
                # print(v)
                for pr in property_list:
                    if pr['t'] in v.keys():
                        hit = v[pr['t']]
                        filter.add(hit)

            content = ""
            #print(filter)
            for hit in filter:
                content = content + hit
            list.append(Tag(name=k,content=content))

        group_pre="group_"
        item = {}
        group_ids = set([i.get('w') for i in tag_list])
        for id in group_ids:
            item[group_pre+str(id)]=''

        for tag in list:
            if tag:
                for v in tag_list:
                    if tag.name==v['t']:
                        k=group_pre + str(v['w'])
                        if  k not in item.keys():
                            item[k] = tag.content
                        else:
                            item[k] = item[k]+tag.content
        #print(item)
        return item

class MogoPipeline(object):

        def __init__(self):
            self.mongoHelper=MongoHelper()

        def process_item(self, item, spider):

            if not item:
                raise DropItem("Empty result: %s" % item)

            ##存 host###
            host_info={}
            host_info['host']=item['host']
            host_info['host_md5']=item['host_md5']

            try:

                if self.mongoHelper.count({'host_md5':host_info['host_md5']},self.mongoHelper.host)==0:
                    self.mongoHelper.upsert(host_info, self.mongoHelper.host, 'host_md5')

                ##存储referer##
                if item['referer_md5']:
                    data={}
                    data['id']=item['id']
                    data['referer'] = item['referer']
                    data['referer_md5']=item['referer_md5']
                    self.mongoHelper.upsert_bind(data, self.mongoHelper.referer, 'id','referer_md5')

                ##统计某个页面被链接的次数
                item['linked_num'] = self.mongoHelper.count({'id': item['id']}, self.mongoHelper.referer)

                ##存 page###
                del item['host']
                del item['referer']
                del item['referer_md5']
                print((item['bookmark_id'],item['url'],item['title']))

                new_item=self.mongoHelper.find_value(item, self.mongoHelper.page, 'id','create_at')
                if new_item:
                    item['create_at'] =new_item['create_at'] #保留原来的时间
                    if item['white']==-1: #删除的不再更新
                        return

                self.mongoHelper.upsert(item,self.mongoHelper.page,'id')

            except Exception as e:
                print ("Insert mongo db error %s"%(e))
        
            return item