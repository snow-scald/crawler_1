# Practice crawler the hard way
对我们网络安全专业的同学来说，只会用轮子当然是不够的，造轮子的能力还是要有的。因此本实验使用非框架的requests，aiohttp等方法与scrapy框架两种方法完成。

## 实验完成度
- [x] 使用pipenv管理项目
- [x] 使用浏览器头骗过网站反爬虫
- [x] 使用正则表达式，beautifulsoup，xpath等多种方式提取元素
- [x] 使用协程爬虫提升爬取效率
- [x] 使用代理技术对抗ip封禁
- [x] 使用logging库记录爬取过程细节
- [x] 使用csv存储结果

- [x] 使用scrapy框架完成爬虫任务

## 非框架方法
使用非框架方法爬取豆瓣上计算机类书籍的评分，评分人数，单价及出版时间，同时在该页面上寻找到相似的书籍链接进一步爬取。

非框架方法下，相似书籍的链接可能循环，因此使用一个队列和一个列表进行管理（这一步可使用数据库改进），每次爬取页面后将该页面id存入列表，获取到新的连接悉数放入队列，下一次爬取时从队列中获取一个链接并检查是否存在于列表中，若不存在则进行爬取，若存在则跳过。

结果见[output.csv](/non-framework/output.csv) 
### pipenv管理
使用pipenv管理项目，配置文件见[Pipfile](/Pipfile)
### 同步爬虫
同步方法使用requests库请求页面，正则表达式提取相关元素，代码见[syncra.py](/non-framework/synccra.py)
用获取新链接为例，正则表达式用法：
```python
    newitemspos=re.findall('<div class="content clearfix">(.*?)</div>',html,re.S)
    newitems=re.findall('<a href="(.*?)"',newitemspos[-1],re.S)

```

使用变量MAXRES控制爬取信息总数。
### 协程爬虫
协程方法使用aiohttp库请求页面，正则表达式配合beautifulsoup提取相关元素，代码见[asynccra.py](/non-framework/asynccra.py)

为了练习多种页面元素定位能力，这里将新链接的定位用beautifulsoup方法改写
```python
    soup=BeautifulSoup(html,'lxml')
    newitemspos=soup.find_all(attrs={'class':"content clearfix"})
    newitems=newitemspos[-1].find_all(name='a')
```

由于过高的并发数量可能影响该网站运行，我们使用`asyncio.Semaphore`控制最大并发数量。
### logging使用
由于爬虫运行步骤较多，若出现问题比较难以调试，因此使用logging库实时监控爬取进程，如果出现了错误则可直接准确定位错误位置。

logging设置如下：

    logging.basicConfig(level=logging.INFO,format='[%(asctime)s]  %(message)s')

可输出每条信息爬取开始及结束的时间。

效果如图:![](/non-framework/img/logging.png)

### 反爬机制对抗

网站的反爬机制主要是检测请求头，ip封锁，账号封锁三种机制，由于我们爬取的内容不涉及账号登录，因此本次实验主要实现了请求头与ip封锁的对抗。

请求头：
```python
    headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36 Edg/103.0.1264.49'}

    #requests中
    requests.get(url,headers=headers)

    #aiohttp中
    async with session.get(url,headers=headers) as response:
```

ip封锁：主要通过使用代理解决，每次执行get时从ip池中随机选取一个ip进行代理。由于经费问题，我们这里选用了一部分不稳定的免费ip构建了一个简易的ip池，每次运行使用随机数从列表中选取一个ip，但免费代理运行情况不稳定。

若需测试
```python
#需将该ip池换为稳定ip
proxies=["59.124.224.205:3128",
            "47.57.188.208:80",
            "117.157.197.18:3128",
            "47.92.113.71:80",
            "218.7.171.91:3128"]
# asynccra.py 37 行
async with session.get(url,headers=headers) as response:
# 以及synccra.py 27行
requests.get(url,headers=headers)

#get中需添加 proxy=参数
```

## scrapy 框架方法
换个爬的内容吧，这次爬书名，准备下个实验用来做词云

工程文件位于[myscrapy1](/myscrapy1/myscrapy1)目录下，结果见[output.json](/myscrapy1/output.json)。
### scrapy优劣：

pros：
- 任务自动管理，省去了部署的细节
- 内禀了异步机制，不用手动实现异步及重复处理
- 爬取出错则会自动跳过，省去了异常处理

cons：
- 调试不直观
- 系统性较强，学习成本高

### 技术细节

输出结果字符编码以及请求头需在settings.py中添加
```python
USER_AGENT='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36 Edg/103.0.1264.49'
FEED_EXPORT_ENCODING = 'utf-8'
```

scrapy的核心爬取函数 prase中，使用了生成器，使得在爬取信息的时候可以同时将新的response和data返回到engine，engine自行识别返回类型并决定分发给spider和schedule。

scrapy会在response队列为空时自动结束，但在这里我们需要手动结束。可以通过全局变量设置结束条件从而结束爬取。

## 总结
本次实验使用了框架方法以及非框架方法爬取了豆瓣上的数据信息以及文字信息，并练习了反爬机制对抗，协程，正则表达式等技术，同时熟悉了scrapy的框架使用。

之后可以进一步提高的内容有：
- 使用selenium进行实时渲染测试
- 使用javascript逆向分析json的练习
- 基于cookie和session的模拟登录练习
- 使用深度学习方法进行验证码识别及页面智能解析
- 对scrapy框架中各middleware的进一步掌握
- 使用Appium爬取app信息
- 在服务器上部署基于Redis的分布式爬虫