config.ini
	�������ã����config.ini �ļ��е�ע��

mm2csv :
	��freemind ��mm �ļ�ת����Ϊcsv;ʹ��ʱ��ע�� ��
		��config.ini ������ ��ע������� config.iniע�ͣ�
			IN_DIR ��mm�ļ���Ŀ¼
			OUT_DIR�����ɺ��csv �ļ�Ŀ¼
	���� python mm2csv.py ��������csvĿ¼

file2redmine:
	��csv �ļ����뵽 redmine �������б�
	���ļ����� mechanize ��ģ�飬��Ҫ��װ ʹ�� �� easy_install mechanize ����ʹ�� fixtools������ֱ�Ӱ�װ
	��config.ini ������ ��ע������� config.iniע�ͣ�
		�޸�	USER_NAME ����¼redmine ���û���
				USER_PWD �� ��¼����
				PROJECT_KEY�� Ϊ��Ŀ��ʾ����Ŀ�����ӣ�Ϊ�½���Ŀʱ�Զ��������
				CSV_FILE �� ��Ҫ�ϴ���csv�ļ���·��
			
		
			
fixtools:
	��������������Զ���װ easy_install ���ߣ�Ȼ���Զ���װ mechanize ����չ��
	����python �޷��޸�ϵͳ����������Ϊ���Ժ󷽱� �����н� %python%\Script ���õ�path �������� �������Ϳ�����cmd��ֱ��ʹ�� easy_install ������
	
��������python 2.6 �в���ͨ����
	
		