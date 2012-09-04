#!/usr/bin/python
#-*- coding:utf-8 -*-

import sys,os
import urllib

pypath = sys.executable
pyroot =  pypath[ 0 : pypath.rfind( os.sep )]

ez_setup_url = "http://peak.telecommunity.com/dist/ez_setup.py"

def download_file(url,filename):
	urllib.urlretrieve(url, filename)
	#print filename,url

def set_path_var(path):
	os.environ["path"] += ";"+path
	
def check_pyroot():
	"""
	"""
	if os.environ["path"].rfind(pyroot) == -1 :
		set_path_var(pyroot)

def setup_ez():
	check_pyroot() 

	down_path = os.path.join(pyroot,"download")
	if not os.path.exists(down_path):
		os.makedirs(down_path)
	#download_file(ez_setup_url,os.path.join(down_path,"ez_setup.py"))
	os.system("python "+os.path.join(down_path,"ez_setup.py"))  #安装easy_install 工具
 	
def setup_extend(pyextend):
	set_path_var(os.path.join(pyroot,"Scripts"))
	os.system("easy_install "+pyextend)
	
if __name__=="__main__":
	#print pyroot
	setup_ez()
	setup_extend("mechanize")
