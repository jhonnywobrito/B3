import os
from tabulate import tabulate

os.system('cls')

def LoadTxt(tipo='todos'):
    L0=[] # Lista que recebrá TXT
    L1={} # DCT que receberá a lista
    with open("main.txt",'r') as Dados:
        for i in Dados:
            if tipo == 'todos':
                L0.append(i.strip().split(","))
            elif tipo in i:
                L0.append(i.strip().split(","))
    for i in L0: # Tranforma lista em dicionario
        L1[i[0]]=[i[1],i[2]]
    return L1

def SaveTxtL(Dict):
    with open("login.txt", 'w') as Dados:
        for chave,dados in Dict.items():
            Dados.write(f"{chave},{dados[0]},{dados[1]}\n")

def FormatReal(my_value):
    a = '{:,.2f}'.format(float(my_value))
    b = a.replace(',', 'v')
    c = b.replace('.', ',')
    return c.replace('v', '.')

def Mes(valor):
    valorF = 0
    i = int(valor) - 1
    m1 = [[0,1,2,3,4,5,6,7,8,9,10,11,12], ["Jan.", "Fev.", "Mar.", "Abr.", "Mai.", "Jun.","Jul.", "Ago.", "Set.", "Out.", "Nov.", "Dez."]]
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
                'Data': Mes(line[6:8].strip()),
                'Tick.': ticker,
                'Abert.': FormatValor(line[56:69].strip()),
                'Máx.': FormatValor(line[78:82].strip()),
                'Mín.': FormatValor(line[91:95].strip()),
                'Fecham.': FormatValor(line[117:121].strip()),
                'Volume': line[152:170].lstrip('0'),
            })

    return data
def Main():
    dados = Processo("dados.txt")

    if dados:
        print(tabulate(dados, headers="keys", tablefmt="grid", stralign="center"))
    else:
        print("Nenhum dado processado.")


Main()
