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
import math
import warnings

warnings.simplefilter("ignore")


def get_urls(soup_input, name_link, link_url):
    for a in soup_input.findAll('a', href=True):
        if a.text:
            try:
                if a['title'].startswith('Subasta') and a['class'][0] == 'resultado-busqueda-link-defecto':
                    name_link.append(a['title'])
                    link_url.append(a['href'])
            except Exception:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                continue
    print('There are {} links'.format(len(link_url)))
    return


def curr2num(str_input):
    num = str_input.replace('€', '').replace(',', '').replace('.', '')
    return float(num) / 100


def open_json(url):
    try:
        with open(url) as json_file:
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


def retrieve_data(page, url_base, file_name):
    pageInfo = [1, 5]
    content_by_subasta = {}
    #file_name = "subastas_to_update_puja.json"
    # Loop over pages of boe
    for num in range(page[0] * 50 - 50, page[1] * 50 - 50, 50):
        print('------------------------ PAGE %d -------------------- %s' % ((num / 50) + 1, datetime.datetime.now()))

        # Request the data
        r = requests.get(url_base + str(num) + '-50')
        data = r.text
        soup_input = BeautifulSoup(data, "html5lib")
        a = soup_input.findAll('a', href=True)
        # The data is retrieved
        name_link = []
        link_url = []
        get_urls(soup_input, name_link, link_url)

        t_new = time.time()
        # Loop over found links (subastas)
        for y in range(0, len(link_url)):
            content = {}
            t_old = t_new
            t_new = time.time()
            print('>> Subasta %d: %s - time %s seconds' % (y, name_link[y], str(t_new - t_old)))
            content['IDENTIFICADOR'] = str(name_link[y]).replace('Subasta ', '')
            try:
                # Loop over page info (over the number of pages that a subasta has)
                for z in range(0, len(pageInfo)):
                    page = pageInfo[z]

                    # URL subasta
                    tempUrl = 'https://subastas.boe.es/' + link_url[y]
                    tempUrl = tempUrl.split('&idBus')
                    url = tempUrl[0] + '&ver={}'.format(page) + '&idBus' + tempUrl[1]

                    r = requests.get(url)
                    data = r.text
                    soup = BeautifulSoup(data, "lxml")
                    data = soup.findAll('tr')

                    label = []
                    dataDw = []
                    url_subasta = {"URL": 'https://subastas.boe.es/' + link_url[y]}

                    try:
                        if (pageInfo[z] == 5):
                            soup2 = soup.find(id='idBloqueDatos8')
                            temp = str(soup2.strong)
                            temp = temp.replace('<strong class="destaca">', '')
                            temp = temp.replace('</strong>', "")
                            label_name = 'PRECIO_PUJA'
                            data_cell = temp
                            content[str(label_name)] = str(data_cell)
                        else:
                            # Fecha de conclusión
                            label_name = unidecode(data[3].find('th').text.replace('\n', '').replace(' ', '_').upper())
                            data_cell = data[3].find('td').text.replace('\n', '')
                            data_cell = data_cell.split(' CET  (ISO:')[0]
                            label.append(label_name)
                            dataDw.append(data_cell)
                            for x in range(0, len(label)):
                                content[str(label[x])] = str(dataDw[x])
                    except AttributeError:
                        content['PRECIO_PUJA'] = 'Cancelado'

            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
                continue

            # Get only closed subastas
            hoy = pd.to_datetime(date.today(), format='%Y-%m-%d')
            hoy = hoy.strftime('%d-%m-%Y')
            hoy = datetime.datetime.strptime(hoy, '%d-%m-%Y')
            try:
                f_conclusion = content['FECHA_DE_CONCLUSION'].split(' ')[0]
                f_conclusion = pd.to_datetime(f_conclusion, format='%d-%m-%Y')
                f_conclusion = f_conclusion.strftime('%d-%m-%Y')
                f_conclusion = datetime.datetime.strptime(f_conclusion, '%d-%m-%Y')
            except Exception:
                content['PRECIO_PUJA'] = 'Cancelado'
                yesterday = hoy - timedelta(days=1)
                yesterday = yesterday.strftime('%d-%m-%Y')
                yesterday = datetime.datetime.strptime(yesterday, '%d-%m-%Y')
                f_conclusion = yesterday
            finally:
                if (len(content) > 0):
                    content_by_subasta["URL"] = url_subasta
                    content_by_subasta['PAGE_1'] = content
                if f_conclusion < hoy:
                    f = open(file_name, "a+")
                    f.truncate(0)
                    f.write(json.dumps(content_by_subasta, indent=4))
                    f.close()


def retrieve_data_lotes(page, url_base, file_name):
    pageInfo = [1, 5]
    content_by_subasta = {}
    #file_name = "subastas_to_update_puja_lotes.json"
    # Loop over pages of boe
    for num in range(page[0] * 50 - 50, page[1] * 50 - 50, 50):
        print('------------------------ PAGE %d -------------------- %s' % ((num / 50) + 1, datetime.datetime.now()))

        # Request the data
        r = requests.get(url_base + str(num) + '-50')
        data = r.text
        soup_input = BeautifulSoup(data, "html5lib")
        a = soup_input.findAll('a', href=True)
        # The data is retrieved
        name_link = []
        link_url = []
        get_urls(soup_input, name_link, link_url)

        t_new = time.time()
        # Loop over found links (subastas)
        for y in range(0, len(link_url)):
            content = {}
            t_old = t_new
            t_new = time.time()
            print('>> Subasta %d: %s - time %s seconds' % (y, name_link[y], str(t_new - t_old)))
            content['IDENTIFICADOR'] = str(name_link[y]).replace('Subasta ', '')
            num_lotes = -1
            try:
                # Loop over page info (over the number of pages that a subasta has)
                for z in range(0, len(pageInfo)):
                    page = pageInfo[z]

                    # URL subasta
                    tempUrl = 'https://subastas.boe.es/' + link_url[y]
                    tempUrl = tempUrl.split('&idBus')
                    url = tempUrl[0] + '&ver={}'.format(page) + '&idBus' + tempUrl[1]

                    r = requests.get(url)
                    data = r.text
                    soup = BeautifulSoup(data, "lxml")
                    data = soup.findAll('tr')

                    label = []
                    dataDw = []
                    url_subasta = {"URL": 'https://subastas.boe.es/' + link_url[y]}

                    try:
                        if (pageInfo[z] == 1):
                            try:
                                # Lotes
                                label_name = unidecode(
                                    data[5].find('th').text.replace('\n', '').replace(' ', '_').upper())
                                if label_name != 'LOTES':
                                    data_cell = data[4].find('td').text.replace('\n', '')
                                elif unidecode(
                                        data[5].find('th').text.replace('\n', '').replace(' ', '_').upper()) != 'LOTES':
                                    data_cell = data[3].find('td').text.replace('\n', '')
                                else:
                                    data_cell = data[5].find('td').text.replace('\n', '')
                                num_lotes = int(data_cell)
                                num_lotes = int(data_cell)
                                label.append(label_name)
                                dataDw.append(data_cell)
                                for x in range(0, len(label)):
                                    content[str(label[x])] = str(dataDw[x])

                                # Fecha de conclusión
                                label_name = unidecode(data[3].find('th').text.replace('\n', '').replace(' ', '_').upper())
                                data_cell = data[3].find('td').text.replace('\n', '')
                                data_cell = data_cell.split(' CET  (ISO:')[0]
                                label.append(label_name)
                                dataDw.append(data_cell)
                                for x in range(0, len(label)):
                                    content[str(label[x])] = str(dataDw[x])
                            except ValueError:
                                pass

                        if (pageInfo[z] == 5):
                            # Extract price only if it has more than 1 lote
                            if num_lotes <= 0:
                                continue
                            else:
                                soup2 = soup.find(id='idBloqueDatos8')
                                # Get pujas table
                                temp = str(soup2.findAll("td"))
                                temp = temp.split('</td>')
                                cont = 1
                                for i, x in enumerate(temp):
                                    if i % 2 > 0:
                                        # Create a label and stored data per lote
                                        label_name = 'PRECIO_PUJA_' + str(cont)
                                        # Get pujas
                                        data_cell = temp[i].replace('<td headers="cantidad">', '').replace('</td>]', "")
                                        data_cell = data_cell.replace('[<td>', '').replace('</td>', '')
                                        data_cell = data_cell.replace(', <td headers="lote">', '').replace(', <td>', '')
                                        data_cell = data_cell.replace(', ', '')
                                        # Store values
                                        content[str(label_name)] = str(data_cell)
                                        cont = cont + 1

                    except AttributeError:
                        content['PRECIO_PUJA'] = 'Cancelado'

            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
                continue

            # Get only closed subastas
            hoy = pd.to_datetime(date.today(), format='%Y-%m-%d')
            hoy = hoy.strftime('%d-%m-%Y')
            hoy = datetime.datetime.strptime(hoy, '%d-%m-%Y')
            try:
                f_conclusion = content['FECHA_DE_CONCLUSION'].split(' ')[0]
                f_conclusion = pd.to_datetime(f_conclusion, format='%d-%m-%Y')
                f_conclusion = f_conclusion.strftime('%d-%m-%Y')
                f_conclusion = datetime.datetime.strptime(f_conclusion, '%d-%m-%Y')
            except Exception:
                content['PRECIO_PUJA'] = 'Cancelado'
                yesterday = hoy - timedelta(days=1)
                yesterday = yesterday.strftime('%d-%m-%Y')
                yesterday = datetime.datetime.strptime(yesterday, '%d-%m-%Y')
                f_conclusion = yesterday
            finally:
                if (len(content) > 0):
                    if num_lotes > 0:  # Save only if there are lotes
                        content_by_subasta["URL"] = url_subasta
                        content_by_subasta['PAGE_1'] = content
                if f_conclusion < hoy:
                    if num_lotes > 0:  # Save only if there are lotes
                        f = open(file_name, "a+")
                        f.truncate(0)
                        f.write(json.dumps(content_by_subasta, indent=4))
                        f.close()


# Update precio puja
def update_precio_puja(df, df_main):
    m = df_main.merge(df, how='left', left_on='IDENTIFICADOR', right_on='IDENTIFICADOR')
    # Data quality
    if 'LOTES' in m.columns:
        m.PRECIO_PUJA_x[(m.LOTES == "Sin lotes") & (m.PRECIO_PUJA_x == "None")] = "Desierta"
    else:
        m.PRECIO_PUJA_x[(m.LOTES_x == "Sin lotes") & (m.PRECIO_PUJA_x == "None")] = "Desierta"
    m.PRECIO_PUJA_x[(m.PRECIO_PUJA_x == "None") | (m.PRECIO_PUJA_x == "")] = m.PRECIO_PUJA_y

    #m.PRECIO_PUJA_x[(isinstance(m.PRECIO_PUJA_x, float)) & (math.isnan(float(m.PRECIO_PUJA_x)))] = m.PRECIO_PUJA_y
    # for i, v in enumerate(m['PRECIO_PUJA_x']):
    #     if m.loc[i, 'PRECIO_PUJA_x'] == "None" or m.loc[i, 'PRECIO_PUJA_x'] == "":
    #         m.loc[i, 'PRECIO_PUJA_x'] = m.loc[i, 'PRECIO_PUJA_y']
    #     elif isinstance(m.loc[i, 'PRECIO_PUJA_x'], float) and math.isnan(float(m.loc[i, 'PRECIO_PUJA_x'])):
    #         m.loc[i, 'PRECIO_PUJA_x'] = m.loc[i, 'PRECIO_PUJA_y']
    #     #elif not m.loc[i, 'PRECIO_PUJA_x']:
    #     #    m.loc[i, 'PRECIO_PUJA_x'] = m.loc[i, 'PRECIO_PUJA_y']
    #     elif m.loc[i, 'LOTES'] == "Sin lotes" and m.loc[i, 'PRECIO_PUJA_x'] == "None":
    #             m.loc[i, 'PRECIO_PUJA_x'] = 'Desierta'
    #     else:
    #         m.loc[i, 'PRECIO_PUJA_x'] = m.loc[i, 'PRECIO_PUJA_y']

    m = m.rename(columns = {"PRECIO_PUJA_x":"PRECIO_PUJA"})
    m = m.rename(columns = {"FECHA_DE_CONCLUSION_x":"FECHA_DE_CONCLUSION"})
    m = m.rename(columns = {"ID_LOTES_x":"ID_LOTES"})
    m = m.rename(columns = {"URL_x":"URL"})
    m = m.rename(columns = {"LOTES_x":"LOTES"})
    if 'PRECIO_PUJA_y' in m.columns:
        m = m.drop(columns = ['PRECIO_PUJA_y'])
    if 'FECHA_DE_CONCLUSION_y' in m.columns:
        m = m.drop(columns = ['FECHA_DE_CONCLUSION_y'])
    if 'ID_LOTES_y' in m.columns:
        m = m.drop(columns = ['ID_LOTES_y'])
    if 'URL_y' in m.columns:
        m = m.drop(columns = ['URL_y'])
    if 'LOTES_y' in m.columns:
        m = m.drop(columns = ['LOTES_y'])

    return m


# Update precio puja lotes
def update_precio_puja_lotes(df, df_main):
    m = df_main.merge(df, how='left', left_on='IDENTIFICADOR', right_on='IDENTIFICADOR')

    m['row_num'] = m.groupby('IDENTIFICADOR').cumcount() + 1
    m['row_num'] = m['row_num'].astype(str)
    m['name_row'] = 'PRECIO_PUJA_' + m['row_num'].astype(str)

    m['new'] = '-'
    m.new[(m.LOTES_x != 'Sin lotes') & (m.PRECIO_PUJA_1.notna())] = m[(m.LOTES_x != 'Sin lotes') & (m.PRECIO_PUJA_1.notna())].lookup(m[(m.LOTES_x != 'Sin lotes') & (m.PRECIO_PUJA_1.notna())].index, m[(m.LOTES_x != 'Sin lotes') & (m.PRECIO_PUJA_1.notna())].name_row)
    m.PRECIO_PUJA[m.new != '-'] = m.new

    # Data quality
    #m.PRECIO_PUJA[m['IDENTIFICADOR'] == 'SUB-NV-2017-295512'] = 'Sin Puja'
    #m.PRECIO_PUJA[m['IDENTIFICADOR'] == 'SUB-NV-2019-326232'] = 'Sin Puja'
    #m.PRECIO_PUJA[m['IDENTIFICADOR'] == 'SUB-NV-2017-275507'] = 'Sin Puja'
    #m.PRECIO_PUJA[(m.LOTES_x != "Sin lotes") & (m.PRECIO_PUJA == '')] = "Cancelado"
    m.PRECIO_PUJA[(m.LOTES_x != "Sin lotes") & ((m.PRECIO_PUJA == '[]') | (m.PRECIO_PUJA == 'Sin Puja'))] = "Desierta"
    m.PRECIO_PUJA[m.PRECIO_PUJA == '\n<strong class="destaca">Cancelado</strong>\n'] = 'Cancelado'

    row_num_max = max(m['row_num'])+1
    m = m.rename(columns = {"PRECIO_PUJA_x":"PRECIO_PUJA"})
    m = m.rename(columns = {"FECHA_DE_CONCLUSION_x":"FECHA_DE_CONCLUSION"})
    m = m.rename(columns = {"ID_LOTES_x":"ID_LOTES"})
    m = m.rename(columns = {"URL_x":"URL"})
    m = m.rename(columns = {"LOTES_x":"LOTES"})
    if 'PRECIO_PUJA_y' in m.columns:
        m = m.drop(columns = ['PRECIO_PUJA_y'])
    if 'FECHA_DE_CONCLUSION_y' in m.columns:
        m = m.drop(columns = ['FECHA_DE_CONCLUSION_y'])
    if 'ID_LOTES_y' in m.columns:
        m = m.drop(columns = ['ID_LOTES_y'])
    if 'URL_y' in m.columns:
        m = m.drop(columns = ['URL_y'])
    if 'LOTES_y' in m.columns:
        m = m.drop(columns = ['LOTES_y'])
    if 'row_num' in m.columns:
        m = m.drop(columns = ['row_num'])
    if 'name_row' in m.columns:
        m = m.drop(columns = ['name_row'])
    if 'new' in m.columns:
        m = m.drop(columns = ['new'])
    
    for pp in range(1,row_num_max):
        if 'PRECIO_PUJA_'+str(pp) in m.columns:
            m = m.drop(columns = ['PRECIO_PUJA_'+str(pp)])

    return m

# MAIN
# Retrieve pujas data from regular subastas and update the database
#retrieve_data(page, url_base)  # Get new precio puja of every finished subasta
#df = adapt_content(open_json("subastas_to_update_puja.json"))
#m = update_precio_puja(df, df_main)  # Change precio puja from None to retrieved value
# Save updated file
#writer = pd.ExcelWriter(r'subastas_output_updated.xlsx', engine='xlsxwriter', options={'strings_to_urls': False})
#m.to_excel(writer, index=False)
#writer.close()

# Lotes: Retrieve pujas data from subastas with lotes and update the database
#retrieve_data_lotes(page, url_base)  # Get new precio puja of every finished subasta
#n = adapt_content(open_json("subastas_to_update_puja_lotes.json"))  # Change precio puja from None to retrieved value
#x = update_precio_puja_lotes(n)
# Save updated file
#writer = pd.ExcelWriter(r'subastas_output_updated_v.xlsx', engine='xlsxwriter', options={'strings_to_urls': False})
#x.to_excel(writer, index=False)
#writer.close()
