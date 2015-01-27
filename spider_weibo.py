import requests
import base64
import re
import urllib
import rsa
import json
import binascii


# get the login parameter
def get_login_parameter():
    # open a request session
    url_prelogin = 'http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=&rsakt=mod&client=ssologin.js(v1.4.5)&_=1364875106625'
    session = requests.Session()
    response = session.get(url_prelogin)

    #get the login parameter servertime, nonce, pubkey, rsakv
    json_data = re.search('\((.*)\)', response.content).group(1)
    data = json.loads(json_data)
    servertime = data['servertime']
    nonce = data['nonce']
    pubkey = data['pubkey']
    rsakv = data['rsakv']
    return servertime, nonce, pubkey, rsakv


# login the weibo
def userlogin(username, password):
    servertime, nonce, pubkey, rsakv = get_login_parameter()

    # calculate the username by encryption
    su = base64.b64encode(urllib.quote(username))

    #calculate the public key
    rsaPublickey= int(pubkey,16)
    key = rsa.PublicKey(rsaPublickey,65537)

    # calculate the password by encryption
    message = str(servertime) +'\t' + str(nonce) + '\n' + str(password)
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
    url_login = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.5)'
    session = requests.Session()
    response = session.post(url_login, data=postdata)
    login_url = re.findall('replace\(\'(.*)\'\)',response.content)[0]

    # get the return login url and retcode
    retcode = re.findall('"retcode":(.*),"arrURL',response.content)[0]
    if retcode != '0':
        return (-1, session)

    # login
    respo = session.get(login_url)
    uid = re.findall('"uniqueid":"(\d+)",',respo.content)[0]
    return (0, session)

if __name__ == "__main__":
    user = "fanko24@gmail.com"
    password = "fanofkobe24"
    ret, session = userlogin(user, password)
    if ret != 0:
        print "login fail"
        sys.exit(1)
    url = "http://weibo.com/liucaofeng"
    response = session.get(url)
    print response.content
