
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
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import requests
from unidecode import unidecode

class NavigateBOE:
    def __init__(self,email,password, chrome_driver_path):
        self.driver = driver
        self.driver.implicitly_wait(30)
        self.base_url = "https://www.google.com/"
        self.verificationErrors = []
        self.accept_next_alert = True
        self.email = email
        self.password = password

    def get_province_code(self,province):
        ciudades = ["Álava", "Albacete", "Alicante", "Almería", "Ávila", "Badajoz",
        "Baleares", "Barcelona", "Burgos", "Cáceres", "Cádiz", "Castellón",
        "Ciudad Real", "Córdoba", "A Coruña", "Cuenca", "Gerona", "Granada", "Guadalajara",
        "Guipúzcoa", "Huelva", "Huesca", "Jaén", "León", "Lérida", "La Rioja", "Lugo", "Madrid",
        "Málaga", "Murcia", "Navarra", "Orense", "Asturias", "Palencia", "Las Palmas", "Pontevedra",
        "Salamanca", "Santa Cruz de Tenerife", "Cantabria", "Segovia", "Sevilla", "Soria", "Tarragona",
        "Teruel", "Toledo", "Valencia", "Valladolid", "Vizcaya", "Zamora", "Zaragoza", "Ceuta"]
        codigos = ["01","02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13", "14", "15",
        "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30",
        "31", "32", "33", "34", "35", "36", "37", "38", "39", "40", "41", "42", "43", "44", "45",
        "46", "47", "48", "49", "50", "51"]
        for y,p in enumerate(ciudades):
            if p == province:
                return codigos[y]

    def sign_in(self,provincia):
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

        id_provincia = Select(driver.find_element_by_id("ID_provincia"))
        id_provincia.select_by_value(self.get_province_code(provincia))
        driver.find_element_by_xpath("//input[@value='Buscar']").click()
        url_pagina1 = driver.current_url
        print(url_pagina1)

        r = requests.get(url_pagina1)
        data = r.text
        soup = BeautifulSoup(data, "html5lib")
        url_pagina2 = soup.findAll('a', href=True)[13]
        print(url_pagina2)
        url_base =url_pagina2[:-5]
        print(url_base)
        return url_base


email = "@gmail.com"
password = ""
driver = webdriver.Chrome(ChromeDriverManager().install())
BOE = NavigateBOE(email=email, password = password, chrome_driver_path = driver)
url_base = BOE.sign_in("Madrid")


# https://chromedriver.chromium.org/mobile-emulation