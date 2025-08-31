import multiprocessing
import time
import json
import os

def log_message(source, log_type, payload):
    """Função helper para padronizar e imprimir logs em JSON."""
    message = {
        "source": source,
        "type": log_type,
        "payload": payload
    }
    print(json.dumps(message), flush=True)

def processo_conversador(shared_data, turn_flag, lock, my_id):
    """
    Função executada por ambos os processos. Eles esperam pelo seu turno
    para ler o valor, escrever uma resposta e passar a vez.
    """
    pid = os.getpid()
    other_id = 1 - my_id  # O ID do outro processo (0 -> 1, 1 -> 0)
    source = f"PROCESSO {my_id + 1} PID: {pid}"
    log_message(source, "status", {"step": "init", "message": "Processo iniciado."})

    # O Processo 1 (id=0) começa a conversa
    if my_id == 0:
        time.sleep(1) # Espera o processo 2 iniciar e começar a escutar
        try:
            lock.acquire()
            log_message(source, "log", {"step": "first_write", "message": "A iniciar a conversa."})
            shared_data.value = 100
            log_message(source, "log", {
                "step": "data_written", "message": "Escreveu o valor inicial.",
                "data": shared_data.value, "size_bytes": shared_data.value.bit_length() // 8 + 1
            })
        finally:
            log_message(source, "log", {"step": "pass_turn", "message": f"A passar a vez para o Processo {other_id + 1}."})
            turn_flag.value = other_id
            lock.release()

    # Loop principal da conversa
    for _ in range(5):
        # Espera ocupada (busy-waiting) pelo turno. Numa aplicação real, usaria-se um Condicionador.
        while turn_flag.value != my_id:
            time.sleep(0.05)
        
        log_message(source, "log", {"step": "its_my_turn", "message": "É a minha vez de comunicar."})

        try:
            lock.acquire()
            # Lê o valor que o outro processo deixou
            current_value = shared_data.value
            log_message(source, "log", {
                "step": "data_read", "message": "Leu o valor da memória.",
                "data": current_value
            })

            # Escreve uma resposta (ex: incrementa o valor)
            new_value = current_value + 1
            shared_data.value = new_value
            log_message(source, "log", {
                "step": "data_written", "message": "Escreveu a resposta.",
                "data": new_value, "size_bytes": new_value.bit_length() // 8 + 1
            })
        finally:
            # Passa a vez para o outro processo
            log_message(source, "log", {"step": "pass_turn", "message": f"A passar a vez para o Processo {other_id + 1}."})
            turn_flag.value = other_id
            lock.release()

    log_message(source, "status", {"step": "finish", "message": "Conversa finalizada."})


def run_shared_memory():
    """Função principal que orquestra a criação da memória e dos processos."""
    shared_data = multiprocessing.Value('i', 0)   # O dado a ser trocado
    turn_flag = multiprocessing.Value('i', 0)     # 0 = vez do Proc 1, 1 = vez do Proc 2
    lock = multiprocessing.Lock()
    
    # Cria dois processos que executam a mesma função, mas com IDs diferentes
    p1 = multiprocessing.Process(target=processo_conversador, args=(shared_data, turn_flag, lock, 0))
    p2 = multiprocessing.Process(target=processo_conversador, args=(shared_data, turn_flag, lock, 1))

    p1.start()
    p2.start()

    p1.join()
    p2.join()

if __name__ == "__main__":
    run_shared_memory()

