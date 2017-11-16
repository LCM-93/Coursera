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
		self.moduleNameDict = {}
		i = 1
		for module in modules:
			dirName = self.title+'/'+str(i)+'.'+str(module['name'])
			self.moduleNameDict[module['id']] = dirName
			description = module['description']
			i += 1
			self.tools.writeFile('简介.txt',description,dirName)

	# 处理课程
	def doForLessons(self):
		lessons = self.courseInfo['onDemandCourseMaterialLessons.v1']
		self.lessonsNameDict= {}
		for lesson in lessons:
			dirName = str(lesson['name'])
			moduleId = str(lesson['moduleId'])
			self.lessonsNameDict[lesson['id']] = dirName
			self.tools.createDir(self.moduleNameDict[moduleId]+'/'+dirName)


	# 处理每一小节的课程
	def doForItems(self):
		items = self.courseInfo['onDemandCourseMaterialItems.v2']

		for item in items:
			lessonId = str(item['lessonId'])
			moduleId = str(item['moduleId'])
			itemId = str(item['id']) 
			slug = str(item['slug'])
			itemName = str(item['name'])
			typeName = str(item['contentSummary']['typeName'])

			# itemUrl = self.url+'/'+typeName+'/'+itemId+'/'+slug
			# print(itemUrl) 
			if 'supplement' == typeName:
				self.doForSupplementPage(itemId,self.moduleNameDict[moduleId]+'/'+self.lessonsNameDict[lessonId],itemName)
			# elif 'lecture' == typeName:
			# 	self.doForVideoPage(itemId,self.moduleNameDict[moduleId]+'/'+self.lessonsNameDict[lessonId],itemName)



	# 解析视频页 视频源
	def doForVideoPage(self,itemId,dirName,itemName):
		url = self.baseurl+'onDemandLectureVideos.v1/%s~%s?'%(self.elementId,itemId) + self.videoInclude
		response = self.urlutil.get(url,self.session)
		response.encoding = 'UTF-8'
		jsonObject = json.loads(response.text)
		sources = jsonObject['linked']['onDemandVideos.v1'][0]['sources']['byResolution']

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


	# 解析文本的页面
	def doForSupplementPage(self,itemId,dirName,itemName):
		url = self.baseurl+'onDemandSupplements.v1/%s~%s?'%(self.elementId,itemId) +self.supplementsInclude
		response = self.urlutil.get(url,self.session)
		response.encoding = 'UTF-8'
		jsonObject = json.loads(response.text)
		content = str(jsonObject['linked']['openCourseAssets.v1'][0]['definition']['value'])

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



	def start(self):
		self.courseInfo = self.getCourseInfo()
		
		self.doForModules()
		self.doForLessons()
		self.doForItems() 
		

