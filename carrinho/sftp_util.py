import os
import shutil
import paramiko

# Configurações do SFTP
SFTP_HOST = "192.168.88.149"
SFTP_PORT = 22
SFTP_USER = "devser"
SFTP_PASS = "123"
SFTP_DIR = "/destino/"

# Diretório local para arquivos enviados
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENVIADOS_DIR = os.path.join(BASE_DIR, "enviados")
os.makedirs(ENVIADOS_DIR, exist_ok=True)

def enviar_sftp(filepath):
    """Envia um arquivo via SFTP e move para a pasta 'enviados'"""
    filename = os.path.basename(filepath)
    try:
        # Cria o cliente SSH
        transport = paramiko.Transport((SFTP_HOST, SFTP_PORT))
        transport.connect(username=SFTP_USER, password=SFTP_PASS)
        sftp = paramiko.SFTPClient.from_transport(transport)

        # Garante que o diretório remoto existe
        try:
            sftp.chdir(SFTP_DIR)
        except IOError:
            # Caso não exista, cria o diretório remoto
            sftp.mkdir(SFTP_DIR)
            sftp.chdir(SFTP_DIR)

        # Envia o arquivo
        remote_path = os.path.join(SFTP_DIR, filename).replace("\\", "/")
        sftp.put(filepath, remote_path)

        # Fecha conexões
        sftp.close()
        transport.close()

        # Move o arquivo local para a pasta "enviados"
        shutil.move(filepath, os.path.join(ENVIADOS_DIR, filename))
        print(f"[OK] {filename} enviado com sucesso via SFTP e movido para 'enviados'.")

    except Exception as e:
        print(f"[ERRO] Falha ao enviar {filename} via SFTP: {e}")
