# _*_ coding:utf-8 _*_

from tools import Tools
import re
import os
from bs4 import BeautifulSoup
from seleniumUtil import SeleniumUtil
from contextlib import closing
import requests

class WeekCourse:

	def __init__(self, urls ,session):
		self.urls = urls
		self.session = session
		self.tools = Tools()
		self.cookies = {}
		# 将requests 请求的 cookies 转换为字典
		for c in self.session.cookies:
			self.cookies[c.name] = c.value
		self.week = '第1周'

		# print('cookies:::'+str(self.cookies))
		self.seleniumUtil = SeleniumUtil()
		self.seleniumUtil.initDriver(self.cookies)

		self.titlePattern = re.compile(r'<h4.*?>(.*?)</h4>',re.S)
		self.urlPattern = re.compile(r'<a.*?href="(.*?)".*?>.*?<h5 class="item-name.*?>.*?<span>(.*?)</span>.*?</h5>',re.S)

	# 区分出每个小章节 
	def getCourseItems(self,soup):
		chapters = soup.select('div[class="rc-NamedItemList"]')
		for chapter in chapters:
			print('------------------------------------------------------------------------------------------------------------')
			title = re.findall(self.titlePattern,str(chapter))[0]
			title = self.tools.removeSpecialChar(str(title))
			print('章节：'+title)
			items = re.findall(self.urlPattern,str(chapter))
			
			if not items:
				continue

			for item in items:
				fileName = self.tools.removeSpecialChar(str(item[1]))
				url = str(item[0])
				# 查看是否已经爬过了
				if self.tools.isSpided(url):
					print('https://www.coursera.org'+url +'  已经爬过了')
					continue
				# 过滤一些测试页面 讨论页面
				if '/exam/' in url or '/programming/' in url or '/discussionPrompt/' in url:
					continue
				# 下载视频
				if '/lecture/' in url:  
					self.downloadVideo(url, self.week+'/'+str(title), fileName+'.mp4')
				# 下载保存文本
				if '/supplement/' in url:
					self.downloadTxt(url, self.week+'/'+str(title), fileName+'.txt')
				# 添加一条记录
				self.tools.addSpidedRecord(url)
			print('------------------------------------------------------------------------------------------------------------\n')

	
	# 下载视频
	def downloadVideo(self,url,fileDir,fileName):
		url = 'https://www.coursera.org'+url
		content = self.seleniumUtil.getJsPage(url,wait_class_name='flex-1',wait_time=10,isVideo=True)
		soup = BeautifulSoup(content,'lxml')
		down = soup.find('video')
		pattern = re.compile(r'<video.*?>.*?<source.*?src="(.*?)".*?/>',re.S)
		if down:
			# 视频地址爬下后 需要做一些处理 去除; &amp 
			videoUrl = re.findall(pattern,str(down))[0]
			videoUrl = re.sub(r';','&',str(videoUrl))
			videoUrl = re.sub(r'&amp','',videoUrl)
			# print('\n视频下载地址：'+ videoUrl)
			self.tools.downLoadFile(videoUrl,self.session,fileDir,fileName)
	

	# 保存文本信息
	def downloadTxt(self,url,fileDir,fileName):
		url = 'https://www.coursera.org'+url
		content = self.seleniumUtil.getJsPage(url,wait_class_name='flex-1',wait_time=10)
		soup = BeautifulSoup(content,'lxml')
		self.downloadPDF(soup,fileDir)
		mainText = soup.select('div[class="content-container feedback-not-fixed-at-bottom"]')[0]
		mainText = self.tools.replaceContent(str(mainText))
		print('保存文件：'+fileName)
		self.tools.writeFile('TXT-'+fileName,mainText,fileDir)

	# 保存PDF
	def downloadPDF(self,soup,fileDir):
		linkList = soup.select('div[class="cml-asset cml-asset-pdf"]')
		if linkList:
			for link in linkList:
				linkinfo = self.tools.getHref(str(link))
				if not linkinfo:
					continue

				url = re.sub(';','&',str(linkinfo[0][0]))
				url = re.sub(r'&amp','',url)

				fileName = 'PDF-'+str(linkinfo[0][1]).strip()
				if not fileName.endswith('.pdf'):
					fileName = fileName+'.pdf'

				self.tools.downLoadFile(url,self.session,fileDir,fileName)


	def start(self):
		i = 1
		for url in self.urls:
			self.week = '第%d周' %i
			print('\n=============== '+self.week+' ===============\n')
			content = self.seleniumUtil.getJsPage(url,'flex-1')
			soup = BeautifulSoup(content,'lxml')
			i += 1
			self.getCourseItems(soup)

		self.seleniumUtil.quit()

def main():
	url='https://d3c33hcgiwev3.cloudfront.net/_7e5ccddd566bf61a9c29e4b0d5612cdf_1_Python_pip__________.pdf?Expires=1510444800&Signature=GI1npv9BKG2Bk0yfw1wUGYTQbhrN8angkK~4n--6dqNWdr-s1AeRSZpHgYybB0YFMftxbqIBUY1iVxVotG-TtGqCOYBtH2v1jhmh7tz9Ukm2UH1wQALmjoHncpXoyoRduoKtW27zSw1s089OGc2mTscK1z~E5QqB0zXcT9MO860_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A'
	response = requests.get(url)
	print(response.text)
	tools = Tools()
	self.tools.writeByte('test.pdf',response.content)


if __name__ == '__main__':
	main()