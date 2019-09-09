# -*- coding: utf-8 -*-
import logging
import requests
import json,time
import random,datetime
import psycopg2
from scrapy.conf import settings
username=settings.get("KUAI_USERNAME")
password=settings.get("KUAI_PASSWORD")

pgsql_uri = settings.get('PGSQL_URI')
pgsql_db = settings.get('PGSQL_DATABASE')
pgsql_user = settings.get('PGSQL_USER')
pgsql_pass = settings.get('PGSQL_PASS')
pgsql_port = settings.get('PGSQL_PORT')


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
	db = psycopg2.connect(database="sikuyitest", user="postgres", password="sikuyi", host="ecs-a025-0002", port=54321)
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