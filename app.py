from flask import Flask, request, jsonify
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from gspread_dataframe import set_with_dataframe

app = Flask(__name__)

def FormatarValor(valor_str):
    try:
        return float(valor_str) / 100
    except:
        return None

def Mes(mes_str):
    meses = {
        '01': 'Jan', '02': 'Fev', '03': 'Mar', '04': 'Abr',
        '05': 'Mai', '06': 'Jun', '07': 'Jul', '08': 'Ago',
        '09': 'Set', '10': 'Out', '11': 'Nov', '12': 'Dez'
    }
    return meses.get(mes_str.zfill(2), mes_str)

def Processo(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()[1:]

    data = []
    for line in lines:
        ticker = line[12:17].strip()
        if ticker.endswith('3') or ticker.endswith('4'):
            data_bruta = line[2:10]
            ano = data_bruta[0:4]
            mes = data_bruta[4:6]
            dia = data_bruta[6:8]
            data.append({
                'Data': f"{dia}/{mes}/{ano}",
                'Tick.': ticker,
                'Abert.': FormatarValor(line[56:69]),
                'Max.': FormatarValor(line[69:82]),
                'Min.': FormatarValor(line[82:95]),
                'Fecham.': FormatarValor(line[108:121]),
                'Volume': int(line[152:170].lstrip('0') or '0')
            })

    return pd.DataFrame(data)

@app.route('/', methods=['POST'])
def pesquisar():
    body = request.json
    pesquisa = body.get("ticker", "").strip().upper()

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name('sistema-b3-13fce9d509f7.json', scopes)
    client = gspread.authorize(creds)
    planilha = client.open("Análise de investimentos").worksheet("ETL")

    df = Processo('dados.txt')
    df_filtrado = df[df['Tick.'].str.contains(pesquisa)]

    planilha.clear()
    set_with_dataframe(planilha, df_filtrado)

    return jsonify({"status": "ok", "linhas": len(df_filtrado)})

if __name__ == '__main__':
    app.run(port=5000, debug=True)
