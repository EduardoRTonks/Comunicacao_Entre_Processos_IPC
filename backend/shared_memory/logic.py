import multiprocessing as mp  # Importa a biblioteca para criar e gerenciar processos.
import json  # Importa a biblioteca para formatar os logs em JSON.
import sys  # Importa a biblioteca para ler argumentos da linha de comando.
import os  # Importa a biblioteca para obter o ID do processo (PID).
import time  # Importa a biblioteca de tempo para adicionar pequenas pausas.

# Função para criar e imprimir logs no formato JSON esperado pela GUI.
def log_message(source, message):
    # Cria um dicionário (estrutura de dados) para o log.
    log_entry = {
        "source": source,  # A origem da mensagem (ex: "PROCESSO ESCRITOR").
        "payload": {"message": message}  # O conteúdo da mensagem.
    }
    # Converte o dicionário para uma string JSON e a imprime na saída padrão.
    print(json.dumps(log_entry), flush=True)

# Função que define o comportamento do processo que escreve na memória.
def processo_escritor(shared_mem, sync_event, msg):
    # Obtém o ID deste processo.
    pid = os.getpid()
    # Define um nome de origem para os logs deste processo.
    source_id = f"PROCESSO ESCRITOR (PID: {pid})"
    
    # Loga que o processo foi iniciado.
    log_message(source_id, "Iniciado.")
    # Adiciona uma pausa para visualização.
    time.sleep(1)

    # Codifica a mensagem (string) para bytes, no formato utf-8.
    msg_bytes = msg.encode('utf-8')

    # Verifica se a mensagem codificada cabe no buffer de memória compartilhada.
    buffer_size = len(shared_mem)
    if len(msg_bytes) >= buffer_size:
        log_message(source_id,
                    f"ERRO: A mensagem ({len(msg_bytes)} bytes) excede o tamanho do buffer ({buffer_size} bytes).")
        log_message(source_id, "Processo encerrado devido a erro.")

        # Ativa o evento mesmo em caso de erro para que o processo leitor não fique esperando para sempre.
        sync_event.set()
        return  # Encerra a função e o processo de forma limpa, evitando o crash.

    log_message(source_id, f"PID: {pid} -> Escrevendo '{msg}' na memória compartilhada.")

    # Escreve os bytes da mensagem na memória compartilhada.
    shared_mem[:len(msg_bytes)] = msg_bytes

    time.sleep(1)
    log_message(source_id, f"PID: {pid} -> Escrita finalizada. Sinalizando o processo leitor.")
    sync_event.set()


# Função que define o comportamento do processo que lê da memória.
def processo_leitor(shared_mem, sync_event):
    # Obtém o ID deste processo.
    pid = os.getpid()
    # Define um nome de origem para os logs deste processo.
    source_id = f"PROCESSO LEITOR (PID: {pid})"

    # Loga que o processo iniciou e está esperando pelo sinal.
    log_message(source_id, f"PID: {pid} -> Iniciado. Aguardando sinal do escritor...")
    # Fica bloqueado aqui até que o evento 'sync_event' seja ativado pelo escritor.
    sync_event.wait()

    # Lê os bytes da memória compartilhada. Se a mensagem for vazia (caso de erro no escritor), não vai ler nada.
    mensagem_lida_bytes = shared_mem[:].rstrip(b'\x00')

    # Só processa se alguma mensagem foi de fato escrita.
    if mensagem_lida_bytes:
        log_message(source_id, f"PID: {pid} -> Sinal recebido! Lendo da memória compartilhada.")
        mensagem_lida = mensagem_lida_bytes.decode('utf-8')
        log_message(source_id, f"PID: {pid} -> Leu da memória: '{mensagem_lida}'")
    else:
        # O escritor sinalizou, mas não escreveu nada (provavelmente por causa do erro de tamanho).
        log_message(source_id, "Sinal recebido, mas sem mensagem para ler. Provavelmente o escritor encontrou um erro.")

    log_message(source_id, f"PID: {pid} -> Encerrando.")


# Ponto de entrada do script.
if __name__ == "__main__":
    # Obtém a mensagem da GUI a partir dos argumentos da linha de comando.
    mensagem_da_gui = sys.argv[1]

    # Cria um 'Evento', um objeto de sincronização simples. Começa "desativado".
    evento = mp.Event()
    # Cria um 'Array' de memória compartilhada de 1024 bytes.
    memoria_compartilhada = mp.Array('c', 1024)

    # Cria o processo escritor, passando a memória, o evento e a mensagem.
    p_escritor = mp.Process(target=processo_escritor, args=(memoria_compartilhada, evento, mensagem_da_gui))
    # Cria o processo leitor, passando a memória e o evento.
    p_leitor = mp.Process(target=processo_leitor, args=(memoria_compartilhada, evento))

    # Inicia a execução dos dois processos.
    p_escritor.start()
    p_leitor.start()

    # O processo principal espera até que ambos os processos filhos terminem.
    p_escritor.join()
    p_leitor.join()

    # Loga o fim da demonstração (este log virá de uma fonte "Desconhecida" na GUI, o que é normal).
    log_message("MAIN", "Demonstração com Memória Compartilhada finalizada.")