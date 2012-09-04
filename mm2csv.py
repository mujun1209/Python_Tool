#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
从计划任务的mm文件转换为csv文件

"""


import xml.etree.cElementTree as ET
import os
import sys
import datetime

#mm文件所在的目录
IN_DIR=u"E:\\temp\\mmtest"

#生成好的csv的文件目录
OUT_DIR=u"E:\\temp\\mmtest"

#解析出来的最终的数据集合
XML_DATA=[]

#标示任务结束符 { / / / } 中的 "/" 分割的每一项代表的含义
CONF=["begintime","endtime","assign","hour"] 

# 任务的作者
AUTHOR = "muj" 

def load_node(node):
	"""
	递归将给定的node 加载到 全局变量 XML_DATA中
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
		for i in range(0,len(atts)):
			issue[CONF[i]] = atts[i]
		XML_DATA.append(issue)
		return
	for child in node.getchildren():
		if child.tag != "node":
			continue
		child.set("TEXT",node.attrib["TEXT"]+"."+child.attrib["TEXT"])
		if node.attrib.has_key("SUBVERSION"):
			child.set("SUBVERSION",node.attrib["SUBVERSION"])
		load_node(child)
	pass
		

		
def load_desc(node):
	"""
	解析一个node 的描叙，要求在一个任务的描叙必须在该任务的子结点，并且以 {desc} 开头
	"""
	for child in node.getchildren():
		if child.tag == "node":
			ntxt = child.attrib["TEXT"]
			if ntxt.startswith("{desc}"):
				return ntxt[6:]
	pass
				
def mm2csv():
	"""
	读取mm文件然后解析xml
	"""
	file_list = [f_name for f_name in os.listdir(IN_DIR) if f_name.endswith('mm')]
	for f_in_name in file_list:
		tree = ET.parse(os.path.join(IN_DIR,f_in_name))
		mmNodes = tree.findall("node")
		for node in mmNodes:
			load_node(node)
		f_out_name = os.path.join(OUT_DIR,f_in_name.split(".")[0]+".csv")
		write_csv(f_out_name)
		print "write file :"+f_out_name
	pass
		

def write_csv(fileurl):
	"""
	将全局XML_DATA中的数据 写到给定的问路径的文件中，以csv格式
	"""

	file =  open(fileurl,"w")
	csvline = "fixed_version,subject,author,assigned_to,start_date,due_date,estimated_hours,description\n"
	file.write(csvline);
	monday = next_monday()
	for issue in XML_DATA:
		if not issue["begintime"] :
			issue["begintime"] = monday
		issue["AUTHOR"] = AUTHOR
		csvline = "%(subversion)s,%(name)s,%(AUTHOR)s,%(assign)s,%(begintime)s,%(endtime)s,%(hour)s,%(desc)s\n" %issue
		file.write(csvline.encode('utf'))
	file.close()
	pass

	
def next_monday(format=None):
	"""
	计算下一个周一
	"""
	import datetime,calendar
	day = datetime.date.today()
	oneday = datetime.timedelta(days=1)
	while day.weekday() != calendar.MONDAY:
		day +=oneday
	if format == None:
		format = "%Y-%m-%d"
	return day.strftime(format)
	
if __name__=="__main__":
	mm2csv()
	#print next_monday()
	
	
	
