# -*- coding: utf-8 -*-
import scrapy
from sikuyiproject.items import *
from scrapy import Request,FormRequest
import time,datetime
from scrapy_redis.spiders import RedisSpider
import pandas as pd
from kafka import KafkaConsumer
import time
class SikuyiSpider(RedisSpider):
	name = 'sikuyi'
	redis_key = 'SikuyiSpider:start_urls'
	allowed_domains = ['jzsc.mohurd.gov.cn']
	def parse(self,response):
		url="http://jzsc.mohurd.gov.cn/dataservice/query/comp/list"
		df = pd.read_csv("gongsi.csv", encoding="utf-8")
		company_list= df['company_name'].tolist()
		for company in company_list:
			if isinstance(company,str):
				if len(company_list)>5:
					formdata = {
						"qy_type":" ",
						"apt_scope":" ",
						"apt_code":" ",
						"qy_name":" ",
						"qy_code":" ",
						"apt_certno":" ",
						"qy_fr_name":" ",
						"qy_gljg":" ",
						"qy_reg_addr":" ",
						"qy_region":" ",
						"complexname":company
					}
					print(company)
					yield scrapy.FormRequest(url,formdata=formdata,callback=self.parse_next)
	def parse_next(self, response):
		company_url=response.xpath("//tbody[@class='cursorDefault']/tr[1]/td[3]/a/@href").extract_first()
		if company_url is not None:
			company_url="http://jzsc.mohurd.gov.cn"+str(company_url)
			print(company_url)
			yield Request(url=company_url,callback=self.parse_company)
	def parse_company(self,response):
		print(response.url)
		c_info = CompanyInformation()
		# 公司名称
		c_info["company_name"] = response.xpath("//div[@class='user_info spmtop']/b/text()").extract_first().strip()
		# 公司ID
		company_id = response.url.split("/")[-1]
		c_info["company_id"] = company_id
		# 统一社会信用代码
		c_info["social_credit_code"] = response.xpath(
			"//div[@class='query_info_box ']/table/tbody/tr[1]/td/text()").extract_first()
		# 企业法定代表人
		c_info["leal_person"] = response.xpath(
			'/html/body/div[3]/div[2]/div/table/tbody/tr[2]/td[1]/text()').extract_first()
		# 企业登记注册类型
		c_info["regis_type"] = response.xpath(
			'/html/body/div[3]/div[2]/div/table/tbody/tr[2]/td[2]/text()').extract_first()
		# 企业注册属地
		c_info["regis_address"] = response.xpath(
			'/html/body/div[3]/div[2]/div/table/tbody/tr[3]/td/text()').extract_first()
		# 企业经营地址
		c_info["business_address"] = response.xpath(
			'/html/body/div[3]/div[2]/div/table/tbody/tr[4]/td/text()').extract_first()
		# print(social_credit_code,leal_person,regis_type,regis_address,business_address)
		c_info["create_time"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		c_info["modification_time"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		c_info["status"] = 1
		c_info["is_delete"] = 0
		c_info["url"]=response.url
		yield c_info
		# 资质资格url
		aptitude_url = response.xpath("//ul[@class='tinyTab datas_tabs']/li[1]/a/@data-url").extract_first()
		aptitude_url = "http://jzsc.mohurd.gov.cn" + aptitude_url
		yield Request(aptitude_url,callback=self.parse_aptitude,meta={"company_id":company_id})
		# 注册人员url
		registered_personnel_url = response.xpath("//ul[@class='tinyTab datas_tabs']/li[2]/a/@data-url").extract_first()
		registered_personnel_url = "http://jzsc.mohurd.gov.cn" + registered_personnel_url
		yield Request(registered_personnel_url, callback=self.get_registered_personnel, meta={"company_id": company_id})
		# 工程项目url
		engineering_project_url = response.xpath("//ul[@class='tinyTab datas_tabs']/li[3]/a/@data-url").extract_first()
		engineering_project_url = "http://jzsc.mohurd.gov.cn" + engineering_project_url
		yield Request(url=engineering_project_url,callback=self.get_engineering_project,meta={"company_id":company_id})
		# 不良行为url
		bad_behavior_url = response.xpath("//ul[@class='tinyTab datas_tabs']/li[4]/a/@data-url").extract_first()
		bad_behavior_url = "http://jzsc.mohurd.gov.cn" + bad_behavior_url
		yield Request(url=bad_behavior_url,callback=self.parse_behavior,meta={"company_id":company_id,"reason":"不良行为"})
		# 良好行为url
		good_behavior_url = response.xpath("//ul[@class='tinyTab datas_tabs']/li[5]/a/@data-url").extract_first()
		good_behavior_url = "http://jzsc.mohurd.gov.cn" + good_behavior_url
		yield Request(url=good_behavior_url, callback=self.parse_behavior,meta={"company_id": company_id, "reason": "良好行为"})
		# 黑名单记录url
		blacklist_url = response.xpath("//ul[@class='tinyTab datas_tabs']/li[6]/a/@data-url").extract_first()
		blacklist_url = "http://jzsc.mohurd.gov.cn" + blacklist_url
		yield Request(url=blacklist_url, callback=self.parse_companny_blacklist,meta={"company_id": company_id, "reason": "黑名单"})
		# 失信联合惩戒记录url
		break_faith_url = response.xpath("//ul[@class='tinyTab datas_tabs']/li[7]/a/@data-url").extract_first()
		break_faith_url = "http://jzsc.mohurd.gov.cn" + break_faith_url
		yield Request(url=break_faith_url, callback=self.parse_company_break_faith,meta={"company_id": company_id, "reason": "黑名单"})
	#解析行为
	def parse_behavior(self,response):
		cuo=response.xpath("//tbody[@class='cursorDefault']/tr[1]/td/text()").extract_first()
		if cuo != "暂未查询到已登记入库信息":
			tr_list=response.xpath("//tbody[@class='cursorDefault']/tr")
			if tr_list:
				for tr in tr_list:
					behavior=BehaviorItem()
					behavior["record_num"] = tr.xpath("./td[1]/text()").extract_first()
					behavior["id"] = tr.xpath("./td[2]/a/@href").extract_first()
					behavior["record_main"] = tr.xpath("./td[2]/a/text()").extract_first()
					if behavior["record_main"] is None:
						behavior["record_main"] = tr.xpath("./td[2]/text()").extract_first()
					behavior["content"] = tr.xpath("./td[3]/text()").extract_first()
					behavior["department"] = tr.xpath("./td[4]/text()").extract_first()
					behavior["useful_date"] = tr.xpath("./td[5]/text()").extract_first()
					behavior["in_date"] = None
					behavior["out_date"] = None
					behavior["legal_person"] = None
					behavior["legal_person_idcard"] = None
					behavior["reason"] = response.meta.get("reason")
					behavior["create_time"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
					behavior["modification_time"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
					behavior["status"] = 1
					behavior["is_delete"] = 0
					yield behavior
	#解析企业黑名单
	def parse_companny_blacklist(self,response):
		cuo = response.xpath("//tbody[@class='cursorDefault']/tr[1]/td/text()").extract_first()
		if cuo != "暂未查询到已登记入库信息":
			tr_list = response.xpath("//tbody[@class='cursorDefault']/tr")
			if tr_list:
				for tr in tr_list:
					behavior = BehaviorItem()
					behavior["record_num"] = str(tr.xpath("./td[1]/text()").extract_first()).strip()
					behavior["id"] = tr.xpath("./td[2]/a/@href").extract_first()
					behavior["record_main"] = tr.xpath("./td[2]/a/text()").extract_first()
					if behavior["record_main"] is None:
						behavior["record_main"] = str(tr.xpath("./td[2]/text()").extract_first()).strip()
						behavior["id"] = str(tr.xpath("./td[2]/a/@href").extract_first()).split("/")[-1]
					else:
						behavior["id"] = str(tr.xpath("./td[2]/a/@href").extract_first()).split("/")[-1]
						behavior["record_main"] = str(tr.xpath("./td[2]/a/text()").extract_first()).strip()
					behavior["content"] = str(tr.xpath("./td[3]")[0].xpath("string(.)").extract_first()).strip()
					behavior["department"] = tr.xpath("./td[4]/text()").extract_first()
					behavior["useful_date"] = None
					behavior["in_date"] = tr.xpath("./td[5]/text()").extract_first()
					behavior["out_date"] = tr.xpath("./td[6]/text()").extract_first()
					behavior["legal_person"] = None
					behavior["legal_person_idcard"] = None
					behavior["reason"] = response.meta.get("reason")
					behavior["create_time"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
					behavior["modification_time"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
					behavior["status"] = 1
					behavior["is_delete"] = 0
					yield behavior
	#解析失信联合惩戒记录
	def parse_company_break_faith(self,response):
		cuo = response.xpath("//tbody[@class='cursorDefault']/tr[1]/td/text()").extract_first()
		if cuo != "暂未查询到已登记入库信息":
			tr_list = response.xpath("//tbody[@class='cursorDefault']/tr")
			if tr_list:
				for tr in tr_list:
					behavior = BehaviorItem()
					behavior["record_num"] = tr.xpath("./td[1]/span/text()").extract_first()
					behavior["id"] = tr.xpath("./td[2]/a/@href").extract_first()
					behavior["record_main"] = tr.xpath("./td[2]/a/text()").extract_first()
					if behavior["record_main"] is None:
						behavior["record_main"] = tr.xpath("./td[2]/text()").extract_first()
						behavior["id"] = str(tr.xpath("./td[2]/a/@href").extract_first()).split("/")[-1]
					else:
						behavior["id"] = str(tr.xpath("./td[2]/a/@href").extract_first()).split("/")[-1]
						behavior["record_main"] = str(tr.xpath("./td[2]/a/text()").extract_first()).strip()
					behavior["content"] = str(tr.xpath("./td[4]/div/span/text()").extract_first()).strip()+" "+str(tr.xpath("./td[4]/text()[2]").extract_first()).strip()
					behavior["department"] =tr.xpath("./td[5]/text()").extract_first()
					behavior["useful_date"] = None
					behavior["in_date"] = tr.xpath("./td[6]/text()").extract_first()
					behavior["out_date"] = None
					behavior["legal_person"] = tr.xpath("./td[3]/div[1]/span/text()").extract_first()
					behavior["legal_person_idcard"] = str(tr.xpath("./td[3]/text()[2]").extract_first()).strip()
					behavior["reason"] = response.meta.get("reason")
					behavior["create_time"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
					behavior["modification_time"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
					behavior["status"] = 1
					behavior["is_delete"] = 0
					yield behavior
	#解析资质
	def parse_aptitude(self, response):
		#print("开始解析资质资格url----"+response.url)
		company_id = response.meta["company_id"]
		aptitude_type = response.xpath("//tbody[@class='cursorDefault']/tr[1]/td[@data-header='资质类别']/text()").extract_first()
		if aptitude_type:
			tr_list = response.xpath("//tbody[@class='cursorDefault']/tr")
			if tr_list:
				for tr in tr_list:
					c_apt=CompanyAptitude()
					c_apt["company_id"]=company_id
					c_apt["aptitude_type"] = tr.xpath("./td[@data-header='资质类别']/text()").extract_first()
					c_apt["aptitude_id"] = tr.xpath("./td[@data-header='资质证书号']/text()").extract_first()
					c_apt["aptitude_name"] = tr.xpath("./td[@data-header='资质名称']/text()").extract_first().strip()
					c_apt["aptitude_startime"] = tr.xpath("./td[@data-header='发证日期']/text()").extract_first()
					c_apt["aptitude_endtime"] = tr.xpath("./td[@data-header='证书有效期']/text()").extract_first()
					c_apt["aptitude_organ"] = tr.xpath("./td[@data-header='发证机关']/text()").extract_first()
					c_apt["url"]=response.url
					c_apt["create_time"] =datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
					c_apt["modification_time"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
					c_apt["status"] = 1
					c_apt["is_delete"] = 0
					yield c_apt
			#print("结束解析资质资格url****" + response.url)
	# 获取人员列表
	def get_registered_personnel(self,response):
		info = response.xpath("//div[@class='clearfix']/script/text()").extract_first()
		if info is not None:
			total_number = eval(str(info).split(",")[1] + '}')["$total"]
			for page in range(1, int(total_number / 25) + 2):
			#for page in range(37, 38):
				data = {
					"$total": str(total_number),
					"$reload": "0",
					"$pg": str(page),
					"$pgsz": "25",
				}
				yield scrapy.FormRequest(url=response.url, formdata=data, callback=self.parse_registered_personnel,meta={"company_id":response.meta["company_id"]})
		else:
			tr_list = response.xpath("//tbody/tr")
			if tr_list:
				for tr in tr_list:
					# 人员基本信息
					person_url = tr.xpath("./td[2]/a/@onclick").extract_first()
					if person_url is not None:
						person_url = "http://jzsc.mohurd.gov.cn" + tr.xpath("./td[2]/a/@onclick").extract_first().split("'")[1]
						person_name = tr.xpath("./td[2]/a/text()").extract_first()
						person_id = person_url.split("/")[-1]
						yield Request(url=person_url, callback=self.parse_person_detail,meta={"person_name": person_name, "person_id": person_id,"company_id": response.meta["company_id"]})
						# 不良行为url
						person_bad_behaviour_url = "http://jzsc.mohurd.gov.cn/dataservice/query/staff/staffCreditRecordList/" + person_id + "/0"
						yield Request(url=person_bad_behaviour_url, callback=self.parse_behavior, meta={"reason": "不良行为"})
						# 良好行为url
						person_good_behaviour_url = "http://jzsc.mohurd.gov.cn/dataservice/query/staff/staffCreditRecordList/" + person_id + "/1"
						yield Request(url=person_good_behaviour_url, callback=self.parse_behavior, meta={"reason": "良好行为"})
						# 黑名单记录url
						person_blacklist_url = "http://jzsc.mohurd.gov.cn/dataservice/query/staff/staffCreditBlackList/" + person_id
						# yield Request(url=person_blacklist_url, callback=self.parse_person_blacklist,meta={"reason": "黑名单"})
						# 变更记录url
						person_change_record_url = "http://jzsc.mohurd.gov.cn/dataservice/query/staff/staffWorkRecordList/" + person_id
						yield Request(url=person_change_record_url, callback=self.parse_change_record,meta={"person_id": person_id, })
	# 解析人员列表
	def parse_registered_personnel(self,response):
		tr_list = response.xpath("//tbody/tr")
		for tr in tr_list[0:-1]:
			# 人员基本信息
			person_url = "http://jzsc.mohurd.gov.cn" + tr.xpath("./td[2]/a/@onclick").extract_first().split("'")[1]
			person_name = tr.xpath("./td[2]/a/text()").extract_first()
			person_id = person_url.split("/")[-1]
			yield Request(url=person_url, callback=self.parse_person_detail,meta={"person_name":person_name,"person_id":person_id,"company_id":response.meta["company_id"]})
			# 不良行为url
			person_bad_behaviour_url = "http://jzsc.mohurd.gov.cn/dataservice/query/staff/staffCreditRecordList/" + person_id + "/0"
			yield Request(url=person_bad_behaviour_url, callback=self.parse_behavior, meta={"reason": "不良行为"})
			# 良好行为url
			person_good_behaviour_url = "http://jzsc.mohurd.gov.cn/dataservice/query/staff/staffCreditRecordList/" + person_id + "/1"
			yield Request(url=person_good_behaviour_url, callback=self.parse_behavior,meta={"reason": "良好行为"})
			# 黑名单记录url
			person_blacklist_url = "http://jzsc.mohurd.gov.cn/dataservice/query/staff/staffCreditBlackList/" + person_id
			#yield Request(url=person_blacklist_url, callback=self.parse_person_blacklist,meta={"reason": "黑名单"})
			# 变更记录url
			person_change_record_url = "http://jzsc.mohurd.gov.cn/dataservice/query/staff/staffWorkRecordList/" + person_id
			yield Request(url=person_change_record_url,callback=self.parse_change_record,meta={"person_id":person_id,})
	# 解析人员基本信息
	def parse_person_detail(self,response):
		p_info=PersonInformation()
		#人员id
		p_info["person_id"]=response.meta["person_id"]
		#姓名
		p_info["person_name"] = response.meta["person_name"]
		# 性别
		p_info["person_sex"] = response.xpath("//div[@class='query_info_box ']/div/div[@class='activeTinyTabContent'][1]/dl/dd[1]/text()").extract_first()
		# 证件类型
		p_info["person_identification_type"] = response.xpath("//div[@class='query_info_box ']/div/div[@class='activeTinyTabContent'][1]/dl/dd[2]/text()").extract_first()
		# 证件号码
		p_info["person_identification_id"] = response.xpath("//div[@class='query_info_box ']/div/div[@class='activeTinyTabContent'][1]/dl/dd[3]/text()").extract_first()
		#企业id
		p_info["company_id"]=response.meta["company_id"]
		p_info["create_time"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		p_info["modification_time"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		p_info["status"] = 1
		p_info["is_delete"] = 0

		# 注册类别
		dl_list=response.xpath("//div[@id='regcert_tab']/dl")
		if dl_list:
			for dl in dl_list:
				p_cert = PersonCertificate()
				if len(dl.xpath("./dd"))==5:
					#人员
					p_cert["person_id"]=p_info["person_id"]
					p_cert["certificate_type"] = dl.xpath("./dd[1]/b/text()").extract_first()
					# 证书编号
					p_cert["certificate_num"] = dl.xpath("./dd[3]/text()").extract_first()
					# 执业印章号
					p_cert["certificate_seal_id"] = dl.xpath("./dd[4]/text()").extract_first()
					# 有效期
					p_cert["certificate_useful_time"] = dl.xpath("./dd[5]/text()").extract_first()
					# 注册单位
					p_cert["certificate_company_name"] = str(dl.xpath("./dt/a/text()").extract_first()).strip()
					# 注册单位id
					p_cert["certificate_company_id"] = dl.xpath("./dt/a/@data-qyid").extract_first()
					#注册专业
					p_cert["major"]=dl.xpath("./dd[2]/text()").extract_first()
				else:
					p_cert["person_id"] = p_info["person_id"]
					p_cert["certificate_type"] = dl.xpath("./dd[1]/b/text()").extract_first()
					# 证书编号
					p_cert["certificate_num"] = dl.xpath("./dd[2]/text()").extract_first()
					# 执业印章号
					p_cert["certificate_seal_id"] = dl.xpath("./dd[3]/text()").extract_first()
					# 有效期
					p_cert["certificate_useful_time"] = dl.xpath("./dd[4]/text()").extract_first()
					# 注册单位
					p_cert["certificate_company_name"] = str(dl.xpath("./dt/a/text()").extract_first()).strip()
					# 注册单位id
					p_cert["certificate_company_id"] = dl.xpath("./dt/a/@data-qyid").extract_first()
				p_cert["create_time"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
				p_cert["modification_time"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
				p_cert["status"] = 1
				p_cert["is_delete"] = 0
				yield p_cert
		yield p_info

	# 解析变更记录
	def parse_change_record(self,response):
		# 注册类别
		registe_type = response.xpath("//td[@data-header='注册类别']/text()").extract_first()
		if registe_type is not None:
			li_list = response.xpath("//ul[@class='cbp_tmtimeline']/li")
			for li in li_list:
				p_change=ChangeItem()
				p_change["id"]=response.meta["person_id"]
				p_change["registe_type"]=registe_type
				# 变更时间
				p_change["change_time"] = li.xpath("./div/span[1]/text()").extract_first().replace("年", "/") + li.xpath("./div/span[2]/text()").extract_first()
				# 变更记录
				p_change["change_record"] = str(li.xpath("./div/p")[0].xpath("string(.)").extract_first()).strip()
				p_change["chenge_subject"] = "人员"
				p_change["create_time"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
				p_change["modification_time"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
				p_change["status"] = 1
				p_change["is_delete"] = 0
				yield p_change
	#获取项目列表
	def get_engineering_project(self,response):
		info = response.xpath("//div[@class='clearfix']/script/text()").extract_first()
		if info is not None:
			total_number = eval(str(info).split(",")[1] + '}')["$total"]
			for page in range(1, int(total_number / 25) + 2):
			#for page in range(1, 2):
				data = {
					"$total": str(total_number),
					"$reload": "0",
					"$pg": str(page),
					"$pgsz": "25",
				}
				yield scrapy.FormRequest(url=response.url,formdata=data,callback=self.get_project_list,meta={"company_id":response.meta["company_id"]})
		else:
			tr_list = response.xpath("//table[@class='pro_table_box pro_table_borderright']/tbody/tr")
			if tr_list is not None:
				for tr in tr_list:
					project_url = tr.xpath("./td[@data-header='项目编码']/text()").extract_first()
					if project_url is not None:
						project_url = "http://jzsc.mohurd.gov.cn/dataservice/query/project/projectDetail/" + tr.xpath("./td[@data-header='项目编码']/text()").extract_first()
						yield Request(url=project_url, callback=self.parse_engineering_project,meta={"company_id": response.meta["company_id"]})
	#解析项目列表
	def get_project_list(self, response):
		tr_list = response.xpath("//table[@class='pro_table_box pro_table_borderright']/tbody/tr")
		for tr in tr_list[0:-1]:
			projeect_url = tr.xpath("./td[@data-header='项目编码']/text()").extract_first()
			if projeect_url is not None:
				projeect_url = "http://jzsc.mohurd.gov.cn/dataservice/query/project/projectDetail/" + tr.xpath("./td[@data-header='项目编码']/text()").extract_first()
				yield Request(url=projeect_url,callback=self.parse_engineering_project,meta={"company_id":response.meta["company_id"]})
	# 解析项目基本信息
	def parse_engineering_project(self, response):
		project_info = ProjectInformation()
		# 项目编号（项目id）
		project_info["project_id"] = response.xpath(
			"//div[@class='query_info_box ']/div[@class='tinyTabContent query_info_dl']/div/dl/dd[1]/text()").extract_first()
		# 企业id
		project_info["company_id"] = response.meta["company_id"]
		# 项目名称
		project_info["project_name"] = response.xpath("//div[@class='user_info spmtop']/b/text()").extract_first()
		# 省级项目编号
		project_info["provincial_project_num"] = response.xpath(
			"//div[@class='query_info_box ']/div[@class='tinyTabContent query_info_dl']/div/dl/dd[2]/text()").extract_first()

		# 省   贵州省-贵阳市
		project_info["region_province"] = response.xpath(
			"//div[@class='query_info_box ']/div[@class='tinyTabContent query_info_dl']/div/dl/dd[3]/text()").extract_first()
		# 建设单位
		project_info["constructe_company"] = response.xpath(
			"//div[@class='query_info_box ']/div[@class='tinyTabContent query_info_dl']/div/dl/dd[4]/text()").extract_first()
		# 建设单位组织机构代码（统一社会信用代码）
		project_info["constructe_company_credit_code"] = response.xpath(
			"//div[@class='query_info_box ']/div[@class='tinyTabContent query_info_dl']/div/dl/dd[5]/text()").extract_first()
		# 项目分类
		project_info["project_type"] = response.xpath(
			"//div[@class='query_info_box ']/div[@class='tinyTabContent query_info_dl']/div/dl/dd[6]/text()").extract_first()
		# 建设性质
		project_info["project_nature"] = response.xpath(
			"//div[@class='query_info_box ']/div[@class='tinyTabContent query_info_dl']/div/dl/dd[7]/text()").extract_first()
		# 工程用途
		project_info["project_purpose"] = response.xpath(
			"//div[@class='query_info_box ']/div[@class='tinyTabContent query_info_dl']/div/dl/dd[8]/text()").extract_first()
		# 总投资
		project_info["total_investment"] = response.xpath(
			"//div[@class='query_info_box ']/div[@class='tinyTabContent query_info_dl']/div/dl/dd[9]/text()").extract_first()
		if project_info["total_investment"] is not None:
			project_info["total_investment"]=str(project_info["total_investment"]).strip("（万元）")
		# 总面积
		project_info["total_area"] = response.xpath(
			"//div[@class='query_info_box ']/div[@class='tinyTabContent query_info_dl']/div/dl/dd[10]/text()").extract_first()
		if project_info["total_area"] is not None:
			project_info["total_area"]=str(project_info["total_area"]).strip("（平方米）")
		# 立项级别
		project_info["project_level"] = response.xpath(
			"//div[@class='query_info_box ']/div[@class='tinyTabContent query_info_dl']/div/dl/dd[11]/text()").extract_first()
		# 立项文号
		project_info["project_reference_num"] = response.xpath(
			"//div[@class='query_info_box ']/div[@class='tinyTabContent query_info_dl']/div/dl/dd[12]/text()").extract_first()
		project_info["create_time"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		project_info["modification_time"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		project_info["status"] = 1
		project_info["is_delete"] = 0
		# 招投标查看url
		log1 = response.xpath("//div[@class='query_info_tab']/ul/li[1]/a/span/em/text()").extract_first()
		if str(log1) != "0":
			bid_url_list = response.xpath("//div[@id='tab_ztb']/table/tbody/tr")
			for tr in bid_url_list:
				bid_url = "http://jzsc.mohurd.gov.cn" + str(
					tr.xpath("./td[@data-header='查看']/a/@data-url").extract_first())
				yield Request(url=bid_url,callback=self.parse_bid_url,meta={"project_id":project_info["project_id"]})
		else:
			pass
		# 施工图纸审查查看url
		log2 = response.xpath("//div[@class='query_info_tab']/ul/li[2]/a/span/em/text()").extract_first()
		if str(log2) != "0":
			construction_review_list = response.xpath("//div[@id='tab_sgtsc']/table/tbody/tr")
			for tr in construction_review_list:
				construction_review_url = "http://jzsc.mohurd.gov.cn" + str(
					tr.xpath("./td[@data-header='查看']/a/@data-url").extract_first())
				yield Request(url=construction_review_url,callback=self.parse_construction_review_url,meta={"project_id":project_info["project_id"]})
		else:
			pass
		# 合同备案查看url
		log3 = response.xpath("//div[@class='query_info_tab']/ul/li[3]/a/span/em/text()").extract_first()
		if str(log3) != "0":
			contract_record_list = response.xpath("//div[@id='tab_htba']/table/tbody/tr")
			for tr in contract_record_list:
				contract_record_url = "http://jzsc.mohurd.gov.cn" + str(
					tr.xpath("./td[@data-header='查看']/a/@data-url").extract_first())
				yield Request(url=contract_record_url, callback=self.parse_contract_record_url,meta={"project_id": project_info["project_id"]})
		else:
			pass
		# 施工许可查看url
		log4 = response.xpath("//div[@class='query_info_tab']/ul/li[4]/a/span/em/text()").extract_first()
		if str(log4) != "0":
			construction_permit_list = response.xpath("//div[@id='tab_sgxk']/table/tbody/tr")
			for tr in construction_permit_list:
				construction_permit_url = "http://jzsc.mohurd.gov.cn" + str(
					tr.xpath("./td[@data-header='查看']/a/@data-url").extract_first())
				certificate_date = tr.xpath("./td[@data-header='发证日期']/text()").extract_first()
				yield Request(url=construction_permit_url, callback=self.parse_construction_permit_url,meta={"project_id": project_info["project_id"],"certificate_date":certificate_date})
		else:
			pass
		# 竣工验收备案查看url
		log5 = response.xpath("//div[@class='query_info_tab']/ul/li[5]/a/span/em/text()").extract_first()
		if str(log5) != "0":
			complete_list = response.xpath("//div[@id='tab_jgysba']/table/tbody/tr")
			for tr in complete_list:
				complete_url = "http://jzsc.mohurd.gov.cn" + str(
					tr.xpath("./td[@data-header='查看']/a/@data-url").extract_first())
				yield Request(url=complete_url, callback=self.parse_complete_url,meta={"project_id": project_info["project_id"]})
		else:
			pass
		yield project_info
	#解析招投标信息
	def parse_bid_url(self, response):
		project_bids=ProjectBidsInformation()
		#项目id
		project_bids["project_id"]=response.meta["project_id"]
		# 中标通知书编号
		project_bids["bid_notification_num"] = response.xpath("//table[@class='pro_table_box datas_table']/tbody/tr[8]/td[1]/text()").extract_first()
		# 省级中标通知书编号
		project_bids["province_bid_notification_num"] = response.xpath("//table[@class='pro_table_box datas_table']/tbody/tr[2]/td[2]/text()").extract_first()
		# 招标类型
		project_bids["bids_type"] = response.xpath("//table[@class='pro_table_box datas_table']/tbody/tr[9]/td[1]/text()").extract_first()
		# 招标方式
		project_bids["bids_method"] = response.xpath("//table[@class='pro_table_box datas_table']/tbody/tr[9]/td[2]/text()").extract_first()
		# 中标金额（万元）
		project_bids["bid_money"]= response.xpath("//table[@class='pro_table_box datas_table']/tbody/tr[10]/td[2]/text()").extract_first()
		# 中标日期
		project_bids["bid_date"] = response.xpath("//table[@class='pro_table_box datas_table']/tbody/tr[10]/td[1]/text()").extract_first()
		# 建设规模
		project_bids["scale_of_construction"] = response.xpath("//table[@class='pro_table_box datas_table']/tbody/tr[11]/td[1]/text()").extract_first()
		# 面积（平方米）
		project_bids["area"] = response.xpath("//table[@class='pro_table_box datas_table']/tbody/tr[12]/td[1]/text()").extract_first()
		# 招标代理单位四库一id
		project_bids["bids_agency_id"]=None
		# 招标代理单位名称
		try:
			project_bids["bids_agency_name"] = response.xpath("//table[@class='pro_table_box datas_table']/tbody/tr[13]/td[1]/text()").extract_first().strip()
		except:
			try:
				project_bids["bids_agency_name"] =response.xpath("//table[@class='pro_table_box datas_table']/tbody/tr[13]/td[1]/a/text()").extract_first().strip()
				project_bids["bids_agency_id"] = response.xpath("//table[@class='pro_table_box datas_table']/tbody/tr[13]/td[1]/a/@href").extract_first().split("/")[-1]
			except:
				project_bids["bids_agency_name"] = None
		# 招标代理单位组织机构代码
		project_bids["bids_agency_num"] = response.xpath("//table[@class='pro_table_box datas_table']/tbody/tr[13]/td[2]/text()").extract_first()
		# 项目经理/总监理工程师四库一id
		project_bids["pm_id"] = None
		# 项目经理/总监理工程师姓名
		try:
			project_bids["pm_name"] = response.xpath("//table[@class='pro_table_box datas_table']/tbody/tr[15]/td[1]/text()").extract_first().strip()
		except:
			try:
				project_bids["pm_name"] = response.xpath("//table[@class='pro_table_box datas_table']/tbody/tr[15]/td[1]/a/text()").extract_first().strip()
				project_bids["pm_id"] = response.xpath("//table[@class='pro_table_box datas_table']/tbody/tr[15]/td[1]/a/@href").extract_first().strip().split("/")[-1]
			except:
				project_bids["pm_name"] = None
		# 项目经理/总监理工程师身份证号码
		project_bids["pm_identification_id"] = response.xpath("//table[@class='pro_table_box datas_table']/tbody/tr[15]/td[2]/text()").extract_first()
		# 记录登记时间
		project_bids["record_date"] = response.xpath("//table[@class='pro_table_box datas_table']/tbody/tr[16]/td[1]/text()").extract_first()
		project_bids["bid_company_id"]= str(response.xpath("//table[@class='pro_table_box datas_table']/tbody/tr[14]/td[1]/a/@href").extract_first()).split("/")[-1]
		try:
			project_bids["bid_company_name"] = response.xpath("//table[@class='pro_table_box datas_table']/tbody/tr[16]/td[1]/a/text()").extract_first()
		except:
			project_bids["bid_company_name"]= response.xpath("//table[@class='pro_table_box datas_table']/tbody/tr[16]/td[1]/text()").extract_first()
		project_bids["bid_company_num"]= response.xpath("//table[@class='pro_table_box datas_table']/tbody/tr[14]/td[2]/text()").extract_first()
		project_bids["create_time"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		project_bids["modification_time"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		project_bids["status"] = 1
		project_bids["is_delete"] = 0
		yield project_bids
	#解析施工图纸审查信息
	def parse_construction_review_url(self,response):
		#print("正在解析施工图纸审查信息----" + response.url)
		project_pdraw=ProjectConstructeDrawing()
		project_pdraw["project_id"] = response.meta["project_id"]
		project_pdraw["constructe_drawing_company_id"] =response.xpath("//div[@class='query_info_box']/table/tbody/tr[8]/td[1]/a/text()").extract_first()
		try:
			project_pdraw["constructe_drawing_company_name"] =response.xpath("//div[@class='query_info_box']/table/tbody/tr[8]/td[1]/a/text()").extract_first()
		except:
			project_pdraw["constructe_drawing_company_name"] = response.xpath("//div[@class='query_info_box']/table/tbody/tr[8]/td[1]/text()").extract_first()
		project_pdraw["constructe_drawing_company_num"] =response.xpath("//div[@class='query_info_box']/table/tbody/tr[8]/td[2]/text()").extract_first()
		project_pdraw["constructe_drawing_num"] =response.xpath("//div[@class='query_info_box']/table/tbody/tr[9]/td[1]/text()").extract_first()
		project_pdraw["province_constructe_drawing_num"] =response.xpath("//div[@class='query_info_box']/table/tbody/tr[9]/td[2]/text()").extract_first()
		project_pdraw["review_complete_date"] =response.xpath("//div[@class='query_info_box']/table/tbody/tr[10]/td[1]/text()").extract_first()
		project_pdraw["construction_scale"] =response.xpath("//div[@class='query_info_box']/table/tbody/tr[11]/td[1]/text()").extract_first()
		project_pdraw["url"]=response.url
		project_pdraw["create_time"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		project_pdraw["modification_time"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		project_pdraw["status"] = 1
		project_pdraw["is_delete"] = 0
		yield project_pdraw
		tr1_list = response.xpath("//div[@class='plr spmtop'][1]//tbody[@class='cursorDefault']/tr")
		for tr in tr1_list:
			project_main = ProjectMainCompany()
			#主体单位角色
			project_main["company_role"] = tr.xpath("./td[@data-header='涉及单位']/text()").extract_first()
			# 主体单位id
			c_id = str(tr.xpath("./td[@data-header='企业名称']/a/@href").extract_first())
			project_main["company_id"] = c_id.split("/")[-1]
			# 主体单位名称
			project_main["company_name"] = tr.xpath("./td[@data-header='企业名称']/a/text()").extract_first()
			if project_main["company_name"] is None:
				project_main["company_name"] = str(tr.xpath("./td[@data-header='企业名称']/text()").extract_first()).strip()
			else:
				project_main["company_name"] = str(tr.xpath("./td[@data-header='企业名称']/a/text()").extract_first()).strip()
			# 主体单位组织机构代码
			project_main["company_num"] = tr.xpath("./td[@data-header='组织机构代码']/text()").extract_first()
			# 主体单位所属省份
			project_main["company_province"] = tr.xpath("./td[@data-header='所在省份']/text()").extract_first()
			#阶段
			project_main["project_stage"] ="施工图审查"
			#项目id
			project_main["project_id"] = response.meta["project_id"]
			project_main["create_time"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
			project_main["modification_time"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
			project_main["status"] = 1
			project_main["is_delete"] = 0
			project_main["id"]=project_pdraw["constructe_drawing_num"]
			yield project_main
		cuo=str(response.xpath("//div[@class='plr spmtop'][2]//tbody[@class='cursorDefault']/tr/td/text()").extract_first())
		if not cuo=="暂未查询到已登记入库信息":
			tr2_list = response.xpath("//div[@class='plr spmtop'][2]//tbody[@class='cursorDefault']/tr")
			for tr in tr2_list:
				project_person=ProjectPerson()
				project_person["company_id"] = tr.xpath("./td[@data-header='所在企业']/a/@href").extract_first()
				project_person["person_id"] = str(tr.xpath("./td[@data-header='姓名']/a/@href").extract_first()).split("/")[-1]
				project_person["project_id"] =response.meta["project_id"]
				project_person["company_name"] = tr.xpath("./td[@data-header='所在企业']/a/text()").extract_first()
				if project_person["company_name"] is None:
					project_person["company_name"] = tr.xpath("./td[@data-header='所在企业']/text()").extract_first()
				project_person["major_name"] = tr.xpath("./td[@data-header='专业名称']/text()").extract_first()
				project_person["role"] = tr.xpath("./td[@data-header='担任角色']/text()").extract_first()
				project_person["person_name"] = tr.xpath("./td[@data-header='姓名']/a/text()").extract_first()
				if project_person["person_name"] is None:
					project_person["person_name"]=str(tr.xpath("./td[@data-header='姓名']/text()").extract_first()).strip()
				project_person["certificate_seal_id"] = tr.xpath("./td[@data-header='执业印章号']/text()").extract_first()
				project_person["project_stage"] = "施工图审查"
				project_person["certificate_type"]=tr.xpath("./td[@data-header='注册类型及等级']/text()").extract_first()
				project_person["identification_id"] = tr.xpath("./td[@data-header='证件号码']/text()").extract_first()
				project_person["create_time"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
				project_person["modification_time"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
				project_person["status"] = 1
				project_person["is_delete"] = 0
				project_person["id"]=project_pdraw["constructe_drawing_num"]
				yield project_person
	#解析合同备案信息
	def parse_contract_record_url(self,response):
		project_record=ProjectContractRecord()
		# 项目编号（项目id）
		project_record["project_id"] = response.meta["project_id"]
		# 合同备案编号
		project_record["contract_record_num"] = response.xpath("//table[@class='pro_table_box datas_table']/tbody/tr[8]/td[1]/text()").extract_first()
		# 省级合同备案编号
		project_record["province_contract_record_num"] = response.xpath("//table[@class='pro_table_box datas_table']/tbody/tr[8]/td[2]/text()").extract_first()
		# 合同编号
		project_record["contract_num"] = response.xpath("//table[@class='pro_table_box datas_table']/tbody/tr[9]/td[1]/text()").extract_first()
		# 合同分类
		project_record["contract_classify"] = response.xpath("//table[@class='pro_table_box datas_table']/tbody/tr[9]/td[2]/text()").extract_first()
		# 合同类别
		project_record["contract_type"] = response.xpath("//table[@class='pro_table_box datas_table']/tbody/tr[10]/td[1]/text()").extract_first()
		# 合同金额（万元）
		project_record["contract_money"] = response.xpath("//table[@class='pro_table_box datas_table']/tbody/tr[10]/td[2]/text()").extract_first()
		# 建设规模
		project_record["construction_scale"] = response.xpath("//table[@class='pro_table_box datas_table']/tbody/tr[11]/td[1]/text()").extract_first()
		# 合同签订日期
		project_record["contract_signing_date"] = response.xpath("//table[@class='pro_table_box datas_table']/tbody/tr[12]/td[1]/text()").extract_first()
		# 发包单位四库一id
		project_record["send_company_id"] = response.xpath("//table[@class='pro_table_box datas_table']/tbody/tr[13]/td[1]/a/@href").extract_first()
		# 发包单位名称
		project_record["send_company_name"] = str(response.xpath("//table[@class='pro_table_box datas_table']/tbody/tr[13]/td[1]/text()").extract_first()).strip()
		if project_record["send_company_id"] is not None:
			project_record["send_company_id"]=str(project_record["send_company_id"]).split("/")[-1]
			project_record["send_company_name"] = response.xpath("//table[@class='pro_table_box datas_table']/tbody/tr[13]/td[1]/a/text()").extract_first()
		# 发包单位组织机构代码
		project_record["send_company_num"] = response.xpath("//table[@class='pro_table_box datas_table']/tbody/tr[13]/td[2]/text()").extract_first()
		# 承包单位四库一id
		project_record["accept_company_id"] = response.xpath("//table[@class='pro_table_box datas_table']/tbody/tr[14]/td[1]/a/@href").extract_first()
		# 承包单位名称
		project_record["accept_company_name"] = str(response.xpath("//table[@class='pro_table_box datas_table']/tbody/tr[14]/td[1]/text()").extract_first()).strip()
		if project_record["accept_company_id"] is not None:
			project_record["accept_company_id"]=str(project_record["accept_company_id"]).split("/")[-1]
			project_record["accept_company_name"]=response.xpath("//table[@class='pro_table_box datas_table']/tbody/tr[14]/td[1]/a/text()").extract_first()
		# 承包单位组织机构代码
		project_record["accept_company_num"] = response.xpath("//table[@class='pro_table_box datas_table']/tbody/tr[14]/td[2]/text()").extract_first()
		# 联合体承包单位id
		project_record["unitaccept_company_id"] = response.xpath("//table[@class='pro_table_box datas_table']/tbody/tr[15]/td[1]/a/@href").extract_first()
		# 联合体承包单位名称
		project_record["unitaccept_company_name"] = str(response.xpath("//table[@class='pro_table_box datas_table']/tbody/tr[15]/td[1]/text()").extract_first()).strip()
		if project_record["unitaccept_company_id"] is not None:
			project_record["unitaccept_company_id"] = str(project_record["unitaccept_company_id"]).split("/")[-1]
			project_record["unitaccept_company_name"]= response.xpath("//table[@class='pro_table_box datas_table']/tbody/tr[15]/td[1]/a/text()").extract_first()
		# 联合体承包单位组织机构代码
		project_record["unitaccept_company_num"] = response.xpath("//table[@class='pro_table_box datas_table']/tbody/tr[15]/td[2]/text()").extract_first()
		# 记录登记时间
		project_record["record_date"] = response.xpath("//table[@class='pro_table_box datas_table']/tbody/tr[16]/td[1]/text()").extract_first()
		project_record["url"]=response.url
		project_record["create_time"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		project_record["modification_time"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		project_record["status"] = 1
		project_record["is_delete"] = 0
		yield project_record
	#解析施工许可信息
	def parse_construction_permit_url(self,response):
		project_lic=ProjectConstructeLicence()
		# 项目编号（项目id）
		project_lic["project_id"] = response.meta["project_id"]
		# 发证日期
		project_lic["certificate_date"] = response.meta["certificate_date"]
		# 施工许可证编号
		project_lic["constructe_licence_num"] = response.xpath("//div[@class='query_info_box']/table/tbody/tr[8]/td[1]/text()").extract_first()
		# 省级施工许可证编号
		project_lic["province_constructe_licence_num"] = response.xpath("//div[@class='query_info_box']/table/tbody/tr[8]/td[2]/text()").extract_first()
		# 合同金额（万元）
		project_lic["contract_money"] = response.xpath("//div[@class='query_info_box']/table/tbody/tr[9]/td[2]/text()").extract_first()
		# 项目经理
		project_lic["pm_name"] = str(response.xpath("//div[@class='query_info_box']/table/tbody/tr[10]/td[1]/text()").extract_first()).strip()
		# 项目经理id
		project_lic["pm_id"] = response.xpath("//div[@class='query_info_box']/table/tbody/tr[10]/td[1]/a/@href").extract_first()
		if project_lic["pm_id"] is not None:
			project_lic["pm_id"]=str(project_lic["pm_id"]).split("/")[-1]
			project_lic["pm_name"]=response.xpath("//div[@class='query_info_box']/table/tbody/tr[10]/td[1]/a/text()").extract_first()
		# 项目经理身份证号
		project_lic["pm_identification_id"] = response.xpath("//div[@class='query_info_box']/table/tbody/tr[10]/td[2]/text()").extract_first()
		# 项目总监
		project_lic["pd_name"] = str(response.xpath("//div[@class='query_info_box']/table/tbody/tr[11]/td[1]/text()").extract_first()).strip()
		# 项目总监id
		project_lic["pd_id"] = response.xpath("//div[@class='query_info_box']/table/tbody/tr[11]/td[1]/a/@href").extract_first()
		if project_lic["pd_id"] is not None:
			project_lic["pd_id"]=str(project_lic["pd_id"]).split("/")[-1]
			project_lic["pd_name"] = response.xpath("//div[@class='query_info_box']/table/tbody/tr[11]/td[1]/a/text()").extract_first()
		# 项目总监身份证号
		project_lic["pd_identification_id"] = response.xpath("//div[@class='query_info_box']/table/tbody/tr[11]/td[2]/text()").extract_first()
		# 面积（平方米）
		project_lic["area"] = response.xpath("//div[@class='query_info_box']/table/tbody/tr[12]/td[1]/text()").extract_first()
		# 记录登记时间
		project_lic["record_date"] = response.xpath("//div[@class='query_info_box']/table/tbody/tr[12]/td[2]/text()").extract_first()
		project_lic["url"]=response.url
		project_lic["create_time"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		project_lic["modification_time"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		project_lic["status"] = 1
		project_lic["is_delete"] = 0
		yield project_lic

		tr1_list = response.xpath("//div[@class='plr spmtop'][1]//tbody[@class='cursorDefault']/tr")
		for tr in tr1_list:
			project_main = ProjectMainCompany()
			# 主体单位角色
			project_main["company_role"] = tr.xpath("./td[@data-header='涉及单位']/text()").extract_first()
			# 主体单位id
			c_id = str(tr.xpath("./td[@data-header='企业名称']/a/@href").extract_first())
			project_main["company_id"] = c_id.split("/")[-1]
			# 主体单位名称
			project_main["company_name"] = tr.xpath("./td[@data-header='企业名称']/a/text()").extract_first()
			if project_main["company_name"] is None:
				project_main["company_name"] = str(tr.xpath("./td[@data-header='企业名称']/text()").extract_first()).strip()
			else:
				project_main["company_name"] = str(
					tr.xpath("./td[@data-header='企业名称']/a/text()").extract_first()).strip()
			# 主体单位组织机构代码
			project_main["company_num"] = tr.xpath("./td[@data-header='组织机构代码']/text()").extract_first()
			# 主体单位所属省份
			project_main["company_province"] = tr.xpath("./td[@data-header='所在省份']/text()").extract_first()
			# 阶段
			project_main["project_stage"] = "施工许可"
			# 项目id
			project_main["project_id"] = response.meta["project_id"]
			project_main["create_time"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
			project_main["modification_time"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
			project_main["status"] = 1
			project_main["is_delete"] = 0
			project_main["id"]=project_lic["constructe_licence_num"]
			yield project_main
		cuo = response.xpath("//div[@class='plr spmtop'][2]//tbody[@class='cursorDefault']/tr/td/text()").extract_first()
		if cuo is not None:
			tr2_list = response.xpath("//div[@class='plr spmtop'][2]//tbody[@class='cursorDefault']/tr")
			for tr in tr2_list:
				project_person = ProjectPerson()
				project_person["company_id"] = tr.xpath("./td[@data-header='所在企业']/a/@href").extract_first()
				project_person["person_id"] = str(tr.xpath("./td[@data-header='姓名']/a/@href").extract_first()).split("/")[-1]
				project_person["project_id"] = response.meta["project_id"]
				project_person["company_name"] = tr.xpath("./td[@data-header='所在企业']/a/text()").extract_first()
				if project_person["company_name"] is None:
					project_person["company_name"] = tr.xpath("./td[@data-header='所在企业']/text()").extract_first()
				project_person["major_name"] = tr.xpath("./td[@data-header='专业名称']/text()").extract_first()
				project_person["role"] = tr.xpath("./td[@data-header='担任角色']/text()").extract_first()
				project_person["person_name"] = tr.xpath("./td[@data-header='姓名']/a/text()").extract_first()
				if project_person["person_name"] is None:
					project_person["person_name"] = str(tr.xpath("./td[@data-header='姓名']/text()").extract_first()).strip()
				project_person["certificate_seal_id"] = tr.xpath("./td[@data-header='执业印章号']/text()").extract_first()
				project_person["project_stage"] = "施工许可"
				project_person["certificate_type"] = tr.xpath("./td[@data-header='注册类型及等级']/text()").extract_first()
				project_person["create_time"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
				project_person["modification_time"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
				project_person["status"] = 1
				project_person["is_delete"] = 0
				project_person["id"]=project_lic["constructe_licence_num"]
				yield project_person
	#解析竣工验收备案
	def parse_complete_url(self,response):
		project_com=ProjectCompleteRecord()
		# 项目编号（项目id）
		project_com["project_id"] = response.meta["project_id"]
		# 竣工备案编号
		project_com["complete_record_num"] = response.xpath("//div[@class='query_info_box']/table/tbody/tr[8]/td[1]/text()").extract_first()
		# 省级竣工备案编号
		project_com["province_complete_record_num"] = str(response.xpath("//div[@class='query_info_box']/table/tbody/tr[8]/td[2]/text()").extract_first()).strip()
		# 实际造价（万元）
		project_com["actual_cost"] = response.xpath("//div[@class='query_info_box']/table/tbody/tr[9]/td[1]/text()").extract_first()
		# 实际面积（平方米）
		project_com["actual_area"] = response.xpath("//div[@class='query_info_box']/table/tbody/tr[9]/td[2]/text()").extract_first()
		# 实际建设规模
		project_com["actual_scale_of_construction"] = response.xpath("//div[@class='query_info_box']/table/tbody/tr[10]/td[1]/text()").extract_first()
		# 结构体系
		project_com["structural_system"] = response.xpath("//div[@class='query_info_box']/table/tbody/tr[11]/td[1]/text()").extract_first()
		# 实际开工日期
		project_com["actual_start_date"] = response.xpath("//div[@class='query_info_box']/table/tbody/tr[12]/td[1]/text()").extract_first()
		# 实际竣工验收日期
		project_com["actual_complete_date"] = response.xpath("//div[@class='query_info_box']/table/tbody/tr[12]/td[2]/text()").extract_first()
		# 记录登记时间
		project_com["record_date"] = response.xpath("//div[@class='query_info_box']/table/tbody/tr[13]/td[1]/text()").extract_first()
		project_com["remark"] = response.xpath("//div[@class='query_info_box']/table/tbody/tr[13]/td[2]/text()").extract_first()
		project_com["create_time"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		project_com["modification_time"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		project_com["status"] = 1
		project_com["is_delete"] = 0
		yield project_com
		tr1_list = response.xpath("//div[@class='plr spmtop'][1]//tbody[@class='cursorDefault']/tr")
		for tr in tr1_list:
			project_main = ProjectMainCompany()
			# 主体单位角色
			project_main["company_role"] = tr.xpath("./td[@data-header='涉及单位']/text()").extract_first()
			# 主体单位id
			c_id = str(tr.xpath("./td[@data-header='企业名称']/a/@href").extract_first())
			project_main["company_id"] = c_id.split("/")[-1]
			# 主体单位名称
			project_main["company_name"] = tr.xpath("./td[@data-header='企业名称']/a/text()").extract_first()
			if project_main["company_name"] is None:
				project_main["company_name"] = str(tr.xpath("./td[@data-header='企业名称']/text()").extract_first()).strip()
			else:
				project_main["company_name"] = str(
					tr.xpath("./td[@data-header='企业名称']/a/text()").extract_first()).strip()
			# 主体单位组织机构代码
			project_main["company_num"] = tr.xpath("./td[@data-header='组织机构代码']/text()").extract_first()
			# 主体单位所属省份
			project_main["company_province"] = tr.xpath("./td[@data-header='所在省份']/text()").extract_first()
			# 阶段
			project_main["project_stage"] = "竣工验收备案"
			# 项目id
			project_main["project_id"] = response.meta["project_id"]
			project_main["create_time"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
			project_main["modification_time"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
			project_main["status"] = 1
			project_main["is_delete"] = 0
			project_main["id"] = project_com["complete_record_num"]
			yield project_main
		cuo = response.xpath("//div[@class='plr spmtop'][2]//tbody[@class='cursorDefault']/tr/td/text()").extract_first()
		if cuo is not None:
			tr2_list = response.xpath("//div[@class='plr spmtop'][2]//tbody[@class='cursorDefault']/tr")
			for tr in tr2_list:
				project_person = ProjectPerson()
				project_person["company_id"] = tr.xpath("./td[@data-header='所在企业']/a/@href").extract_first()
				project_person["person_id"] = str(tr.xpath("./td[@data-header='姓名']/a/@href").extract_first()).split("/")[-1]
				project_person["project_id"] = response.meta["project_id"]
				project_person["company_name"] = tr.xpath("./td[@data-header='所在企业']/a/text()").extract_first()
				if project_person["company_name"] is None:
					project_person["company_name"] = tr.xpath("./td[@data-header='所在企业']/text()").extract_first()
				project_person["major_name"] = tr.xpath("./td[@data-header='专业名称']/text()").extract_first()
				project_person["role"] = tr.xpath("./td[@data-header='担任角色']/text()").extract_first()
				project_person["person_name"] = tr.xpath("./td[@data-header='姓名']/a/text()").extract_first()
				if project_person["person_name"] is None:
					project_person["person_name"] = str(tr.xpath("./td[@data-header='姓名']/text()").extract_first()).strip()
				project_person["certificate_seal_id"] = tr.xpath("./td[@data-header='执业印章号']/text()").extract_first()
				project_person["project_stage"] = "竣工验收备案"
				project_person["certificate_type"] = tr.xpath("./td[@data-header='注册类型及等级']/text()").extract_first()
				project_person["create_time"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
				project_person["modification_time"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
				project_person["status"] = 1
				project_person["is_delete"] = 0
				project_person["id"]=project_com["complete_record_num"]
				yield project_person
	#解析人员黑名单记录
	def parse_person_blacklist(self,response):
		cuo = response.xpath("//tbody[@class='cursorDefault']/tr[1]/td/text()").extract_first()
		if cuo != "暂未查询到已登记入库信息":
			tr_list = response.xpath("//tbody[@class='cursorDefault']/tr")
			for tr in tr_list:
				behavior = BehaviorItem()
				behavior["record_num"] = str(tr.xpath("./td[1]/text()").extract_first()).strip()
				behavior["id"] = tr.xpath("./td[2]/a/@href").extract_first()
				behavior["record_main"] = tr.xpath("./td[2]/a/text()").extract_first()
				if behavior["record_main"] is None:
					behavior["record_main"] = str(tr.xpath("./td[2]/text()").extract_first()).strip()
					behavior["id"] = str(tr.xpath("./td[2]/a/@href").extract_first()).split("/")[-1]
				else:
					behavior["id"] = str(tr.xpath("./td[2]/a/@href").extract_first()).split("/")[-1]
					behavior["record_main"] = str(tr.xpath("./td[2]/a/text()").extract_first()).strip()
				behavior["content"] = str(tr.xpath("./td[3]")[0].xpath("string(.)").extract_first()).strip()
				behavior["department"] = tr.xpath("./td[4]/text()").extract_first()
				behavior["useful_date"] = None
				behavior["in_date"] = tr.xpath("./td[5]/text()").extract_first()
				behavior["out_date"] = tr.xpath("./td[6]/text()").extract_first()
				behavior["legal_person"] = None
				behavior["legal_person_idcard"] = None
				behavior["reason"] = response.meta.get("reason")
				behavior["create_time"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
				behavior["modification_time"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
				behavior["status"] = 1
				behavior["is_delete"] = 0
				yield behavior