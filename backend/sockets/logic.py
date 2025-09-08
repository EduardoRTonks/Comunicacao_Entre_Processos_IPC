# -----------------------------------------------------------------------------
# ARQUIVO: backend/sockets/logic.py
# DESCRIÇÃO: Lógica de comunicação cliente-servidor usando Sockets.
# -----------------------------------------------------------------------------

import multiprocessing as mp  # Importa a biblioteca para criar e gerenciar processos.
import socket  # Importa a biblioteca de Sockets para comunicação em rede.
import time  # Importa a biblioteca de tempo para adicionar pequenas pausas.
import os  # Importa a biblioteca do sistema para obter o ID do processo (PID).
import json  # Importa a biblioteca para formatar os logs em JSON.
import sys  # Importa a biblioteca para ler argumentos da linha de comando.

# Define o endereço do host (localhost) e a porta para a comunicação.
HOST = '127.0.0.1'  # Endereço de loopback, significa "este computador".
PORT = 65432       # Porta a ser usada. Acima de 1023 para não precisar de privilégios.

# Função para criar e imprimir logs no formato JSON esperado pela GUI.
def log_message(source, message):
    # Cria um dicionário (estrutura de dados) para o log.
    log_entry = {
        "source": source,  # A origem da mensagem (ex: "SERVIDOR").
        "payload": {"message": message}  # O conteúdo da mensagem.
    }
    # Converte o dicionário para uma string JSON e a imprime na saída padrão.
    print(json.dumps(log_entry), flush=True)

# Função que define o comportamento do processo Servidor.
def processo_servidor():
    # Obtém o ID deste processo.
    pid = os.getpid()
    # Define um nome de origem para os logs.
    source_id = f"SERVIDOR (PID: {pid})"

    # Cria um objeto socket. AF_INET é para IPv4, SOCK_STREAM é para TCP.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Associa o socket ao endereço (host) e à porta definidos.
        s.bind((HOST, PORT))
        # Coloca o socket em modo de escuta, aguardando conexões.
        s.listen()
        # Loga que o servidor está pronto e escutando.
        log_message(source_id, f"PID: {pid} -> Escutando por conexões em {HOST}:{PORT}")

        # Aceita uma conexão. A execução fica bloqueada aqui até um cliente se conectar.
        # 'conn' é o novo socket para comunicar com o cliente, 'addr' é o endereço do cliente.
        conn, addr = s.accept()
        # Usa um bloco 'with' para garantir que a conexão 'conn' seja fechada no final.
        with conn:
            # Loga que uma conexão foi aceita.
            log_message(source_id, f"PID: {pid} -> Conexão aceita de {addr}")
            
            # Recebe dados do cliente (até 1024 bytes). Fica bloqueado até receber algo.
            data = conn.recv(1024)
            # Decodifica os bytes recebidos para uma string.
            mensagem_recebida = data.decode('utf-8')
            # Loga a mensagem que foi recebida.
            log_message(source_id, f"PID: {pid} -> Recebeu: '{mensagem_recebida}'")

            # Prepara uma resposta de "eco".
            resposta = f"Eco do servidor: {mensagem_recebida}"
            # Loga a resposta que será enviada.
            log_message(source_id, f"Enviando resposta: '{resposta}'")
            # Envia a resposta de volta para o cliente, codificando a string para bytes.
            conn.sendall(resposta.encode('utf-8'))
            
    # Loga que o servidor está encerrando.
    log_message(source_id, f"PID: {pid} -> Encerrado.")

# Função que define o comportamento do processo Cliente.
def processo_cliente(msg):
    # Obtém o ID deste processo.
    pid = os.getpid()
    # Define um nome de origem para os logs.
    source_id = f"CLIENTE (PID: {pid})"
    
    # Loga que o cliente foi iniciado.
    log_message(source_id, f"PID: {pid} -> Iniciado.")
    # Adiciona uma pausa de 1 segundo para dar tempo ao servidor de iniciar primeiro.
    time.sleep(1)

    # Cria um objeto socket, igual ao do servidor.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Loga que está tentando se conectar ao servidor.
        log_message(source_id, f"PID: {pid} -> Conectando a {HOST}:{PORT}...")
        # Tenta se conectar ao servidor no endereço e porta especificados.
        s.connect((HOST, PORT))
        # Loga que a conexão foi bem-sucedida.
        log_message(source_id, f"PID: {pid} -> Conexão estabelecida.")

        # Loga a mensagem que será enviada.
        log_message(source_id, f"PID: {pid} -> Enviando mensagem: '{msg}'")
        # Envia a mensagem (recebida da GUI), codificando-a para bytes.
        s.sendall(msg.encode('utf-8'))

        # Espera pela resposta do servidor (até 1024 bytes).
        resposta_data = s.recv(1024)
        # Loga a resposta recebida, decodificando-a de volta para string.
        log_message(source_id, f"PID: {pid} -> Resposta recebida: '{resposta_data.decode('utf-8')}'")
        
    # Loga que o cliente está encerrando.
    log_message(source_id, f"PID: {pid} -> Encerrado.")


# Ponto de entrada do script.
if __name__ == "__main__":
    # Obtém a mensagem da GUI a partir dos argumentos da linha de comando.
    mensagem_da_gui = sys.argv[1]

    # Cria um processo para executar a função 'processo_servidor'.
    servidor = mp.Process(target=processo_servidor)
    # Cria um processo para executar a função 'processo_cliente', passando a mensagem.
    cliente = mp.Process(target=processo_cliente, args=(mensagem_da_gui,))

    # Inicia a execução do processo servidor.
    servidor.start()
    # Inicia a execução do processo cliente.
    cliente.start()

    # O processo principal espera que o processo servidor termine.
    servidor.join()
    # O processo principal espera que o processo cliente termine.
    cliente.join()
    
    # Loga o fim da demonstração.
    log_message("MAIN", "Demonstração com Sockets finalizada.")