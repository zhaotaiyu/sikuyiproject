# -*- coding: utf-8 -*-

# Scrapy settings for sikuyiproject1 project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'sikuyiproject'

SPIDER_MODULES = ['sikuyiproject.spiders']
NEWSPIDER_MODULE = 'sikuyiproject.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = random.choice(USER_AGENT_LIST)
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
# Obey robots.txt rules
ROBOTSTXT_OBEY = False
# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 0.3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'sikuyiproject1.middlewares.SikuyiprojectSpiderMiddleware': 543,
#}
DOWNLOAD_FAIL_ON_DATALOSS = False
# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
   # 'sikuyiproject.middlewares.AbuyunProxyMiddleware': 544,
   'sikuyiproject.middlewares.MyUseragent': 545,
   'sikuyiproject.middlewares.KuaidailiMiddleware': 543,
   'sikuyiproject.middlewares.MyRetryMiddleware': 700,
   # 'sikuyiproject.middlewares.ProxyMiddleware': 546,
}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   'sikuyiproject.pipelines.SikuyiprojectPipeline': 300,
   'sikuyiproject.pipelines.DatechangePipeline': 301,
   # 'sikuyiproject.pipelines.ScrapyKafkaPipeline': 304,
   'sikuyiproject.pipelines.PgsqlPipeline': 302,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
#scrapy-redis配置
#SCHEDULER = "scrapy_redis.scheduler.Scheduler"
# 去重类，要使用Bloom Filter请替换DUPEFILTER_CLASS
# Ensure use this Scheduler
SCHEDULER = "scrapy_redis_bloomfilter.scheduler.Scheduler"
# Ensure all spiders share same duplicates filter through redis
DUPEFILTER_CLASS = "scrapy_redis_bloomfilter.dupefilter.RFPDupeFilter"
# 散列函数的个数，默认为6，可以自行修改
BLOOMFILTER_HASH_NUMBER = 6
# Bloom Filter的bit参数，默认30，占用128MB空间，去重量级1亿
BLOOMFILTER_BIT = 30
SCHEDULER_PERSIST = True
REDIS_URL = 'redis://:Z43saw9vGH4Ey3d8@r-2ze7fb50627e7a14pd.redis.rds.aliyuncs.com:6379/13'
SCHEDULER_QUEUE_CLASS = "scrapy_redis.queue.FifoQueue"
DOWNLOAD_TIMEOUT=100
RETRY_HTTP_CODES = [500, 502, 503, 504, 400, 403, 408, 429, 407]
RETRY_TIMES = 300

#日志等级
LOG_LEVEL = 'DEBUG'
#PGSQL
PGSQL_URI="ecs-a025-0002"
PGSQL_DATABASE="cic_database"
PGSQL_PASS="sikuyi"
PGSQL_USER="postgres"
PGSQL_PORT=54321
#MONGO配置
MONGOCLIENT='mongodb://ecs-a025-0002:27017/'
MONGODATABASE='sikuyilog'
MONGOTABLE='sikuyi'
#KAFKA配置
BOOTSTRAP_SERVER="49.4.90.247:6667"
TOPIC="TOPIC_sikuyifinally"
#abuyun代理配置
PROXYUSER="H7895G9300YN511D"
PROXYPASS="AC67F9AA92D6F49F"
PROXYSERVER="http://http-dyn.abuyun.com:9020"
#快代理配置
KUAI_USERNAME="zhao_tai_yu"
KUAI_PASSWORD="7av2i9t5"
#其他配置
MAXTIME=4
