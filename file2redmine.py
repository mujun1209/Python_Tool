#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""csv�ļ�����redmine ����
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
	��ʼ������ 
		@param 	ini_cfg	:����һ������ʵ��������о�ֱ��ʹ�ø�ʵ��
				file 	������һ�������ļ�·����ֻ����û�и��� cfgʵ�������ǲ�������
		@type 	ini_cfg ��ConfigParser d
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
	#��ʼ���ϴ��ļ�����
	is_send_mail = cfg.getboolean("redmine","IS_SEND_MAIL")
	is_add_category = cfg.getboolean("redmine","IS_ADD_CATEGORY")
	is_add_version = cfg.getboolean("redmine","IS_ADD_VERSION")
	is_update_issue = cfg.getboolean("redmine","IS_UPDATE_ISSUE")

def init_br():
	"""
	��ʼ�����������
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
	��½redmine
		@param 	br		:��ǰ�����������
				username:��¼�õ��û���
				pwd		:��¼�õ�����
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
	������ϴ��ļ�ҳ���ύ�ϴ��ļ�
		@param 	br		:��ǰ�����������
				porject_key:��Ҫִ�в�����project��key 
				file_path	:�ϴ��ļ���·��
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
	
	br.select_form(nr=1) #ѡ���ϴ��ļ��ı�
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
	���� csv �ļ��Ķ�Ӧ���У�csv�ļ���title Ĭ��ʹ�ú�redmine ����������ơ�����ʡ��
	ע�⣺br ����������Ѿ��ϴ��ļ��ɹ���
	
		@param 	br		:��ǰ�����������
				is_send_mail:�Ƿ��������ʼ��������ڼ�Ĭ���� False 
				is_add_category	:�Զ������������ Ĭ�� False 
				is_add_version	:�Զ�����Ŀ��汾 Ĭ�� True 
				is_update_issue :�����Ѵ��ڵ����� Ĭ�� False 
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
		return re_group and re_group.group(1) or "û�е�����"
	
	br.select_form(nr=1)
	import_form = br.form
	

	send_mail_control = import_form.find_control("send_emails",type="checkbox")
	send_mail_control.items[0].selected = is_send_mail # �����ʼ����� 
	
	add_categories_control = import_form.find_control("add_categories",type="checkbox")
	add_categories_control.items[0].selected = is_add_category # �Զ������������
	
	add_versions_control = import_form.find_control("add_versions",type="checkbox")
	add_versions_control.items[0].selected = is_add_version # �Զ�����Ŀ��汾
	
	update_issue_control = import_form.find_control("update_issue",type="checkbox")
	update_issue_control.items[0].selected = is_update_issue # �����Ѵ��ڵ�����
	
	import_response = br.submit()
	import_htm = import_response.read()
	write_to(import_htm,"import.html")
	print get_import_result(import_htm)#���������д��Ľ�
	
def write_to(content,filep):
	"""
	���ַ����ݱ��浽�ļ���
		@param 	content		:��Ҫд����ļ�����
				filep		: �ļ�·��
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
	�����ϴ��ļ���ָ������Ŀ
		@param 	batch_dict :����dict�����õ����ļ�����Ŀ
				logined_br :�Ѿ���½�����������
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
		@param 	f_dir :������Ҫ������ļ���
				logined_br :�Ѿ���½�����������
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
	ͨ����Ŀ�����������ڸ�����map �в���key 
		@param 	chname:
				pro_map:�������ҵ�map
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
		
def run_file2redmine():
	"""
	ִ��Ĭ�ϵ��ļ����빦��
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
	if not def_csv_file or not def_pro_key: #���û��������Ҫ�ϴ���csv���ļ������Ȳ��� redmine=>BATCH_DICT������
		batch_dict = eval(cfg.get("redmine","BATCH_DICT"))
		if batch_dict : #�����������ϴ��ֵ�
			batch_import(br,batch_dict)
		else :	#û������ redmine=>BATCH_DICT,Ĭ���� mm=>OUT_DIRĿ¼������ csv�ļ�
			out_dir = get_out_dir(cfg)
			batch_import_dir(br,out_dir)
	else:
		if not os.path.exists(def_csv_file): #�Ǿ���·����ֻ�����ļ���
			def_csv_file = os.path.join(get_out_dir(cfg),def_csv_file)
		if to_import(br,def_pro_key,def_csv_file):
			do_import(br,is_send_mail,is_add_category,is_add_version,is_update_issue)

def get_out_dir(cfg):
	"""�� cfg �л�ȡ���õ����Ŀ¼�����û��Ĭ���ǵ�ǰ�Ľű�ִ��Ŀ¼
		@param 	chname:
		@type 	chname :str
		@return none
		@rtype 	none
	"""
	out_dir = cfg.get("mm","OUT_DIR")
	return (out_dir and out_dir) or os.getcwd()
			
if __name__=="__main__":
	run_file2redmine()
	
	