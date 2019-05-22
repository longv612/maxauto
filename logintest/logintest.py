#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time,os,sys,subprocess,json
from tools.filetools import write_file
from appium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from tools.loggers import JFMlogging
logger = JFMlogging().getloger()
from config import logintest_app_log,appium_log
from time import sleep


class AppiumDriver(object):
    driver = None
    def  __init__(self ,device_name,pck_name,lanuch_activity):
        self.device_name = device_name
        self.url = "127.0.0.1"
        self.port = "4725"
        self.pck_name = pck_name
        self.lanuch_activity = lanuch_activity
        self.appium_log = appium_log

    def init_capability(self):
        '''
        启动配置文件
        :return:
        '''
        desired_caps = {
            "platformName": "Android",
            "appPackage": self.pck_name,
            "platformVersion ": "7.0",
            "appActivity": self.lanuch_activity,
            "autoLaunch": "true",
            "unicodeKeyboard": "true", # 使用appium的输入法，支持中文并隐藏键盘
            "resetKeyboard": "true", # 重置键盘
            #"newCommandTimeout": 120, # 设置driver超时时间
            #"automationName": "uiautomator2"
        }
        desired_caps["deviceName"] = self.device_name
        desired_caps.update()
        AppiumDriver.driver = webdriver.Remote('http://{}:{}/wd/hub'.format(self.url ,self.port), desired_caps)
        return AppiumDriver.driver


    def kill_appium(self):
        '''
        结束appium进程
        :return:
        '''
        if os.popen('lsof -i:{}'.format(self.port)).read() == '':
            logger.info('appium进程不存在')
        else:
            pid = os.popen('lsof -i:{}'.format(self.port)).readlines()[1].split()[1]
            subprocess.call('kill -9 {}'.format(pid),shell=True)
            logger.info('停止appium进程:{}'.format(pid))


    def start_appium(self):
        '''
        启动appium服务
        :return:
        '''
        self.kill_appium()
        args = 'appium --log {} --session-override --udid {} -a {} -p {}'.\
            format(self.appium_log,self.device_name ,self.url,self.port)
        logger.info('appium启动命令:{}'.format(args))
        appium = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, bufsize=1,close_fds=True)
        while True:
            appium_line = appium.stdout.readline().strip().decode()
            time.sleep(1)
            logger.info("启动appium中...")
            if 'Welcome to Appium' in appium_line or 'Error: listen' in appium_line:
                logger.info("appium启动成功")
                break
        return self.init_capability()


    def reset_keyboard(self ,device):
        '''
        重置键盘
        :return:
        '''
        try:
            cmd = "adb -s {} shell ime list -s | grep -v 'appium'".format(device)
            cmdline = subprocess.Popen(cmd ,shell=True, stdout=subprocess.PIPE)
            Keyboard = cmdline.stdout.readlines()[0].replace("\r\n" ,"")
            resetcmd = "adb -s {} shell ime set {}".format(device ,Keyboard)
            subprocess.call(resetcmd ,shell=True)
            logger.info("重置输入法完成")
        except Exception as e:
            logger.info("重置输入法异常!{}".format(e))


class LoginApp():

    def __init__(self,device_name,pck_name,lanuch_activity):
        '''
        初始化外部入参数
        '''
        self.device_name = device_name
        self.pck_name = pck_name
        self.lanuch_activity = lanuch_activity
        self.allow = "//*[@text='始终允许']"
        self.phone_login = "com.xunlei.tdlive:id/phone_login"
        self.xunlei_login = "com.xunlei.tdlive:id/change_login"
        self.input_name = "com.xunlei.tdlive:id/account_edt"
        self.input_passwd = "com.xunlei.tdlive:id/password_edt"
        self.login_button = "com.xunlei.tdlive:id/login_btn"
        self.ctext = "//*[@text='wxulf1565@163.com']"


    def is_element_exist(self,driver, *loc):
        try:
            WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located(loc))
            self.driver.find_element(*loc)
            return True
        except Exception as e:
            logger.warning(str(e))
            return False

    def always_allow(self,driver,number=2):
        logger.info("跳过系统权限")
        for i in range(number):
            allow_button = (By.XPATH, self.allow)
            try:
                a_button = WebDriverWait(self.driver,1,0.5).until(EC.presence_of_element_located(allow_button))
                a_button.click()
            except Exception as e:
                pass


    def logcat(self,log_path,delay):
        time.sleep(delay)
        cmd = 'adb logcat > {}'.format(log_path)
        subprocess.call(cmd,shell=True)
        logger.info('启动logcat')


    def test_login(self):
        '''
        登录测试
        :return:
        '''
        login_result = 'fail'
        try:
            self.appium_driver = AppiumDriver(self.device_name, self.pck_name, self.lanuch_activity)
            self.driver = self.appium_driver.start_appium()
            self.driver.implicitly_wait(5)
            logger.info("启动app中.....")
            sleep(5)
            self.always_allow(self.driver)
            logger.info("点击手机登录按钮")
            sleep(5)
            self.driver.find_element(By.ID, self.phone_login).click()
            sleep(5)
            logger.info("切换到迅雷账号登录")
            sleep(5)
            self.driver.find_element(By.ID, self.xunlei_login).click()
            sleep(5)
            logger.info("输入用户名")
            # self.driver.find_element(By.ID, self.input_name).click()
            self.driver.set_value(self.driver.find_element(By.ID, self.input_name),"xxx")
            logger.info("输入密码")
            self.driver.find_element(By.ID, self.input_passwd).click()
            sleep(3)
            self.driver.set_value(self.driver.find_element(By.ID, self.input_passwd), xxx)
            logger.info("点击登录按钮")
            sleep(5)
            self.driver.find_element(By.ID, self.login_button).click()
            time.sleep(10)
            login_result = 'success'
            logger.info('登录成功')
        except Exception as e:
            logger.info('登录测试异常:{}'.format(e))
        finally:
            self.appium_driver.kill_appium()
            write_file(logintest_app_log, login_result, is_cover=True)

