# _*_ coding:utf-8 _*_

from tools import Tools
import re
import os
from bs4 import BeautifulSoup
import requests
from urlutil import UrlUtil
import json
from pprint import pprint

class WeekCourse:

	def __init__(self,title,url,session):
		self.title = title
		self.url = url
		self.session = session
		self.tools = Tools()
		self.urlutil = UrlUtil()
		self.baseurl = 'https://www.coursera.org/api/'
		self.includesParam = 'includes=modules%2Clessons%2CpassableItemGroups%2CpassableItemGroupChoices%2CpassableLessonElements%2Citems%2Ctracks%2CgradePolicy&fields=moduleIds%2ConDemandCourseMaterialModules.v1(name%2Cslug%2Cdescription%2CtimeCommitment%2ClessonIds%2Coptional%2ClearningObjectives)%2ConDemandCourseMaterialLessons.v1(name%2Cslug%2CtimeCommitment%2CelementIds%2Coptional%2CtrackId)%2ConDemandCourseMaterialPassableItemGroups.v1(requiredPassedCount%2CpassableItemGroupChoiceIds%2CtrackId)%2ConDemandCourseMaterialPassableItemGroupChoices.v1(name%2Cdescription%2CitemIds)%2ConDemandCourseMaterialPassableLessonElements.v1(gradingWeight)%2ConDemandCourseMaterialItems.v2(name%2Cslug%2CtimeCommitment%2CcontentSummary%2CisLocked%2ClockableByItem%2CitemLockedReasonCode%2CtrackId%2ClockedStatus)%2ConDemandCourseMaterialTracks.v1(passablesCount)&showLockedItems=true'
		self.videoInclude = 'includes=video&fields=onDemandVideos.v1(sources%2Csubtitles%2CsubtitlesVtt%2CsubtitlesTxt)'
		self.supplementsInclude = 'includes=asset&fields=openCourseAssets.v1(typeName)%2CopenCourseAssets.v1(definition)'
		self.assetsInclude = 'fields=audioSourceUrls%2C+videoSourceUrls%2C+videoThumbnailUrls%2C+fileExtension%2C+tags'
		# 判断 文本 课程页是否包含额外文件的 正则匹配
		self.assetPattern = re.compile(r'<asset.*?id="(.*?)".*?name="(.*?)".*?extension="(.*?)".*?/>',re.S)

	# 获取所有课程信息 Json 数据
	def getCourseInfo(self):
		params = self.url.split('/')
		slug = ''
		if params[-1]:
			slug = params[-1]
		else:
			slug = params[-2]
		url = self.baseurl + 'onDemandCourseMaterials.v2?q=slug&slug=%s&' %slug +self.includesParam
		response = self.urlutil.get(url,self.session)
		response.encoding='UTF-8'
		jsonObject = json.loads(response.text)
		self.elementId = jsonObject['elements'][0]['id']
		return jsonObject['linked']

	# 处理章节
	def doForModules(self):
		modules = self.courseInfo['onDemandCourseMaterialModules.v1']
		self.moduleNameDict = {} #创建 module 目录名称字典 方便后面保存文件时保存到相应目录
		i = 1
		for module in modules:
			dirName = self.title+'/'+str(i)+'.'+str(module['name'])
			self.moduleNameDict[module['id']] = dirName
			description = module['description']
			i += 1
			self.tools.writeFile('简介.txt',description,dirName) # 写入章节简介信息

	# 处理课程
	def doForLessons(self):
		lessons = self.courseInfo['onDemandCourseMaterialLessons.v1']
		self.lessonsNameDict= {} #创建 lessons 目录名称字典 方便后面保存文件时保存到相应目录
		i = 1;
		for lesson in lessons:
			dirName = str(i)+'.'+str(lesson['name'])
			moduleId = str(lesson['moduleId'])
			i += 1
			self.lessonsNameDict[lesson['id']] = dirName
			self.tools.createDir(self.moduleNameDict[moduleId]+'/'+dirName) # 创建目录


	# 处理每一小节的课程
	def doForItems(self):
		items = self.courseInfo['onDemandCourseMaterialItems.v2']
		i = 1;
		for item in items:
			lessonId = str(item['lessonId'])
			moduleId = str(item['moduleId'])
			itemId = str(item['id']) 
			slug = str(item['slug'])
			itemName = str(i)+'.'+str(item['name'])
			typeName = str(item['contentSummary']['typeName'])

			i +=1

			if self.tools.isSpided(itemId):
				print(itemName+' 已经爬过了')
				continue
			# itemUrl = self.url+'/'+typeName+'/'+itemId+'/'+slug  # 每节课程的地址
			# print(itemUrl) 
			
			# 这里只对视频课程以及文本课程进行处理   测试、讨论类的课程直接过滤
			if 'supplement' == typeName:
				self.doForSupplementPage(itemId,self.moduleNameDict[moduleId]+'/'+self.lessonsNameDict[lessonId],itemName)
			elif 'lecture' == typeName:
				self.doForVideoPage(itemId,self.moduleNameDict[moduleId]+'/'+self.lessonsNameDict[lessonId],itemName)



	# 解析视频页 视频源
	def doForVideoPage(self,itemId,dirName,itemName):
		url = self.baseurl+'onDemandLectureVideos.v1/%s~%s?'%(self.elementId,itemId) + self.videoInclude
		response = self.urlutil.get(url,self.session)
		response.encoding = 'UTF-8'
		jsonObject = json.loads(response.text)
		sources = jsonObject['linked']['onDemandVideos.v1'][0]['sources']['byResolution']
		subtitles = jsonObject['linked']['onDemandVideos.v1'][0]['subtitles']

		videoUrl = ''
		if not sources:
			print('视频源解析失败')
			return;
		if sources['720p']:
			videoUrl = sources['720p']['mp4VideoUrl']
		elif sources['540p']:
			videoUrl = sources['540p']['mp4VideoUrl']
		else:
			videoUrl = sources['360p']['mp4VideoUrl']

		print('发现视频：%s'%itemName)
		itemName = self.tools.removeSpecialChar(itemName)
		self.tools.downLoadFile(videoUrl,self.session,dirName,itemName+'.mp4')
		print('保存视频 '+itemName+'.mp4 成功\n')

		subtitleUrl = ''
		if 'zh-CN' in subtitles.keys():
			subtitleUrl = 'https://www.coursera.org'+subtitles['zh-CN']
		elif 'zh-TW' in subtitles.keys():
			subtitleUrl = 'https://www.coursera.org'+subtitles['zh-TW']

		if subtitleUrl:
			print('下载字幕 %s.srt\n'%itemName)
			response = self.urlutil.get(subtitleUrl,self.session)
			response.encoding = 'UTF-8'
			self.tools.writeFile(itemName+'.srt',response.text,dirName)

		self.tools.addSpidedRecord(itemId) 


	# 解析文本的页面
	def doForSupplementPage(self,itemId,dirName,itemName):
		url = self.baseurl+'onDemandSupplements.v1/%s~%s?'%(self.elementId,itemId) +self.supplementsInclude
		response = self.urlutil.get(url,self.session)
		response.encoding = 'UTF-8'
		jsonObject = json.loads(response.text)
		content = str(jsonObject['linked']['openCourseAssets.v1'][0]['definition']['value'])

		# 文本中可能包含一些附加文件  进行下载
		assetInfo = re.findall(self.assetPattern,content)
		if assetInfo:
			self.doForAsset(str(assetInfo[0][0]),dirName,str(assetInfo[0][1]),str(assetInfo[0][2]))

		content = content.replace('</text>','</text><br><br>')
		content = content.replace('<code>','<pre>')
		content = content.replace('</code>','</pre><br><br>')
		content = '<html><head></head><body>' + content + '</body></html>'

		print('发现网页：%s'%itemName)
		itemName = self.tools.removeSpecialChar(itemName)
		self.tools.writeFile(itemName+'.html',content,dirName)
		print('保存网页 '+itemName+'.html 成功\n')
		self.tools.addSpidedRecord(itemId)


	# 如果有需要下载到文件如pdf等  进行处理
	def doForAsset(self,assetId,dirName,itemName,assetsType):
		url = self.baseurl+'assets.v1?ids=%s&'%assetId + self.assetsInclude
		response = self.urlutil.get(url,self.session)
		response.encoding = 'UTF-8'
		jsonObject = json.loads(response.text)
		assetsUrl = jsonObject['elements'][0]['url']['url']

		print('发现文件：%s'%itemName)
		itemName = self.tools.removeSpecialChar(itemName)
		self.tools.downLoadFile(assetsUrl,self.session,dirName,itemName+'.'+assetsType)
		print('保存文件 '+itemName+'.'+assetsType+' 成功\n')



	def start(self):
		self.courseInfo = self.getCourseInfo()
		
		self.doForModules()
		self.doForLessons()
		self.doForItems() 
		

