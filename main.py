#!/usr/bin/python
#-*- coding:utf-8 -*-

"""将mm 文件直接生成cvs,上传redmine 导入问题列表
@version: @Id$
@author: U{mujun<mailto:360144561@qq.com>}
@license:GPL
@contact:360144561@qq.com
@see:
"""

import mm2csv
import file2redmine
import fixtools

if __name__=="__main__":
	try:
		import mechanize
	except:
		fixtools.setup_ez()
		fixtools.setup_extend("mechanize") # 安装python 扩展
	
	mm2csv.run_mm2csv() #将文件转换成csv
	
	file2redmine.init_conifg(mm2csv.cfg) #初始化cfg 配置
	file2redmine.run_file2redmine()  #导入redmine