import time

from numpy import int64
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
        self.dirty_words = "嫂子|QQ群|电影完整版|最新电影|最新动漫|最新小说|热门影视|热门小说|流行电影|流行音乐|最新专辑|潮流音乐|微信群|赌博|8x|菠菜|博彩|64|1989|台北|六四|棋牌|赌注|真人|土改|土地革命|土地改革|伦理|母牛|sev|帅同|美足|粗大|好爽|猛烈|虎逼|淫奸|男体|男色|真炮|淫妹妹|国产|精品|性之助|藏姬|伪娘|变性|狼盟 |屁屁|女優|素人|小澤|幼齒|手淫|性虎|蒼井空|1024|淫荡|1000giri|水蜜桃妹妹|房中术|淫幕|蝌蚪|羞涩|1030社區|艳居|性福|G点|虐爱|性奴|凤雅楼|蓝恋|女奴|SM|恋足|调教|母狗|欲望|阴茎|狼友|性吧|性论坛|Pussy|Cunt|Exempt|无遮|H剧|SILK LABO|铃木|网页发布|网址更新|淫語|凌辱|色中色|性交|彼女|情欲|最新网址|女优|情情爱爱|爱色|小姐|华人|Ｓ７Ｃ８．ＣＯＭ|A漫|禁漫|大尺度|虐待|2048|萝莉|草榴|H漫|gv|美腿|金瓶梅|轮理|色站|胴体|暴力|黄书|Gay|上车|Sex|boy|suck|搜同|断茎|Twink|最新地址|xHamster|東京熱|脱裤|番号|Yellow|XNXX|桃花|露出|成人|女郎|老司机|会所|傻逼|丝袜|熟女|人体|艳照门|porn|奸淫|無碼|狼桥梦遗|无码|泷泽萝|推川悠里|三级|快播|福利片|情色|同志|援交|干炮|约炮|拔插|同人|AV成人|A片|成人影片|vpn|科学上网|ssr|自由门|Shadowsocks|Shadowsocks|V2Ray|VLESS|Clash|Trojan|加速器|梯子|无界下载|找小姐|ladyboy|一夜情|AV社区|偷窥|街拍|性癖|操逼|宅男|男人网站|榴图床|爆乳|激情小说|成人论坛|成人漫畫|成人电影|性爱|色情|看av|恋臀|福利漫画|福利导航|翻墙|3P|69|91|carib|sex|sm|SOD|tokyo|一本道|万艾可|上下蠕动|上压下顶|上床|上翘|不举|不孕|不孕症|不泄|不洁性交|不育|东京热|两情相悦|两腿|两腿之间|丽香|久久|乐趣|乱伦|乱射|乱揉|乱摸|乱淌|乱舔|乳房|乳房叶|乾妈|乾姊|亚洲|亚洲无码|亢奋|亢进|交媾|交缠|交而不泄|交配|人兽|人妖|人妻|人类乳突病|伏在|优香|会阴|会阴中心腱|会阴浅横肌|会阴浅隙|会阴深横肌|会阴深隙|会阴部肌肉群|伤精|伪装|低嚎|低潮期|体位|体内的阴茎|体壁|体毛|体液|体香|供精|侧臀|俏眼|俏脸|保精|保育细胞|俯弄|倒骑|假性湿疣|做爱|停经|偷欢|偷汉|偷香|催情|傲然挺立|允吸|充血|先射|先摸|先肾后心|免疫性不孕|全彩实录|共浴|内射|冒水|冲插|冷阴症|処女|出血|出血性膀胱炎|切除子宫|初血|刮官|刮宫|刺插|刺激|剃掉|前列腺增生|前庭大腺|前庭大腺炎|前庭球|前戏|副性腺炎|加藤鹰|勃发|勃起|勃起功能障碍ED|勇猛|包皮|包皮嵌顿|包皮炎|包皮环切手术|包皮环切术|包皮系带|包皮系带撕裂|包皮腔|包皮龟头炎|包茎|包覆|卧式|卧式性交|去吮|去操|去能因子|又咬又舔又吸|又肿又大|叉开|叉我|发丝|发情|发抖|发春|发泄|发浪|发涨|发热|发痒|发颤|发骚|发麻|取悦|变硬|变粗|变软|口交|口含|口唇|口活儿|口爆|叫声|叫床|右乳|右臀|合体|合拢|吉泽明步|同性恋|名器|吞食|吮了|吮吸|吮吻|吮咬|吮奶|吮着|吮舐|吮著|吸允|吸吻|吸咬|吸舔|吹弹欲破|吹萧|吻向|吻摸|吻遍|呻吟|命根子|唇片|唇瓣|唇缝|唇肉|唇舌|唇间|唤起|啃咬|啜吸|啜著|喷出|喷射|喷泄|喷涌|喷潮|噘起|圆粗|地点|坚实|坚挺|坚挺的东西|坚硬|垂软|堂嫂|塞入|塞进|增粗|壁肉|够骚|大奶|大抽|大桥未久|大波|天海翼|夫妻|失精|夹著|奇淫|奇痒|套上|套动|套弄|套紧|女上位|女上式|女人的BB|女前男后|女器|女女|女婿|女子性冷淡|女尻|女方跪臀位|女阴|奶子|奸尸|奸弄|奸我|奸插|奸虐|奸辱|她的波|她的花蕊|她的阴核|她的阴部|好性|如醉如痴|妇人|妇方|妈咪|妊娠|妊娠中断|妊娠期|妙目|妞媚|姦淫|娇吟|娇啼|娇声|娇娘|娇媚|娇嫩|娇容|娇小|娇弱|娇态|娇笑|娇艳|娇躯|娇软|婶婶|媚态|媚术|媚液|媚笑|媚艳|嫩娃|嫩白|嫩穴|嫩红|嫩腿|嫩臀|子孙袋子|子宫下段|子宫下段剖宫产|子宫体|子宫切除手术|子宫切除术|子宫后倾|子宫后屈位|子宫圆韧带|子宫峡部|子宫平滑肌|子宫恶性肉瘤|子宫畸形|子宫粘膜|子宫肌瘤|子宫脱垂|子宫腔|子宫腺|子宫角|孕卵|孕妇|孕激素|孕酮|实臀|宫内膜炎|宫内避孕器|宫口|宫外孕|宫旁组织|宫腔粘连|宫颈外口|宫颈息肉|宫颈扩张|宫颈炎|宫颈癌|宫颈管内膜刮取术|宫颈管型癌症|宫颈粘液|宫颈粘液观察法|宫颈糜烂|宫颈肿瘤|宫颈腺癌|宫颈锥切术|宫颈阴道段|宫颈鳞状上皮|密合|密处|密汁|密洞|密穴|密窥|射出|射向|射姐姐|射液|射精|将嘴套至|小乳|小便|小咀|小唇|小屁眼|小弟弟|小弟第|小核|小泽玛利亚|小洞|小穴|小缝|小舌|小逼|小鸡鸡|少妇|少婦|少精子症|尖挺|尖硬|尖锐湿疣|尻臀|尽根|尿后流白|尿味|尿囊膜|尿意|尿末滴白|尿毒|尿毒症|尿水|尿浊|尿液|尿生殖膈|尿生殖膈上盘膜|尿生殖隔|尿生膈下筋膜|尿痛|尿血|尿路感染|尿路结石|尿道上裂|尿道下裂|尿道外口|尿道外括约肌|尿道炎|尿道狭窄|尿道肉阜|尿道腺|尿道腺液|尿频|屁穴|屁道|屁门|屄缝|展露|嵌顿包茎|嵌顿性包茎|巧春|巴氏腺|師母|干过炮|并睾|幹了個|幼女|幼嫩|幼稚型子宫|幽户|幽洞|床事|床戏|应召|底裤|开苞|弄湿|弄破|弄穴|引诱|引逗|张开了嘴|张开双唇|张开红唇|弱入强出|弱精子症|强奸|强暴|强精|微隆|忍精|怒张|急喘|急性外阴炎|急性女阴溃疡|急性输卵管炎|急抽|性用品|性虐|恋人|恋母|恋童|想操|想舔|愈插愈快|慢性输卵管炎|我射了|我的乳头|我的花蕊|我的阴核|戳穴|戳穿|房事|房事昏厥症|房室伤|扁平湿疣|扒开|打炮|扭动|扭捏|扭腰|扭臀|把玩|抓弄|抓捏|抓揉|抚慰|抚捏|抚揉|抚摩|抚摸|抚模|抚爱|抚玩|抚着|抚著|抛浪|抠弄|抠挖|抠摸|抱坐|抱紧|抽出|抽动|抽弄|抽打|抽捣|抽插|抽搐|抽擦|抽缩|抽送|抽送着|拔出|拥吻|拨开|拨开阴毛|拨弄|指技|挑动|挑弄|挑逗|挖弄|挺实|挺立的性器|挺腰|挺起|挺进|捅了|捅进|捏弄|捏挤|捏捏|捏掐|捏揉|捏揪|捏摸|掀开|排入|排出|排卵|排卵日|排卵期|排射|排泄|排精|排过精|探入|接吻|控制射精|提前排卵|提枪|提睾筋膜|插入|插奶|插她|插弄|插死你|插爆|插穴|插进|插进插出|插送|握缩感|揩擦|搅弄|搔弄|搔痒|摧残|摸乳|摸他|摸向|摸弄|摸我|摸抠|摸捏|摸揉|摸摸|摸玩|摸着|摸鸡巴|撅着|撩乱|撩动|撩开|撩弄|撩拨|撩起|操屄|操我|操穴|放尿|敏感带|教兽|整根阴茎|断背|无毛|无睾症|无精子症|日韩|早泄|旺盛|昂奋|春宫|春心|春情|春洞|春药|晚期流产|暗红|暴胀|暴露|曲细精管|曲细精管发育不全|曼妙|替我|月经|月经周期|有舒有缓|服囊肉膜|木耳|杀精|李宗瑞|松岛枫|极品美女|林醉|柔唇|柔嫩|柔毛|柔滑|柔肌|柔腻|档部|梅毒疹|梅毒螺旋体|梦交|梦失精|梦泄精|植物性神经|椒乳|樱井莉亚|樱口|樱口之技|樱口之枝|樱唇|欢吟|欢悦|欢愉|欢爱|欧美|欲感|欲火|欲焰|武藤兰|毛囊|毛片|气氛|汩汩|沟缝|油黑|治荡|泡彦|泡疹性外阴炎|波多野结衣|洁阴法|活塞|流出|浅会阴筋膜|浅出浅入|浆汁|浑圆|浓密的阴毛|浓浊|浓热|浓稠|浓精|浓黑|海外华人|浸润|浸润癌|浸淫|浸湿|消精亡阴|涌入|涌出|涌泉|涔涔|润湿|润滑|淋巴管|淋巴结|淋病|淫乳|淫事|淫人|淫友|淫嘴|淫声|淫女|淫媚|淫宴|淫情|淫挚|淫欲|淫毛|淫汁|淫液|淫痒|淫神|淫糜|淫纵|淫肉|淫舌|淫色|淫艳|淫语|淫逸|淫骚|深会阴筋膜|深喉|深插|混圆|温存|温湿|温热|温热感|温软|游移|湿乎乎|湿漉漉|湿濡|湿热|湿热下注证|湿软|湿透|滑入|滑出|滑到|滑向|滑嫩|滑抚|滑润|滑湿|滑溜|滑爽|滑粘|滑美|滑进|滑顺|满胀|满面潮红|滴出|滴虫性阴道炎|漂亮美眉|漆黑的阴毛|潜欲|激发性地区|激射|激烈的性交|濡湿|火柱|火热鸡巴|火辣|热吻|热烫|热穴|熟妇|爆射|爱侣|爱欲|爽快|爽死|爽滑|牝户|狂热|狗交|狗爬|狠干|狠插|猛冲|猛刺|猛喘|猛干|猛抽|猛挺|猛插|猛搅|猛撞|猛操|猛男|猛舔|猛颤|猥琐|猬亵|玉乳|玉体|玉卿|玉娘|玉娟|玉户|玉指|玉柱|玉浆|玉液|玉液般|玉穴|玉肌|玉脚|玉腿|玉臀|玉茎|玉蕊|玉面|玉颈|玉麈|珍珠状阴茎丘疹|理想|生殖器念珠菌病|生殖器损伤|生殖器疱疹|生殖器粘膜|生殖器脓疱|生殖支原体|生殖系炎症|生殖系统|生殖细胞|生殖腺|生殖道|生殖道分泌物|生精|生精小管|生精细胞|用力|用力一顶|疲软|病毒性睾丸炎|痔内静脉丛|痛快|痴女|瘫软|白丝|盆膈下筋膜|盈满|直挺挺|直精小管|直肠|直肠壶腹|直肠柱|直肠瓣|直肠阴道瘘|看片|睾丸坠痛|睾丸增生|睾丸小叶|睾丸小隔|睾丸损伤|睾丸液|睾丸激素|睾丸生精功能障碍|睾丸甾酮|睾丸移植|睾丸精索鞘膜|睾丸系带|睾丸系膜|睾丸素|睾丸纵隔|睾丸结核|睾丸网|睾丸酮|睾丸间质|睾丸鞘膜|睾网液|石淋|破处|破贞|破身|硕乳|硕壮|硬下疳|硬挺|硬梆梆|硬涨|硬热|硬物|硬硬|硬立|硬绑绑|硬胀|硬茎|硬邦邦|秘唇|秘洞|秘穴|秘缝|秘肉|秽物|秽疮|稣胸|窄窄|立花里子|站位性交|站立式性交|童男|童貞|第一会所|箍住|类菌质体|粗涨|粘乎乎|粘滑|粘稠|精关失固|精巢|精浆|精满自溢|精索内筋膜|精索外筋膜|精索静脉曲张|精索鞘韧带|精脱|精虫|精门|精门开|精阜|素女经|紧小|紧抓|紫红色|纯熟|经前痤疮|经期|经期紊乱|经痛|经血|经血来潮|经质粘稠|绒毛状乳头状瘤|结缔组织|绝经|绵软|缓慢|缓进速出|缠抱|缠绵|缸交|美乳|美伶|美体|美唇|美妇|美目|美穴|美肉|美脚|美臀|美香|群交|翘臀|翘起|翻动|翻弄|翻搅|耗精伤气|耻毛|耻骨尾骨肌|肉丘|肉体|肉团|肉圈|肉柱|肉欲|肉牙儿|肉球|肉眼|肉穴|肉腔|肉臀|肉色|肉芽|肉芽肿|肉身|肉香|肏人|肏干|肏我|肏死|肛乳头炎|肛交|肛尾韧带|肛柱|肛窦炎|肛管|肛管内括约肌|肛管外括约肌|肛管直肠环|肛肉|肛腺|肛部|肛门|肛门交|肠壁|肠梨形鞭毛虫病|肠源性紫绀|股沟|肢体|肥奶|肾上腺|肾气不固症|肾盂|肾结核|肾肿瘤|胀疼|胀破|胀硬|胀红|胀胀|背飞凫|胎盘|胎膜早破|胞漏疮|脏病|脓尿|脚交|脱下|脱光|脱去|腔内|腔肉|腹股沟淋巴结肿大|腹股沟淋巴肉芽肿|腹股沟疝|腹股沟管|腹股沟肉芽肿|腻滑|腿根|腿间|膀胱三角|膀胱肿瘤|膀胱阴道瘘|膏淋|臀下|臀丘|臀孔|臀尖|臀後|臀沟|臀洞|臀瓣|臀眼|臀缝|臀肉|臀股|臀腿|臂部|自慰|自拍|自淫|自渎|舌头|舌尖|舐去|舐吮|舐吻|舐弄|舐着|舐著|舔乾|舔他|舔到|舔去|舔吮|舔吻|舔奶|舔弄|舔拭|舔舐|舔触|舔起|舔遍|色欲|色色|花唇|花穴|花芯|花蕾|芳香|苍井空|苍老师|茂密|茂盛|茎头|茎底|荡叫|荡声|荡妇|萎缩|萎软|葡萄胎|蓝灯|蕾苞|蚀骨|蛋子|蛋蛋|蛮腰|蜜唇|蜜壶|蜜意|蜜汁|蜜洞|蜜液|蜜穴|蜜肉|蠢蠢欲动|行房|行淫|表姊|表嫂|裆部|裸体|裸体男女|裸女|裸着|裸睡|裸聊|裸背|裸胸|裸臀|裸身|裸躯|裸露|褪下|诱惑|调情|调戏|调经|调逗|豪乳|贝肉|贪淫|赤裸|赤裸裸|起性|蹂躏|蹼状阴茎|身子|身无寸缕|轮奸|轮暴|软下|软下疳|软性下疳|软玉温香|软瘫|软瘫了|软绵绵|软肉|软软|轻喘|轻抚|轻揉|轻搓|轻撩|进入|连炮几炮|迫进|迷情|逆行射精|造爱|逼里|酡红|酥爽|酥痒|酥胸|酥酥|酸痒|酸软|铁硬|销魂|锁精术|闭经|间质细胞|间质细胞刺激素|间质部|闷哼|阵阵快感|附件炎|附属性腺|附性腺分泌液|附睾|附睾丸|附睾小叶|附睾液|附睾炎|附睾管|附睾结核|随心所欲|隐睾|隐睾症|雌二醇|雌性激素|雌激素|雞巴|雨宫琴音|霉疮|霉菌性阴道炎|鞘膜腔|顶体素|频度|颜射|颤动|颤抖|风骚|飞机杯|饥渴|饱胀|騷女|骄穴|骄躯|骑乘位|骚B|骚动|骚劲|骚味|骚声|骚女|骚媚|骚幽|骚情|骚水|骚浪|骚浪叫|骚浪样子|骚淫|骚热|骚状|骚痒|骚穴|骚货|骚逼|骨感|骨盆|骨盆腔|骶丛|高亢|高潮|鱼水|鲜嫩|鲜润|麈柄|p站|福利|麻生希|麻酥|麻酥酥|黄体生成素|黄体酮|黏滑|黏稠|黏糊|黏膜|黑丝|黑毛|黑色的阴毛|黑黑的阴毛|鼓胀|丝袜"

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
        template.size=int64(item['size'])
        template.host=item['host']
        template.bookmark_id=int64(item['bookmark_id'])
        template.folder_id=int64(item['folder_id'])
        template.referer=item['referer']
        template.create_at=int64(int(round(time.time() * 1000)))
        template.update_at=int64(int(round(time.time() * 1000)))
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