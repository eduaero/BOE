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
    oj = open_json()
    # If the file is empty, return an empty array
    if oj == '':
        return []
    df = adapt_content(oj)
    subastas_in_db = df['IDENTIFICADOR'].values.tolist()  # read from database identificadores
    return subastas_in_db


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

    def perform_loop(self):
        for num in range(self.page[0] * 50 - 50, self.page[1] * 50 - 50, 50):
            if self.break_code: break
            print('------------------------ PAGE %d -------------------- %s' % ((num/50)+1, datetime.datetime.now()))

            # Request the data
            r = requests.get(self.url_base + str(num) + '-50')
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
                    #print("New subasta found: %s" % str(self.name_link[y]))
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
                                        #print(exc_type, fname, exc_tb.tb_lineno)
                                        #print('Exception 1')
                                        continue
                            # Only 1 lote
                            else:
                                pageLabel2pass = self.pageLabel[z] + "_LOTE_1"
                                try:
                                    num_lotes = self.getdata2json(url, pageLabel2pass, z, y, num_lotes)
                                except Exception as e:
                                    exc_type, exc_obj, exc_tb = sys.exc_info()
                                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                                    #print(exc_type, fname, exc_tb.tb_lineno)
                                    #print('Exception 2')
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
                    file_name = "subastas.json"
                    f = open(file_name, "a+")
                    f.write(json.dumps(self.content_by_subasta, indent=4))
                    f.close()
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
        with open('subastas.json') as json_file:
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
        try: c = ast.literal_eval(j)
        except: continue
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






# CODE
page = [1, 5]
subastas_list = get_subastas_in_db()
subastas_list_stop = 5  # Number of previous subastas to be found before breaking the code
url_base = open("url_base.txt", "r").read()
GetDataBoe = GetDataBoe(page=page, subastas_list=subastas_list, subastas_list_stop=subastas_list_stop, url_base=url_base)
GetDataBoe.perform_loop()
newbies = GetDataBoe.newbies  # New subastas found in the execution
# Save newbies
with open('newbies.csv', 'w', newline='') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter='\n', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    spamwriter.writerow(newbies)

# Load data from json, create dataframe and create an excel
b = open_json()
df = adapt_content(b)
df.to_excel("subastas_output.xlsx", index=False)