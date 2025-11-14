#!/usr/bin/env python3
"""
Script de teste para validar a lógica de conexão FTP
"""
from ftplib import FTP, error_perm
import socket

def test_ftp_connection(host, porta, usuario, senha, diretorio=None):
    """Testa conexão FTP com tratamento de erros"""
    ftp = None
    try:
        print(f"[INFO] Testando conexão FTP...")
        print(f"  Host: {host}")
        print(f"  Porta: {porta}")
        print(f"  Usuário: {usuario}")
        print(f"  Diretório: {diretorio or '/'}")
        
        # Validações
        if not host or not host.strip():
            print("[ERRO] Host FTP não configurado")
            return False
        
        if not usuario or not usuario.strip():
            print("[ERRO] Usuário FTP não configurado")
            return False
        
        # Conectar
        try:
            ftp = FTP()
            print(f"[INFO] Conectando ao servidor {host}:{porta}...")
            ftp.connect(host.strip(), porta, timeout=30)
            print(f"[OK] Conectado ao servidor")
            
            print(f"[INFO] Autenticando como {usuario}...")
            ftp.login(usuario.strip(), senha)
            print(f"[OK] Autenticado com sucesso")
            
        except socket.gaierror as e:
            print(f"[ERRO] Não foi possível resolver o endereço '{host}'")
            print(f"  Detalhes: {str(e)}")
            return False
        except socket.timeout:
            print(f"[ERRO] Tempo esgotado ao conectar ao servidor '{host}'")
            return False
        except error_perm as e:
            print(f"[ERRO] Erro de autenticação: {str(e)}")
            return False
        except Exception as e:
            print(f"[ERRO] Erro ao conectar: {str(e)}")
            return False
        
        # Navegar para diretório
        if diretorio and diretorio.strip():
            try:
                print(f"[INFO] Navegando para diretório '{diretorio}'...")
                ftp.cwd(diretorio.strip())
                print(f"[OK] Diretório acessado")
            except error_perm as e:
                print(f"[ERRO] Diretório '{diretorio}' não encontrado")
                if ftp:
                    ftp.quit()
                return False
        
        # Listar arquivos
        try:
            print(f"[INFO] Listando arquivos no diretório...")
            files = []
            ftp.retrlines('LIST', files.append)
            print(f"[OK] {len(files)} arquivos encontrados")
            for f in files[:5]:  # Mostrar apenas os 5 primeiros
                print(f"  - {f}")
        except Exception as e:
            print(f"[AVISO] Erro ao listar arquivos: {str(e)}")
        
        if ftp:
            ftp.quit()
            print(f"[OK] Conexão encerrada")
        
        return True
        
    except Exception as e:
        print(f"[ERRO] Erro inesperado: {str(e)}")
        if ftp:
            try:
                ftp.quit()
            except:
                pass
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("TESTE DE CONEXÃO FTP")
    print("=" * 60)
    
    # Exemplo de teste
    # Substitua pelos valores reais
    test_ftp_connection(
        host="ftp.exemplo.com.br",
        porta=21,
        usuario="usuario_teste",
        senha="senha_teste",
        diretorio="1"
    )
    
    print("\n" + "=" * 60)
    print("Teste concluído")
    print("=" * 60)
