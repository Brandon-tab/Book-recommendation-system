import json
import time
import csv

import django
import pandas as pd
import os
import requests
from lxml import etree
import re
import random
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE','doubanBook.settings')
django.setup()
from myApp.models import BookList

class spider(object):
    # init
    def __init__(self, tag, page):
        self.tag = tag # 图书标签（如"小说"）
        self.page = page # 分页页码
        self.spiderUrl = 'https://book.douban.com/tag/%s?start=%s'
        self.bookId = 0
        self.headers = { # 请求头（模拟浏览器）
            'HOST': 'book.douban.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
            'Referer': 'https://book.douban.com/tag/',
        }

    def main(self):
        resq = requests.get(self.spiderUrl % (self.tag, self.page * 20), headers=self.headers)
        print('爬取页面为:' + self.spiderUrl % (self.tag, self.page * 20))
        # print(resq.text)
        respXpath = etree.HTML(resq.text)
        # get all <ul></ul>
        li_list = respXpath.xpath('//ul[@class="subject-list"]/li/div[2]/h2/a')
        # print(li_list)
        # all <a> href
        detailLinks = [x.xpath('@href')[0] for x in li_list]
        # print(detailLinks)
        for i in detailLinks:
            try:
                print('The target URL being scraped is ' + i)
                respDetail = requests.get(i, headers=self.headers)
                respDetailXpath = etree.HTML(respDetail.text)
                # title
                title = respDetailXpath.xpath('//span[@property="v:itemreviewed"]/text()')[0]
                # cover
                cover = respDetailXpath.xpath('//img[@rel="v:photo"]/@src')[0]
                # info
                info = respDetailXpath.xpath('//div[@id="info"]')[0]
                # author
                author = info.xpath('./span[1]/a/text()')[0]
                # press
                press = info.xpath('./a/text()')[0]
                # year
                year = re.search('\d{4}-\d{1,2}', "".join(respDetailXpath.xpath('//div[@id="info"]/text()'))).group()
                # pageNum
                regex = re.compile(r"\d{4}-\d{1,2}")
                pageNum = re.search('\d{3}',
                                    regex.sub('', "".join(respDetailXpath.xpath('//div[@id="info"]/text()')))).group()
                # price
                try:
                    price = re.search('(\d+)\.\d+元?',
                                      "".join(respDetailXpath.xpath('//div[@id="info"]/text()'))).group(1)
                except:
                    price = random.randint(1, 1000)
                # rate
                rate = respDetailXpath.xpath('//strong[@property="v:average"]/text()')[0].strip()
                # startList
                startList = json.dumps(
                    [float(x.text.replace('%', '')) for x in respDetailXpath.xpath('//span[@class="rating_per"]')])

                # summary
                summary = ""
                for s in [x.text for x in
                          respDetailXpath.xpath('//div[@id="link-report"]/span[@class="short"]/div[@class="intro"]/p')]:
                    if s: summary += s

                # detailLink
                detailLink = i
                createTime = time.localtime(time.time())

                # comment_len
                comment_len = re.search('\d+',
                                        respDetailXpath.xpath('//div[@class="mod-hd"]//span[@class="pl"]/a/text()')[
                                            0]).group()

                # commentList
                commentList = []
                for c in respDetailXpath.xpath('//ul/li[@class="comment-item"]'):
                    try:
                        userNmae = c.xpath('.//h3/span[@class="comment-info"]/a[1]/text()')[0]
                        start = int(int(re.search('\d+', c.xpath('.//h3/span[@class="comment-info"]/span[1]/@class')[
                            0]).group()) / 10)
                        userId = random.randint(1, 100)
                        createTime = c.xpath('.//h3/span[@class="comment-info"]/a[2]/text()')[0][:10]
                        content = c.xpath('.//p[@class="comment-content"]/span/text()')[0]
                        commentList.append({
                            'userNmae': userNmae,
                            'start': start,
                            'bookId': self.bookId,
                            'userId': userId,
                            'createTime': createTime,
                            'content': content
                        })
                    except:
                        continue
                commentList = json.dumps(commentList)
                self.save_to_csv([
                    self.bookId,
                    self.tag,
                    title,
                    cover,
                    author,
                    press,
                    year,
                    pageNum,
                    price,
                    rate,
                    startList,
                    summary,
                    detailLink,
                    createTime,
                    comment_len,
                    commentList
                ])
                self.bookId += 1
            except:
                continue

    def save_to_csv(self, rowData):
        with open('./temp.csv', 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(rowData)

    def init(self):
        if not os.path.exists('./temp.csv'):
            with open('./temp.csv', 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(
                    ["bookId", "tag", "title", "cover", "author", "press", "year", "pageNum", "price", "rate",
                     "startList", "summary", "detailLink",
                     "createTime", "comment_len", "commentList"])

    #Deduplication
    def clearData(self):
        df = pd.read_csv('./temp.csv')
        df.dropna(inplace=True)
        df.drop_duplicates(inplace=True)
        #总数居条数为
        print("总数居条数为%d" % df.shape[0])
        return df.values

    def save_to_sql(self):
        data = self.clearData()
        for book in data:
            print(book[0])
            BookList.objects.create(
                bookId=book[0],
                tag=book[1],
                title=book[2],
                cover=book[3],
                author=book[4],
                press=book[5],
                year=book[6],
                pageNum=book[7],
                price=book[8],
                rate=book[9],
                startList=book[10],
                summary=book[11],
                detailLink=book[12],
                createTime=book[13],
                comment_len=book[14],
                commentList=book[15]
            )
# 爬取数据（main()）。
# 初始化CSV表头（init()，实际未调用）。
# 清洗数据并存入数据库（save_to_sql()）。
if __name__ == '__main__':
    spiderObj = spider('小说', 0)
    # spiderObj.main()
    # spiderObj.init()
    spiderObj.save_to_sql()