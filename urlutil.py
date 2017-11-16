# _*_ coding:utf-8 _*_

import requests
import re
import random
import time

class UrlUtil:

	def __init__(self):
		self.iplist = []
		self.getIPList()
		# 获取请求头列表
		self.user_agent_list = [
			"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
			"Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
			"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
			"Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
			"Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
			"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
			"Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
			"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
			"Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
			"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
			"Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
			"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
			"Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
			"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
			"Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
			"Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
			"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
			"Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
		]

	# 获取代理地址
	def getIPList(self):
		response = requests.get('http://31f.cn/area/%E4%B8%AD%E5%9B%BD/')
		content = response.text
		pattern = re.compile(r'<tr>.*?<td>\d.*?</td>.*?<td>(.*?)</td>.*?<td>(.*?)</td>',re.S)
		items = re.findall(pattern,content)
		for item in items:
			self.iplist.append(item[0]+':'+item[1])

	# requests post请求
	def post(self, url, data, session, cookies=None, timeouts=10, header = None, proxy=None, num_retries=6):
		UA = random.choice(self.user_agent_list) 
		mHeader = {'User-Agent': UA,'Content-Type':'application/x-www-form-urlencoded'} 
		if header:
			mHeader = dict(mHeader,**header)

		if proxy == None: 
			try:
				if cookies:
					return session.post(url,data=data, cookies=cookies, headers=mHeader, timeout=timeouts)
				else:
					return session.post(url,data=data, headers=mHeader, timeout=timeouts)
			except Exception as e: 
				# print(str(e))
				if num_retries > 0: 
					time.sleep(5) 
					print('获取网页出错，5S后将获取倒数第：'+ str(num_retries) +'次')
					return self.post(url, data, session, cookies, timeouts, header, proxy, num_retries-1)  
				else:
					print(u'开始使用代理')
					time.sleep(5)
					IP = ''.join(str(random.choice(self.iplist)).strip())
					proxy = {'http': IP}
					return self.post(url, data, session, cookies, timeouts, header, proxy) 

		else: 
			try:
				IP = ''.join(str(random.choice(self.iplist)).strip()) 
				proxy = {'http': IP} 
				if cookies:
					return session.post(url,data=data, cookies=cookies,proxies=proxy, headers=mHeader, timeout=timeouts)
				else:
					return session.post(url,data=data, headers=mHeader,proxies=proxy,timeout=timeouts)
			except:

				if num_retries > 0:
					time.sleep(5)
					IP = ''.join(str(random.choice(self.iplist)).strip())
					proxy = {'http': IP}
					print('正在更换代理，5S后将重新获取倒数第'+ str(num_retries) +'次')
					print('当前代理是：'+ str(proxy))
					return self.post(url, data, session, cookies, timeouts, header, proxy, num_retries-1)
				else:
					print(u'代理也不好使了！取消代理')
					return self.post(url, data, session, cookies, timeouts, header)


	# requests get请求
	def get(self, url, session, cookies=None, timeouts=10, header = None, proxy=None, num_retries=6):
		UA = random.choice(self.user_agent_list) 
		mHeader = {'User-Agent': UA,'Content-Type':'application/x-www-form-urlencoded'} 
		if header:
			mHeader = dict(mHeader,**header)

		if proxy == None: 
			try:
				if cookies:
					return session.get(url, cookies=cookies, headers=mHeader, timeout=timeouts)
				else:
					return session.get(url, headers=mHeader, timeout=timeouts)
			except Exception as e: 
				# print(str(e))
				if num_retries > 0: 
					time.sleep(5) 
					print('获取网页出错，5S后将获取倒数第：'+ str(num_retries) +'次')
					return self.get(url,  session, cookies, timeouts, header, proxy, num_retries-1)  
				else:
					print(u'开始使用代理')
					time.sleep(5)
					IP = ''.join(str(random.choice(self.iplist)).strip())
					proxy = {'http': IP}
					return self.get(url, session, cookies, timeouts, header, proxy) 

		else: 
			try:
				IP = ''.join(str(random.choice(self.iplist)).strip()) 
				proxy = {'http': IP} 
				if cookies:
					return session.get(url, cookies=cookies,proxies=proxy, headers=mHeader, timeout=timeouts)
				else:
					return session.get(url, headers=mHeader,proxies=proxy,timeout=timeouts)
			except:

				if num_retries > 0:
					time.sleep(5)
					IP = ''.join(str(random.choice(self.iplist)).strip())
					proxy = {'http': IP}
					print('正在更换代理，5S后将重新获取倒数第'+ str(num_retries) +'次')
					print('当前代理是：'+ str(proxy))
					return self.get(url, session, cookies, timeouts, header, proxy, num_retries-1)
				else:
					print(u'代理也不好使了！取消代理')
					return self.get(url, session, cookies, timeouts, header)








