# encoding: utf-8

import sys
import json


class WEIBO_USER:
    def __init__(self):
        self.uid = None
        self.pid = None
        self.nickname = None

        self.fans_number = None
        self.follows_number = None
        self.tweets_number = None

        self.sex = None
        self.birth = None
        self.loc = None
        self.education = []
        self.vocation = []
        self.register_time = None
        self.qq = None
        self.mail = None
        self.tag_list = []
        self.fans_list = []
        self.follows_list = []


    def json_dump(self):
        user_dict = {}
        user_dict["uid"]= self.uid
        user_dict["pid"]= self.pid
        user_dict["nickname"]= self.nickname
        user_dict["fans_number"]= self.fans_number
        user_dict["follows_number"]= self.follows_number
        user_dict["tweets_number"]= self.tweets_number
        user_dict["sex"]= self.sex
        user_dict["birth"]= self.birth
        user_dict["loc"]= self.loc
        user_dict["education"]= self.education
        user_dict["vocation"]= self.vocation
        user_dict["register_time"]= self.register_time
        user_dict["qq"]= self.qq
        user_dict["mail"]= self.mail
        user_dict["tag_list"]= self.tag_list
        user_dict["fans_list"]= self.fans_list
        user_dict["follows_list"]= self.follows_list
        json_str = json.dumps(user_dict)
        return json_str


    def __str__(self):
        result = ""

        result += "用户id   : %s\n" %self.uid.encode("utf-8")
        result += "主页id   : %s\n" %self.pid.encode("utf-8")
        result += "昵称     : %s\n" %self.nickname
        result += "粉丝数   : %d\n" %self.fans_number
        result += "关注数   : %d\n" %self.follows_number
        result += "微博数   : %d\n" %self.tweets_number

        if self.register_time:
            result += "注册时间 : %s\n" %self.register_time.encode("utf-8")
        else:
            result += "注册时间 : 未知\n"

        if self.qq:
            result += "QQ       : %s\n" %self.qq.encode("utf-8")
        else:
            result += "QQ       : 未知\n"

        if self.mail:
            result += "邮箱     : %s\n" %self.mail.encode("utf-8")
        else:
            result += "邮箱     : 未知\n"

        if self.sex:
            result += "性别     : %s\n" %self.sex.encode("utf-8")
        else:
            result += "性别     : 未知\n"

        if self.birth:
            result += "生日     : %s\n" %self.birth.encode("utf-8")
        else:
            result += "生日     : 未知\n"

        if self.loc:
            result += "省市     : %s\n" %self.loc.encode("utf-8")
        else:
            result += "省市     : 未知\n"

        if self.tag_list:
            tags = " || ".join(self.tag_list)
            result += "标签     : %s\n" %tags.encode("utf-8")
        else:
            result += "标签     : 未知\n"

        for i in range(len(self.education)):
            result += "学校     : %s\n" %self.education[i][0].encode("utf-8")
            result += "学校类型 : %s\n" %self.education[i][1].encode("utf-8")
            if self.education[i][2]:
                result += "入学时间 : %s\n" %self.education[i][2].encode("utf-8")
            else:
                result += "入学时间 : 未知\n"

        for i in range(len(self.vocation)):
            result += "公司     : %s\n" %self.vocation[i][0].encode("utf-8")
            if self.vocation[i][1]:
                result += "入职时间 : %s\n" %self.vocation[i][1].encode("utf-8")
            else:
                result += "入职时间 : 未知\n"

            if self.vocation[i][2]:
                result += "离职时间 : %s\n" %self.vocation[i][2].encode("utf-8")
            else:
                result += "离职时间 : 未知\n"

        result += "粉丝     : " + " ".join([uid.encode("utf-8") for uid in self.fans_list]) + "\n"
        result += "关注     : " + " ".join([uid.encode("utf-8") for uid in self.follows_list]) + "\n"
        return result
