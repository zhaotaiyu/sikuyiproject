# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html
from scrapy import signals
import requests
import json
import logging
from scrapy import signals
import base64
from twisted.internet.error import TimeoutError, TCPTimedOutError
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from .utils import fetch_one_proxy
import time
from scrapy.conf import settings
from scrapy.utils.response import response_status_message
import pymongo
import datetime
import random

DOWNLOADER_MIDDLEWARES=settings.get("DOWNLOADER_MIDDLEWARES")
if "sikuyiproject.middlewares.KuaidailiMiddleware" in DOWNLOADER_MIDDLEWARES:
	fetch_time,proxy = fetch_one_proxy()
mongoclient=settings.get("MONGOCLIENT")
mongodatabase=settings.get("MONGODATABASE")
mongotable=settings.get("MONGOTABLE")
class AbuyunProxyMiddleware():
	def __init__(self,proxyuser,proxypass,proxyserver):
		self.proxyuser = proxyuser
		self.proxypass = proxypass
		self.proxyserver = proxyserver
		self.proxyauth = "Basic " + base64.urlsafe_b64encode(bytes((self.proxyuser + ":" + self.proxypass), "ascii")).decode("utf8")
	def process_request(self,request,spider):
		request.meta["proxy"] = self.proxyserver
		request.headers["Proxy-Authorization"] = self.proxyauth
		print("正在使用代理："+str(self.proxyserver))
	def process_exception(self, request, exception, spider):
		myclient = pymongo.MongoClient('mongodb://ecs-a025-0002:27017/')
		mydb = myclient[mongodatabase]
		mycol = mydb[mongotable]
		mydict = {"exception": "下载错误",
				  "body":request.body,
				  "url": request.url,
				  'time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
		mycol.insert_one(mydict)
		myclient.close()
	@classmethod
	def from_crawler(cls,crawler):
		return cls(
			proxyuser=crawler.settings.get("PROXYUSER"),
			proxypass=crawler.settings.get("PROXYPASS"),
			proxyserver=crawler.settings.get("PROXYSERVER"),
		)
class KuaidailiMiddleware():
	def __init__(self,username,password):
		self.username=username
		self.password=password
	def process_request(self, request, spider):
		proxy_url = 'http://%s:%s@%s' % (self.username, self.password, proxy)
		request.meta['proxy'] = proxy_url 
		auth = "Basic %s" % (base64.b64encode(('%s:%s' % (self.username, self.password)).encode('utf-8'))).decode('utf-8')
		request.headers['Proxy-Authorization'] = auth
	def process_response(self,request,response,spider):
		global fetch_time,proxy
		if response.status!=200:
			now_time = time.time() - 20
			if now_time>fetch_time:
				fetch_time,proxy = fetch_one_proxy()
			myclient = pymongo.MongoClient('mongodb://ecs-a025-0002:27017/')
			mydb=myclient[mongodatabase] 
			mycol=mydb[mongotable]
			mydict = {"response_status":response.status,"url":response.url,'time':datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
			mycol.insert_one(mydict)
			myclient.close()
		return response
	@classmethod
	def from_crawler(cls,crawler):
		return cls(
			username=crawler.settings.get("KUAI_USERNAME"),
			password=crawler.settings.get("KUAI_PASSWORD")
			)
class MyRetryMiddleware(RetryMiddleware):
	logger = logging.getLogger(__name__)
	def process_response(self,request,response,spider ):
		global fetch_time,proxy
		if 400<=response.status<500 or response.status>=600:
			now_time = time.time() - 20
			if now_time>fetch_time:
				fetch_time,proxy = fetch_one_proxy()
				fetch_time,proxy = fetch_one_proxy()
		retries = request.meta.get('retry_times', 0) + 1
		retry_times = settings.getint('RETRY_TIMES')
		if retries > retry_times:
			myclient = pymongo.MongoClient('mongodb://ecs-a025-0002:27017/')
			mydb = myclient[mongodatabase]
			mycol = mydb[mongotable]
			mydict = {"exception": "Gave up retrying {} failed {} times".format(request.url, retries, ),
					  "url": request.url,
					  'time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
			mycol.insert_one(mydict)
			myclient.close()
		return response

	def process_exception(self, request, exception, spider):
		global fetch_time,proxy
		now_time = time.time() - 100
		if now_time>fetch_time:
			fetch_time,proxy = fetch_one_proxy()
class MyUseragent():
	def process_request(self,request,spider):
		USER_AGENT_LIST = [
		'MSIE (MSIE 6.0; X11; Linux; i686) Opera 7.23',
		'Opera/9.20 (Macintosh; Intel Mac OS X; U; en)',
		'Opera/9.0 (Macintosh; PPC Mac OS X; U; en)',
		'iTunes/9.0.3 (Macintosh; U; Intel Mac OS X 10_6_2; en-ca)',
		'Mozilla/4.76 [en_jp] (X11; U; SunOS 5.8 sun4u)',
		'iTunes/4.2 (Macintosh; U; PPC Mac OS X 10.2)',
		'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:5.0) Gecko/20100101 Firefox/5.0',
		'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:9.0) Gecko/20100101 Firefox/9.0',
		'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:16.0) Gecko/20120813 Firefox/16.0',
		'Mozilla/4.77 [en] (X11; I; IRIX;64 6.5 IP30)',
		'Mozilla/4.8 [en] (X11; U; SunOS; 5.7 sun4u)'
			]
		agent = random.choice(USER_AGENT_LIST)
		request.headers['User_Agent'] =agent


			