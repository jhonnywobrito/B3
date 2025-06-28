from flask import Flask, request, jsonify
import gspread
from gspread_dataframe import set_with_dataframe
import json, os, io, pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.readonly"
]
keyfile_dict = json.loads(os.getenv('GOOGLE_CREDENTIALS'))
credentials = service_account.Credentials.from_service_account_info(keyfile_dict, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=credentials)

def encontrar_id_por_nome_na_pasta(folder_id, nome_arquivo):
    query = f"'{folder_id}' in parents and name = '{nome_arquivo}' and trashed = false"
    resp = drive_service.files().list(q=query, fields="files(id, name)").execute()
    arquivos = resp.get('files', [])
    return arquivos[0]['id'] if arquivos else None

def baixar_drive(file_id, destino):
    req = drive_service.files().get_media(fileId=file_id)
    fh = io.FileIO(destino, 'wb')
    downloader = MediaIoBaseDownload(fh, req)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    fh.close()

def FormatarValor(valor_str):
    try: return float(valor_str) / 100
    except: return None

def Processo(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()[1:]
    data = []
    for line in lines:
        ticker = line[12:17].strip()
        if ticker.endswith('3') or ticker.endswith('4'):
            d = line[2:10]
            data.append({
                'Data': f"{d[6:8]}/{d[4:6]}/{d[0:4]}",
                'Tick.': ticker,
                'Abert.': FormatarValor(line[56:69]),
                'Max.': FormatarValor(line[69:82]),
                'Min.': FormatarValor(line[82:95]),
                'Fecham.': FormatarValor(line[108:121]),
                'Volume': int(line[152:170].lstrip('0') or '0')
            })
    return pd.DataFrame(data)

app = Flask(__name__)

@app.route('/', methods=['POST'])
def pesquisar():
    pasta_id = "11XYVzfUxrBkGEvgQE6ZVkKaOntfFHfvh"
    arquivos = request.json.get("ticker","").strip().upper()
    file_id = encontrar_id_por_nome_na_pasta(pasta_id, "dados.txt")
    
    if not file_id:
        return jsonify({"status":"erro","msg":"dados.txt não encontrado"}), 404
    destino = '/tmp/dados.txt'
    
    baixar_drive(file_id, destino)
    df = Processo(destino)
    
    df_filtrado = df[df['Tick.'].str.contains(arquivos)]
    
    gs = gspread.authorize(credentials)
    plan = gs.open("Análise de investimentos").worksheet("ETL")
    
    plan.clear()
    set_with_dataframe(plan, df_filtrado)
    return jsonify({"status":"ok","linhas":len(df_filtrado)})

if __name__ == '__main__':
    app.run(port=5000, debug=True)
