from collections import defaultdict
from statistics import mean
import os
from tabulate import tabulate

os.system('cls')

def FormatReal(my_value):
    a = '{:,.2f}'.format(float(my_value))
    b = a.replace(',', 'v')
    c = b.replace('.', ',')
    return c.replace('v', '.')

def Mes(valor):
    valorF = 0
    i = int(valor) - 1
    m1 = [[0, 1, 2, 3, 4, 5, 6], ["Jan.", "Fev.", "Mar.", "Abr.", "Mai.", "Jun."]]
    if i in m1[0]:
        valorF = m1[1][i]
    return valorF

def FormatValor(valor):
    valor_str = valor.lstrip('0') 
    if len(valor_str) == 4:
        return f"{valor_str[:2]},{valor_str[2:]}"
    elif len(valor_str) == 3:
        return f"{valor_str[:1]},{valor_str[1:]}"
    elif len(valor_str) < 3:
        return f"0,{valor_str.zfill(2)}"
    else:
        return valor_str[:-2] + ',' + valor_str[-2:]

def Processo(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()[1:]

    data = []
    for line in lines:
        ticker = line[12:24].strip()
        if ticker.endswith('3') or ticker.endswith('4'): 
            data.append({
                'Data': line[2:10].strip(),
                'Tick.': ticker,
                'Abert.': FormatValor(line[56:69].strip()),
                'Máx.': FormatValor(line[78:82].strip()),
                'Mín.': FormatValor(line[91:95].strip()),
                'Fecham.': FormatValor(line[117:121].strip()),
                'Volume': line[152:170].lstrip('0'),
            })

    return data

def print_table(data):
    if len(data) == 0:
        print("Nenhum dado encontrado.")
        return
    
    print(tabulate(data, headers="keys", tablefmt="grid", numalign="right", stralign="left"))

filename = 'dados.txt'
dados = Processo(filename)

grupo_mes = defaultdict(lambda: {'fechamentos': [], 'volumes': []})

for entrada in dados:
    data_mes = Mes(entrada['Data'][4:6])
    fechamento = float(entrada['Fecham.'].replace(',', '.'))
    volume = float(entrada['Volume'])
    chave = (entrada['Tick.'], data_mes)
    grupo_mes[chave]['fechamentos'].append(fechamento)
    grupo_mes[chave]['volumes'].append(volume)


liquidez_mensal = []
for chave, valores in grupo_mes.items():
    ticker, mes = chave
    media_fechamento = mean(valores['fechamentos'])
    media_volume = mean(valores['volumes'])
    liquidez = media_fechamento * media_volume
    if liquidez > 3000000:
        liquidez_mensal.append({
            'Tick.': ticker,
            'Mês': mes,
            'M. Fech.': FormatReal(media_fechamento),
            'M. Volume': int(media_volume),
            'Liquidez Mens.': FormatReal(liquidez),
        })

liquidez_mensal.sort(key=lambda x: x['Tick.'])
print_table(liquidez_mensal)

'''
dados.sort(key=lambda x: x['Tick.'])
print_table(dados)
'''