#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""csv文件导入redmine 工具
@version: @Id$
@author: U{mujun<mailto:360144561@qq.com>}
@license:GPL
@contact:360144561@qq.com
@see:
"""

import os,re,sys
import mechanize
import cookielib

cfg = None
is_send_mail = False
is_add_category = False
is_add_version = False
is_update_issue = False


def init_conifg(ini_cfg = None,file = "config.ini"):
	"""
	初始化配置 
		@param 	ini_cfg	:给定一个配置实例，如果有就直接使用该实例
				file 	：给定一个配置文件路径，只有在没有给定 cfg实例参数是才起作用
		@type 	ini_cfg ：ConfigParser d
				file	:string
		@return none
		@rtype 	none
	"""
	global cfg,is_send_mail,is_add_category,is_add_version,is_update_issue
	if not ini_cfg:
		import ConfigParser 
		ini_cfg = ConfigParser.ConfigParser()
		ini_cfg.read(file)
	cfg = ini_cfg
	#初始化上传文件配置
	is_send_mail = cfg.getboolean("redmine","IS_SEND_MAIL")
	is_add_category = cfg.getboolean("redmine","IS_ADD_CATEGORY")
	is_add_version = cfg.getboolean("redmine","IS_ADD_VERSION")
	is_update_issue = cfg.getboolean("redmine","IS_UPDATE_ISSUE")

def init_br():
	"""
	初始化浏览器对象
		@param 	none
		@type 	none
		@return none
		@rtype 	none
	"""
	br = mechanize.Browser(factory=mechanize.RobustFactory())
	# Cookie Jar
	cj = cookielib.LWPCookieJar()
	br.set_cookiejar(cj)

	# Browser options
	br.set_handle_equiv(True)
	br.set_handle_gzip(False)
	br.set_handle_redirect(True)
	br.set_handle_referer(True)
	br.set_handle_robots(False)

	# Follows refresh 0 but not hangs on refresh > 0
	br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

	# Want debugging messages?
	#br.set_debug_http(True)
	#br.set_debug_redirects(True)
	#br.set_debug_responses(True)
	
	br._factory.encoding = "utf8"
	br._factory._forms_factory.encoding = "utf8"
	br._factory._links_factory._encoding = "utf8"
	
	# User-Agent (this is cheating, ok?)
	#br.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 6.1; rv:15.0) Gecko/20100101 Firefox/15.0')]
	#br.add_password(cfg.get("redmine","REDMINE_HOST"),cfg.get("redmine","USER_NAME"),cfg.get("redmine","USER_PWD"))
	return br

def login_redmine(br,username="",pwd = ""):
	"""
	登陆redmine
		@param 	br		:当前的浏览器对象
				username:登录用的用户名
				pwd		:登录用的密码
		@type 	br		:mechanize.Browser
				username:str
				pwd		:str
		@return none
		@rtype 	none
	
	"""
	response = br.open(mechanize.urljoin(cfg.get("redmine","REDMINE_HOST"),"login"))
	br.select_form(nr=0)
	br.form["username"] = (username and  username) or cfg.get("redmine","USER_NAME")
	br.form["password"] = (pwd and pwd) or cfg.get("redmine","USER_PWD")
	login_response = br.submit()
	write_to(login_response.read(),"login.html")
	
def to_import(br,porject_key = None,file_path = None):

	"""
	进入的上传文件页，提交上传文件
		@param 	br		:当前的浏览器对象
				porject_key:需要执行操作的project的key 
				file_path	:上传文件的路径
		@type 	br		:mechanize.Browser
				porject_key	:str
				file_path	:str
		@return none
		@rtype 	none
	"""
	if not porject_key or not file_path:
		print "no param of porject_key or upload file path ,which project[file] you want to operate?"
		return
	print cfg.get("redmine","REDMINE_HOST"),porject_key
	response = br.open(mechanize.urljoin(cfg.get("redmine","REDMINE_HOST"),"importer?project_id="+porject_key))
	real_url = response.geturl()
	if real_url.rfind("/login?")>0:
		print "loginout ... "
		return False
	
	br.select_form(nr=1) #选择上传文件的表单
	upload_form = br.form
	
	#enc_control = upload_form.find_control("encoding",type="select")
	#enc_control.get("U").selected = True
	#upload_form["splitter"] =","
	#upload_form["wrapper"] ="\""
	
	upload_form.add_file(open(file_path,"rb"),"application/vnd.ms-excel",file_path,name="file")
	#print upload_form
	upload_response = br.submit()
	write_to(upload_response.read(),"upload.html")
	return True

def do_import(br,is_send_mail = False,is_add_category = False,is_add_version = True,is_update_issue =False ):
	""""
	设置 csv 文件的对应的列，csv文件的title 默认使用和redmine 中相符的名称。设置省略
	注意：br 浏览器对象，已经上传文件成功。
	
		@param 	br		:当前的浏览器对象
				is_send_mail:是否发送提醒邮件，测试期间默认是 False 
				is_add_category	:自动新增问题类别 默认 False 
				is_add_version	:自动新增目标版本 默认 True 
				is_update_issue :更新已存在的问题 默认 False 
		@type 	br		:mechanize.Browser
				is_send_mail:boolean
				is_add_category	:boolean
				is_add_version :boolean
				is_update_issue :boolean
		@return none
		@rtype 	none
	
	"""
	def get_import_result(htmlstr):
		re_result = re.compile("</h2>([\s\S]*)<hr/>",re.X)
		re_group = re_result.search(htmlstr)
		return re_group and re_group.group(1) or "没有导入结果"
	
	br.select_form(nr=1)
	import_form = br.form
	

	send_mail_control = import_form.find_control("send_emails",type="checkbox")
	send_mail_control.items[0].selected = is_send_mail # 发送邮件设置 
	
	add_categories_control = import_form.find_control("add_categories",type="checkbox")
	add_categories_control.items[0].selected = is_add_category # 自动新增问题类别
	
	add_versions_control = import_form.find_control("add_versions",type="checkbox")
	add_versions_control.items[0].selected = is_add_version # 自动新增目标版本
	
	update_issue_control = import_form.find_control("update_issue",type="checkbox")
	update_issue_control.items[0].selected = is_update_issue # 更新已存在的问题
	
	import_response = br.submit()
	import_htm = import_response.read()
	write_to(import_htm,"import.html")
	print get_import_result(import_htm)#导入结果，有待改进
	
def write_to(content,filep):
	"""
	将字符内容保存到文件中
		@param 	content		:需要写入的文件内容
				filep		: 文件路径
		@type 	content		:string
				filep		:str
		@return none
		@rtype 	nones
	"""
	file = open(filep,"w")
	file.write(content)
	file.close()

def batch_import(logined_br,batch_dict=None):
	"""
	批量上传文件到指定的项目
		@param 	batch_dict :按照dict的配置导入文件到项目
				logined_br :已经登陆的浏览器对象
		@type 	batch_dict :dict
				logined_br :mechanize.Browser
		@return none
		@rtype 	none
	"""
	
	for project in  batch_dict:
		por_file = batch_dict[project]
		if to_import(logined_br,project,por_file):
			do_import(logined_br,is_send_mail,is_add_category,is_add_version,is_update_issue)
		print "batch import form dict : import file: %s  to :%s over "%(por_file,project)
		
def batch_import_dir(logined_br,f_dir):
	"""
		@param 	f_dir :给定需要导入的文件夹
				logined_br :已经登陆的浏览器对象
		@type 	f_dir :str
				logined_br :mechanize.Browser
		@return none
		@rtype 	none
	"""

	pro_map = eval(cfg.get("project","PROJECT_MAP"))
	flist = [f_name for f_name in os.listdir(f_dir) if f_name.endswith('csv')]
	if not flist:
		print "in dir :",f_dir ,"not found .csv file ,please run mm2csv"
		return False
	for csv_f in flist :
		cvs_name = os.path.basename(csv_f)
		p_name = cvs_name[0:cvs_name.rfind(".")]
		pro_key = find_project_key(p_name,pro_map)
		if not pro_key :
			print u"can not find the csv file:"+p_name +"mapping project key ,skip this file"
			continue
		if to_import(logined_br,pro_key,csv_f):
			do_import(logined_br,is_send_mail,is_add_category,is_add_version,is_update_issue)
		print "batch import from dir ",f_dir," file :",csv_f ,"to porject:",pro_key
		

def find_project_key(chname,pro_map):
	"""
	通过项目的中文名称在给定的map 中查找key 
		@param 	chname:
				pro_map:给定查找的map
		@type 	chname :str
				pro_map: dict
		@return none
		@rtype 	none
	"""
	if pro_map.has_key(chname):
		return pro_map[chname]
	else:
		print "not found project name:",chname
	# for pro_name in pro_map:
		# if pro_name == chname:
			# print "find:"+pro_name
			# return pro_map[pro_name]
		
def main():
	"""
	执行默认的文件导入功能
	"""
	if not cfg:
		init_conifg()

	if not cfg:
		print "the cfg not init..."
		return
	br = init_br()
	login_redmine(br)
	
	def_pro_key = cfg.get("redmine","PROJECT_KEY")
	def_csv_file = cfg.get("redmine","CSV_FILE")
	if not def_csv_file or not def_pro_key: #如果没有配置需要上传的csv的文件，优先查找 redmine=>BATCH_DICT的配置
		batch_dict = eval(cfg.get("redmine","BATCH_DICT"))
		if batch_dict : #配置了批量上传字典
			batch_import(br,batch_dict)
		else :	#没有配置 redmine=>BATCH_DICT,默认找 mm=>OUT_DIR目录下所有 csv文件
			out_dir = get_out_dir(cfg)
			batch_import_dir(br,out_dir)
	else:
		if not os.path.exists(def_csv_file): #非绝对路径，只配置文件名
			def_csv_file = os.path.join(get_out_dir(cfg),def_csv_file)
		if to_import(br,def_pro_key,def_csv_file):
			do_import(br,is_send_mail,is_add_category,is_add_version,is_update_issue)

def get_out_dir(cfg):
	"""从 cfg 中获取配置的输出目录，如果没有默认是当前的脚本执行目录
		@param 	chname:
		@type 	chname :str
		@return none
		@rtype 	none
	"""
	out_dir = cfg.get("mm","OUT_DIR")
	return (out_dir and out_dir) or os.getcwd()
			
if __name__=="__main__":
	main()
	
	