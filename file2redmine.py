#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os,re,sys
import mechanize
import cookielib

#redmine ��������
REDMINE_HOST =  "http://192.168.1.41:3000/"
#��½redmine���û���
USER_NAME = "muj"
#��½����
USER_PWD = "asdfjkl;"
#��Ӧ��Ŀ��redmine �е��Զ�������
PROJECT_KEY = "ms-tg-it-yf-mhsq-csy"
#Ҫ�ϴ���csv�ļ���·��
CSV_FILE = "E:\\temp\\mmtest\\������1.csv"

#�����������Ŀ�����ļ�
BATCH_DICT = {"ms-tg-it-yf-*":"filepath","p2":"f2"}

def init_br():
	"""
	��ʼ�����������
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
	"""��½redmine
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
	������ϴ��ļ�ҳ���ύ�ϴ��ļ�
	"""
	porject_key = (porject_key and porject_key) or PROJECT_KEY
	
	response = br.open(mechanize.urljoin(REDMINE_HOST,"importer?project_id="+porject_key))
	print response.geturl()
	br.select_form(nr=1) #ѡ���ϴ��ļ��ı�
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
	���� csv �ļ��Ķ�Ӧ���У�csv�ļ���title Ĭ��ʹ�ú�redmine ����������ơ�����ʡ��
	����  :�Ƿ��������ʼ��������ڼ�Ĭ���� False 
			�Զ������������ Ĭ�� False 
			�Զ�����Ŀ��汾 Ĭ�� True 
			�����Ѵ��ڵ����� Ĭ�� False 
	ע�⣺br ����������Ѿ��ϴ��ļ��ɹ���
	
	"""
	def get_import_result(htmlstr):
		re_result = re.compile("</h2>([\s\S]*)<hr/>",re.X)
		re_group = re_result.search(htmlstr)
		return re_group and re_group.group(1) or "û�е�����"
	
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
	send_mail_control.items[0].selected = False # �����ʼ����� 
	
	add_categories_control = import_form.find_control("add_categories",type="checkbox")
	add_categories_control.items[0].selected = False # �Զ������������
	
	add_versions_control = import_form.find_control("add_versions",type="checkbox")
	add_versions_control.items[0].selected = True # �Զ�����Ŀ��汾
	
	update_issue_control = import_form.find_control("update_issue",type="checkbox")
	update_issue_control.items[0].selected = False # �����Ѵ��ڵ�����
	
	import_response = br.submit()
	import_htm = import_response.read()
	write_to(import_htm,"import.html")
	print get_import_result(import_htm)
	
def write_to(content,filep):
	"""
	���ַ����ݱ��浽�ļ���
	"""
	file = open(filep,"w")
	file.write(content)
	file.close()

def batch_main():
	"""
	�����ϴ��ļ���ָ������Ŀ
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
	ִ��Ĭ�ϵ��ļ����빦��
	"""
	br = init_br()
	login_redmine(br)
	to_import(br)
	do_import(br)

if __name__=="__main__":
	main()