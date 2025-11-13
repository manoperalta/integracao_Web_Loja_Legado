import os
import shutil
from ftplib import FTP

# Configurações do FTP
FTP_HOST = "45.152.44.100"
FTP_USER = "u609642582.manoperaltaftp"
FTP_PASS = "@Maral123"
FTP_DIR = "/destino/"

# Diretório local para arquivos enviados
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENVIADOS_DIR = os.path.join(BASE_DIR, "enviados")
os.makedirs(ENVIADOS_DIR, exist_ok=True)

def enviar_ftp(filepath):
    """Envia um arquivo para o FTP e move para a pasta 'enviados'"""
    filename = os.path.basename(filepath)
    try:
        with FTP(FTP_HOST) as ftp:
            ftp.login(FTP_USER, FTP_PASS)
            ftp.cwd(FTP_DIR)

            with open(filepath, "rb") as f:
                ftp.storbinary(f"STOR {filename}", f)

        # Após envio, mover para pasta 'enviados'
        shutil.move(filepath, os.path.join(ENVIADOS_DIR, filename))
        print(f"[OK] {filename} enviado com sucesso e movido para 'destino'.")

    except Exception as e:
        print(f"[ERRO] Falha ao enviar {filename} via FTP: {e}")
