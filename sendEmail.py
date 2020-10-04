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


def prepare_email(df, newbies):
    # columnas = ['ANUNCIO_BOE','Antigüedad','CANTIDAD_RECLAMADA','CARGAS','CODIGO','CODIGO_POSTAL',
    # 'CORREO_ELECTRONICO','Clase','Clase de cultivo','Coeficiente de participación','DEPOSITO',
    # 'DESCRIPCION','DIRECCION','Escalera','FAX','FECHA_DE_ADQUISICION','FECHA_DE_CONCLUSION',
    # 'FECHA_DE_INICIO','FECHA_DE_MATRICULACION','FORMA_ADJUDICACION','IDENTIFICADOR','IDUFIR',
    # 'IMPORTE_DEL_DEPOSITO','INFORMACION_ADICIONAL','INSCRIPCION_REGISTRAL','Intensidad productiva',
    # 'LOCALIDAD','LOTES','Localización','MARCA','MATRICULA','MODELO','NIF','NOMBRE','NUMERO_DE_BASTIDOR',
    # 'PAIS','PROVINCIA','PUJA_MINIMA','Planta','Puerta','REFERENCIA_CATASTRAL','REFERENCIA_REGISTRAL',
    # 'Referencia Catastral','SITUACION_POSESORIA','Subparcelas','Superficie','Superficie (ha)',
    # 'Superficie Catastral (m2)','TASACION','TELEFONO','TIPO_DE_SUBASTA','TITULO_JURIDICO',
    # 'TRAMOS_ENTRE_PUJAS','URL','Uso','VALOR_SUBASTA','VISITABLE','VIVIENDA_HABITUAL']
    drop_columns = ['ANUNCIO_BOE', 'Antigüedad', 'CARGAS', 'CODIGO',
'CORREO_ELECTRONICO', 'Clase', 'Clase de cultivo', 'Coeficiente de participación', 'DEPOSITO',
'Escalera', 'FAX', 'FECHA_DE_ADQUISICION', 'FECHA_DE_CONCLUSION', 'Referencia Catastral',
'FECHA_DE_MATRICULACION', 'FORMA_ADJUDICACION', 'IDUFIR',
'IMPORTE_DEL_DEPOSITO', 'INFORMACION_ADICIONAL', 'INSCRIPCION_REGISTRAL', 'Intensidad productiva',
'LOTES', 'Localización', 'MARCA', 'MATRICULA', 'MODELO', 'NUMERO_DE_BASTIDOR',
'PROVINCIA', 'PUJA_MINIMA', 'Planta', 'Puerta', 'REFERENCIA_CATASTRAL', 'REFERENCIA_REGISTRAL',
'SITUACION_POSESORIA', 'Subparcelas', 'Superficie', 'Superficie (ha)',
'TASACION', 'TELEFONO', 'TIPO_DE_SUBASTA', 'TITULO_JURIDICO',
'TRAMOS_ENTRE_PUJAS', 'Uso', 'VISITABLE', 'VIVIENDA_HABITUAL']
    e = df.drop(columns=drop_columns)
    try:
        e = e.drop(coulmns=['NIF', 'NOMBRE', 'PAIS'])
    except Exception:
        print('')

    # Filter email by date (yesterday)
    e['FECHA_DE_INICIO'] = pd.to_datetime(e['FECHA_DE_INICIO'])
    e['FECHA_DE_INICIO'] = e['FECHA_DE_INICIO'].dt.strftime('%d-%m-%Y')
    ayer = pd.to_datetime(date.today()-timedelta(days=1), format='%Y-%m-%d')
    ayer = ayer.strftime('%d-%m-%Y')
    e = e.drop(columns=['FECHA_DE_INICIO'])

    e['URL'] = str("<a href='") + e['URL'] + str("'>Subasta</a>")  # URL to the subasta

    # Change string type for num
    try:
        if e['VALOR_SUBASTA'] == 'Ver valor de subasta en cada lote (los lotes se subastan de forma independiente)':
            e['VALOR_SUBASTA'] = 0
        else:
            e['VALOR_SUBASTA'] = e['VALOR_SUBASTA'].astype('float64')
    except ValueError:
        print('')

    e = e[e['IDENTIFICADOR'].isin(newbies)]  # select only new values

    return e


def send_mail(df, newbies):
    email_content = prepare_email(df, newbies)
    output = build_table(email_content, 'blue_light')  # Format of the email
    body = output.replace('&lt;', '<').replace('&gt;', '>')

    # Content of the email
    message = MIMEMultipart()
    hoy = pd.to_datetime(date.today(), format='%Y-%m-%d')
    hoy = hoy.strftime('%d-%m-%Y')
    message['Subject'] = 'Subastas BOE del ' + str(hoy)
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
# Get credentials and email list
SENDING_EMAIL = open("email_credentials.txt", "r").read().split('\n')[0]
PASSWORD = open("email_credentials.txt", "r").read().split('\n')[1]
TO_EMAILS = open("emails.txt", "r").read().replace('\n', ';')


# Get new subastas
newbies = []
with open('newbies.csv', newline='') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
    for row in spamreader:
        newbies.append(row[0])

# Get data
df = pd.read_excel("subastas_output.xlsx")

# Send email if there are new subastas
if newbies != []:
    send_mail(df, newbies)
    print("Mail sent successfully.")