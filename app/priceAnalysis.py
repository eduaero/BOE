import json
import pandas as pd
import csv
import warnings

warnings.simplefilter("ignore")


# Change precio puja and valor subasta to float
def str_to_float(df):
    df.VALOR_SUBASTA[df.VALOR_SUBASTA == 'Ver valor de subasta en cada lote (los lotes se subastan de forma independiente)'] = 0.0
    df.VALOR_SUBASTA[df.VALOR_SUBASTA == 'No consta'] = 0.0
    df.VALOR_SUBASTA[df.VALOR_SUBASTA == 'Sin puja'] = 0.0
    df['VALOR_SUBASTA'] = df['VALOR_SUBASTA'].astype('float64')

    df.PRECIO_PUJA[df.PRECIO_PUJA == 'None'] = 0.0
    df.PRECIO_PUJA[df.PRECIO_PUJA == ''] = 0.0
    df.PRECIO_PUJA[df.PRECIO_PUJA == 'Cancelado'] = 0.0
    df.PRECIO_PUJA[df.PRECIO_PUJA == 'Cancelada'] = 0.0
    df.PRECIO_PUJA[df.PRECIO_PUJA == 'Desierta'] = 0.0
    df.PRECIO_PUJA[df.PRECIO_PUJA == 'Sin puja'] = 0.0
    df.PRECIO_PUJA[df.PRECIO_PUJA == 'Sin Puja'] = 0.0
    df.PRECIO_PUJA[df.PRECIO_PUJA == 'Con puja (inicie sesión para consultar el importe)'] = 0.0
    for i, v in enumerate(df['PRECIO_PUJA']):
        if str(df.loc[i, 'PRECIO_PUJA'])[-1] == '€':
            df.loc[i, 'PRECIO_PUJA'] = str(df.loc[i, 'PRECIO_PUJA']).replace(' €', '').replace('€', '').replace('.', '').replace(',', '.')
    df['PRECIO_PUJA'] = df['PRECIO_PUJA'].astype('float64')
    return df

def valor_subasta_lotes_correction(df):
    for i,v in enumerate(df['VALOR_SUBASTA']):
        if df.loc[i, 'LOTES'] != 'Sin lotes':
            s = 'Ver valor de subasta en cada lote (los lotes se subastan de forma independiente)'
            if df.loc[i, 'VALOR_SUBASTA'] == s:

            else:



def codigos_postales(df):
    #cols = ['IDENTIFICADOR', 'CODIGO_POSTAL', 'VALOR_SUBASTA', 'PRECIO_PUJA']  # , 'CANTIDAD_RECLAMADA'
    #df = df[cols]
    # Filter not null pujas, precio puja 50k-500k and Madrid data
    df = df[df['PRECIO_PUJA'] != 0]
    #df = df[df['PRECIO_PUJA'] >= 50000]
    #df = df[df['PRECIO_PUJA'] <= 500000]
    df = df[df['CODIGO_POSTAL'] >= 28000]
    df = df[df['CODIGO_POSTAL'] < 29000]

    # Create aggregations
    group = df.groupby(by='CODIGO_POSTAL').mean()
    group_count = df.groupby(by='CODIGO_POSTAL').count()
    output = group.merge(group_count, how='left', left_on='CODIGO_POSTAL', right_on='CODIGO_POSTAL')

    # Create variation columns
    output['var'] = output['PRECIO_PUJA_x'] - output['VALOR_SUBASTA_x']
    output['var%'] = output['var']/output['VALOR_SUBASTA_x']

    cols = ['VALOR_SUBASTA_x', 'PRECIO_PUJA_x', 'var', 'var%', 'IDENTIFICADOR']
    output = output[cols]
    output.columns = ['VALOR_SUBASTA_medio', 'PRECIO_PUJA_medio', 'var_media', 'var%_media', 'Bienes']

    # Consider only postal codes with more than 10 items
    #output = output[output['Bienes'] > 10]

    # Save data to excel
    writer = pd.ExcelWriter(r'codigos_postales.xlsx', engine='xlsxwriter', options={'strings_to_urls': False})
    output.to_excel(writer, index=True)
    writer.close()


# Import data
df = pd.read_excel("subastas_output_updated_v.xlsx")
df = str_to_float(df)
