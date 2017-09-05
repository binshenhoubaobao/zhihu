#-*- coding:utf-8 -*-
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Required
- requests (必须)
- pillow (可选)
'''

import requests
try:
    import cookielib
except:
    import http.cookiejar as cookielib
import re
import time
import os.path
try:
    from PIL import Image
except:
    pass
import sys

import MySQLdb
reload(sys)
sys.setdefaultencoding('utf-8')

headers = {'User-Agent': "Mozilla/5.0 (X11; Linux i686; rv:43.0) Gecko/20100101 Firefox/43.0 Iceweasel/43.0.4",
               'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
               'Accept - Encoding': "gzip, deflate",
               'Host': 'www.zhihu.com',
               'Referer': "https://www.zhihu.com/"}

session = requests.session()
session.cookies = cookielib.LWPCookieJar(filename='cookies')
try:
    session.cookies.load(ignore_discard=True)
except:
    print("Cookie 未能加载")

class ZhiHu(object):
    def __init__(self,user_name,password):

        self.user_name = user_name
        self.password = password

    def get_xsrf(self):
        '''_xsrf 是一个动态变化的参数'''
        index_url = 'https://www.zhihu.com'
        # 获取登录时需要用到的_xsrf
        index_page = session.get(index_url, headers=headers)
        html = index_page.text
        pattern = r'name="_xsrf" value="(.*?)"'
        # 这里的_xsrf 返回的是一个list
        _xsrf = re.findall(pattern, html)
        return _xsrf[0]

    def get_captcha(self):
        t = str(int(time.time() * 1000))
        captcha_url = 'https://www.zhihu.com/captcha.gif?r=' + t + "&type=login"
        r = session.get(captcha_url, headers=headers)
        with open('captcha.jpg', 'wb') as f:
            f.write(r.content)
            f.close()
        # 用pillow 的 Image 显示验证码
        # 如果没有安装 pillow 到源代码所在的目录去找到验证码然后手动输入
        try:
            im = Image.open('captcha.jpg')
            im.show()
            im.close()
        except:
            print '请到 %s 目录找到captcha.jpg 手动输入' % os.path.abspath('captcha.jpg')
        captcha = raw_input("输入图片中的验证码：\n>")
        return captcha

    @property
    def login_zhihu(self):
        # 通过输入的用户名判断是否是手机号
        if re.match(r"^1\d{10}$", self.user_name):
            print("手机号登录 \n")
            post_url = 'https://www.zhihu.com/login/phone_num'
            postdata = {
                '_xsrf': self.get_xsrf(),
                'password': self.password,
                'remember_me': 'true',
                'phone_num': self.user_name,
            }
        # 可加上邮箱的判断，这里不加了
        else:
            print("邮箱登录 \n")
            post_url = 'https://www.zhihu.com/login/email'
            postdata = {
                '_xsrf': self.get_xsrf(),
                'password': self.password,
                'remember_me': 'true',
                'email': self.user_name,
            }
        try:
            # 不需要验证码直接登录成功
            login_page = session.post(post_url, data=postdata, headers=headers)
            login_code = login_page.text
            print(login_page.status)
            print(login_code)
        except:
            # 需要输入验证码后才能登录成功
            postdata["captcha"] = self.get_captcha()
            login_page = session.post(post_url, data=postdata, headers=headers)
            login_code = eval(login_page.text)
            print  login_code['msg'].decode('utf-8')

            return login_code['r']
        session.cookies.save()

    def isLogin(self):
        # 通过查看用户个人信息来判断是否已经登录
        url = "https://www.zhihu.com/settings/profile"
        login_code = session.get(url, allow_redirects=False).status_code
        if int(x=login_code) == 200:
            print('您已经登录')
            return True
        else:
            print('正在登录，请稍等。。。。。')
            return False

def get_following():
    '''<input autocomplete="off" class="zg-form-text-input" name="url_token" id="url_token" value="bing-shen-hou-bao-bao" required>'''
    profile_url = "https://www.zhihu.com/settings/profile"
    profile_page = session.get(profile_url,headers=headers).text
    pattern_yuming = re.compile("<input autocomplete=\"off\" class=\"zg-form-text-input\" name=\"url_token\" id=\"url_token\" value=\"(.*?)\"")
    yuming = re.findall(pattern_yuming,profile_page)[0]
    print yuming
    following_url = 'https://www.zhihu.com/people/'+yuming+'/following'
    following_page = session.get(following_url,headers=headers).text
    following_page.decode('utf-8')
    '''
    pattern_HeaderName = re.compile("class=\"ProfileHeader-name\">(.*?)</span>")
    str_HeaderName = re.findall(pattern_HeaderName,following_page)[0]

    pattern_headline = re.compile("class=\"RichText ProfileHeader-headline\">(.*?)</span>")
    str_headline = re.findall(pattern_headline, following_page)[0]

    pattern_HeaderTips = re.compile("class=\"ProfileHeader-tips\">(.*?)</span>")
    str_HeaderTips = re.findall(pattern_HeaderTips, following_page)[0]

    pattern_Header = re.compile("class=\"ProfileHeader-contentHead\">.*?class=\"ProfileHeader-name\">(.*?)</span>.*?class=\"RichText ProfileHeader-headline\">(.*?)</span>.*?class=\"ProfileHeader-tips\">(.*?)</span>")

    print '昵称：%s \n签名：%s\n个人资料：%s\n'%(str_HeaderName,str_headline,str_HeaderTips)
    '''

    pattern_Header = re.compile('class="ProfileHeader-name">(.*?)</span><span class="RichText ProfileHeader-headline">(.*?)</span>')

    result = re.findall(pattern_Header,following_page)
    print '个人资料 昵称：%s \n签名：%s\n个人资料：\n' % (result[0])

    pattern_ContentItem = re.compile('a class="UserLink-link".*? href="(.*?)".*?src="(.*?)".*?alt="(.*?)"')
    result_content = re.findall(pattern_ContentItem, following_page)
    follow = []
    for item in result_content:
        print '我关注的人 个人主页：%s \n头像：%s\n昵称：%s\n' % (item)
        follow.append(item[0])
    return follow


def get_info():
    profile_url = "https://www.zhihu.com/settings/profile"
    profile_page = session.get(profile_url,headers=headers).text
    pattern_yuming = re.compile("<input autocomplete=\"off\" class=\"zg-form-text-input\" name=\"url_token\" id=\"url_token\" value=\"(.*?)\"")
    yuming = re.findall(pattern_yuming,profile_page)[0]
    print yuming
    following_url = 'https://www.zhihu.com/people/'+ yuming
    following_page = session.get(following_url,headers=headers).text
    following_page.decode('utf-8')

    pattern_Header = re.compile('class="ProfileHeader-name">(.*?)</span><span class="RichText ProfileHeader-headline">(.*?)</span></h1></div><span class="ProfileHeader-tips">(.*?)</span>')

    result = re.findall(pattern_Header,following_page)
    print '个人资料 昵称：%s \n签名：%s\n个人资料：\n' % (result[0])

    pattern_ContentItem = re.compile('a class="UserLink-link".*? href="(.*?)".*?src="(.*?)".*?alt="(.*?)"')
    result_content = re.findall(pattern_ContentItem, following_page)
    for item in result_content:
        print '我关注的人 个人主页：%s \n头像：%s\n昵称：%s\n' % (item)
    return yuming


if __name__ =='__main__':
    print '登录知乎测试!!'
    '''
    profile_url = "https://www.zhihu.com/people/bing-shen-hou-bao-bao/following"
    profile_page = session.get(profile_url, headers=headers).text
    profile_page.decode('utf-8')

    html_txt = open('./following.txt')
    try:
        html_str = html_txt.read()
    except:
        html_txt.close()
    html_txt.close()

    pattern_ContentItem = re.compile('a class="UserLink-link".*? href="(.*?)".*?src="(.*?)".*?alt="(.*?)"')
    result_content = re.findall(pattern_ContentItem, html_str)
    for item in result_content:
        print '我关注的人 个人主页：%s \n头像：%s\n昵称：%s\n' % (item)
    '''
    userName = raw_input('用户名: ')
    password = raw_input('密码: ')
    zhihu = ZhiHu(userName,password)
    if zhihu.isLogin():
        print '您已经登录'
    else:
        result = zhihu.login_zhihu
        if result == 0:
            # 爬取登录成功后的网站内容
            conf_url = "https://www.zhihu.com/settings/profile"
            text = session.get(conf_url, headers=headers).text
            follows = get_following()
            for follow in follows:
                print follow


