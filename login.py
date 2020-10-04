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
import ast
import smtplib
from string import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP
from pretty_html_table import build_table
import pandas as pd


class NavigateBOE:
    def __init__(self, email, password, chrome_driver_path):
        self.driver = driver
        self.driver.implicitly_wait(30)
        self.verificationErrors = []
        self.accept_next_alert = True
        self.email = email
        self.password = password


    # Get the code used to identify each province in the site
    def get_province_code(self, province):
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
        for y, p in enumerate(ciudades):
            if p == province:
                return codigos[y]


    # Get the price of the puja
    def find_puja(self, pujas):
        try:
            driver.find_element_by_xpath("//strong[@class='destaca']").text
        # if there is no puja
        except Exception:
            puja = 'Sin pujas'
            pujas.append(puja)
        else:
            puja = driver.find_element_by_xpath("//strong[@class='destaca']").text
            pujas.append(puja)
        return pujas


    # Main function
    def sign_in(self, provincia, subasta_following):
        # Creation of the driver and log in with credentials
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

        # Search for the province chosen
        id_provincia = Select(driver.find_element_by_id("ID_provincia"))
        id_provincia.select_by_value(self.get_province_code(provincia))
        driver.find_element_by_xpath("//input[@value='Buscar']").click()

        # Search for the subastas to follow
        pujas = []
        id_page = 0
        for s in subasta_following:
            subasta_text = "//a[@title='Subasta " + s + "']"
            # Search for subasta in first page
            try:
                driver.find_element_by_xpath(subasta_text).click()
            # if the subasta is not in the first page, go to the second
            except NoSuchElementException as exception:
                id_page = 2
                driver.find_element_by_partial_link_text("2").click()
                try:
                    driver.find_element_by_xpath(subasta_text).click()
                # if the subasta is not in the second page, go to the third
                # Execution in page 3
                except NoSuchElementException as exception:
                    id_page = 3
                    driver.find_element_by_partial_link_text("3").click()
                    driver.find_element_by_xpath(subasta_text).click()
                    driver.find_element_by_partial_link_text("Pujas").click()
                    # Retrieve puja
                    pujas = self.find_puja(pujas)
                # Execution in page 2
                else:
                    driver.find_element_by_partial_link_text("Pujas").click()
                    #Retrieve puja
                    pujas = self.find_puja(pujas)

            # Execution in page 1
            else:
                id_page = 1
                driver.find_element_by_partial_link_text("Pujas").click()
                pujas = self.find_puja(pujas)
            # Go back to the main site to search for more subastas
            finally:
                if id_page == 1:
                    driver.execute_script("window.history.go(-2)")
                if id_page == 2:
                    driver.execute_script("window.history.go(-3)")
                if id_page == 3:
                    driver.execute_script("window.history.go(-4)")

        return pujas


def send_mail(email_content):
    output = build_table(email_content, 'blue_light')  # Format of the email
    body = output.replace('&lt;', '<').replace('&gt;', '>')

    # Content of the email
    message = MIMEMultipart()
    message['Subject'] = 'Seguimiento subastas'
    message['From'] = SENDING_EMAIL
    message['To'] = TO_EMAILS
    body_content = body
    message.attach(MIMEText(body_content, "html"))
    msg_body = message.as_string()

    # Server setup
    server = SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(message['From'], PASSWORD)
    server.sendmail(message['From'], message['To'], msg_body)
    server.quit()


# CODE
# Get credentials from credentials.txt
email = open("credentials.txt", "r").read().split('\n')[0]
password = open("credentials.txt", "r").read().split('\n')[1]

# Define Chrome driver
option = webdriver.ChromeOptions()
option.add_argument("--incognito")  # Execute in incognito window
option.add_argument("--headless")  # Don't show execution
driver = webdriver.Chrome(ChromeDriverManager().install(), options=option)

# Get subastas to follow from subastas_following.txt
subastas_following = open("subastas_following.txt", "r").read().split('\n')

# Create navigation object and get pujas data
BOE = NavigateBOE(email=email, password=password, chrome_driver_path=driver)
pujas = BOE.sign_in("Madrid", subastas_following)
email_content = pd.DataFrame(pujas)
email_content['ID'] = subastas_following
email_content.columns = ['Estado', 'ID']

# Get credentials and email list
SENDING_EMAIL = open("email_credentials.txt", "r").read().split('\n')[0]
PASSWORD = open("email_credentials.txt", "r").read().split('\n')[1]
TO_EMAILS = open("emails.txt", "r").read().replace('\n', ';')

# Send email with updates
send_mail(email_content)

# https://chromedriver.chromium.org/mobile-emulation