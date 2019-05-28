import requests
import urllib
import re
import os
import time
from urllib.parse import urlparse

'''
广度爬虫，通过baidu来进行爬取，输入一些特定的关键词，来对网站进行抓取
'''

page = int(input('爬取页数(一页10个url)：'))
sleep = 0.5     # 每次请求延迟时间，防止被ban

day = time.strftime('%Y-%m-%d',time.localtime(time.time()))

a = 1

def collect_url(keyword,pages):
    '''
    收集百度结果的链接
    :param keyword:关键字
    :param pages: 第pages页
    :return:返回去重后的列表
    '''
    page = str(int(pages) - 1) + '0'
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0'}
    url = 'https://www.baidu.com/s?wd=%s&pn=%s' % (keyword,page)
    try:
        response = requests.get(url=url,headers=headers)
        url_results = re.findall(r'<a target="_blank" href="(\S+)" class="c-showurl"',response.text)        #findall()的参数必须是string，所以要用.txt(unicode)为不是.content(byte)
        return list(set(url_results))                                                                       #set是为了去重
    except Exception as e:
        return []

def url_location(url):
    '''
    获取相应头的location内容，即真正的url
    :param url: 百度结果页面的url，并不是我们真正想要的url
    :return:获取相应头的location内容，即真正的url
    '''
    try:
        time.sleep(0.5)
        ret = requests.get(url,allow_redirects=False).headers.get('location')
        return ret
    except Exception:
        pass


def main():

    script = input('请输入要爬取的site-例：*.gov.cn、*.edu.cn等正规域名(不可为空)：')
    script1 = input("请输入要爬取的inurl-例：php、asp、html(为空请填-1):")
    script2 = input("请输入要爬取的intitle-例:登陆(为空请填-1):")
    if (script != '-1' and script1 != '-1' and script2 != '-1'):
       keywords = 'site:{} inurl:{} intitle:{}'.format( script, script1, script2)
    elif (script1 == '-1' and script2 == '-1'):
        keywords = 'site:{} '.format(script)
    elif(script2 == '-1'):
        keywords = 'site:{} inurl:{} '.format( script, script1 )
    elif(script1 == '-1'):
        keywords = 'site:{} intitle:{}'.format( script, script2)


    keyword = urllib.parse.quote(keywords)                                              #对关键字编码
    print('Crawling : [%s]  正在爬取..................' % keywords)

    for pageNum in range(0,page):
        eachPage_url = map(url_location,collect_url(keyword=keyword,pages=pageNum))                     #从百度结果获取的url得到真正的url
        for each_url in set(eachPage_url):                                                              #去重
            print('Baidu-Page:{0}>>>{1}'.format(pageNum,each_url))
            if each_url != None:
                with open('goodqueries.txt', 'a+') as f:
                    # TODO 对文件名的修改，将good.txt改成goodqueries.txt，方便样本集的聚合，只读取goodqueries.txt与badqueries.txt两个样本集
                    f.writelines(each_url + '\n')                                                                      #写入文件



if __name__ == '__main__':
    main()
