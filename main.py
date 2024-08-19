import os

os.system('cls')

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
                'Data': line[2:10].strip(),
                'Tick.': ticker,
                'Abert.': FormatValor(line[56:69].strip()),
                'Máx.': FormatValor(line[78:82].strip()),
                'Mín.': FormatValor(line[91:95].strip()),
                'Fecham.': FormatValor(line[117:121].strip()),
                'Volume': line[152:170].lstrip('0'),
            })

    return data
