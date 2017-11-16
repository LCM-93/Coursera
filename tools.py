# _*_ coding:utf-8 _*_
import re
import requests
from contextlib import closing
from progressBar import ProgressBar
import os


class Tools:
	def __init__(self):
		# 去除img标签，7位长空格
		self.removeImg = re.compile('<img.*?>| {7}')
		# 删除超链接标签
		self.removeAddr = re.compile('<a.*?>|</a>')
		# 把换行的标签换为\n
		self.replaceLine = re.compile('<tr>|</tr>|<div>|</div>|</p>')
		# 把表格制表换为 \t
		self.replaceTD = re.compile('<td>')
		# 把段落开头换为\n 加空两格
		self.replacePara = re.compile('<p.*?>')
		# 将换行符或双换行符替换为\n
		self.replaceBR = re.compile('<br><br>|<br>')
		# 将其余标签剔除
		self.removeExtraTag = re.compile('<.*?>')

		self.recordName = 'recordFile.txt'

		self.hrefPattern = re.compile('<a.*?href="(.*?)".*?>(.*?)</a>')

	# 保存网页  方便分析页面
	def writeFile(self,fileName,content,fileDir=None):
		if fileDir:
			self.createDir(fileDir)
			fileName = fileDir+'/'+fileName

		file = open(fileName,'w+')
		file.write(content)
		file.close()



	# 去除所有标签 方便提取文字
	def removeTag(self,x):
		x = re.sub(self.removeExtraTag,'',x)
		return x.strip()

	# 去除标题的特殊字符  防止创建文件失败 
	def removeSpecialChar(self,x):
		x = re.sub(r'[\/:*?"<>|]','-',str(x))
		return x.strip()

	def replaceContent(self,x):
		x = re.sub(self.removeImg,'',x)
		x = re.sub(self.removeAddr,'',x)
		x = re.sub(self.replaceTD,'\t',x)
		x = re.sub(self.replaceLine,'\n',x)
		x = re.sub(self.replacePara,'\n',x)
		x = re.sub(self.replaceBR,'\n',x)
		x = re.sub(self.removeExtraTag,'',x)
		return x.strip()

	def getHref(self,x):
		result = re.findall(self.hrefPattern,x)
		return result

	# 创建目录文件夹
	def createDir(self,fileDir):
		curpath = os.getcwd()
		if not os.path.isdir(curpath+'/'+fileDir):
			os.makedirs(curpath+'/'+fileDir)

	# 判断是否已经爬过
	def isSpided(self,url):
		curPath = os.getcwd()
		filePath = curPath+'/'+self.recordName
		if not os.path.isfile(filePath):
			return False
		f = open(filePath,'r')
		items = f.readlines()
		if items:
			if (url+'\n' in items):
				return True
			else:
				return False
		else:
			return False

	# 爬过的网页记录地址 
	def addSpidedRecord(self,url):
		curPath = os.getcwd()
		filePath = curPath+'/'+self.recordName
		f = open(filePath,'a')
		f.write(url+'\n')

	# 下载视频
	def downLoadFile(self,url,session,fileDir,fileName):
		self.createDir(fileDir)
		header = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}
		with closing(session.get(url,headers = header, stream=True)) as response:
			chunk_size = 1024 # 单次请求最大值
			content_size = int(response.headers['content-length']) # 内容体总大小
			progress = ProgressBar(fileName, total=content_size,
								unit="KB", chunk_size=chunk_size, run_status="正在下载", fin_status="下载完成")
			with open(fileDir+'/'+fileName, "wb") as file:
				for data in response.iter_content(chunk_size=chunk_size):
					file.write(data)
					progress.refresh(count=len(data))


def main():
	tools= Tools()
	name = '张三:李四*王五>赵六<成七|哈哈'
	print(name)
	name = tools.removeSpecialChar(name)
	print(name)

if __name__ == '__main__':
	main()