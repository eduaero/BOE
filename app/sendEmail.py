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
warnings.simplefilter("ignore")


def prepare_email(df, newbies):
    
    #drop_columns = ['ANUNCIO_BOE', 'Antigüedad', 'CARGAS', 'CODIGO', 'CUOTA', 'NIF','NOMBRE',
#'CORREO_ELECTRONICO', 'Clase', 'Clase de cultivo', 'Coeficiente de participación', 'DEPOSITO',
#'Escalera', 'FAX', 'FECHA_DE_ADQUISICION', 'FECHA_DE_CONCLUSION', 'Referencia Catastral',
#'FECHA_DE_MATRICULACION', 'FORMA_ADJUDICACION', 'IDUFIR', 'PAIS', 'PARCELA', 'Situación',
#'IMPORTE_DEL_DEPOSITO', 'INFORMACION_ADICIONAL', 'INSCRIPCION_REGISTRAL', 'Intensidad productiva',
#'LOTES', 'Localización', 'MARCA', 'MATRICULA', 'MODELO', 'NUMERO_DE_BASTIDOR', 'Referencia catastral',
#'PROVINCIA', 'PUJA_MINIMA', 'Planta', 'Puerta', 'REFERENCIA_CATASTRAL', 'REFERENCIA_REGISTRAL',
#'SITUACION_POSESORIA', 'Subparcelas', 'Superficie', 'Superficie (ha)', 'PRECIO_PUJA',
#'TASACION', 'TELEFONO', 'TIPO_DE_SUBASTA', 'TITULO_JURIDICO', 'VALOR_DE_TASACION',
#'TRAMOS_ENTRE_PUJAS', 'Uso', 'VISITABLE', 'VIVIENDA_HABITUAL', 'DESCRIPCION']
    cols = ['CANTIDAD_RECLAMADA','CODIGO_POSTAL','DIRECCION','FECHA_DE_INICIO','IDENTIFICADOR','LOCALIDAD', 'URL', 'VALOR_SUBASTA', 'Superficie Catastral (m2)','Superficie']
    e = df[cols]

    # Filter email by date (yesterday)
    #e['FECHA_DE_INICIO'] = pd.to_datetime(e['FECHA_DE_INICIO'])
    #e['FECHA_DE_INICIO'] = e['FECHA_DE_INICIO'].dt.strftime('%d-%m-%Y')
    #ayer = pd.to_datetime(date.today()-timedelta(days=1), format='%Y-%m-%d')
    #ayer = ayer.strftime('%d-%m-%Y')
    e = e.drop(columns=['FECHA_DE_INICIO'])

    # Define URL link properly to make it clickable
    e['URL'] = str("<a href='") + e['URL'] + str("'>Subasta</a>")  # URL to the subasta

    # Change string type for num
    try:
        if e['VALOR_SUBASTA'] == 'Ver valor de subasta en cada lote (los lotes se subastan de forma independiente)':
            e['VALOR_SUBASTA'] = 0
        else:
            e['VALOR_SUBASTA'] = e['VALOR_SUBASTA'].astype('float64')
    except ValueError: print('')

    # Select only new values
    e = e[e['IDENTIFICADOR'].isin(newbies)]

    # Adapt quantities with the proper format
    s = 'Ver valor de subasta en cada lote (los lotes se subastan de forma independiente)'
    e.VALOR_SUBASTA[e['VALOR_SUBASTA'] == s] = 0
    e['VALOR_SUBASTA'] = e['VALOR_SUBASTA'].astype('float64')
    e['CODIGO_POSTAL'] = e['CODIGO_POSTAL'].astype('object')
    e['Superficie Catastral (m2)'] = e['Superficie Catastral (m2)'].astype('object')
    e['Superficie'] = e['Superficie'].astype('object')
    e['VALOR_SUBASTA'] = e['VALOR_SUBASTA'].map('{:,.2f} €'.format)
    e['CANTIDAD_RECLAMADA'] = e['CANTIDAD_RECLAMADA'].map('{:,.2f} €'.format)

    # Change order of columns
    cols = ['LOCALIDAD', 'VALOR_SUBASTA', 'DIRECCION', 'CANTIDAD_RECLAMADA',
            'CODIGO_POSTAL', 'Superficie Catastral (m2)', 'Superficie', 'URL', 'IDENTIFICADOR']
    e = e[cols]
    e = e.reset_index()

    # Introduce link to map
    for i, v in enumerate(e['DIRECCION']):
        direccion = e.loc[i, 'DIRECCION'].replace(' ', '+')
        codigo_postal = str(e.loc[i, 'CODIGO_POSTAL']).replace('.0', '')
        localidad = str(e.loc[i, 'LOCALIDAD'])
        e.loc[i, 'DIRECCION'] = str("<a href='https://maps.google.com/?q=") + direccion + str(
            ",+") + codigo_postal + str("+") + localidad + str("'>") + e.loc[i, 'DIRECCION'] + str("</a>")

    return e


def send_mail(df, newbies, TO_EMAILS):
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
emails = list(open("emails.txt", "r").read().split('\n'))


# Get new subastas
newbies = []
with open('newbies_Marbella.csv', newline='') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
    for row in spamreader:
        newbies.append(row[0])

# Get data
df = pd.read_excel("subastas_output_updated_Marbella.xlsx")

# Send email if there are new subastas
if newbies != []:
    for TO_EMAILS in emails:
        send_mail(df, newbies, TO_EMAILS)
    print("Mails sent successfully.")