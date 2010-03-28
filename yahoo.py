#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Yahoo!奇摩拍賣 資料探勘程式 0.1.2 at 2008/11/06
#License: GNU General Public License v2
#Author: DreamerC <dreamerwolf.tw+yahoo@gmail.com>

from sgmllib import SGMLParser

class dig(SGMLParser):
    "Yahoo! Kimo Bid Parser (http://tw.bid.yahoo.com/)"

    def parse(self, s):
        "剖析器主程序"
        self.feed(s)
        self.close()

    def reset(self):
        "初始化"

        self.hyperlinks = []
        self.descriptions = []
        self.hyperlinks_image = []
        self.dollars = []
        self.usernames = []
        self.inside_a_element = 0
        self.inside_values = []
        self.inside_elements = ["root","body"]
        SGMLParser.reset(self)


    def start_tr(self, attributes):
        for name, value in attributes:
            if name == "class" and (value == "title" or value == "title hlight"):
                self.inside_elements.append("tr")
                self.inside_values.append(value)


    def end_tr(self):
        if self.inside_elements[-1] == "tr":
            self.inside_elements.pop()
            self.inside_values.pop()

    def start_th(self, attributes):
        self.inside_elements.append("th")

    def end_th(self):
        self.inside_elements.pop()

    def start_td(self, attributes):
        self.inside_elements.append("td")

    def end_td(self):
        self.inside_elements.pop()

    def start_li(self, attributes):
        self.inside_elements.append("li")
    
    def end_li(self):
        self.inside_elements.pop()

    def start_ul(self, attributes):
        self.inside_elements.append("ul")

    def end_ul(self):
        self.inside_elements.pop()

    def start_strong(self, attributes):
        self.inside_elements.append("strong")

    def end_strong(self):
        self.inside_elements.pop()

    def start_div(self, attributes):
        for name, value in attributes:
            if name == "class" and value == "puimg": 
                self.inside_elements.append("div")
                self.inside_values.append(value)

    def end_div(self):
        if self.inside_elements[-1] == "div":
            self.inside_elements.pop()
            self.inside_values.pop()

    def start_img(self, attributes):
        for name, value in attributes:
            if name == "src" and self.inside_elements[-2] == "th":
                self.hyperlinks_image.append(value)

    def end_img(self):
        pass

    def start_a(self, attributes):
        for name, value in attributes:
            if name == "href" and self.inside_elements[-2] == "tr":
                self.hyperlinks.append(value)
                self.inside_a_element = 1
            elif name == "href" and self.inside_elements[-1] == "li":
                import re
                if bool(re.search(u'http://tw.user.bid.yahoo.com/',value) or re.search(u'http://tw.mall.yahoo.com/',value)):
                    self.usernames.append(value)

    def end_a(self):
        self.inside_a_element = 0

    def handle_data(self, data):
        if self.inside_a_element and self.inside_elements[-2] == "tr" and self.inside_elements[-1] == "th":
            self.descriptions.append(data)
        if self.inside_elements[-2] == "td" and self.inside_elements[-1] == "strong":
            self.dollars.append(data)

    def get_hyperlinks(self):
        return self.hyperlinks

    def get_descriptions(self):
        return self.descriptions

    def get_hyperlinks_image(self):
        return self.hyperlinks_image

    def get_dollars(self):
        return self.dollars

    def get_usernames(self):
        return self.usernames

def run(url="http://tw.search.bid.yahoo.com/search/ac?p=wii",debug=1,proxies={'http': 'http://localhost:8118'}):

# 擷取網頁並儲存 cookie

    import urllib2, cookielib
    
    cj = cookielib.MozillaCookieJar()

    try:
        cj.load(filename='cookies.txt')
    except:
        print 'cookie 不存在, 將重新產生\n'

    fo = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    urllib2.install_opener(fo)
    fo.addheaders = [("User-agent", "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.5) Gecko/20031107 Debian/1.5-3"),("Accept", "text/html, image/jpeg, image/png, text/*, image/*, */*")]

    f = urllib2.urlopen(url)
    s = f.read()
    cj.save(filename='cookies.txt')

# 轉碼 & 修正
    
    import re
    utf8 = re.sub(re.compile('&quot;'), "\"", s.decode('cp950'))
    if debug == 1:
        print utf8
    try:
        items = int(re.findall(u'，<strong>(\d+)</strong>項商品', utf8)[0])
        try:
            url_next = str(re.findall(u'=\"/search/ac\?p=(.+?)\">下一頁</a>', utf8)[0])
        except:
            url_next = ''
    except:
        return -1,url_next
    utf8 = re.sub(u'&amp;', u'和', utf8)
    utf8 = re.sub(u'&gt;', u' ', utf8)
    utf8 = re.sub(u'沒有圖片', "<a><img src=\"http://localhost/nopic.jpg\"></a>", utf8)
    utf8 = re.sub(u"(\d),(\d)", r"\1\2", utf8)
    utf8 = re.sub(u'&#(.+?);',u' ',utf8)

# 剖析    
    dig_yahoo = dig()
    dig_yahoo.parse(utf8)

# 輸出
#   print len(dig_yahoo.get_hyperlinks())
    for x in range(len(dig_yahoo.get_hyperlinks())):
        p = dig_yahoo.get_descriptions()[x] + '  ' 
        p += dig_yahoo.get_hyperlinks()[x] + '  ' 
        p += dig_yahoo.get_hyperlinks_image()[x] + '  ' 
        p += dig_yahoo.get_dollars()[x] + '  ' 
        p += dig_yahoo.get_usernames()[x]
        if debug == 1:
            print p
        fopen = open("yahoo_bid.txt","a+")
        fopen.write(p.encode('utf-8')+"\n")
        fopen.close()

    return items,url_next

def print_help():
    print '''\
Yahoo!奇摩拍賣 資料探勘程式 0.1.2 at 2008/11/06

功能： 搜尋 奇摩! 雅虎拍賣

yahoo.py 擷取主程式
yahoo_bid.txt 產生資料
cookies.txt 自動產生 cookie 紀錄

python yahoo.py <選項> <關鍵字>

預設尋找 wii

選項功能:
  --debug   : 除錯模式
  --help    : 顯示本功能
'''

#
# 主程式開始
#


url = 'http://tw.search.bid.yahoo.com/search/ac?p='
search = u'皮靴'
debug = 0

import sys

if len(sys.argv) < 2:
    print_help()
    sys.exit()

if sys.argv[1].startswith('--'):
    option = sys.argv[1][2:]
    if option == 'debug':
        debug = 1
    else:
        print_help()
        sys.exit()

for keyword in sys.argv[1:]:
    search = keyword.decode('utf8')

import urllib2

# 需轉換成 CP950 的編碼再轉成 url encode
search = urllib2.quote(search.encode('cp950'))

import time
timer_a = time.clock()
print url+search+' 執行中....'
items,url_next = run(url+search,debug)

if items == -1:
    print '解析錯誤, 進行測試.'
    aa,url_next = run(url+u'wii',debug)
    if aa == -1:
        print u'999 Error 或是版本過舊, 請聯絡程式撰寫人. 立即結束本程式'
        import sys
        sys.exit()
    else:
        print u'解析成功, 重新嘗試'
        items,url_next = run(url+search,debug)

timer_b = time.clock()

print u'花費了 %f 秒解析成功...資料共 %d 筆' % ((timer_b-timer_a),items) ,
print u'暫停 5 秒'
time.sleep(5)

timer_c = 0

for i in range(52,items,51):
    timer_a = time.clock()
    urls = url+search+"&b="+str(i)
    print u'已抓取 ' + str(i - 1) + u' 筆....正在抓取 ' + urls ,
    if i == 52:
        a,url_next = run(urls,debug)
    else:
        if debug == 1:
            print url + url_next
        a,url_next = run(url+url_next,debug)

    if a == -1:
        print u'999 錯誤, 等待 600 秒後測試'
        time.sleep(600)
        aa,url_next = run(urls,debug)
        if aa == -1:
            print u'再度發生錯誤, 結束程式'
            import sys
            sys.exit()
        else:
            print u'測試成功, 重新執行'
            a,url_next = run(urls,debug)
    timer_b = time.clock()
    timer_c += timer_b-timer_a+1
    print u'花費了 %f 秒, 總共耗費 %f 秒' % ((timer_b-timer_a),timer_c)
    time.sleep(1)

print u'工作完成...........'
