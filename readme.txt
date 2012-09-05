config.ini
	程序配置，详见config.ini 文件中的注释

mm2csv :
	将freemind 的mm 文件转换成为csv;使用时请注意 ：
		在config.ini 中配置 （注意事项见 config.ini注释）
			IN_DIR ：mm文件的目录
			OUT_DIR：生成后的csv 文件目录
	运行 python mm2csv.py 即可生成csv目录

file2redmine:
	将csv 文件导入到 redmine 的问题列表；
	该文件依赖 mechanize 的模块，需要安装 使用 ： easy_install mechanize 或者使用 fixtools工具来直接安装
	在config.ini 中配置 （注意事项见 config.ini注释）
		修改	USER_NAME ：登录redmine 的用户名
				USER_PWD ： 登录密码
				PROJECT_KEY： 为项目标示即项目的链接，为新建项目时自定义的名称
				CSV_FILE ： 需要上传的csv文件的路径
fixtools:
	用来解决依赖，自动安装 easy_install 工具，然后自动安装 mechanize 的扩展。
	由于python 无法修改系统环境变量，为了以后方便 请自行将 %python%\Script 配置到path 环境变量 。这样就可以在cmd中直接使用 easy_install 工具了

mian.py
	该文件是直接根据配置调用 fixtools,mm2csv ,file2redmine 直接将mm文件转换csv导入到redmine。程序会尝试解决依赖问题，安装easy_install 。
	
以上是在python 2.6 中测试通过。
	
		