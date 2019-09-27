import scrapy
#企业基本信息
class CompanyInformation(scrapy.Item):
    collection="companyinformation"
    company_id=scrapy.Field()
    company_name=scrapy.Field()
    social_credit_code=scrapy.Field()
    leal_person=scrapy.Field()
    regis_address=scrapy.Field()
    business_address=scrapy.Field()
    regis_type=scrapy.Field()
    url=scrapy.Field()
    create_time=scrapy.Field()
    modification_time=scrapy.Field()
    status=scrapy.Field()
    is_delete=scrapy.Field()
#企业资质
class CompanyAptitude(scrapy.Item):
    collection = "companyaptitude"
    company_id=scrapy.Field()
    aptitude_type=scrapy.Field()
    aptitude_id=scrapy.Field()
    aptitude_name=scrapy.Field()
    aptitude_startime=scrapy.Field()
    aptitude_endtime=scrapy.Field()
    aptitude_organ=scrapy.Field()
    url=scrapy.Field()
    create_time=scrapy.Field()
    modification_time=scrapy.Field()
    status=scrapy.Field()
    is_delete=scrapy.Field()
#企业备案地
class CompanyProvinceRecord(scrapy.Item):
    collection = "companyprovincerecord"
    company_id=scrapy.Field()
    province=scrapy.Field()
    create_time=scrapy.Field()
    modification_time=scrapy.Field()
    status=scrapy.Field()
    is_delete=scrapy.Field()
#人员基本信息
class PersonInformation(scrapy.Item):
    collection = "personinformation"
    person_id=scrapy.Field()
    company_id = scrapy.Field()
    person_name=scrapy.Field()
    person_sex=scrapy.Field()
    person_identification_type=scrapy.Field()
    person_identification_id=scrapy.Field()
    create_time=scrapy.Field()
    modification_time=scrapy.Field()
    status=scrapy.Field()
    is_delete=scrapy.Field()
#人员执业证书信息
class PersonCertificate(scrapy.Item):
    collection = "personcertificate"
    certificate_num = scrapy.Field()
    person_id=scrapy.Field()
    major=scrapy.Field()
    aptitude_name=scrapy.Field()
    certificate_seal_id=scrapy.Field()
    certificate_useful_time=scrapy.Field()
    certificate_company_name=scrapy.Field()
    certificate_company_id=scrapy.Field()
    create_time=scrapy.Field()
    modification_time=scrapy.Field()
    status=scrapy.Field()
    is_delete=scrapy.Field()
#项目基本信息
class ProjectInformation(scrapy.Item):
    collection = "projectinformation"
    project_id=scrapy.Field()
    company_id=scrapy.Field()
    bidding_company_id=scrapy.Field()
    project_name=scrapy.Field()
    provincial_project_num=scrapy.Field()
    region_province=scrapy.Field()
    region_city=scrapy.Field()
    region_county=scrapy.Field()
    constructe_company=scrapy.Field()
    constructe_company_credit_code=scrapy.Field()
    project_type=scrapy.Field()
    project_nature=scrapy.Field()
    project_purpose=scrapy.Field()
    total_investment=scrapy.Field()
    total_area=scrapy.Field()
    project_level=scrapy.Field()
    project_reference_num=scrapy.Field()
    url=scrapy.Field()
    create_time=scrapy.Field()
    modification_time=scrapy.Field()
    status=scrapy.Field()
    is_delete=scrapy.Field()
#项目招投标信息
class ProjectBidsInformation(scrapy.Item):
    collection = "projectbidsinformation"
    project_id=scrapy.Field()
    bid_notification_num=scrapy.Field()
    province_bid_notification_num=scrapy.Field()
    bids_type=scrapy.Field()
    bids_method=scrapy.Field()
    bid_money=scrapy.Field()
    bid_date=scrapy.Field()
    scale_of_construction=scrapy.Field()
    area=scrapy.Field()
    bids_agency_id=scrapy.Field()
    bids_agency_name=scrapy.Field()
    bids_agency_num=scrapy.Field()
    pm_id=scrapy.Field()
    pm_name=scrapy.Field()
    pm_identification_id=scrapy.Field()
    record_date=scrapy.Field()
    bid_company_id = scrapy.Field()
    bid_company_name=scrapy.Field()
    bid_company_num=scrapy.Field()
    url=scrapy.Field()
    create_time=scrapy.Field()
    modification_time=scrapy.Field()
    status=scrapy.Field()
    is_delete=scrapy.Field()
#项目施工图纸审查信息
class ProjectConstructeDrawing(scrapy.Item):
    collection = "projectconstructedrawing"
    project_id=scrapy.Field()
    constructe_drawing_company_id=scrapy.Field()
    constructe_drawing_company_name=scrapy.Field()
    constructe_drawing_company_num=scrapy.Field()
    constructe_drawing_num=scrapy.Field()
    province_constructe_drawing_num=scrapy.Field()
    review_complete_date=scrapy.Field()
    construction_scale=scrapy.Field()
    url=scrapy.Field()
    create_time=scrapy.Field()
    modification_time=scrapy.Field()
    status=scrapy.Field()
    is_delete=scrapy.Field()
#项目从业人员信息
class ProjectPerson(scrapy.Item):
    collection = "projectperson"
    person_id = scrapy.Field()
    project_id = scrapy.Field()
    company_id=scrapy.Field()
    company_name=scrapy.Field()
    major_name=scrapy.Field()
    role=scrapy.Field()
    person_name=scrapy.Field()
    certificate_seal_id=scrapy.Field()
    aptitude_name = scrapy.Field()
    project_stage=scrapy.Field()
    identification_id=scrapy.Field()
    create_time=scrapy.Field()
    modification_time=scrapy.Field()
    status=scrapy.Field()
    is_delete=scrapy.Field()
    id=scrapy.Field()
#项目合同备案信息
class ProjectContractRecord(scrapy.Item):
    collection = "projectcontractrecord"
    project_id=scrapy.Field()
    contract_record_num=scrapy.Field()
    province_contract_record_num=scrapy.Field()
    contract_num=scrapy.Field()
    contract_classify=scrapy.Field()
    contract_type=scrapy.Field()
    contract_money=scrapy.Field()
    construction_scale=scrapy.Field()
    contract_signing_date=scrapy.Field()
    send_company_id=scrapy.Field()
    send_company_name=scrapy.Field()
    send_company_num=scrapy.Field()
    accept_company_id=scrapy.Field()
    accept_company_name=scrapy.Field()
    accept_company_num=scrapy.Field()
    unitaccept_company_id=scrapy.Field()
    unitaccept_company_name=scrapy.Field()
    unitaccept_company_num=scrapy.Field()
    record_date=scrapy.Field()
    url=scrapy.Field()
    create_time=scrapy.Field()
    modification_time=scrapy.Field()
    status=scrapy.Field()
    is_delete=scrapy.Field()
#项目施工许可信息
class ProjectConstructeLicence(scrapy.Item):
    collection = "projectconstructelicence"
    project_id=scrapy.Field()
    certificate_date=scrapy.Field()
    constructe_licence_num=scrapy.Field()
    province_constructe_licence_num=scrapy.Field()
    contract_money=scrapy.Field()
    pm_name=scrapy.Field()
    pm_id=scrapy.Field()
    pm_identification_id=scrapy.Field()
    pd_name=scrapy.Field()
    pd_id=scrapy.Field()
    pd_identification_id=scrapy.Field()
    area=scrapy.Field()
    record_date=scrapy.Field()
    url=scrapy.Field()
    create_time=scrapy.Field()
    modification_time=scrapy.Field()
    status=scrapy.Field()
    is_delete=scrapy.Field()
#项目竣工验收备案
class ProjectCompleteRecord(scrapy.Item):
    collection = "projectcompleterecord"
    project_id=scrapy.Field()
    complete_record_num=scrapy.Field()
    province_complete_record_num=scrapy.Field()
    actual_cost=scrapy.Field()
    actual_area=scrapy.Field()
    actual_scale_of_construction=scrapy.Field()
    structural_system=scrapy.Field()
    actual_start_date=scrapy.Field()
    actual_complete_date=scrapy.Field()
    record_date=scrapy.Field()
    remark=scrapy.Field()
    url=scrapy.Field()
    create_time=scrapy.Field()
    modification_time=scrapy.Field()
    status=scrapy.Field()
    is_delete=scrapy.Field()
#企业主体信息
class ProjectMainCompany(scrapy.Item):
    collection = "projectmaincompany"
    project_id=scrapy.Field()
    company_id=scrapy.Field()
    company_role=scrapy.Field()
    company_name=scrapy.Field()
    company_num=scrapy.Field()
    company_province=scrapy.Field()
    project_stage=scrapy.Field()
    create_time = scrapy.Field()
    modification_time = scrapy.Field()
    status = scrapy.Field()
    is_delete = scrapy.Field()
    id=scrapy.Field()
#行为信息
class BehaviorItem(scrapy.Item):
    collection = "behavioritem"
    main_id = scrapy.Field()
    record_main = scrapy.Field()
    main_type = scrapy.Field()
    record_name = scrapy.Field()
    record_type = scrapy.Field()
    reason = scrapy.Field()
    reason_type = scrapy.Field()
    content = scrapy.Field()
    department = scrapy.Field()
    publish_date = scrapy.Field()
    useful_date = scrapy.Field()
    in_date = scrapy.Field()
    out_date = scrapy.Field()
    legal_person = scrapy.Field()
    legal_person_idcard = scrapy.Field()
    source = scrapy.Field()
    relevant_project = scrapy.Field()
    relevant_person = scrapy.Field()
    area_code = scrapy.Field()
    url = scrapy.Field()
    status = scrapy.Field()
    created_at = scrapy.Field()
    creator = scrapy.Field()
    updated_at = scrapy.Field()
    record_num = scrapy.Field()
    refer_num = scrapy.Field()

#变更信息
class ChangeItem(scrapy.Item):
    collection = "changeitem"
    id=scrapy.Field()
    registe_type=scrapy.Field()
    change_certificate_num=scrapy.Field()
    change_time=scrapy.Field()
    change_record=scrapy.Field()
    chenge_subject=scrapy.Field()
    create_time=scrapy.Field()
    modification_time=scrapy.Field()
    status=scrapy.Field()
    is_delete=scrapy.Field()





