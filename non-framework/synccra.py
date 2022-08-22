import time
import requests
import logging
import re
import csv
from queue import Queue
from bs4 import BeautifulSoup

#设置基本信息
firurl="https://book.douban.com/subject/26912767/"
headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36 Edg/103.0.1264.49'}
#使用logging库实时记录爬取进程
logging.basicConfig(level=logging.INFO,format='[%(asctime)s]  %(message)s')
csvoutput=open('output.csv','w',newline="")
writer=csv.writer(csvoutput)

myque=Queue()
myque.put(firurl)
mylist=[]

count=0

def crawl(url):
    global count,myque,mylist
    time.sleep(0.5)
    logging.info('Crawling %d %s',count,url)
    orihtml=requests.get(url,headers=headers)
    html=orihtml.text
    #评分
    score_res=re.findall('<strong class="ll rating_num " property="v:average">(.*?)</strong>',html,re.S)
    #投票人数
    voter_res=re.findall('<span property="v:votes">(.*?)</span>',html,re.S)
    #价格
    price_res=re.findall('<span class="pl">定价:</span>(.*?)([0-9.]*)(\D*?)<br/>',html,re.S)
    #出版时间
    publish_res=re.findall('<span class="pl">出版年:</span> (\d{4})(.*?)<br/>',html,re.S)
    writer.writerow([float(score_res[0]),int(voter_res[0]),float(price_res[0][1]),int(publish_res[0][0])])
    logging.info('Crawled %d %s',count,url)
    count=count+1

    newitemspos=re.findall('<div class="content clearfix">(.*?)</div>',html,re.S)
    newitems=re.findall('<a href="(.*?)"',newitemspos[-1],re.S)
    for i in newitems:
        myque.put(i)

while (count<50) and (not myque.empty()):
    u=myque.get()
    if u in mylist:
        continue
    else:
        crawl(u)
        mylist.append(u)

csvoutput.close()





