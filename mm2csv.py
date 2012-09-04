#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
�Ӽƻ������mm�ļ�ת��Ϊcsv�ļ�

"""


import xml.etree.cElementTree as ET
import os
import sys
import datetime

#mm�ļ����ڵ�Ŀ¼
IN_DIR=u"E:\\temp\\mmtest"

#���ɺõ�csv���ļ�Ŀ¼
OUT_DIR=u"E:\\temp\\mmtest"

#�������������յ����ݼ���
XML_DATA=[]

#��ʾ��������� { / / / } �е� "/" �ָ��ÿһ�����ĺ���
CONF=["begintime","endtime","assign","hour"] 

# ���������
AUTHOR = "muj" 

def load_node(node):
	"""
	�ݹ齫������node ���ص� ȫ�ֱ��� XML_DATA��
	"""
	if node.tag != "node":
		return
	issuename=node.attrib["TEXT"]
	
	if issuename.endswith("]"):
		node.set("SUBVERSION",issuename[issuename.rindex("[")+1:-1])
		node.set("TEXT",issuename[0:issuename.rindex("[")])
	
	if issuename.endswith("}"):
		#�������}��β��ʾ����һ����������
		aindex = issuename.rindex("{")
		astr = issuename[aindex+1:-1] #��ȡ��{}�м������
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
	����һ��node ������Ҫ����һ���������������ڸ�������ӽ�㣬������ {desc} ��ͷ
	"""
	for child in node.getchildren():
		if child.tag == "node":
			ntxt = child.attrib["TEXT"]
			if ntxt.startswith("{desc}"):
				return ntxt[6:]
	pass
				
def mm2csv():
	"""
	��ȡmm�ļ�Ȼ�����xml
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
	��ȫ��XML_DATA�е����� д����������·�����ļ��У���csv��ʽ
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
	������һ����һ
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
	
	
	
