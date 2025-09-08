# -----------------------------------------------------------------------------
# ARQUIVO: backend/pipes/logic.py
# DESCRIÇÃO: Lógica de comunicação entre dois processos usando Pipes.
# -----------------------------------------------------------------------------

import multiprocessing as mp  # Importa a biblioteca para criar e gerenciar processos.
import json  # Importa a biblioteca para formatar os logs em JSON.
import sys  # Importa a biblioteca do sistema para ler argumentos da linha de comando.
import os  # Importa a biblioteca do sistema para obter o ID do processo (PID).
import time  # Importa a biblioteca de tempo para adicionar pequenas pausas.

# Função para criar e imprimir logs no formato JSON esperado pela GUI.
def log_message(source, message):
    # Cria um dicionário (estrutura de dados) para o log.
    pid = os.getpid()

    log_entry = {
        "source": source,  # A origem da mensagem (ex: "PROCESSO PAI").
        "payload": {"message": message}  # O conteúdo da mensagem.
    }
    # Converte o dicionário para uma string JSON e a imprime na saída padrão.
    # 'flush=True' força a impressão imediata, sem esperar o buffer encher.
    print(json.dumps(log_entry), flush=True)

# Função que define o comportamento do processo filho.
def processo_filho(conn):
    # Obtém o ID deste processo.
    pid = os.getpid()
    # Define um nome de origem para os logs deste processo.
    source_id = f"PROCESSO FILHO (PID: {pid})"
    
    # Loga que o processo foi iniciado.
    log_message(source_id, f"PID: {pid} -> Iniciado e aguardando mensagem do pai.")

    # Fica bloqueado aqui até receber uma mensagem do pai através do pipe 'conn'.
    mensagem = conn.recv()
    # Loga a mensagem que foi recebida.
    log_message(source_id, f"PID: {pid} -> Recebeu: '{mensagem}'")
    
    # Adiciona uma pequena pausa para visualização.
    time.sleep(1)
    
    # Prepara uma resposta para o pai.
    resposta = f"Obrigado pela mensagem, pai!"
    # Loga que está enviando a resposta.
    log_message(source_id, f"PID: {pid} -> Enviando resposta: '{resposta}'")
    # Envia a resposta para o pai através do pipe.
    conn.send(resposta)
    
    # Fecha sua ponta da conexão do pipe.
    conn.close()
    # Loga que o processo está terminando.
    log_message(source_id, f"PID: {pid} -> Conexão fechada. Encerrando.")

# Ponto de entrada do script.
if __name__ == "__main__":
    # Obtém a mensagem enviada pela GUI a partir dos argumentos da linha de comando.
    # sys.argv[0] é o nome do script, sys.argv[1] é o primeiro argumento.
    mensagem_da_gui = sys.argv[1]
    
    # Obtém o ID do processo principal (que atuará como o pai).
    pid_pai = os.getpid()
    # Define um nome de origem para os logs do processo pai.
    source_id_pai = f"PROCESSO PAI (PID: {pid_pai})"
    
    # Loga o início da operação.
    log_message(source_id_pai, f"PID: {pid_pai} -> Iniciando demonstração com Pipes.")

    # Cria um Pipe. Isso retorna duas pontas de conexão: uma para o pai, outra para o filho.
    conn_pai, conn_filho = mp.Pipe()
    
    # Cria um novo processo que executará a função 'processo_filho'.
    # Passa a ponta do pipe do filho ('conn_filho') como argumento para a função.
    p_filho = mp.Process(target=processo_filho, args=(conn_filho,))
    
    # Inicia a execução do processo filho.
    p_filho.start()
    
    # O processo pai fecha a ponta do pipe do filho, pois não a usará.
    conn_filho.close()
    
    # Adiciona uma pequena pausa para garantir que o filho esteja pronto para receber.
    time.sleep(1)
    
    # Loga a mensagem que será enviada.
    log_message(source_id_pai, f"PID: {pid_pai} -> Enviando mensagem: '{mensagem_da_gui}'")
    # Envia a mensagem da GUI para o filho através da sua ponta do pipe.
    conn_pai.send(mensagem_da_gui)
    
    # Loga que está aguardando a resposta.
    log_message(source_id_pai, f"PID: {pid_pai} -> Aguardando resposta do filho...")
    # Fica bloqueado aqui até receber a resposta do filho.
    resposta_filho = conn_pai.recv()
    # Loga a resposta recebida.
    log_message(source_id_pai, f"PID: {pid_pai} -> Recebeu a resposta: '{resposta_filho}'")

    # Espera até que o processo filho termine sua execução.
    p_filho.join()
    
    # Fecha a ponta do pipe do pai.
    conn_pai.close()
    # Loga o fim da demonstração.
    log_message(source_id_pai, f"PID: {pid_pai} -> Demonstração com Pipes finalizada.")