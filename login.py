
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

    #Get the code used to identify each province in the site
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

    def sign_in(self,provincia,subasta_following):
        #Creation of the driver and log in with credentials
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

        #Search for the province chosen
        id_provincia = Select(driver.find_element_by_id("ID_provincia"))
        id_provincia.select_by_value(self.get_province_code(provincia))
        driver.find_element_by_xpath("//input[@value='Buscar']").click()

        #Search for the subastas to follow
        pujas = []
        id_page = 0
        for s in subasta_following:
            subasta_text = "//a[@title='Subasta " + s + "']"
            try:
                driver.find_element_by_xpath(subasta_text).click()
            except NoSuchElementException as exception:
                # if the subasta is not in the first page, go to the second
                id_page = 2
                driver.find_element_by_partial_link_text("2").click()
                driver.find_element_by_xpath(subasta_text).click()
                driver.find_element_by_partial_link_text("Pujas").click()
                try:
                    driver.find_element_by_xpath("//strong[@class='destaca']").text
                except Exception:
                    puja = 'Sin pujas'
                    pujas.append(puja)
                else:
                    puja = driver.find_element_by_xpath("//strong[@class='destaca']").text
                    pujas.append(puja)
            else:
                id_page = 1
                #driver.find_element_by_xpath(subasta_text).click()
                driver.find_element_by_partial_link_text("Pujas").click()
                try:
                    driver.find_element_by_xpath("//strong[@class='destaca']").text
                except Exception:
                    puja = 'Sin pujas'
                    pujas.append(puja)
                else:
                    puja = driver.find_element_by_xpath("//strong[@class='destaca']").text
                    pujas.append(puja)
            finally:
                if id_page == 1:
                    driver.execute_script("window.history.go(-2)") #Go back to the main site to search for more subastas
                else:
                    driver.execute_script("window.history.go(-3)")  # Go back to the main site to search for more subastas
        return pujas

email = "@gmail.com"
password = ""

option = webdriver.ChromeOptions()
option.add_argument("--incognito") #Execute in incognito window
option.add_argument("--headless") #Don't show execution
driver = webdriver.Chrome(ChromeDriverManager().install(), options=option)

subasta_following = ['SUB-JA-2020-151496','SUB-NE-2020-555938','SUB-JA-2020-151351','SUB-JA-2020-151495']

BOE = NavigateBOE(email=email, password = password, chrome_driver_path = driver)
pujas = BOE.sign_in("Madrid", subasta_following)
print(subasta_following)
print(pujas)


# https://chromedriver.chromium.org/mobile-emulation


