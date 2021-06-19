from bs4 import BeautifulSoup
import requests
from unidecode import unidecode
import json
import time
from datetime import datetime
from datetime import date
from datetime import timedelta
import dataset
import sys
import os
import datetime
import pandas as pd
import ast
import smtplib
from string import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP
from pretty_html_table import build_table
import warnings
import csv
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

# Initial conditions
pd.set_option('display.max_colwidth', 1000)
pd.options.display.float_format = '{:,.2f} €'.format
warnings.simplefilter("ignore")


# Functions defined
def curr2num(str_input):
    num = str_input.replace('€', '').replace(',', '').replace('.', '')
    return float(num) / 100


def date2format(str_input):
    my_date = str_input.split('CET')
    return my_date[0]


def get_subastas_in_db():
    return []


# Object to retrieve the data
class GetDataBoe:
    def __init__(self, page, subastas_list, subastas_list_stop, url_base):
        self.page = page
        self.subastas_list = subastas_list
        self.subastas_list_stop = subastas_list_stop
        self.url_base = url_base
        self.num_subastas = 0
        self.break_code = False
        self.link_url = []
        self.name_link = []
        self.pageInfo = [1, 2, 3, 4, 5]  # , 6, 7, 8, 9]
        self.pageLabel = ["PAGE_1", "PAGE_2", "PAGE_3", "PAGE_4", "PAGE_5", "PAGE_6", "PAGE_7", "PAGE_8", "PAGE_9"]
        self.content_by_subasta = {}
        self.soup_input = "????"
        self.subastas_in_db = get_subastas_in_db()
        self.newbies = []

        print("The object has been initialized")

    # We get the URL from the subastas
    # We filter the URL for the ones that are for "subastas" and the variable link is updated with the links.
    def get_urls(self):
        for a in self.soup_input.findAll('a', href=True):
            if a.text:
                try:
                    if a['title'].startswith('Subasta') and a['class'][0] == 'resultado-busqueda-link-defecto':
                        self.name_link.append(a['title'])
                        self.link_url.append(a['href'])
                except Exception:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    continue
        print('There are {} links'.format(len(self.link_url)))
        return

    def get_data_ref_cat(self, url_ref_c):
        r = requests.get(url_ref_c)
        data = r.text
        soup = BeautifulSoup(data, "html5lib")
        a = soup.findAll('a', href=True)

        link = []
        for a in soup.findAll('a', href=True):
            if a.text:
                try:
                    if a['title'].startswith('Abre datos catastrales en nueva ventana'):
                        link.append(a['href'])
                except:
                    continue
        url_rc = 'https://subastas.boe.es/' + link[0]

        r = requests.get(url_rc)
        data = r.text
        soup = BeautifulSoup(data, "lxml")
        data = soup.findAll('tr')

        label = []
        data_dw = []
        content = {}
        titulos = {}
        cont = {}
        for a in data:
            thall = a.findAll('th')
            tdall = a.findAll('td')
            if len(thall) == 1:
                label_name = a.find('th').text
                label.append(label_name)
                data_cell = a.find('td').text
                data_dw.append(data_cell)
            else:
                for i, value in enumerate(thall):
                    titulos[i] = value.text
                for i, value in enumerate(thall):
                    label.append(titulos[i])

                for i, value in enumerate(tdall):
                    cont[i] = value.text
                for i, value in enumerate(tdall):
                    data_dw.append(cont[i])

        for x in range(0, len(label)):
            content[str(label[x])] = str(data_dw[x])

        sol = {}
        if len(content) > 0:
            sol['PAGE_C'] = content
            self.content_by_subasta['PAGE_C'] = content

        return sol

    def perform_loop(self, f):
        for num in range(0, 1):
            if self.break_code: break

            # Request the data
            r = requests.get(self.url_base)
            data = r.text
            self.soup_input = BeautifulSoup(data, "html5lib")
            a = self.soup_input.findAll('a', href=True)
            # The data is retrieved
            self.get_urls()

            t_new = time.time()
            # Loop over found links (subastas)
            for y in range(0, len(self.link_url)):
                if self.break_code: break

                # Check if this subasta has already been loaded to the database
                self.subastas_in_db = get_subastas_in_db()
                if str(self.name_link[y]).replace("Subasta ", "") in self.subastas_in_db:
                    if self.subastas_list_stop > 0:
                        self.subastas_list_stop = self.subastas_list_stop - 1
                        continue
                    else:
                        self.break_code = True
                        break
                else:
                    new_to_append = str(self.name_link[y]).replace("Subasta ", "")
                    self.newbies.append(new_to_append)

                t_old = t_new
                t_new = time.time()
                print('>> Subasta %d: %s - time %s seconds' % (y, self.name_link[y], str(t_new - t_old)))
                num_lotes = -1
                self.content_by_subasta = {}
                try:
                    # Loop over page info (over the number of pages that have a subasta)
                    for z in range(0, len(self.pageInfo)):
                        if self.break_code: break
                        page = self.pageInfo[z]

                        # URL subasta
                        tempUrl = 'https://subastas.boe.es/' + self.link_url[y]
                        tempUrl = tempUrl.split('&idBus')

                        # URL of each page in the subasta
                        url = tempUrl[0] + '&ver={}'.format(page) + '&idBus' + tempUrl[1]

                        # Loop to manage subastas with several lotes
                        if int(self.pageInfo[z]) == 3:
                            # More than one lote
                            if int(num_lotes) != 0:
                                print('Num lotes: ' + str(num_lotes))
                                # Iteration over lotes
                                for numL in range(1, int(num_lotes) + 1):
                                    print('-----------Lote:' + str(numL) + ' de ' + str(num_lotes))
                                    url = url + '&idLote=' + str(numL) + '&numPagBus='
                                    pageLabel2pass = self.pageLabel[z] + "_LOTE_" + str(numL)
                                    try:
                                        num_lotes = self.getdata2json(url, pageLabel2pass, z, y, num_lotes)
                                    except Exception as e:
                                        exc_type, exc_obj, exc_tb = sys.exc_info()
                                        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

                                        continue
                            # Only 1 lote
                            else:
                                pageLabel2pass = self.pageLabel[z] + "_LOTE_1"
                                try:
                                    num_lotes = self.getdata2json(url, pageLabel2pass, z, y, num_lotes)
                                except Exception as e:
                                    exc_type, exc_obj, exc_tb = sys.exc_info()
                                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

                                    continue
                            # Management of subastas with referencia catastral
                            try:
                                contenido_REF_CAT = self.get_data_ref_cat(url)
                            except Exception as e:
                                if str(e) == 'list index out of range':
                                    continue
                                else:
                                    continue
                        # Loop to get data from catastro
                        elif int(self.pageInfo[z]) == 4:
                            print('')
                        else:
                            try:
                                num_lotes = self.getdata2json(url, self.pageLabel[z], z, y, num_lotes)
                            except Exception as e:
                                continue

                    # This part of the code will stop the execution whether the subastas identifier are already in the database
                    if any(self.content_by_subasta["PAGE_1"]["IDENTIFICADOR"] in s for s in self.subastas_list):
                        print("The subasta was already in the database")
                        self.num_subastas = self.num_subastas + 1
                        print(self.num_subastas)
                        if self.num_subastas == self.subastas_list_stop:
                            print("The code is stopping from executing")
                            self.break_code = True
                            if self.break_code: break
                        else:
                            continue
                    else:
                        print("Subasta not in dB")

                    f.write(json.dumps(self.content_by_subasta, indent=4))

                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    #print(exc_type, fname, exc_tb.tb_lineno)
                    continue

    def getdata2json(self, url, page_label, z, y, num_lotes):
        r = requests.get(url)
        data = r.text
        soup = BeautifulSoup(data, "lxml")
        if (page_label == "PAGE_5" or page_label == "PAGE_8"):
            soup2 = soup.find(id='idBloqueDatos8')
            temp = str(soup2.strong)
            temp = temp.replace('<strong class="destaca">', '')
            temp = temp.replace('</strong>', "")
        data = soup.findAll('tr')

        label = []
        dataDw = []
        content = {}
        url_subasta = {"URL": 'https://subastas.boe.es/' + self.link_url[y]}

        if (page_label == "PAGE_5" or page_label=='PAGE_8'):
            label_name = 'PRECIO_PUJA'
            data_cell = temp
            if '€' in data_cell:
                data_cell = curr2num(data_cell)
            else:
                data_cell = unidecode(data_cell)

            content[str(label_name)] = str(data_cell)
        else:
            for a in data:
                label_name = unidecode(a.find('th').text.replace('\n', '').replace(' ', '_').upper())
                data_cell = a.find('td').text.replace('\n', '')

                # We gotta: (1) format in the dates; (2) euro format correct; (3) delete acentos
                if 'CET  (ISO:' in data_cell:
                    data_cell = date2format(data_cell)
                elif '€' in data_cell:
                    data_cell = curr2num(data_cell)
                else:
                    data_cell = unidecode(data_cell)

                label.append(label_name)
                dataDw.append(data_cell)

            for x in range(0, len(label)):
                # downloaded[label[x]] = dataDw[x]
                content[str(label[x])] = str(dataDw[x])
                if (self.pageInfo[z] == 1):
                    if label[x] == 'LOTES':
                        num_lotes = dataDw[x]
                        if num_lotes == 'Sin lotes':
                            num_lotes = 0

        if (len(content) > 0):
            if (z == 0):
                self.content_by_subasta["URL"] = url_subasta
                self.content_by_subasta[page_label] = content
            else:
                self.content_by_subasta[page_label] = content
        return  num_lotes


def open_json():
    try:
        with open('subastas_celebrandose.json') as json_file:
            file = json_file.read()
        content = file.replace('}{', '}-----{')
        b = content.split('-----')
        return b
    except IOError:
        print("The file does not exist")
        return ''


def adapt_content(b):
    rows_list = []
    for j in b:
        try:
            c = ast.literal_eval(j)
        except:
            continue
        if ('PAGE_1' in c) & ('PAGE_2' in c):
            if c['PAGE_1']['LOTES'] != 'Sin lotes':
                num_lotes = int(c['PAGE_1']['LOTES'])
                for i in range(1, num_lotes + 1):
                    d1 = c['URL']
                    d2 = c['PAGE_1']
                    d1.update(d2)
                    d3 = c['PAGE_2']
                    d1.update(d3)

                    page3 = 'PAGE_3_LOTE_' + str(i)
                    if page3 in c:
                        d4 = c[page3]
                        d1.update(d4)

                    if 'PAGE_4' in c:
                        d10 = c['PAGE_4']
                        d1.update(d10)

                    if 'PAGE_5' in c:
                        d7 = c['PAGE_5']
                        d1.update(d7)

                    if 'PAGE_C' in c:
                        d11 = c['PAGE_C']
                        d1.update(d11)

                    if 'PAGE_8' in c:
                        d12 = c['PAGE_8']
                        d1.update(d12)

                    rows_list.append(d1)

            else:
                d1 = c['URL']
                d2 = c['PAGE_1']
                d1.update(d2)
                d3 = c['PAGE_2']
                d1.update(d3)

                if 'PAGE_3_LOTE_1' in c:
                    d4 = c['PAGE_3_LOTE_1']
                    d1.update(d4)

                if 'PAGE_4' in c:
                    d10 = c['PAGE_4']
                    d1.update(d10)

                if 'PAGE_5' in c:
                    d5 = c['PAGE_5']
                    d1.update(d5)

                if 'PAGE_C' in c:
                    d11 = c['PAGE_C']
                    d1.update(d11)

                if 'PAGE_8' in c:
                    d12 = c['PAGE_8']
                    d1.update(d12)

                rows_list.append(d1)

    df = pd.DataFrame(rows_list)
    #if 'CANTIDAD_RECLAMADA' in df.columns:
    #    df['CANTIDAD_RECLAMADA'] = pd.to_numeric(df['CANTIDAD_RECLAMADA'].fillna(0))
    #if 'IMPORTE_DEL_DEPOSITO' in df.columns:
    #    df['IMPORTE_DEL_DEPOSITO'] = pd.to_numeric(df['IMPORTE_DEL_DEPOSITO'].fillna(0))
    #if 'PUJA_MINIMA' in df.columns:
    #    df['PUJA_MINIMA'][df['PUJA_MINIMA'] == "Sin puja minima"] = 0.0
    #if 'TASACION' in df.columns:
    #    df['TASACION'][df['TASACION'] == "No consta"] = 0.0
    #if 'TRAMOS_ENTRE_PUJAS' in df.columns:
    #    df['TRAMOS_ENTRE_PUJAS'][df['TRAMOS_ENTRE_PUJAS'] == "Sin tramos"] = 0.0
    #if 'VALOR_SUBASTA' in df.columns:
    #    df['VALOR_SUBASTA'][df['VALOR_SUBASTA'] == "No consta"] = 0.0
    return df


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

        # Search for Buscar
        driver.find_element_by_xpath("//li[@class='buscar']").click()

        driver.find_element_by_xpath("//label[@for='idEstadoEJ']").click()  # Celebrándose

        # Search for the province chosen
        id_provincia = Select(driver.find_element_by_id("BIEN.COD_PROVINCIA"))
        id_provincia.select_by_value("28")

        # Fechas
        hoy = pd.to_datetime(date.today(), format='%Y-%m-%d') + timedelta(days=0)
        hoy = hoy.strftime('%m/%d/%Y')
        print(hoy)
        driver.find_element_by_id("desdeFP").send_keys(hoy)
        driver.find_element_by_id("hastaFP").send_keys(hoy)

        #Buscar
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
                print(exception)
                #id_page = 2
                #driver.find_element_by_partial_link_text("2").click()
                #try:
                #    driver.find_element_by_xpath(subasta_text).click()
                # if the subasta is not in the second page, go to the third
                # Execution in page 3
                #except NoSuchElementException as exception:
                    #id_page = 3
                    #driver.find_element_by_partial_link_text("3").click()
                    #driver.find_element_by_xpath(subasta_text).click()
                    #driver.find_element_by_partial_link_text("Pujas").click()
                    # Retrieve puja
                    #pujas = self.find_puja(pujas)
                # Execution in page 2
                #else:
                    #driver.find_element_by_partial_link_text("Pujas").click()
                    #Retrieve puja
                    #pujas = self.find_puja(pujas)

            # Execution in page 1
            else:
                id_page = 1
                driver.find_element_by_partial_link_text("Pujas").click()
                pujas = self.find_puja(pujas)
            # Go back to the main site to search for more subastas
            finally:
                if id_page == 1:
                    driver.execute_script("window.history.go(-2)")
                #if id_page == 2:
                #    driver.execute_script("window.history.go(-3)")
                #if id_page == 3:
                #    driver.execute_script("window.history.go(-4)")

        return pujas


def prepare_email(pujas, subastas_following):
    # Get subastas following
    email_content = pd.DataFrame(pujas)
    email_content['IDENTIFICADOR'] = subastas_following
    email_content.columns = ['PUJA', 'IDENTIFICADOR']
    print(email_content)
    # Get data from database
    subastas = pd.read_excel("subastas_output_updated_v.xlsx")
    subset = subastas.loc[subastas["IDENTIFICADOR"].isin(subastas_following)]
    subset = subset.drop(columns=['ANUNCIO_BOE', 'Antigüedad', 'CARGAS', 'CODIGO',
                                  'CORREO_ELECTRONICO', 'CUOTA', 'Clase',
                                  'Clase de cultivo', 'Coeficiente de participación', 'DEPOSITO',
                                  'DESCRIPCION', 'Escalera', 'FAX', 'FECHA_DE_ADQUISICION',
                                  'FECHA_DE_INICIO', 'FECHA_DE_MATRICULACION',
                                  'FORMA_ADJUDICACION', 'IDUFIR', 'IMPORTE_DEL_DEPOSITO',
                                  'INFORMACION_ADICIONAL', 'INSCRIPCION_REGISTRAL',
                                  'Intensidad productiva', 'LOTES', 'Localización', 'MARCA',
                                  'MATRICULA', 'MODELO', 'NIF', 'NOMBRE', 'NUMERO_DE_BASTIDOR', 'PAIS',
                                  'PARCELA', 'PRECIO_PUJA', 'PROVINCIA', 'PUJA_MINIMA', 'Planta',
                                  'Puerta', 'REFERENCIA_CATASTRAL', 'REFERENCIA_REGISTRAL',
                                  'Referencia Catastral', 'Referencia catastral', 'SITUACION_POSESORIA',
                                  'SUPERFICIE', 'Situación', 'Subparcelas', 'Superficie',
                                  'Superficie (ha)', 'Superficie Catastral (m2)', 'TASACION', 'TELEFONO',
                                  'TIPO_DE_SUBASTA', 'TITULO_JURIDICO', 'TRAMOS_ENTRE_PUJAS',
                                  'Uso', 'VALOR_DE_TASACION', 'CANTIDAD_RECLAMADA', 'VISITABLE', 'VIVIENDA_HABITUAL'])
    # Merge data and format table columns
    email_content = email_content.merge(subset, left_on='IDENTIFICADOR', right_on='IDENTIFICADOR')
    cols = ['IDENTIFICADOR', 'PUJA', 'VALOR_SUBASTA', 'DIRECCION',
       'FECHA_DE_CONCLUSION', 'URL', 'CODIGO_POSTAL', 'LOCALIDAD']
    email_content = email_content[cols]
    email_content['VALOR_SUBASTA'] = email_content['VALOR_SUBASTA'].astype('float64')
    email_content['VALOR_SUBASTA'] = email_content['VALOR_SUBASTA'].map('{:,.2f} €'.format)
    email_content['URL'] = str("<a href='") + email_content['URL'] + str("'>Subasta</a>")  # URL to the subasta

    # Introduce link to map
    for i, v in enumerate(email_content['DIRECCION']):
        direccion = email_content.loc[i, 'DIRECCION'].replace(' ', '+')
        codigo_postal = str(email_content.loc[i, 'CODIGO_POSTAL']).replace('.0', '')
        localidad = email_content.loc[i, 'LOCALIDAD']
        email_content.loc[i, 'DIRECCION'] = str("<a href='https://maps.google.com/?q=") + direccion + str(",+") + codigo_postal + str("+") + localidad + str("'>") + email_content.loc[i, 'DIRECCION'] + str("</a>")

    email_content = email_content.drop(columns=['CODIGO_POSTAL', 'LOCALIDAD'])
    return email_content


def send_mail(email_content):
    output = build_table(email_content, 'blue_light')  # Format of the email
    body = output.replace('&lt;', '<').replace('&gt;', '>')

    # Content of the email
    message = MIMEMultipart()
    message['Subject'] = 'Subastas que acaban hoy'
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
# Extract today's subastas
page = [1, 3]
subastas_list = get_subastas_in_db()
subastas_list_stop = 5  # Number of previous subastas to be found before breaking the code

hoy = pd.to_datetime(date.today(), format='%Y-%m-%d')
hoy = hoy.strftime('%Y-%m-%d')
url_base_1 = 'https://subastas.boe.es/subastas_ava.php?campo%5B0%5D=SUBASTA.ORIGEN&dato%5B0%5D=&campo%5B1%5D=SUBASTA.ESTADO&dato%5B1%5D=EJ&campo%5B2%5D=BIEN.TIPO&dato%5B2%5D=&dato%5B3%5D=&campo%5B4%5D=BIEN.DIRECCION&dato%5B4%5D=&campo%5B5%5D=BIEN.CODPOSTAL&dato%5B5%5D=&campo%5B6%5D=BIEN.LOCALIDAD&dato%5B6%5D=&campo%5B7%5D=BIEN.COD_PROVINCIA&dato%5B7%5D=&campo%5B8%5D=SUBASTA.POSTURA_MINIMA_MINIMA_LOTES&dato%5B8%5D=&campo%5B9%5D=SUBASTA.NUM_CUENTA_EXPEDIENTE_1&dato%5B9%5D=&campo%5B10%5D=SUBASTA.NUM_CUENTA_EXPEDIENTE_2&dato%5B10%5D=&campo%5B11%5D=SUBASTA.NUM_CUENTA_EXPEDIENTE_3&dato%5B11%5D=&campo%5B12%5D=SUBASTA.NUM_CUENTA_EXPEDIENTE_4&dato%5B12%5D=&campo%5B13%5D=SUBASTA.NUM_CUENTA_EXPEDIENTE_5&dato%5B13%5D=&campo%5B14%5D=SUBASTA.ID_SUBASTA_BUSCAR&dato%5B14%5D=&campo%5B15%5D=SUBASTA.FECHA_FIN_YMD&dato%5B15%5D%5B0%5D='
url_base_2 = '&dato%5B15%5D%5B1%5D='
url_base_3 = '&campo%5B16%5D=SUBASTA.FECHA_INICIO_YMD&dato%5B16%5D%5B0%5D=&dato%5B16%5D%5B1%5D=&page_hits=500&sort_field%5B0%5D=SUBASTA.FECHA_FIN_YMD&sort_order%5B0%5D=desc&sort_field%5B1%5D=SUBASTA.FECHA_FIN_YMD&sort_order%5B1%5D=asc&sort_field%5B2%5D=SUBASTA.HORA_FIN&sort_order%5B2%5D=asc&accion=Buscar'
url_base = 'https://subastas.boe.es/subastas_ava.php?campo%5B0%5D=SUBASTA.ORIGEN&dato%5B0%5D=&campo%5B1%5D=SUBASTA.ESTADO&dato%5B1%5D=EJ&campo%5B2%5D=BIEN.TIPO&dato%5B2%5D=&dato%5B3%5D=&campo%5B4%5D=BIEN.DIRECCION&dato%5B4%5D=&campo%5B5%5D=BIEN.CODPOSTAL&dato%5B5%5D=&campo%5B6%5D=BIEN.LOCALIDAD&dato%5B6%5D=&campo%5B7%5D=BIEN.COD_PROVINCIA&dato%5B7%5D=28&campo%5B8%5D=SUBASTA.POSTURA_MINIMA_MINIMA_LOTES&dato%5B8%5D=&campo%5B9%5D=SUBASTA.NUM_CUENTA_EXPEDIENTE_1&dato%5B9%5D=&campo%5B10%5D=SUBASTA.NUM_CUENTA_EXPEDIENTE_2&dato%5B10%5D=&campo%5B11%5D=SUBASTA.NUM_CUENTA_EXPEDIENTE_3&dato%5B11%5D=&campo%5B12%5D=SUBASTA.NUM_CUENTA_EXPEDIENTE_4&dato%5B12%5D=&campo%5B13%5D=SUBASTA.NUM_CUENTA_EXPEDIENTE_5&dato%5B13%5D=&campo%5B14%5D=SUBASTA.ID_SUBASTA_BUSCAR&dato%5B14%5D=&campo%5B15%5D=SUBASTA.FECHA_FIN_YMD&dato%5B15%5D%5B0%5D=2020-10-28&dato%5B15%5D%5B1%5D=2020-10-28&campo%5B16%5D=SUBASTA.FECHA_INICIO_YMD&dato%5B16%5D%5B0%5D=&dato%5B16%5D%5B1%5D=&page_hits=500&sort_field%5B0%5D=SUBASTA.FECHA_FIN_YMD&sort_order%5B0%5D=desc&sort_field%5B1%5D=SUBASTA.FECHA_FIN_YMD&sort_order%5B1%5D=asc&sort_field%5B2%5D=SUBASTA.HORA_FIN&sort_order%5B2%5D=asc&accion=Buscar'
#url_base_1 + hoy + url_base_2 + hoy + url_base_3
GetDataBoe = GetDataBoe(page=page, subastas_list=subastas_list, subastas_list_stop=subastas_list_stop, url_base=url_base)
f = open("subastas_celebrandose.json", "a+")
f.truncate(0)
GetDataBoe.perform_loop(f)
f.close()

# Load data from json, create dataframe and create an excel
b = open_json()
df = adapt_content(b)

# Remove canceled subastas
df = df[df.PRECIO_PUJA != 'Cancelado']

# Save celebrandose ids
celebrandose = df['IDENTIFICADOR']

# Get credentials from credentials.txt
email = open("credentials.txt", "r").read().split('\n')[0]
password = open("credentials.txt", "r").read().split('\n')[1]

# Define Chrome driver
option = webdriver.ChromeOptions()
option.add_argument("--incognito")  # Execute in incognito window
#option.add_argument("--headless")  # Don't show execution
driver = webdriver.Chrome(ChromeDriverManager().install(), options=option)

# Create navigation object and get pujas data
BOE = NavigateBOE(email=email, password=password, chrome_driver_path=driver)
pujas = BOE.sign_in("Madrid", celebrandose)
email_content = prepare_email(pujas, celebrandose)

# Get only subastas without pujas
email_content = email_content[email_content.PUJA == 'Sin pujas']

# Get credentials and email list
SENDING_EMAIL = open("email_credentials.txt", "r").read().split('\n')[0]
PASSWORD = open("email_credentials.txt", "r").read().split('\n')[1]
TO_EMAILS = open("emails.txt", "r").read().replace('\n', ';')

# Send email with updates
send_mail(email_content)
