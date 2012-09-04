mm2csv :
	将freemind 的mm 文件转换成为csv;使用时请注意 ：
		IN_DIR ：mm文件的目录
		OUT_DIR：生成后的csv 文件目录
	运行 python mm2csv.py 即可生成csv目录

file2redmine:
	将csv 文件导入到 redmine 的问题列表；
	该文件依赖 mechanize 的模块，需要安装 使用 ： easy_install mechanize 或者使用 fixtools工具来直接安装
	需要注意：
		修改	USER_NAME ：登录redmine 的用户名
				USER_PWD ： 登录密码
				PROJECT_KEY： 为项目标示即项目的链接，为新建项目时自定义的名称
				CSV_FILE ： 需要上传的csv文件的路径
			
			另支持批量上传，（暂未测试）
			修改 
			if __name__=="__main__":
				main()
				将 main() 改为： batch_main() 即可。
			配置 BATCH_DICT 字典为 {“projectkey”:"filepath"} 对应每个项目制定一个csv 的文件路径即可
			
fixtools:
	用来解决依赖，自动安装 easy_install 工具，然后自动安装 mechanize 的扩展。
	由于python 无法修改系统环境变量，为了以后方便 请自行将 %python%\Script 配置到path 环境变量 。这样就可以在cmd中直接使用 easy_install 工具了
	
以上是在python 2.6 中测试通过。
	
		