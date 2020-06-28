from bs4 import BeautifulSoup
import requests
from unidecode import unidecode
import json
import time
from datetime import datetime
import dataset

import os
import datetime

# Functions defined
url_madrid_base = 'https://subastas.boe.es/subastas_ava.php?accion=Mas&id_busqueda=_WjJnR095Q0t6Mkt6NGhrT0dWVmFTSnhQNlB3aHh2d3ZkZEtMMGc2UWswa3hjWXI3N1dMazhoT0lFSVF3REhyZ3FvRWtrdzRQcnBWTTJnNzFmQ0lGMlJxQ3FLNnRTUG9WL3lpYy9URmNsVnRGaktYNlIwT3NscWoyK3BpTlVValMvSTVSQkxrN2tCSzV5eTdiWEh2dWxRRlFwRVhvVVUvc1JtUUl1TE9DbVE0cFlQbGEwdHFtam9YUlFUZXE2SExjeS95ODhTOFdWTjArZHBBTmdCaG5PQk01ODQrbXgrenVlOTRzS2U1eWNhQndubS9rMzhwVDFpSlBIZ2NxVkxEWk00dzFYZzZ0R0oyRllzaUJQRlNsdXNod1FhMUI2MDZzbHJkQkkzVkhCSkE9-'
page = [1, 3]
subastas_list = ["SUB-AT-2020-19R2886001764", "SUB-AT-2020-19R2886001764",
                 "SUB-AT-2020-19R2886001829" "SUB-AT-2020-20R2886002012", ] # Subastas identifier to find them
subastas_list_stop = 3  # Number of previous subastas to be found before breaking the code


num_subastas = 0
break_code = False


def curr2num(str_input):
    num = str_input.replace('€', '').replace(',', '').replace('.', '')
    return float(num) / 100


def date2format(str_input):
    date = str_input.split('CET')
    return date[0]


date2format('21-06-2018 18:00:00 CET  (ISO: 2018-06-21T18:00:00+02:00)')


# We get the URL from the subastas
# We filter the URL for the ones that are for "subastas" and the variable link is updated with the links.
def get_urls(soup_input):
    link_url = []
    name_link = []
    for a in soup_input.findAll('a', href=True):
        if a.text:
            try:

                if a['title'].startswith('Subasta') and a['class'][0] == 'resultado-busqueda-link-defecto':
                    # print(a['title'])
                    name_link.append(a['title'])
                    link_url.append(a['href'])
            except:
                continue
    print('El número de links econtrados es de {}'.format(len(link_url)))
    return link_url, name_link


def getdata2json(content_by_subasta, url, page_label, z, link, y, page_info, num_lotes):
    r = requests.get(url)
    # print('https://subastas.boe.es/'+url)
    data = r.text
    soup = BeautifulSoup(data, "lxml")
    if page_label == "PAGE_8":
        soup2 = soup.find(id='idBloqueDatos8')
        temp = str(soup2.span)
        # print(temp)
        temp = temp.replace('<span class="destaca">', '')
        temp = temp.replace('</span>', "")
        # print(temp)
        # print(soup2.span("class").get())
        # print(soup2.span("class").get_text())
    data = soup.findAll('tr')

    label = []
    dataDw = []
    content = {}
    url_subasta = {"URL": 'https://subastas.boe.es/' + link[y]}
    # try:
    if (page_label == "PAGE_8"):
        label_name = 'PRECIO_PUJA'
        data_cell = temp
        # print(data_cell)
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
            downloaded[label[x]] = dataDw[x]
            # value = str('{}: {}'.format(label[x],dataDw[x]))
            content[str(label[x])] = str(dataDw[x])
            if (page_info[z] == 1):
                if label[x] == 'LOTES':
                    num_lotes = dataDw[x]
                    if num_lotes == 'Sin lotes':
                        num_lotes = 0

    #  except:
    #      continue
    # print(content)
    # print(pageLabel)
    if (len(content) > 0):
        if (z == 0):
            content_by_subasta["URL"] = url_subasta
            content_by_subasta[page_label] = content
        else:
            content_by_subasta[page_label] = content
    return content_by_subasta, num_lotes


nameDataDB = 'BOE'
tableName = 'MAD'
# dirPath = 'C:\\Users\as857sb\\Documents\\Python Scripts'
# pathDB='sqlite:///'+dirPath+'\\'+nameDataDB
# print(pathDB)
# db=dataset.connect(pathDB)
# table=db[tableName]


for num in range(page[0] * 50, page[1] * 50, 50):  # 8800,50):
    if break_code: break
    print('------------------------ PAGE %d -------------------- %s' % (num / 50, datetime.datetime.now()))
    url_madrid = url_madrid_base + str(num) + '-50'
    # print(url_madrid)

    # url_madrid='https://subastas.boe.es/subastas_ava.php?campo%5B1%5D=SUBASTA.ESTADO&dato%5B1%5D=EJ&campo%5B2%5D=BIEN.TIPO&dato%5B2%5D=I&campo%5B7%5D=BIEN.COD_PROVINCIA&dato%5B7%5D=28&campo%5B16%5D=SUBASTA.FECHA_INICIO_YMD&dato%5B16%5D%5B0%5D=&dato%5B16%5D%5B1%5D=&page_hits=40&sort_field%5B0%5D=SUBASTA.FECHA_FIN_YMD&sort_order%5B0%5D=desc&sort_field%5B1%5D=SUBASTA.FECHA_FIN_YMD&sort_order%5B1%5D=asc&sort_field%5B2%5D=SUBASTA.HORA_FIN&sort_order%5B2%5D=asc&accion=Buscar'
    r = requests.get(url_madrid)
    data = r.text
    soup = BeautifulSoup(data, "html5lib")

    a = soup.findAll('a', href=True)
    print('El número de links econtrados es de {}'.format(len(a)))
    link, name_link = get_urls(soup)

    # type(data)
    # len(data)
    pageInfo = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    # pageName=['Información general','Autoridad Gestora','Bien','Acreedor','Pujas']
    pageLabel = ["PAGE_1", "PAGE_2", "PAGE_3", "PAGE_4", "PAGE_5", "PAGE_6", "PAGE_7", "PAGE_8", "PAGE_9"]
    downloaded = {}
    t_old = time.time()
    t_new = time.time()
    for y in range(0, len(link)):
        if break_code: break
        t_old = t_new
        t_new = time.time()
        print('>> ITERATION %d: time %s seconds' % (y, str(t_new - t_old)))
        num_lotes = -1
        content_by_subasta = {}
        try:
            for z in range(0, len(pageInfo)):
                if break_code: break
                # print(str('Page {} out of {}'.format(pageInfo[z],max(pageInfo))))
                page = pageInfo[z]
                # print('------------{}'.format(pageName[z]) )
                tempUrl = 'https://subastas.boe.es/' + link[y]
                tempUrl = tempUrl.split('&idBus')
                url = tempUrl[0] + '&ver={}'.format(page) + '&idBus' + tempUrl[1]

                if int(pageInfo[z]) == 3:
                    if int(num_lotes) != 0:
                        # print('entra')
                        for numL in range(1, int(num_lotes) + 1):
                            # print('-----------Lote:'+str(numL)+'    '+str(numLotes))
                            url = url + '&idLote=' + str(numL) + '&numPagBus='
                            pageLabel2pass = pageLabel[z] + "_LOTE_" + str(numL)
                            try:
                                # print("numlotes>1")
                                content_by_subasta, num_lotes = getdata2json(content_by_subasta, url, pageLabel2pass, z,
                                                                             link, y, pageInfo, num_lotes)
                            except Exception as e:
                                print(e)
                                print('1')
                                continue
                    else:
                        pageLabel2pass = pageLabel[z] + "_LOTE_1"
                        try:
                            # print("numlotes == 1")
                            content_by_subasta, num_lotes = getdata2json(content_by_subasta, url, pageLabel2pass, z,
                                                                         link, y,
                                                                         pageInfo, num_lotes)
                        except Exception as e:
                            print(e)
                            print('2')
                            continue
                else:
                    try:
                        # print("other")
                        content_by_subasta, num_lotes = getdata2json(content_by_subasta, url, pageLabel[z], z, link, y,
                                                                     pageInfo, num_lotes)
                        # print(content_by_subasta)
                    except Exception as e:
                        print(e)
                        print(pageInfo[z])
                        continue
                        # print("error other")
            # print(content_by_subasta["PAGE_1"])
            print(content_by_subasta["PAGE_1"]["IDENTIFICADOR"])
            # This part of the code will stop the execution whether the subastas identifier are already in the database
            if any(content_by_subasta["PAGE_1"]["IDENTIFICADOR"] in s for s in subastas_list):
                print("The subasta was already in the data base")
                num_subastas = num_subastas + 1
                if num_subastas == subastas_list_stop:
                    print("The code is stopping from executing")
                    break_code = True
                    if break_code: break
                else:
                    continue
            else:
                print("Subasta not in dB")
            # content_by_subasta[str(content_by_subasta["PAGE_1"]["IDENTIFICADOR"])] = content_by_subasta
            # print(content_by_subasta)
            file_name = "subastas" + + ".json"
            # file_name = "subastas" + datetime.now().strftime("%Y-%m-%d-%Hh-%Mm") + ".json"
            print(file_name)
            f = open(file_name, "a+")
            f.write(json.dumps(content_by_subasta, indent=4))
            f.close()
        except:
            continue


