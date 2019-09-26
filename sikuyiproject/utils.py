# -*- coding: utf-8 -*-
import logging
import re

import requests
import json,time
import random,datetime
import psycopg2
from .settings import *
username=KUAI_USERNAME
password=KUAI_PASSWORD

pgsql_uri = PGSQL_URI
pgsql_db = PGSQL_DATABASE
pgsql_user = PGSQL_USER
pgsql_pass = PGSQL_PASS
pgsql_port = PGSQL_PORT


orderid = '966404044351881'  # 订单号
# 提取代理链接，以私密代理为例
api_url = "http://dps.kdlapi.com/api/getdps/?orderid={}&num=1&pt=1&format=json&sep=1"
test_url="http://jzsc.mohurd.gov.cn/"
headers = {
    "Accept-Encoding": "Gzip",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"
}
def fetch_one_proxy():
    logging.debug("**********************************切换代理*********************************************")
    time.sleep(1)
    while 1:
        time.sleep(2)
        try:
            fetch_url = api_url.format(orderid)
            r = requests.get(fetch_url,timeout=5)
            if r.status_code == 200:
                content = json.loads(r.content.decode('utf-8'))
                ips = content['data']['proxy_list']
                proxy=ips[0]
                proxies = {
                    "http": "http://%(user)s:%(pwd)s@%(proxy)s/" % {'user': username, 'pwd': password, 'proxy': proxy},
                    "https": "http://%(user)s:%(pwd)s@%(proxy)s/" % {'user': username, 'pwd': password, 'proxy': proxy}
                }
                logging.debug("正在进行安全狗认证")
                req=requests.get(test_url,headers=headers,proxies=proxies,timeout=20,allow_redirects=False)
                #安全狗认证
                loc_url = req.headers.get("Location")
                if loc_url:
                    loc_url = 'http://jzsc.mohurd.gov.cn' + loc_url
                    safe = requests.get(loc_url,headers=headers,proxies=proxies,timeout=20,allow_redirects=False)
                    logging.debug("安全狗认证成功")
                    fetch_time = time.time()
                    logging.debug("已成功获取代理")
                    return fetch_time,proxy
                logging.debug("安全认证失败")
            logging.debug("获取代理失败")
        except:
            logging.debug("获取代理失败")

def get_id(sql):
    db = psycopg2.connect(database="province", user="postgres", password="sikuyi", host="ecs-a025-0002", port=54321)
    cursor = db.cursor()
    cursor.execute(sql)
    datalist = []
    alldata = cursor.fetchall()
    for s in alldata:
        data = s[0].split("?")[0]
        if len(data)>5:
            datalist.append(data)
    cursor.close()
    db.close()
    return datalist
class Wash:
    def __init__(self):
        self.company_set = set()
        self.company_list = list()
        self.conn = psycopg2.connect(host='119.3.206.20', port=54321, user='postgres', password='postgres',
                                     database='sikuyilatest')
        self.cursor = self.conn.cursor()

        sql = "select company_name from company_wash.company_finally"
        self.cursor.execute(sql)
        company_msgs = self.cursor.fetchall()
        for company_msg in company_msgs:
            if company_msg[0]:
                self.company_list.append(company_msg[0].strip())

    @staticmethod
    def bigger_start_index(a, b):
        return a + 1 if a > b else b + 1

    @staticmethod
    def litter_end_index(*args):
        args = [arg for arg in args if arg != -1]
        if args:
            args.sort()
            return args[0]
        return -1

    @staticmethod
    def find_chinese(file):
        pattern = re.compile(r'[^\u4e00-\u9fa5]')
        chinese = re.sub(pattern, '', file)
        return chinese

    def main(self):
        for i in self.company_list:
            chinese = self.find_chinese(i)
            if len(chinese) > 5:
                start = 0
                end = None
                # 头
                sheng = i.find('省') if i.find('省') >= len(i) // 2 else -1
                shi = i.find('市') if i.find('市') >= len(i) // 2 else -1
                shizheng = i.find('市政')
                # 尾
                kuohao_en = i.find('(') if i.find('(') >= len(i) // 2 else -1
                kuohao_ch = i.find('（') if i.find('（') >= len(i) // 2 else -1
                youxiangongsi = i.find('有限公司') if i.find('有限公司') >= len(i) // 2 else -1
                gongsi = i.find('公司') if i.find('公司') >= len(i) // 2 else -1
                youxianzerengongsi = i.find('有限责任公司') if i.find('有限责任公司') >= len(i) // 2 else -1
                jituan = i.find('集团') if i.find('集团') >= len(i) // 2 else -1
                yanjiuyuan = i.find('研究院') if i.find('研究院') >= len(i) // 2 else -1
                if sheng != -1 or (shi != -1 and shizheng == -1):
                    start = self.bigger_start_index(sheng, shi)
                if kuohao_ch != -1 or kuohao_en != -1:
                    end = self.litter_end_index(kuohao_en, kuohao_ch)
                if end is None and (
                        youxiangongsi != -1 or youxianzerengongsi != -1 or jituan != -1 or yanjiuyuan != -1 or gongsi != -1):
                    end = self.litter_end_index(youxiangongsi, youxianzerengongsi, jituan, yanjiuyuan, gongsi)
                msg = ''.join(list(map(lambda x: re.sub('\s', '', x), i[start: end])))
                self.company_set.add(msg.strip('（').strip('('))

        self.company_list = []
        self.cursor.close()
        self.conn.close()


