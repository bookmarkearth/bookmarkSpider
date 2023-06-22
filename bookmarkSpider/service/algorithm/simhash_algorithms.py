# coding=utf-8
'''
Created on 2022-3-27

@author: www.bookmarkearth.com
'''

from simhash import Simhash
from bookmarkSpider.model.local_redis import RedisHelper


class SimhashAlgorithmService():

    def __init__(self):
        self.similarity_allow=3
        self.cut_seg=4 #cut 1 seg
        self.helper = RedisHelper()
        self.key_pre="t_f_k{1}_"

    ##diff##
    def diffHash(self,hash1,hash2):
        return hash1.distance(hash2)

    ##diff##
    def diffValue(self,v1,v2):

        x = (v1 ^ v2) & ((1 << 64) - 1)
        ans = 0
        while x:
            ans += 1
            x &= x - 1
        return ans

    ##64b 2进制##
    def tobin(self,hash):
        return str(bin(hash).replace('0b', '').replace('-', '').zfill(64)[-64:])

    ##切割成平均4份##
    def cut_average(self,binstr,num):

        rs=[]
        size=int(len(binstr)/num)
        for i in range(0,num):
            rs.append(binstr[i*size:(i+1)*size])
        return rs

    def drop_it(self,no,k,v):

        new_k = self.key_pre.replace("{1}",str(no)) + str(int(k,2))
        values = self.helper.smembers(new_k)

        if len(values) > 0:
            if(self.is_same(v, values)):
                return True

        self.helper.sadd(new_k,v)  ##存储hash值
        return False

    def is_same(self,v,values):

        for v2 in values:
            dif=self.diffValue(int(v2.decode()),v)
            #print("##############################",int(v2.decode()),v,dif,values)
            if dif <= self.similarity_allow:
                return True
        return False

    def analysis_item(self,body):

        ##simhash printfinger##
        hashValue=Simhash(body).value
        rs=self.cut_average(self.tobin(hashValue),self.cut_seg)

        ##save and find##
        for i in range(0, self.cut_seg):
            if self.drop_it(i,rs[i],hashValue):
                return True
        return False

'''测试'''
class TestMongoHelper():

  #algorithm = SimhashAlgorithmService()
  #rs=algorithm.diff2(3579946741507768605,3579946741507768105)
  #print(rs)
  # str1="并没fds成 yes  开心，所32不开心”，自定义到词典中来达到目的 开心，所32不开心”，自定义到词典中来达到目的 /  开心，所32不开心”，自定义到词典中来达到目的】"
  # str2="并没fds成 开心，所32不开心”，自定义到词典中来达到目的 yes  /  开心，所32 开心，所32不开心”，自定义到词典中来达到目的 开心，所32不开心”，自定义到词典中来达到目的不开心”，自定义到词典中来达到目的】"
  #
  # print(Simhash(str1).value)
  # print(algorithm.tobin(Simhash(str1).value))
  # print(algorithm.cut_average(algorithm.tobin(Simhash(str1).value),4))
  # print(Simhash(str2).value)
  # print(algorithm.cut_average(algorithm.tobin(Simhash(str2).value),4))
  #
  # r2 = algorithm.diff(Simhash(str1), Simhash(str2))
  # print(r2)
  pass