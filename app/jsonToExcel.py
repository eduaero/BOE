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


def open_json(provincia):
    try:
        file_name = "subastas_" + str(provincia) + ".json"
        with open(file_name) as json_file:
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
            # Con lotes
            if c['PAGE_1']['LOTES'] != 'Sin lotes':
                num_lotes = int(c['PAGE_1']['LOTES'])
                for i in range(1, num_lotes + 1):
                    d1 = {"ID_LOTES": c['PAGE_1']['IDENTIFICADOR']+'_'+str(i)}
                    d0 = c['URL']
                    d1.update(d0)
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

                    pagec = 'PAGE_C_LOTE_' + str(i)
                    if pagec in c:
                        d11 = c[pagec]
                        d1.update(d11)

                    if 'PAGE_8' in c:
                        d12 = c['PAGE_8']
                        d1.update(d12)

                    rows_list.append(d1)

            # Sin lotes
            else:
                d1 = {"ID_LOTES": c['PAGE_1']['IDENTIFICADOR']}
                d0 = c['URL']
                d1.update(d0)
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

                if 'PAGE_C_LOTE_1' in c:
                    d11 = c['PAGE_C_LOTE_1']
                    d1.update(d11)

                if 'PAGE_8' in c:
                    d12 = c['PAGE_8']
                    d1.update(d12)

                rows_list.append(d1)

    df = pd.DataFrame(rows_list)

    return df

provincia = "Madrid"

# Load data from json, create dataframe and create an excel
b = open_json(provincia)
df = adapt_content(b)
file_name = "subastas_" + str(provincia) + ".xlsx"
writer = pd.ExcelWriter(file_name, engine='xlsxwriter', options={'strings_to_urls': False})
df.to_excel(writer, index=False)
writer.close()
