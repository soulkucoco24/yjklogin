# -*- coding: utf-8 -*-
from selenium import webdriver
import time
import sys
from imapclient import IMAPClient
import ssl
import email
import re


class AutoLogin(object):
    argv = ""
    driver = {}

    # url信息
    url = {
    }

    # 用户名密码安全码
    username = ""
    password = ""
    safe_code = ""

    # email info
    email_address = ""
    email_password = ""
    email_server = ""

    def __init__(self):
        self.argv = sys.argv[1]
        if self.argv not in self.url.keys():
            print("argv error")
            exit()
        # 线上环境登陆使用邮件安全码和线上密码
        if self.argv in ["bm", "zx"]:
            self.get_email()
            self.password = ""
        self.driver_name = 'chrome'
        self.executable_path = '/Users/taurus/Downloads/chromedriver'

    # 登陆
    def start(self):
        option = webdriver.ChromeOptions()
        option.add_argument('disable-infobars')
        self.driver = webdriver.Chrome(self.executable_path, chrome_options=option)
        url = self.url[self.argv]
        print('START:>>>'+url)
        self.driver.get(url)
        self.driver.find_element_by_name("username").send_keys(self.username)
        self.driver.find_element_by_name("password").send_keys(self.password)
        self.driver.find_element_by_name("safecode").send_keys(self.safe_code)
        self.driver.find_element_by_name("checking").click()
        # 防止速度太快同时点击checking和submit
        time.sleep(0.5)
        self.driver.find_element_by_class_name("submit").click()

    # 获取线上邮箱安全码
    def get_email(self):
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        mail = IMAPClient(self.email_server, ssl=True, ssl_context=context)

        try:
            mail.login(self.email_address, self.email_password)
        except BaseException as e:
            return "ERROR: >>> " + str(e)

        mail.select_folder('INBOX', readonly=True)
        res = mail.search()
        # 防止循环太多邮件,只查16个
        j = 0
        for i in res[::-1]:
            if j > 15:
                print "EMAIL SEARCH TOO MUCH"
                exit()
            msg_dict = mail.fetch(i, ['BODY.PEEK[]'])
            mail_body = msg_dict[i][b'BODY[]']
            e = email.message_from_string(mail_body)
            decode_subject = email.Header.decode_header(e['Subject'])
            utf_subject = decode_subject[0][0]

            # 获取安全码标题邮件
            if utf_subject.find("通用安全码更新通知") != -1:
                print "GET EMAIL CODING......"
                payload = e.get_payload()
                self.safe_code = re.findall(r"<font color=red>(.*?)</font>", payload)[0]
                mail.logout()
                return
            j = j + 1

        mail.logout()
        return


if __name__ == '__main__':
    auto_login = AutoLogin()
    auto_login.start()
