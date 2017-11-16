# Coursera
使用Python3写的Coursera课程爬虫

[master](https://github.com/lichenming0516/Coursera/tree/master)分支是使用Selenium来加载js页面，再通过正则匹配等解析数据，效率较低。

[Coursera2](https://github.com/lichenming0516/Coursera/tree/Coursera2)分支是通过分析网络请求，直接通过接口请求页面json数据进行解析，效率较高。


### 使用

1. 命令行进入项目目录
2. 运行命令
	
	```
	python3 coursera.py -e email -p  password
	```

	`email`和 `password`分别换成你自己的账号密码

3. 输入你注册的课程主页地址
	
	例：[https://www.coursera.org/learn/hipython](https://www.coursera.org/learn/hipython)
	

	