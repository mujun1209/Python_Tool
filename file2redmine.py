#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os,re,sys
import mechanize
import cookielib

#redmine 的主域名
REDMINE_HOST =  "http://192.168.1.41:3000/"
#登陆redmine的用户名
USER_NAME = "muj"
#登陆密码
USER_PWD = "asdfjkl;"
#对应项目在redmine 中的自定义名称
PROJECT_KEY = "ms-tg-it-yf-mhsq-csy"
#要上传的csv文件的路径
CSV_FILE = "E:\\temp\\mmtest\\测试用1.csv"

#批量导入的项目名和文件
BATCH_DICT = {"ms-tg-it-yf-*":"filepath","p2":"f2"}

def init_br():
	"""
	初始化浏览器对象
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
	
	br.add_password(REDMINE_HOST,USER_NAME,USER_PWD)
	
	return br


def login_redmine(br,username="",pwd = ""):
	"""登陆redmine
	"""
	response = br.open(mechanize.urljoin(REDMINE_HOST,"login"))
	br.select_form(nr=0)
	br.form["username"] = (username and  username) or USER_NAME
	br.form["password"] = (pwd and pwd) or USER_PWD
	login_response = br.submit()
	write_to(login_response.read(),"login.html")
	#print loginresponse.info()

def to_import(br,porject_key = None,file_path = None):

	"""
	进入的上传文件页，提交上传文件
	"""
	porject_key = (porject_key and porject_key) or PROJECT_KEY
	
	response = br.open(mechanize.urljoin(REDMINE_HOST,"importer?project_id="+porject_key))
	print response.geturl()
	br.select_form(nr=1) #选择上传文件的表单
	upload_form = br.form
	
	enc_control = upload_form.find_control("encoding",type="select")
	#enc_control.get("U").selected = True
	
	#upload_form["splitter"] =","
	#upload_form["wrapper"] ="\""
	
	file_path = (file_path and file_path) or CSV_FILE
	
	upload_form.add_file(open(file_path,"rb"),"application/vnd.ms-excel",file_path,name="file")
	
	#print upload_form
	
	upload_response = br.submit()
	write_to(upload_response.read(),"upload.html")

def do_import(br,is_send_mail = False,is_add_category = False,is_add_version = True,is_update_issue =False ):
	""""
	设置 csv 文件的对应的列，csv文件的title 默认使用和redmine 中相符的名称。设置省略
	设置  :是否发送提醒邮件，测试期间默认是 False 
			自动新增问题类别 默认 False 
			自动新增目标版本 默认 True 
			更新已存在的问题 默认 False 
	注意：br 浏览器对象，已经上传文件成功。
	
	"""
	def get_import_result(htmlstr):
		re_result = re.compile("</h2>([\s\S]*)<hr/>",re.X)
		re_group = re_result.search(htmlstr)
		return re_group and re_group.group(1) or "没有导入结果"
	
	br.select_form(nr=1)
	import_form = br.form
	
	"""
	for control in import_form.controls:
		if control.type == "select":
			
			if control.value == "author":
				control.value = ""
				print control.get("")
				control.get("").selected = True
			if control.value == "assigned_to":
				control.value = ""
				control.get("").selected = True
			#print "control name,and value",control.name,control.value
	"""

	send_mail_control = import_form.find_control("send_emails",type="checkbox")
	send_mail_control.items[0].selected = False # 发送邮件设置 
	
	add_categories_control = import_form.find_control("add_categories",type="checkbox")
	add_categories_control.items[0].selected = False # 自动新增问题类别
	
	add_versions_control = import_form.find_control("add_versions",type="checkbox")
	add_versions_control.items[0].selected = True # 自动新增目标版本
	
	update_issue_control = import_form.find_control("update_issue",type="checkbox")
	update_issue_control.items[0].selected = False # 更新已存在的问题
	
	import_response = br.submit()
	import_htm = import_response.read()
	write_to(import_htm,"import.html")
	print get_import_result(import_htm)
	
def write_to(content,filep):
	"""
	将字符内容保存到文件中
	"""
	file = open(filep,"w")
	file.write(content)
	file.close()

def batch_main():
	"""
	批量上传文件到指定的项目
	"""
	br = init_br()
	login_redmine(br)
	
	for project in  BATCH_DICT:
		por_file = BATCH_DICT[project]
		to_import(br,project,por_file)
		do_import(br)
		print "debug : import file: %s  to :%s over "%(por_file,project)

def main():
	"""
	执行默认的文件导入功能
	"""
	br = init_br()
	login_redmine(br)
	to_import(br)
	do_import(br)

if __name__=="__main__":
	main()