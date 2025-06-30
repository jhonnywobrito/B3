from flask import Flask, request, jsonify # type: ignore
import gspread
from gspread_dataframe import set_with_dataframe # type: ignore
import json, os, io, pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build # type: ignore
from googleapiclient.http import MediaIoBaseDownload # type: ignore

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.readonly"
]

# credenciais
cred_str = os.getenv('GOOGLE_CREDENTIALS')
if not cred_str:
    raise RuntimeError("A variável de ambiente GOOGLE_CREDENTIALS não foi definida.")

keyfile_dict = json.loads(cred_str)
credentials = service_account.Credentials.from_service_account_info(keyfile_dict, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=credentials)

def encontrar_id_pasta(folder_id, nome_arquivo):
    query = f"'{folder_id}' in parents and name = '{nome_arquivo}' and trashed = false"
    resp = drive_service.files().list(q=query, fields="files(id, name)").execute()
    arquivos = resp.get('files', [])
    return arquivos[0]['id'] if arquivos else None

def baixar_drive(file_id, destino):
    try:
        req = drive_service.files().get_media(fileId=file_id)
        fh = io.FileIO(destino, 'wb')
        downloader = MediaIoBaseDownload(fh, req)
        done = False
        while not done:
            status, done = downloader.next_chunk()
        fh.close()
    except Exception as e:
        raise RuntimeError(f"Erro ao baixar o arquivo do Drive: {str(e)}")

def FormatarValor(valor_str):
    try:
        return float(valor_str) / 100
    except:
        return None

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
    pasta_id = os.getenv("DRIVE_FOLDER_ID", "11XYVzfUxrBkGEvgQE6ZVkKaOntfFHfvh")
    ticker_busca = request.json.get("ticker", "").strip().upper()

    file_id = encontrar_id_pasta(pasta_id, "dados.txt")
    if not file_id:
        return jsonify({"status": "erro", "msg": "dados.txt não encontrado"}), 404

    destino = '/tmp/dados.txt'
    try:
        baixar_drive(file_id, destino)
    except Exception as e:
        return jsonify({"status": "erro", "msg": str(e)}), 500

    dados = []
    try:
        with open(destino, 'r', encoding='utf-8') as f:
            next(f)  # pula header
            for line in f:
                ticker = line[12:17].strip()
                if ticker == ticker_busca:
                    d = line[2:10]
                    dados.append({
                        'Data': f"{d[6:8]}/{d[4:6]}/{d[0:4]}",
                        'Tick.': ticker,
                        'Abert.': FormatarValor(line[56:69]),
                        'Max.': FormatarValor(line[69:82]),
                        'Min.': FormatarValor(line[82:95]),
                        'Fecham.': FormatarValor(line[108:121]),
                        'Volume': int(line[152:170].lstrip('0') or '0')
                    })
    except Exception as e:
        return jsonify({"status": "erro", "msg": f"Erro ao processar o arquivo: {str(e)}"}), 500

    if not dados:
        return jsonify({"status": "ok", "linhas": 0, "msg": "Nenhum dado encontrado para o ticker."})

    df_filtrado = pd.DataFrame(dados)

    try:
        gs = gspread.authorize(credentials)
        plan = gs.open("Análise de investimentos").worksheet("ETL")
        plan.clear()
        set_with_dataframe(plan, df_filtrado)
    except Exception as e:
        return jsonify({"status": "erro", "msg": f"Erro ao atualizar planilha: {str(e)}"}), 500

    return jsonify({"status": "ok", "linhas": len(df_filtrado)})


if __name__ == '__main__':
    app.run(port=5000, debug=True)
