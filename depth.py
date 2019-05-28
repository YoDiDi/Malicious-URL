import requests
import re

'''
深度爬虫，输入一个网址，以此作为种子，根据里面的href进行深度爬取链接
'''

def url_is_correct():
    '''
    使用requests.get方法判断url是否正确,并返回url
    :return:
    '''
    try:
        url = input("请输入需要深度爬取的url例：-https://www.taobao.com(需要包含http、https协议的url):")
        requests.get(url)
        return url
    except:
        print('请输入正确的url！')
    return url_is_correct()

url = url_is_correct()   #将验证为正确的url地址赋值给url


def url_protocol(url):
    '''
    获取输入的url地址的协议，是http、https等
    '''
    print('该站使用的协议是：' + re.findall(r'.*(?=://)',url)[0])
    return re.findall(r'.*(?=://)',url)[0]

urlprotocol = url_protocol(url)

def same_url(url):
    '''
    处理用户输入的url，并为后续判断是否为一个站点的url做准备，爬取的时候不能爬到其它站，那么爬取将无止境
    '''
    #将完整的url中的http://、https://删除
    url = url.replace(urlprotocol + '://','')
    #判断删除http://之后的url有没有www，如果没有就加上‘www.’，但不存储，
    #只是为了同化所有将要处理的url，都有了‘www.’之后，
    #就可以找以‘www.’开始的到第一个‘/’结束中的所有字符串作为该站的主域名
    if re.findall(r'^www',url) == []:#如果没有www.
        sameurl = 'www.' + url
        if sameurl.find('/') != -1: # 找不到'/',返回-1
            sameurl = re.findall(r'(?<=www.).*?(?=/)', sameurl)[0]
        else:
            sameurl = sameurl + '/'
            sameurl = re.findall(r'(?<=www.).*?(?=/)', sameurl)[0]

    else:
        if url.find('/') != -1:  # 找不到'/',返回-1
            sameurl = re.findall(r'(?<=www.).*?(?=/)', url)[0]
        else:
            sameurl = url + '/'
            sameurl = re.findall(r'(?<=www.).*?(?=/)', sameurl)[0]
    print('同站域名地址：' + sameurl)
    return sameurl

domain_url = same_url(url)

class linkQuence:
    def __init__(self):
        self.visited = []    #已访问过的url初始化列表
        self.unvisited = []  #未访问过的url初始化列表

    def getVisitedUrl(self):  #获取已访问过的url
        return self.visited
    def getUnvisitedUrl(self):  #获取未访问过的url
        return self.unvisited
    def addVisitedUrl(self,url):  #添加已访问过的url
        return self.visited.append(url)
    def addUnvisitedUrl(self,url):   #添加未访问过的url
        if url != '' and url not in self.visited and url not in self.unvisited:
            return self.unvisited.insert(0,url)

    def removeVisited(self,url):   #删除访问过的url
        return self.visited.remove(url)
    def popUnvisitedUrl(self):    #从未访问过的url中取出一个url
        try:                      #pop动作会报错终止操作，所以需要使用try进行异常处理
            return self.unvisited.pop()
        except:
            return None
    def unvisitedUrlEmpty(self):   #判断未访问过列表是不是为空
        return len(self.unvisited) == 0

class Spider():
    '''
    真正的爬取程序
    '''
    def __init__(self,url):
        self.linkQuence = linkQuence()     #引入linkQuence类
        self.linkQuence.addUnvisitedUrl(url)   #并将需要爬取的url添加进linkQuence对列中，未访问过的url列表
        self.current_deepth = 1      #设置爬取的深度

    def getPageLinks(self,url):
        '''
        获取页面中的所有链接
        '''
        pageSource = requests.get(url).text
        pageLinks = re.findall(r'(?<=href=\").*?(?=\")|(?<=href=\').*?(?=\')',pageSource)  #利用正则查找所有连接

        return pageLinks

    def processUrl(self,url):
        '''
        判断正确的链接及处理相对路径为正确的完整url
        '''
        true_url = []
        for l in self.getPageLinks(url):
            if re.findall(r'/',l):  #返回"/",即查找url中是否有"/"
                if re.findall(r':',l):   #返回":",即查找url中是否有":"
                    true_url.append(l)
                else:
                    true_url.append(urlprotocol + '://' + domain_url + l)

        return true_url

    def sameTargetUrl(self,url):
        '''
        判断是否为同一站点链接，防止爬出站外，然后导致无限尝试爬取
        '''
        same_target_url = []
        for l in self.processUrl(url): #判断是否是正确的链接
            if re.findall(domain_url,l):
                same_target_url.append(l)

        return same_target_url

    def unrepectUrl(self,url):
        '''
        删除重复url
        '''
        unrepect_url = []
        for l in self.sameTargetUrl(url):
            if l not in unrepect_url:
                unrepect_url.append(l)

        for l in unrepect_url:
            print(url + '该url下不重复的url有------：' + l)
            # l = re.sub("http://", "", l) #过滤掉http://
            # l = re.sub("https://", "", l) #过滤掉https://
            f = open('goodqueries.txt', 'a+',encoding='utf-8')
            # TODO 将good.txt改成goodqueries.txt，方便样本集的聚合，只读取goodqueries.txt与badqueries.txt两个样本集
            f.writelines(l+'\n')
            f.close()

        return unrepect_url

    def crawler(self,crawl_deepth):
        '''
        正式的爬取，并依据深度进行爬取层级控制
        '''
        while self.current_deepth <= crawl_deepth:
            while not self.linkQuence.unvisitedUrlEmpty(): #不在未访问的url表中
                visitedUrl = self.linkQuence.popUnvisitedUrl() #从未访问的url表中取一个出来

                if visitedUrl is None or visitedUrl == '': #取出来的url是none或者为空，继续
                    continue

                links = self.unrepectUrl(visitedUrl) #删除重复url
                self.linkQuence.addVisitedUrl(visitedUrl) #添加url进入访问过的url表
                for link in links:
                    self.linkQuence.addUnvisitedUrl(link) #添加url进入未访问过的url表
            self.current_deepth += 1 #深度加一
        print(self.linkQuence.visited)
        return self.linkQuence.visited


if __name__ == '__main__':
    spider = Spider(url)
    depth = input('请输入要爬取的深度:')
    depth1 = int(depth)
    spider.crawler(depth1)