from bs4 import BeautifulSoup
import requests
from unidecode import unidecode
import json
import time
from datetime import datetime
import dataset
import sys, os
import datetime


# Functions defined
def curr2num(str_input):
    num = str_input.replace('€', '').replace(',', '').replace('.', '')
    return float(num) / 100

def date2format(str_input):
    date = str_input.split('CET')
    return date[0]

# Object to retrieve the data
class GetDataBoe:
    def __init__(self, page, subastas_list, subastas_list_stop):
        self.page = page
        self.subastas_list = subastas_list
        self.subastas_list_stop = subastas_list_stop
        self.url_madrid_base = 'https://subastas.boe.es/subastas_ava.php?accion=Mas&id_busqueda=_WjJnR095Q0t6Mkt6NGhrT0dWVmFTSnhQNlB3aHh2d3ZkZEtMMGc2UWswa3hjWXI3N1dMazhoT0lFSVF3REhyZ3FvRWtrdzRQcnBWTTJnNzFmQ0lGMlJxQ3FLNnRTUG9WL3lpYy9URmNsVnRGaktYNlIwT3NscWoyK3BpTlVValMvSTVSQkxrN2tCSzV5eTdiWEh2dWxRRlFwRVhvVVUvc1JtUUl1TE9DbVE0cFlQbGEwdHFtam9YUlFUZXE2SExjeS95ODhTOFdWTjArZHBBTmdCaG5PQk01ODQrbXgrenVlOTRzS2U1eWNhQndubS9rMzhwVDFpSlBIZ2NxVkxEWk00dzFYZzZ0R0oyRllzaUJQRlNsdXNod1FhMUI2MDZzbHJkQkkzVkhCSkE9-'
        self.url_all = 'https://subastas.boe.es/reg/subastas_ava.php?campo%5B0%5D=SUBASTA.ORIGEN&dato%5B0%5D=&campo%5B1%5D=SUBASTA.ESTADO&dato%5B1%5D=&campo%5B2%5D=BIEN.TIPO&dato%5B2%5D=&dato%5B3%5D=&campo%5B4%5D=BIEN.DIRECCION&dato%5B4%5D=&campo%5B5%5D=BIEN.CODPOSTAL&dato%5B5%5D=&campo%5B6%5D=BIEN.LOCALIDAD&dato%5B6%5D=&campo%5B7%5D=BIEN.COD_PROVINCIA&dato%5B7%5D=&campo%5B8%5D=SUBASTA.POSTURA_MINIMA_MINIMA_LOTES&dato%5B8%5D=&campo%5B9%5D=SUBASTA.NUM_CUENTA_EXPEDIENTE_1&dato%5B9%5D=&campo%5B10%5D=SUBASTA.NUM_CUENTA_EXPEDIENTE_2&dato%5B10%5D=&campo%5B11%5D=SUBASTA.NUM_CUENTA_EXPEDIENTE_3&dato%5B11%5D=&campo%5B12%5D=SUBASTA.NUM_CUENTA_EXPEDIENTE_4&dato%5B12%5D=&campo%5B13%5D=SUBASTA.NUM_CUENTA_EXPEDIENTE_5&dato%5B13%5D=&campo%5B14%5D=SUBASTA.ID_SUBASTA_BUSCAR&dato%5B14%5D=&campo%5B15%5D=SUBASTA.FECHA_FIN_YMD&dato%5B15%5D%5B0%5D=&dato%5B15%5D%5B1%5D=&campo%5B16%5D=SUBASTA.FECHA_INICIO_YMD&dato%5B16%5D%5B0%5D=&dato%5B16%5D%5B1%5D=&page_hits=50&sort_field%5B0%5D=SUBASTA.FECHA_FIN_YMD&sort_order%5B0%5D=desc&sort_field%5B1%5D=SUBASTA.FECHA_FIN_YMD&sort_order%5B1%5D=asc&sort_field%5B2%5D=SUBASTA.HORA_FIN&sort_order%5B2%5D=asc&accion=Buscar'
        self.num_subastas = 0
        self.break_code = False
        self.link_url = []
        self.name_link = []
        self.pageInfo = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        self.pageLabel = ["PAGE_1", "PAGE_2", "PAGE_3", "PAGE_4", "PAGE_5", "PAGE_6", "PAGE_7", "PAGE_8", "PAGE_9"]
        self.content_by_subasta = {}
        self.soup_input = "????"

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
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    print(exc_type, fname, exc_tb.tb_lineno)
                    continue
        print('El número de links econtrados es de {}'.format(len(self.link_url)))
        return

    def perform_loop(self):
        for num in range(self.page[0] * 50, self.page[1] * 50, 50):
            if self.break_code: break
            print('------------------------ PAGE %d -------------------- %s' % (num / 50, datetime.datetime.now()))

            # Request the data
            r = requests.get(self.url_madrid_base + str(num) + '-50')
            data = r.text
            self.soup_input = BeautifulSoup(data, "html5lib")
            a = self.soup_input.findAll('a', href=True)
            print('El número de links econtrados es de {}'.format(len(a)))

            # The data is retrieved
            self.get_urls()

            t_new = time.time()
            for y in range(0, len(self.link_url)):
                if self.break_code: break
                t_old = t_new
                t_new = time.time()
                print('>> ITERATION %d: time %s seconds' % (y, str(t_new - t_old)))
                num_lotes = -1
                content_by_subasta = {}
                try:
                    for z in range(0, len(self.pageInfo)):
                        if self.break_code: break
                        page = self.pageInfo[z]
                        # print('------------{}'.format(pageName[z]) )
                        tempUrl = 'https://subastas.boe.es/' + self.link_url[y]
                        # print(tempUrl)
                        tempUrl = tempUrl.split('&idBus')
                        url = tempUrl[0] + '&ver={}'.format(page) + '&idBus' + tempUrl[1]

                        if int(self.pageInfo[z]) == 3:
                            if int(num_lotes) != 0:
                                # print('entra')
                                for numL in range(1, int(num_lotes) + 1):
                                    # print('-----------Lote:'+str(numL)+'    '+str(numLotes))
                                    url = url + '&idLote=' + str(numL) + '&numPagBus='
                                    pageLabel2pass = self.pageLabel[z] + "_LOTE_" + str(numL)
                                    # print(pageLabel2pass)
                                    try:
                                        # print("numlotes>1")
                                        num_lotes = self.getdata2json(url, pageLabel2pass, z, y, num_lotes)
                                    except Exception as e:
                                        exc_type, exc_obj, exc_tb = sys.exc_info()
                                        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                                        print(exc_type, fname, exc_tb.tb_lineno)
                                        continue
                            else:
                                pageLabel2pass = self.pageLabel[z] + "_LOTE_1"
                                try:
                                    num_lotes = self.getdata2json(url, pageLabel2pass, z, y, num_lotes)
                                except Exception as e:
                                    exc_type, exc_obj, exc_tb = sys.exc_info()
                                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                                    print(exc_type, fname, exc_tb.tb_lineno)
                                    continue
                        else:
                            try:
                                num_lotes = self.getdata2json(url, self.pageLabel[z], z, y, num_lotes)
                            except Exception as e:
                                print(e)
                                print(self.pageInfo[z])
                                continue
                                # print("error other")
                    # print(content_by_subasta["PAGE_1"])
                    # This part of the code will stop the execution whether the subastas identifier are already in the database
                    if any(self.content_by_subasta["PAGE_1"]["IDENTIFICADOR"] in s for s in self.subastas_list):
                        print("The subasta was already in the data base")
                        self.num_subastas = self.num_subastas + 1
                        if self.num_subastas == self.subastas_list_stop:
                            print("The code is stopping from executing")
                            self.break_code = True
                            if self.break_code: break
                        else:
                            continue
                    else:
                        print("Subasta not in dB")
                    file_name = "subastas" + ".json"
                    # file_name = "subastas" + datetime.now().strftime("%Y-%m-%d-%Hh-%Mm") + ".json"
                    print(file_name)
                    f = open(file_name, "a+")
                    f.write(json.dumps(self.content_by_subasta, indent=4))
                    f.close()
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    print(exc_type, fname, exc_tb.tb_lineno)
                    continue

    def getdata2json(self, url, page_label, z, y, num_lotes):
        r = requests.get(url)
        data = r.text
        soup = BeautifulSoup(data, "lxml")
        if page_label == "PAGE_8":
            soup2 = soup.find(id='idBloqueDatos8')
            temp = str(soup2.span)
            temp = temp.replace('<span class="destaca">', '')
            temp = temp.replace('</span>', "")
        data = soup.findAll('tr')

        label = []
        dataDw = []
        content = {}
        url_subasta = {"URL": 'https://subastas.boe.es/' + self.link_url[y]}
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



# Code to execute
page = [1, 3]
subastas_list = ["SUB-AT-2020-19R2886001764", "SUB-AT-2020-19R2886001764",
                 "SUB-AT-2020-19R2886001829" "SUB-AT-2020-20R2886002012", ]  # Subastas identifier to find them
subastas_list_stop = 3  # Number of previous subastas to be found before breaking the code
GetDataBoe = GetDataBoe(page=page, subastas_list=subastas_list, subastas_list_stop=subastas_list_stop)
GetDataBoe.perform_loop()

# Include json in GetDataBoe

#


