# -----------------------------------------------------------------------------
# ARQUIVO: main_gui.py
# DESCRIÇÃO: Interface gráfica principal para selecionar e visualizar os
#            métodos de Comunicação entre Processos (IPC).
# -----------------------------------------------------------------------------

import tkinter as tk  # Importa a biblioteca Tkinter para criar a interface gráfica e a renomeia para 'tk'.
from tkinter import scrolledtext, ttk, messagebox  # Importa componentes específicos do Tkinter.
import subprocess  # Importa a biblioteca para executar processos externos (os scripts de backend).
import json  # Importa a biblioteca para trabalhar com dados no formato JSON.
import threading  # Importa a biblioteca para executar tarefas em paralelo (evitar que a GUI trave).
import queue  # Importa uma estrutura de fila segura para comunicação entre threads.
import sys  # Importa a biblioteca do sistema, usada aqui para encontrar o executável do Python.


# Define a classe principal da aplicação.
class App:
    # Dicionário de configuração para cada método de IPC.
    IPC_CONFIG = {
        # Mapeia o nome do backend para os rótulos que aparecerão na tela.
        "pipes": {"labels": ["Processo Pai", "Processo Filho"]},
        "sockets": {"labels": ["Servidor", "Cliente"]},
        "shared_memory": {"labels": ["Processo Escritor", "Processo Leitor"]}
    }

    # Método construtor, que é executado quando a classe é criada.
    def __init__(self, root):
        self.root = root  # Armazena a janela principal (root) na variável da classe.
        self.root.title("Visualizador de IPC Unificado")  # Define o título da janela.
        self.root.geometry("950x650")  # Define o tamanho inicial da janela.
        self.stopping = False
        self.process = None  # Variável para armazenar o processo de backend em execução (começa como nulo).
        self.log_queue = queue.Queue()  # Cria uma fila para receber as mensagens de log do backend.

        # Cria uma variável especial do Tkinter para armazenar qual método de IPC foi escolhido.
        self.ipc_method_var = tk.StringVar(value="pipes")  # O valor inicial é "pipes".

        self._create_widgets()  # Chama o método que cria todos os botões, caixas de texto, etc.

        # Agenda a função 'process_log_queue' para ser executada a cada 100ms para verificar novos logs.
        self.root.after(100, self.process_log_queue)
        # Define uma função a ser chamada quando o usuário clica no 'X' para fechar a janela.
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.is_terminating_manually = False  # Flag para indicar encerramento manual

    # Método para criar os componentes visuais (widgets) da interface.
    def _create_widgets(self):
        """Cria e organiza todos os widgets na janela."""

        # --- Frame Superior: Controles ---
        # Cria um contêiner (frame) para os controles de configuração.
        controls_frame = ttk.LabelFrame(self.root, text="Configuração", padding=(10, 10))
        # Posiciona o frame na janela, com algum espaçamento.
        controls_frame.pack(padx=10, pady=10, fill=tk.X)

        # 1. Seleção do Método IPC
        # Cria um sub-frame para os botões de rádio (seleção de IPC).
        ipc_select_frame = ttk.Frame(controls_frame)
        # Posiciona o sub-frame dentro do frame de controles.
        ipc_select_frame.pack(fill=tk.X, pady=(0, 10))
        # Cria um rótulo de texto "Método IPC:".
        ttk.Label(ipc_select_frame, text="Método IPC:").pack(side=tk.LEFT, padx=(0, 10))

        # Itera sobre as chaves do nosso dicionário de configuração (pipes, sockets, etc.).
        for method in self.IPC_CONFIG.keys():
            # Para cada método, cria um botão de rádio.
            rb = ttk.Radiobutton(
                ipc_select_frame,  # Onde o botão será inserido.
                text=method.replace("_", " ").title(),  # Texto do botão (ex: "shared_memory" vira "Shared Memory").
                variable=self.ipc_method_var,  # Associa o botão à nossa variável de controle.
                value=method  # O valor que a variável terá quando este botão for selecionado.
            )
            # Posiciona o botão de rádio à esquerda do anterior.
            rb.pack(side=tk.LEFT, padx=5)

        # 2. Caixa de Texto para a Mensagem
        # Cria um frame para a entrada de mensagem.
        message_frame = ttk.Frame(controls_frame)
        # Posiciona o frame na tela.
        message_frame.pack(fill=tk.X, pady=(0, 10))
        # Cria o rótulo "Mensagem a ser enviada:".
        ttk.Label(message_frame, text="Mensagem a ser enviada:").pack(side=tk.LEFT, padx=(0, 10))
        # Cria o campo de entrada de texto.
        self.message_entry = ttk.Entry(message_frame, width=60)
        # Posiciona o campo de entrada, fazendo-o se expandir para preencher o espaço.
        self.message_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        # Insere um texto padrão no campo de entrada.
        self.message_entry.insert(0, "Olá, mundo do IPC!")

        # 3. Botões de Ação
        # Cria um frame para os botões de ação.
        button_frame = ttk.Frame(controls_frame)
        # Posiciona o frame na tela.
        button_frame.pack(fill=tk.X)
        # Cria o botão "Iniciar Comunicação" e associa ao método 'start_process'.
        self.start_button = ttk.Button(button_frame, text="Iniciar Comunicação", command=self.start_process)
        # Posiciona o botão à esquerda.
        self.start_button.pack(side=tk.LEFT, padx=5)
        # Cria o botão "Parar" e associa ao método 'stop_process', começando desabilitado.
        self.stop_button = ttk.Button(button_frame, text="Parar", command=self.stop_process, state=tk.DISABLED)
        # Posiciona o botão à esquerda do anterior.
        self.stop_button.pack(side=tk.LEFT, padx=5)

        # --- Frame Inferior: Logs ---
        # Cria um frame para a área de logs.
        log_frame = ttk.Frame(self.root, padding=(10, 10))
        # Posiciona o frame, fazendo-o ocupar todo o espaço restante.
        log_frame.pack(pady=10, padx=10, expand=True, fill=tk.BOTH)
        # Configura as colunas do grid para terem o mesmo peso (se expandirem igualmente).
        log_frame.grid_columnconfigure(0, weight=1)
        log_frame.grid_columnconfigure(1, weight=1)
        # Configura a linha do grid para se expandir verticalmente.
        log_frame.grid_rowconfigure(1, weight=1)

        # Cria o rótulo para a primeira área de log.
        self.log_label_1 = ttk.Label(log_frame, text="Processo 1", font=("Helvetica", 12, "bold"))
        # Posiciona o rótulo na primeira linha e primeira coluna do grid.
        self.log_label_1.grid(row=0, column=0, pady=(0, 5))
        # Cria o rótulo para a segunda área de log.
        self.log_label_2 = ttk.Label(log_frame, text="Processo 2", font=("Helvetica", 12, "bold"))
        # Posiciona o rótulo na primeira linha e segunda coluna do grid.
        self.log_label_2.grid(row=0, column=1, pady=(0, 5))

        # Cria a primeira caixa de texto com barra de rolagem para os logs.
        self.log_area_1 = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, width=45, height=20)
        # Posiciona a caixa de texto para ocupar todo o espaço da célula do grid.
        self.log_area_1.grid(row=1, column=0, sticky="nsew", padx=(0, 5))
        # Cria a segunda caixa de texto com barra de rolagem.
        self.log_area_2 = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, width=45, height=20)
        # Posiciona a segunda caixa de texto na célula ao lado.
        self.log_area_2.grid(row=1, column=1, sticky="nsew", padx=(5, 0))

    # Método chamado quando o botão "Iniciar" é clicado.
    def start_process(self):
        """Inicia o processo backend com base nas seleções do usuário."""
        self.stopping = False

        # Limpa o conteúdo das duas áreas de log.
        self.log_area_1.delete('1.0', tk.END)
        self.log_area_2.delete('1.0', tk.END)

        # Obtém o método de IPC selecionado (ex: "pipes").
        ipc_method = self.ipc_method_var.get()
        # Obtém o texto digitado na caixa de mensagem.
        message_to_send = self.message_entry.get()

        # Verifica se a mensagem não está vazia.
        if not message_to_send.strip():
            # Se estiver vazia, mostra uma mensagem de erro.
            messagebox.showerror("Erro", "A mensagem não pode estar vazia.")
            # E para a execução do método.
            return

        # Busca os rótulos corretos no dicionário de configuração (ex: ["Processo Pai", "Processo Filho"]).
        labels = self.IPC_CONFIG[ipc_method]["labels"]
        # Atualiza o texto do primeiro rótulo de log.
        self.log_label_1.config(text=labels[0])
        # Atualiza o texto do segundo rótulo de log.
        self.log_label_2.config(text=labels[1])

        # Monta o comando que será executado no terminal.
        # Ex: ["python", "-m", "backend.pipes.logic", "minha mensagem"]
        command = [sys.executable, "-m", f"backend.{ipc_method}.logic", message_to_send]

        # Inicia a execução do comando em um novo processo.
        self.process = subprocess.Popen(
            command,  # O comando a ser executado.
            stdout=subprocess.PIPE,  # Redireciona a saída padrão do processo para que possamos lê-la.
            stderr=subprocess.PIPE,  # Redireciona a saída de erro também.
            text=True,  # Lê a saída como texto (string).
            encoding='utf-8'  # Define a codificação do texto como UTF-8.
        )

        # Cria e inicia uma nova thread para ler a saída do processo sem travar a GUI.
        threading.Thread(target=self.read_output, args=(self.process.stdout,), daemon=True).start()
        # Cria e inicia outra thread para ler a saída de erro.
        threading.Thread(target=self.read_output, args=(self.process.stderr,), daemon=True).start()

        # Desabilita o botão "Iniciar" para evitar múltiplos cliques.
        self.start_button.config(state=tk.DISABLED)
        # Habilita o botão "Parar".
        self.stop_button.config(state=tk.NORMAL)

    # Método chamado quando o botão "Parar" é clicado.
    def stop_process(self):
        """Para o processo backend em execução."""
        self.stopping = True
        # Verifica se existe um processo e se ele ainda está rodando.
        if self.process and self.process.poll() is None:
            # Envia um sinal para o processo terminar de forma "amigável".
            self.process.terminate()
            # Adiciona uma mensagem na área de log informando que o processo foi parado.
            log_msg = {"source": "App", "payload": {"message": "Processo finalizado pelo usuário."}}
            # Coloca a mensagem na fila de logs.
            self.log_queue.put(json.dumps(log_msg) + '\n')

        # Habilita o botão "Iniciar" novamente.
        self.start_button.config(state=tk.NORMAL)
        # Desabilita o botão "Parar".
        self.stop_button.config(state=tk.DISABLED)

    # Método executado pelas threads para ler a saída do processo de backend.
    def read_output(self, pipe):
        """Lê a saída (stdout/stderr) do processo linha por linha e a coloca na fila."""
        # Loop que lê cada linha da saída do processo.
        for line in iter(pipe.readline, ''):
            # Se a linha não estiver vazia.
            if line:
                # Coloca a linha na fila para ser processada pela thread principal da GUI.
                self.log_queue.put(line)
        # Fecha o canal de comunicação quando a leitura terminar.
        pipe.close()

    # Método que é executado repetidamente para exibir os logs na tela.
    def process_log_queue(self):
        """Processa as mensagens da fila e as exibe nas áreas de log corretas."""
        # Tenta executar o código abaixo.
        try:
            # Loop infinito para esvaziar a fila de logs.
            while True:
                # Pega um item da fila sem bloquear. Se a fila estiver vazia, gera um erro 'queue.Empty'.
                line = self.log_queue.get_nowait()
                # Tenta decodificar a linha como um JSON.
                try:
                    # Converte a string JSON em um objeto Python (dicionário).
                    log_entry = json.loads(line)
                    # Pega a origem da mensagem (ex: "SERVIDOR").
                    source = log_entry.get('source', 'Desconhecido')
                    # Pega o conteúdo da mensagem.
                    payload = log_entry.get('payload', {})
                    # Pega a mensagem específica de dentro do payload.
                    message = payload.get('message', '')
                    # Formata o log para exibição.
                    formatted_log = f"-> {message}\n"

                    # Pega o método de IPC atualmente selecionado.
                    ipc_method = self.ipc_method_var.get()
                    # Pega os rótulos correspondentes a esse método.
                    labels = self.IPC_CONFIG[ipc_method]["labels"]

                    # Verifica se a origem do log corresponde ao primeiro rótulo (ex: "SERVIDOR").
                    if labels[0].upper() in source.upper():
                        # Se sim, insere o log na primeira área de texto.
                        self.log_area_1.insert(tk.END, formatted_log)
                        # Rola a área de texto para mostrar a última mensagem.
                        self.log_area_1.see(tk.END)
                    # Senão, verifica se corresponde ao segundo rótulo (ex: "CLIENTE").
                    elif labels[1].upper() in source.upper():
                        # Se sim, insere o log na segunda área de texto.
                        self.log_area_2.insert(tk.END, formatted_log)
                        # Rola a área de texto para mostrar a última mensagem.
                        self.log_area_2.see(tk.END)
                    # Se não corresponder a nenhum dos dois.
                    else:
                        # Insere na primeira área como um log geral do sistema.
                        self.log_area_1.insert(tk.END, f"[{source.upper()}]: {message}\n")
                        self.log_area_1.see(tk.END)

                # Se a linha não for um JSON válido, um erro ocorrerá.
                except json.JSONDecodeError:
                    # Neste caso, apenas exibe a linha como texto bruto na primeira área.
                    if not self.stopping:
                        self.log_area_1.insert(tk.END, f"[LOG BRUTO]: {line}")
        # Se a fila estiver vazia, o 'get_nowait' gera este erro.
        except queue.Empty:
            pass  # Não faz nada, o que é o comportamento esperado.

        # Verifica se o processo de backend já terminou por conta própria.
        if self.process and self.process.poll() is not None:
            # Se terminou, reabilita o botão "Iniciar".
            self.start_button.config(state=tk.NORMAL)
            # E desabilita o botão "Parar".
            self.stop_button.config(state=tk.DISABLED)
            # Define a variável do processo como nula, pois ele não existe mais.
            self.process = None

        # Agenda a próxima verificação da fila para daqui a 100 milissegundos.
        self.root.after(100, self.process_log_queue)

    # Método chamado quando a janela é fechada.
    def on_close(self):
        """Função chamada ao fechar a janela."""
        # Para qualquer processo de backend que esteja em execução.
        self.stop_process()
        # Fecha e destrói a janela da aplicação.
        self.root.destroy()


# Ponto de entrada do script: este código só executa se o arquivo for o principal.
if __name__ == "__main__":
    root = tk.Tk()  # Cria a janela principal da aplicação.
    app = App(root)  # Cria uma instância da nossa classe App.
    root.mainloop()  # Inicia o loop de eventos do Tkinter, que mantém a janela aberta.
