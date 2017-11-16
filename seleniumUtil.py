# _*_ coding:utf-8 _*_

import time
import os
import sys
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC 
from selenium.common.exceptions import TimeoutException

class SeleniumUtil:

	def __init__(self):
		# chrome 浏览器驱动 mac版
		self.chromedriver = os.getcwd()+'/chromedriver'
		# phantomjs 驱动 mac版
		self.phantomJsDriver = os.getcwd()+'/phantomjs'

		# 设置不加载图片
		self.chrome_options = webdriver.ChromeOptions()
		prefs = {"profile.managed_default_content_settings.images":2}
		self.chrome_options.add_experimental_option("prefs",prefs)


	# 初始化driver  把cookies加入driver中  需要先加载地址  再添加cookie
	def initDriver(self,cookies):
		print('正在初始化 selenium')
		baseUrl = 'https://www.coursera.org'
		try:
			self.driver = webdriver.Chrome(self.chromedriver,chrome_options= self.chrome_options)
			# 使用 PhantomJS无界面浏览器失败 
			# self.driver = webdriver.PhantomJS(executable_path=self.phantomJsDriver)
			self.driver.get(baseUrl)
			elem = WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.CLASS_NAME,'rc-DRTVBanner')))

			for key in cookies:
				cookie = {}
				cookie['name'] = key
				cookie['value'] = cookies[key]
				self.driver.add_cookie(cookie)

			print('初始化 selenium 完成 \n')
		except NoSuchElementException:
			print('can not find')
			self.initDriver(cookies)
		except Exception as e:
			print('初始化失败')
			if hasattr(e,'reason'):
				print(e.reason)
			sys.exit()


	def getJsPage(self,url,wait_class_name = None,wait_time=0,isVideo = False):
		try:
			print('正在加载页面：'+str(url))
			self.driver.get(url)
			if wait_class_name:
				# 显示等待 
				elem = WebDriverWait(self.driver,20).until(EC.presence_of_element_located((By.CLASS_NAME,wait_class_name)))

			# 页面有时停止加载后  js并没有将数据写到页面中，所以这里设置了等待时间
			time.sleep(wait_time)

			# 如果是视频页 禁止视频播放
			if isVideo:
				video = self.driver.find_element_by_xpath('//*[@id="c-video_html5_api"]')
				self.driver.execute_script("return arguments[0].pause();", video)

			return self.driver.page_source

		except NoSuchElementException:
			print('加载页面失败  can not find')
			return self.getJsPage(url,wait_class_name,wait_time,isVideo)
		except TimeoutException:
			print('加载页面超时  重新加载。。。')
			return self.getJsPage(url,wait_class_name,wait_time,isVideo)
		except Exception:
			print('未知错误')


	def quit(self):
		self.driver.quit()

	def close(self):
		self.driver.close()