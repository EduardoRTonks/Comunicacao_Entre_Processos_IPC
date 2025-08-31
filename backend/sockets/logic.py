import multiprocessing
import socket
import time
import os
import json

def log_message(source, log_type, step, message, data=None):
    """Função auxiliar para padronizar a criação e impressão de logs em JSON."""
    payload = {
        "step": step,
        "message": message
    }
    if data is not None:
        payload["data"] = data
        payload["size_bytes"] = len(str(data).encode('utf-8'))

    log_entry = {
        "source": source,
        "type": log_type,
        "payload": payload
    }
    print(json.dumps(log_entry), flush=True)

def processo_servidor(host, port):
    """
    Lógica do processo Servidor. Ele espera uma conexão, recebe uma mensagem e envia uma resposta.
    """
    pid = os.getpid()
    source_id = f"SERVIDOR PID: {pid}"
    
    # Cria o socket TCP/IP
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        log_message(source_id, "status", "listening", f"Servidor escutando em {host}:{port}")
        
        # Aceita a conexão do cliente. A chamada é bloqueante.
        conn, addr = s.accept()
        with conn:
            log_message(source_id, "status", "connection_accepted", f"Conexão aceita de {addr}")
            
            while True:
                log_message(source_id, "log", "blocking_on_recv", "Aguardando (bloqueado) para receber dados...")
                data = conn.recv(1024) # Recebe até 1024 bytes
                
                if not data:
                    log_message(source_id, "status", "connection_closed_by_client", "Cliente fechou a conexão.")
                    break
                
                mensagem_recebida = data.decode('utf-8')
                log_message(source_id, "log", "data_received", "Dados recebidos do cliente.", data=mensagem_recebida)
                
                # Envia uma resposta
                resposta = f"ECO para '{mensagem_recebida}'"
                log_message(source_id, "log", "sending_data", "Enviando resposta para o cliente.", data=resposta)
                conn.sendall(resposta.encode('utf-8'))

    log_message(source_id, "status", "terminated", "Servidor encerrado.")

def processo_cliente(host, port):
    """
    Lógica do processo Cliente. Ele se conecta, envia uma série de mensagens e espera respostas.
    """
    pid = os.getpid()
    source_id = f"CLIENTE PID: {pid}"
    log_message(source_id, "status", "init", "Processo cliente iniciado.")
    
    time.sleep(1) # Dá um tempo para o servidor iniciar

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            log_message(source_id, "status", "connecting", f"Conectando ao servidor em {host}:{port}...")
            s.connect((host, port))
            log_message(source_id, "status", "connected", "Conectado com sucesso.")

            mensagens = ["Olá, servidor!", "Teste de Sockets", "FIM"]
            for msg in mensagens:
                time.sleep(1.5)
                log_message(source_id, "log", "sending_data", "Enviando dados para o servidor.", data=msg)
                s.sendall(msg.encode('utf-8'))

                log_message(source_id, "log", "blocking_on_recv", "Aguardando resposta do servidor...")
                resposta_data = s.recv(1024)
                log_message(source_id, "log", "data_received", "Resposta recebida.", data=resposta_data.decode('utf-8'))

    except ConnectionRefusedError:
        log_message(source_id, "error", "connection_refused", "Conexão recusada. O servidor está rodando?")
    finally:
        log_message(source_id, "status", "terminated", "Cliente encerrado.")

def run_sockets():
    """Orquestra a criação dos processos de servidor e cliente."""
    HOST = '127.0.0.1'  # Endereço de loopback (localhost)
    PORT = 65432        # Porta para escutar

    servidor = multiprocessing.Process(target=processo_servidor, args=(HOST, PORT))
    cliente = multiprocessing.Process(target=processo_cliente, args=(HOST, PORT))

    servidor.start()
    cliente.start()

    servidor.join()
    cliente.join()

if __name__ == "__main__":
    run_sockets()
