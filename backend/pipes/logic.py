import multiprocessing
import time
import os
import json

def log_message(source, log_type, step, message, data=None):
    """
    Função auxiliar para padronizar a criação e impressão de logs em JSON.
    Isso torna o código principal mais limpo.
    """
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
    # flush=True garante que a saída seja enviada imediatamente, essencial para a GUI.
    print(json.dumps(log_entry), flush=True)

def processo_filho(conn):
    """
    Lógica do processo filho. Agora ele recebe e responde às mensagens.
    """
    pid = os.getpid()
    source_id = f"FILHO PID: {pid}"
    log_message(source_id, "status", "init", "Processo iniciado.")

    try:
        # Loop de conversação
        while True:
            log_message(source_id, "log", "blocking_on_recv", "Aguardando (bloqueado) para receber dados do pipe...")
            
            # conn.recv() bloqueia a execução até que algo seja recebido
            mensagem_recebida = conn.recv()
            log_message(source_id, "log", "data_received", f"Dados recebidos do pipe.", data=mensagem_recebida)

            if mensagem_recebida == "FIM":
                log_message(source_id, "status", "end_signal_received", "Sinal de FIM recebido. Encerrando.")
                break
            
            # Prepara e envia uma resposta
            time.sleep(0.5) # Simula algum "processamento"
            resposta = f"PONG para '{mensagem_recebida}'"
            log_message(source_id, "log", "sending_data", f"Enviando resposta para o pipe.", data=resposta)
            conn.send(resposta)

    except EOFError:
        log_message(source_id, "error", "pipe_closed", "O pipe foi fechado inesperadamente pelo processo pai.")
    finally:
        conn.close()
        log_message(source_id, "status", "terminated", "Conexão fechada. Processo filho encerrado.")


def processo_pai(conn, filho_pid):
    """
    Lógica do processo pai. Agora ele envia uma mensagem e espera uma resposta.
    """
    pid = os.getpid()
    source_id = f"PAI PID: {pid}"
    log_message(source_id, "status", "init", f"Processo iniciado. Filho tem o PID: {filho_pid}")

    # Lista de mensagens para iniciar a conversação
    mensagens = ["PING 1", "PING 2", "PING 3"]

    for msg in mensagens:
        time.sleep(1.5) # Pausa para melhor visualização na GUI
        log_message(source_id, "log", "sending_data", f"Enviando mensagem para o processo filho.", data=msg)
        conn.send(msg)

        log_message(source_id, "log", "blocking_on_recv", "Aguardando (bloqueado) para receber resposta do pipe...")
        resposta_recebida = conn.recv()
        log_message(source_id, "log", "data_received", f"Resposta recebida do pipe.", data=resposta_recebida)

    # Envia o sinal de encerramento
    time.sleep(1.5)
    log_message(source_id, "log", "sending_end_signal", "Enviando sinal de FIM para o filho.", data="FIM")
    conn.send("FIM")

    conn.close()
    log_message(source_id, "status", "terminated", "Conexão fechada. Processo pai encerrado.")

def run_pipes():
    """
    Orquestra a criação do Pipe e dos processos.
    """
    # multiprocessing.Pipe() é bidirecional por padrão.
    conn_pai, conn_filho = multiprocessing.Pipe()

    p_filho = multiprocessing.Process(target=processo_filho, args=(conn_filho,))
    
    # Inicia o filho primeiro para que possamos obter seu PID.
    p_filho.start()
    
    p_pai = multiprocessing.Process(target=processo_pai, args=(conn_pai, p_filho.pid))
    p_pai.start()
    
    # Aguarda ambos os processos terminarem
    p_pai.join()
    p_filho.join()

if __name__ == "__main__":
    run_pipes()
