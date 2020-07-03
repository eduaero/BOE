
# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import unittest, time, re




class NavigateBOE:
    def __init__(self,email,password, chrome_driver_path):
        self.driver = driver
        self.driver.implicitly_wait(30)
        self.base_url = "https://www.google.com/"
        self.verificationErrors = []
        self.accept_next_alert = True
        self.email = email
        self.password = password

    def sign_in(self):
        print("entra")
        driver = self.driver
        driver.get("https://subastas.boe.es/")
        driver.find_element_by_xpath("//div[@id='menu_principal']/ul/li[4]/a/span").click()
        driver.find_element_by_xpath("(//a[contains(text(),'Conectar')])[2]").click()
        driver.find_element_by_id("labelUsuario").click()
        driver.find_element_by_id("labelUsuario").clear()
        driver.find_element_by_id("labelUsuario").send_keys(self.email)
        driver.find_element_by_id("labelPassword").click()
        driver.find_element_by_id("labelPassword").clear()
        driver.find_element_by_id("labelPassword").send_keys(self.password)
        driver.find_element_by_id("conectar").click()

email = "eduardotolalosa@gmail.com"
password = ""
driver = webdriver.Chrome(ChromeDriverManager().install())
BOE = NavigateBOE(email=email, password = password, chrome_driver_path = driver)
BOE.sign_in()

# https://chromedriver.chromium.org/mobile-emulation