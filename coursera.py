# _*_ coding:utf-8 _*_

import requests
from tools import Tools
from urlutil import UrlUtil
from bs4 import BeautifulSoup
import re
from weekcourse import WeekCourse
import sys
import getopt

class Coursera:
	
	def __init__(self,user,password):
		self.tools = Tools()
		self.urlUtil = UrlUtil()
		self.user = user
		self.password = password
		self.session = requests.Session()
		self.courseUrl = 'https://www.coursera.org/learn/hipython'
		# self.courseUrl = 'https://www.coursera.org/learn/da-xue-hua-xue'

	# 登录你的Coursera账号
	def login(self):
		url = 'https://www.coursera.org/api/login/v3Ssr?csrf3-token=1510823580.eRKpKzepl351P5ij&src=undefined'
		param = {'email':self.user,'password':self.password}
		# 通过header头中的Referer参数  返回登录成功后的页面
		header = {'Origin':'https://www.coursera.org','Referer':self.courseUrl+'/home/welcome'}
		cookies = {'CSRF3-Token':'1510823580.eRKpKzepl351P5ij'}	
		response = self.urlUtil.post(url,param,self.session,cookies=cookies,header=header)
		response.encoding='utf-8'
		return response.text
		
	# 获取课程标题
	def getTitle(self,soup):
		title = soup.select('h1[class="course-name color-primary-text display-3-text"]')
		if not title:
			print('获取课程标题 失败')
			return None
		title = self.tools.removeTag(str(title[0]))
		print('发现课程：《'+title+'》\n')
		return title


	def start(self):
		# self.courseUrl = input('\n请输入课程主页地址（例https://www.coursera.org/learn/hipython）：\n')
		content = self.login()
		soup = BeautifulSoup(content,'lxml')
		title = self.getTitle(soup)
		if not title:
			title = input('请输入课程名称：')
		weekcourse = WeekCourse(title ,self.courseUrl,self.session)
		weekcourse.start()
		
	
def main(argv):
	email = ''
	password = ''
	try:
		opts, args = getopt.getopt(argv,'he:p:',['mail=','pwd='])
	except getopt.GetoptError:
		print('coursera.py -e <email> -p <password>')
		sys.exit(2)

	for opt,arg in opts:
		if opt == '-h':
			print('coursera.py -e <email> -p <password>')
			sys.exit()
		elif opt in ('-e','--mail'):
			email = arg
		elif opt in ('-p','--pwd'):
			password = arg

	if not email or not password:
		print('coursera.py -e <email> -p <password>')
		sys.exit()

	coursera = Coursera(email,password)
	coursera.start()

	

if __name__ == '__main__':
    main(sys.argv[1:])

