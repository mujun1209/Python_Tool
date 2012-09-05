#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""从计划任务的mm文件转换为csv文件
@version: @Id$
@author: U{mujun<mailto:360144561@qq.com>}
@license:GPL
@contact:360144561@qq.com
@see:
"""


import xml.etree.cElementTree as ET
import os,sys,ConfigParser
import datetime

cfg = None

def init_config(file="config.ini"):
	"""初始化配置文件
		@param 	none
		@type 	none
		@return none
		@rtype 	none
	
	"""
	global cfg
	cfg=ConfigParser.ConfigParser()
	cfg.read(file)

	
def load_node(node,xml_data):
	"""
	递归将给定的node的子结点 加载到 全局变量 XML_DATA中
		@param 	node:一个xml的节点
				xml_data:将解析后的数据放入到给定的数组中
		@type 	node:element 
				xml_data:list
		@return none
		@rtype none
	"""
	
	if node.tag != "node":
		return
	issuename=node.attrib["TEXT"]
	
	if issuename.endswith("]"):
		node.set("SUBVERSION",issuename[issuename.rindex("[")+1:-1])
		node.set("TEXT",issuename[0:issuename.rindex("[")])
	
	if issuename.endswith("}"):
		#如果是以}结尾表示这是一个完整任务
		aindex = issuename.rindex("{")
		astr = issuename[aindex+1:-1] #截取到{}中间的属性
		atts = astr.split("/")
		issue={}
		issue["name"] =issuename[0:aindex]
		issue["desc"] = load_desc(node)
		issue["subversion"] = node.attrib["SUBVERSION"]
		splite_config = eval(cfg.get("mm","SPLITE_CONF")) #将配置的字符串转成python对象
		for i in range(0,len(atts)):
			issue[splite_config[i]] = atts[i]
		xml_data.append(issue)
		return
	for child in node.getchildren():
		if child.tag != "node":
			continue
		child.set("TEXT",node.attrib["TEXT"]+"."+child.attrib["TEXT"])
		if node.attrib.has_key("SUBVERSION"):
			child.set("SUBVERSION",node.attrib["SUBVERSION"])
		load_node(child,xml_data)
	pass
	
	
def load_desc(node):
	"""
	解析一个node 的描叙，要求在一个任务的描叙必须在该任务的子结点，并且以 {desc} 开头
		@param 	node:一个xml的节点
		@type node:element 
		@return 这个节点的描叙内容
		@rtype str
	"""
	for child in node.getchildren():
		if child.tag == "node":
			ntxt = child.attrib["TEXT"]
			if ntxt.startswith("{desc}"):
				return ntxt[6:]
	pass

	
def mm2csv(in_dir,out_dir):
	"""
	读取mm文件然后解析xml
		@param 	none
		@type none
		@return none
		@rtype none
	"""
	file_list = [f_name for f_name in os.listdir(in_dir) if f_name.endswith('mm')]
	if not file_list:
		print "sorry ! not found mm file in the dir:",in_dir
		return
		
	for f_in_name in file_list:
		xml_data = []
		tree = ET.parse(os.path.join(in_dir,f_in_name))
		mmNodes = tree.findall("node")
		for node in mmNodes:
			load_node(node,xml_data)
		f_out_name = os.path.join(out_dir,f_in_name[0:f_in_name.rfind(".")]+".csv")
		write_csv(f_out_name,xml_data)
		print "write file :"+f_out_name
	
	pass
		

def write_csv(filepath,xml_data):
	"""
	将XML_DATA中的数据 写到给定的问路径的文件中，以csv格式
		@param 	filepath : 需要写入的文件路径
				xml_data : 要写入的数据list
		@type 	filepath : str
				xml_data : list
		@return none
		@rtype none
	
	"""
	if not xml_data:
		print "the xml_data is empty!"
		return
	file =  open(filepath,"w")
	csvline = cfg.get("mm","CSV_HEADER") + "\n" #读取配置
	file.write(csvline);
	monday = next_monday()
	for issue in xml_data:
		if not issue["begintime"] :
			issue["begintime"] = monday
		issue["AUTHOR"] = cfg.get("mm","AUTHOR")
		
		csvline = cfg.get("mm","CSV_FORMAT")
		csvline = csvline.replace("@","%") % issue +"\n"
		# csvline +="\n"
		file.write(csvline.encode('utf'))
	
	file.close()
	pass

	
def next_monday(format=None):
	"""
	计算下一个周一
		@param 	fromat :时间的格式化字符
		@type 	fromat:str
		@return str:格式化好的时间字符
		@rtype str
	"""
	import datetime,calendar
	day = datetime.date.today()
	oneday = datetime.timedelta(days=1)
	while day.weekday() != calendar.MONDAY:
		day +=oneday
	if format == None:
		format = "%Y-%m-%d"
	return day.strftime(format)

def run_mm2csv():
	init_config() #初始化配置文件
	if not cfg :
		print "config init error! over the program"
		return
	
	current_script_path = os.getcwd()
	in_dir = cfg.get("mm","IN_DIR")
	out_dir = cfg.get("mm","OUT_DIR")
	in_dir = (in_dir and in_dir) or current_script_path #如果配置文件中没有配置，默认当前脚本目录
	out_dir = (out_dir and out_dir) or current_script_path
	mm2csv(in_dir,out_dir)
	
if __name__=="__main__":
	run_mm2csv()
	
	
	
