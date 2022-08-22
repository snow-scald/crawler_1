import logging
import re
import csv
from random import randint
from queue import Queue
from bs4 import BeautifulSoup
import aiohttp
import asyncio

CONCURRENCY=5
MAXRES=10
session=None
semaphore=asyncio.Semaphore(CONCURRENCY)

proxies=["59.124.224.205:3128",
            "47.57.188.208:80",
            "117.157.197.18:3128",
            "47.92.113.71:80",
            "218.7.171.91:3128"]
firurl="https://book.douban.com/subject/26912767/"
headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36 Edg/103.0.1264.49'}

logging.basicConfig(level=logging.INFO,format='[%(asctime)s]  %(message)s')
csvoutput=open('output.csv','w',newline="")
writer=csv.writer(csvoutput)

myque=Queue()
myque.put(firurl)
mylist=[]

count=0

async def crawl(url):
    async with semaphore:
        global count,myque,mylist
        logging.info('Crawling %d %s',count,url)
        async with session.get(url,headers=headers) as response:
            html=await response.text()
            #print(html)
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

            soup=BeautifulSoup(html,'lxml')
            newitemspos=soup.find_all(attrs={'class':"content clearfix"})
            newitems=newitemspos[-1].find_all(name='a')

        for i in newitems:
            myque.put(i.get('href'))

async def main():
    global session
    session=aiohttp.ClientSession()
    while (count<MAXRES) and (not myque.empty()):
        u=myque.get()
        if u in mylist:
            continue
        else:
            await crawl(u)
            mylist.append(u)
    csvoutput.close()

if __name__=='__main__':
    asyncio.get_event_loop().run_until_complete(main())

