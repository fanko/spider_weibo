# encoding: utf-8
# author: fanko24@gmail.com

import requests
import base64
import re
import urllib
import urllib2
import rsa
import json
import binascii
import time
from bs4 import BeautifulSoup
from weibo_user import *


class WEIBO:
    # init the class
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.session = None
        self.uid = None
        self.userlogin()


    # login the weibo
    def userlogin(self):
        servertime, nonce, pubkey, rsakv = self.get_login_parameter()

        # calculate the username by encryption
        su = base64.b64encode(urllib.quote(self.username))

        #calculate the public key
        rsaPublickey= int(pubkey, 16)
        key = rsa.PublicKey(rsaPublickey, 65537)

        # calculate the password by encryption
        message = str(servertime) +'\t' + str(nonce) + '\n' + str(self.password)
        sp = binascii.b2a_hex(rsa.encrypt(message,key))

        # the post data for login
        postdata = {'entry': 'weibo',
                    'gateway': '1',
                    'from': '',
                    'savestate': '7',
                    'userticket': '1',
                    'ssosimplelogin': '1',
                    'vsnf': '1',
                    'vsnval': '',
                    'su': su,
                    'service': 'miniblog',
                    'servertime': servertime,
                    'nonce': nonce,
                    'pwencode': 'rsa2',
                    'sp': sp,
                    'encoding': 'UTF-8',
                    'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
                    'returntype': 'META',
                    'rsakv' : rsakv,
                   }

        # login url
        pre_login_url = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.5)'
        self.session = requests.Session()
        response = self.session.post(pre_login_url, data=postdata)
        time.sleep(1)
        login_url = re.findall('replace\(\'(.*)\'\)',response.content)[0]

        # get the personal login url and retcode
        retcode = re.findall('"retcode":(.*),"arrURL',response.content)[0]
        if retcode != '0':
            return -1

        # login
        respo = self.session.get(login_url)
        time.sleep(1)
        self.uid = re.findall('"uniqueid":"(\d+)",',respo.content)[0]
        return 0


    # get the login parameter
    def get_login_parameter(self):
        # open a request session
        url_prelogin = 'http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=&rsakt=mod&client=ssologin.js(v1.4.5)&_=1364875106625'
        self.session = requests.Session()
        response = self.session.get(url_prelogin)
        time.sleep(1)

        #get the login parameter servertime, nonce, pubkey, rsakv
        json_data = re.search('\((.*)\)', response.content).group(1)
        data = json.loads(json_data)
        servertime = data['servertime']
        nonce = data['nonce']
        pubkey = data['pubkey']
        rsakv = data['rsakv']
        return servertime, nonce, pubkey, rsakv


    # 退出登录
    def exit(self):
        url = "http://weibo.com/logout.php?backurl=%2F"
        response = self.session.get(url)
        time.sleep(1)
        return 0


    # 计算每个uid的基本信息
    def compute_user(self, uid):
        user = WEIBO_USER()
        url = "http://weibo.com/u/"+uid
        response = self.session.get(url)
        time.sleep(1)

        # page id
        pid = re.findall("CONFIG\['page_id'\]='(.*)'; " ,response.content)
        if pid:
            user.pid = pid[0]

        # user id
        uid = re.findall("CONFIG\['oid'\]='(.*)'; " ,response.content)
        if uid:
            user.uid = uid[0]

        # nickname
        nickname = re.findall("CONFIG\['onick'\]='(.*)'; " ,response.content)
        if nickname:
            user.nickname = nickname[0]

        # regex for number of followers, followed and tweets
        regex = ur'<strong class=\\"W_f18\\">(\d+)<\\/strong>.*<strong class=\\"W_f18\\">(\d+)<\\/strong>.*<strong class=\\"W_f18\\">(\d+)<\\/strong>'
        link = re.findall(regex, response.content)
        if link:
            # number of follows
            user.follows_number = int(link[0][0])
            # number of fans
            user.fans_number = int(link[0][1])
            # number of tweets
            user.tweets_number = int(link[0][2])

        # user information
        if user.pid:
            ret = self.compute_info(user)

        # user fans list
        if user.pid and user.fans_number:
            ret = self.compute_fans(user)

        # user follow list
        if user.pid and user.follows_number:
            ret = self.compute_follows(user)

        return user


    def compute_info(self, user):
        info_url = "http://weibo.com/p/%s/info" %user.pid
        response = self.session.get(info_url)
        time.sleep(1)
        soup = BeautifulSoup(response.content)
        script = soup.find_all("script")
        for item in script:
            if ur"<span class=\"main_title W_fb W_f14\">基本信息<\/span><\/h4>" in item.string:
                # sex of user
                re_sex = re.findall(ur"性别：<\\/span><span class=\\\"pt_detail\\\">(.*?)<\\/span>", item.string)
                if re_sex:
                    user.sex = re_sex[0]

                # birth of user
                re_birth = re.findall(ur"生日：<\\/span><span class=\\\"pt_detail\\\">(.*?)<\\/span>", item.string)
                if re_birth:
                    user.birth = re_birth[0]

                # location of user
                re_loc = re.findall(ur"所在地：<\\/span><span class=\\\"pt_detail\\\">(.*?)<\\/span>", item.string)
                if re_loc:
                    user.loc = re_loc[0]

                re_rt = re.findall(ur"注册时间：<\\/span>\\r\\n\\t\\t\\t\\t\\t\\t\\t\\t\\t<span class=\\\"pt_detail\\\">\\r\\n\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t(.*?)\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t<\\/span>", item.string)
                if re_rt:
                    user.register_time = re_rt[0]

                # QQ of user
                re_qq = re.findall(ur"QQ：<\\/span>\\r\\n        \\t\\t\\t\\t\\t\\t\\t<span class=\\\"pt_detail\\\">(.*?)<\\/span>", item.string)
                if re_qq:
                    user.qq = re_qq[0]

                # mail of user
                re_mail = re.findall(ur"邮箱：<\\/span><span class=\\\"pt_detail\\\">(.*?)<\\/span>", item.string)
                if re_mail:
                    user.mail = re_mail[0]

                # vocation of user
                comp = re.findall(ur"target=\\\"_blank\\\">(.*?)<\\/a>", item.string)
                work_year = re.findall(ur"\((\d*?) - (\d*?)\)", item.string)
                for i in range(min(len(work_year), len(comp))):
                    user.vocation.append((comp[i], work_year[i][0], work_year[i][1]))


                # education of user
                begin = item.string.find(u"教育信息")
                if begin != -1:
                    edu = re.findall(ur"<li class=\\\"li_1 clearfix\\\"><span class=\\\"pt_title S_txt2\\\">(.*?)：<\\/span>\\r\\n\\t\\t\\t\\t\\t\\t\\t\\t<span class=\\\"pt_detail\\\">\\r\\n\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t<a href=\\\"http:\\/\\/s.weibo.com\\/user\\/&school=.*?loc=infedu\\\">(.*?)<\\/a> ((\(.*?\))*)\\t", item.string[begin:])
                    user.education = [(i[0], i[1], i[2].strip("()")) for i in edu]

                # tag of user
                begin = item.string.find(u"标签：")
                if begin != -1:
                    user.tag_list = re.findall(ur"<\\/em>\\r\\n\\t\\t\\t\\t\\t\\t\\t\\t<\\/span>\\r\\n\\t\\t\\t\\t\\t\\t\\t\\t(.*?)\\t\\t\\t\\t\\t\\t\\t\\t<\\/a>", item.string[begin:])
        return 0


    def compute_fans(self, user):
        MAX_PAGE = 5
        page = min((user.fans_number-1)/20+1, MAX_PAGE)
        for i in range(1, page+1):
            fans_url = "http://weibo.com/p/%s/follow?relate=fans&page=%d" %(user.pid, i)
            response = self.session.get(fans_url)
            time.sleep(1)
            soup = BeautifulSoup(response.content)
            script = soup.find_all("script")
            for item in script:
                if item.string:
                    if ur"<!--关注\/粉丝列表--" in item.string:
                        re_uid = re.findall(ur"action-type=\\\".*?\\\" action-data=\\\"uid=(\d+?)&fnick=", item.string)
                        user.fans_list.extend(re_uid)
        user.fans_list = {}.fromkeys(user.fans_list).keys()
        return 0


    def compute_follows(self, user):
        MAX_PAGE = 5
        page = min((user.follows_number-1)/20+1, MAX_PAGE)
        for i in range(1, page+1):
            follow_url = "http://weibo.com/p/%s/follow?page=%d" %(user.pid, i)
            response = self.session.get(follow_url)
            time.sleep(1)
            soup = BeautifulSoup(response.content)
            script = soup.find_all("script")
            for item in script:
                if item.string:
                    if ur"<!--关注\/粉丝列表--" in item.string:
                        re_uid = re.findall(ur"action-type=\\\".*?\\\" action-data=\\\"uid=(\d+?)&fnick=", item.string)
                        user.follows_list.extend(re_uid)
        user.follows_list = {}.fromkeys(user.follows_list).keys()
        return 0


if __name__ == "__main__":
    fout = open("user.profile", "w")
    ffail = open("user.id.fail", "w")
    fsuccess = open("user.id.success", "w")
    account_list = [("fanko24@qq.com", "fanofkobe"), ("8137125@qq.com", "fanofkobe"), ("2949948008@qq.com", "fanofkobe"), ("fanko23@qq.com", "fanofkobe")]

    already_dict = {}
    id_list = [u"1290899453"]
    count = 0
    weibo = None
    user = None
    account_id = 0
    while id_list:
        uid = id_list[0]
        if uid in already_dict:
            id_list = id_list[1:]
            continue
        already_dict[uid] = 1

        if count % 100 == 0:
            if not weibo:
                weibo.exit()
            username = account_list[account_id][0]
            password = account_list[account_id][1]
            weibo = WEIBO(username, password)
            account_id = (account_id + 1)%len(account_list)

        day = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        try:
            user = weibo.compute_user(uid)
            fsuccess.write("%s\t%s\n" %(uid, day))
            fsuccess.flush()
        except:
            ffail.write("%s\t%s\n" %(uid, day))
            ffail.flush()
        json_str = user.json_dump()
        fout.write("%s\t%s\t%s\n" %(uid, day, json_str))
        fout.flush()
        id_list.extend(user.fans_list)
        id_list.extend(user.follows_list)
        id_list = id_list[1:]
        count += 1
        time.sleep(1)
    fout.close()
    ffail.close()
    fsuccess.close()
