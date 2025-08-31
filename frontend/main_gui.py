import tkinter as tk
from tkinter import scrolledtext, ttk
import subprocess
import json
import threading
import queue

class IPC_Tab(tk.Frame):
    """
    Um frame que representa uma aba para um método de IPC específico.
    Esta classe é reutilizável para Pipes, Sockets, etc.
    """
    def __init__(self, parent, backend_module_name, process_labels):
        super().__init__(parent)
        self.backend_module = backend_module_name
        self.process = None
        self.log_queue = queue.Queue()
        self.process_finished_logged = False

        # Frame de botões
        button_frame = tk.Frame(self)
        button_frame.pack(pady=5)
        self.start_button = tk.Button(button_frame, text=f"Iniciar {backend_module_name.capitalize()}", command=self.start_process)
        self.start_button.pack(side=tk.LEFT, padx=5)
        self.stop_button = tk.Button(button_frame, text="Parar", command=self.stop_process, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        # Frame de logs com 3 colunas
        log_frame = tk.Frame(self)
        log_frame.pack(pady=10, padx=10, expand=True, fill=tk.BOTH)
        log_frame.grid_columnconfigure(0, weight=1)
        log_frame.grid_columnconfigure(1, weight=1) # Coluna central
        log_frame.grid_columnconfigure(2, weight=1)
        log_frame.grid_rowconfigure(1, weight=1)

        # Coluna 1: Processo 1
        ttk.Label(log_frame, text=process_labels[0], font=("Helvetica", 12, "bold")).grid(row=0, column=0, pady=(0,5))
        self.log_area_1 = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, width=40, height=15, bg="#f0f0f0")
        self.log_area_1.grid(row=1, column=0, sticky="nsew", padx=(0, 5))
        self.log_area_1.tag_config('ERROR', foreground='red')

        # Coluna 2: Log de Atividades (Buffer)
        ttk.Label(log_frame, text="Log de Atividades", font=("Helvetica", 12, "bold")).grid(row=0, column=1, pady=(0,5))
        self.log_area_buffer = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, width=40, height=15, bg="#e6e6fa")
        self.log_area_buffer.grid(row=1, column=1, sticky="nsew", padx=5)
        self.log_area_buffer.tag_config('ERROR', foreground='red')

        # Coluna 3: Processo 2
        ttk.Label(log_frame, text=process_labels[1], font=("Helvetica", 12, "bold")).grid(row=0, column=2, pady=(0,5))
        self.log_area_2 = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, width=40, height=15, bg="#f0f0f0")
        self.log_area_2.grid(row=1, column=2, sticky="nsew", padx=(5, 0))
        self.log_area_2.tag_config('ERROR', foreground='red')

        self.process_labels = process_labels
        self.after(100, self.process_log_queue)

    def start_process(self):
        self.log_area_1.delete('1.0', tk.END)
        self.log_area_2.delete('1.0', tk.END)
        self.log_area_buffer.delete('1.0', tk.END) # Limpa o log central
        self.process_finished_logged = False
        
        command = ["python3", "-m", f"backend.{self.backend_module}.logic"]
        
        try:
            self.process = subprocess.Popen(
                command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, bufsize=1, universal_newlines=True, encoding='utf-8'
            )
        except FileNotFoundError:
            self.log_area_1.insert(tk.END, "ERRO: O interpretador 'python3' não foi encontrado.\n", 'ERROR')
            return

        threading.Thread(target=self.read_pipe, args=(self.process.stdout, False), daemon=True).start()
        threading.Thread(target=self.read_pipe, args=(self.process.stderr, True), daemon=True).start()

        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

    def read_pipe(self, pipe, is_error_stream):
        for line in iter(pipe.readline, ''):
            if line:
                self.log_queue.put({"line": line, "is_error": is_error_stream})
        pipe.close()

    def process_log_queue(self):
        try:
            while True:
                item = self.log_queue.get_nowait()
                line = item["line"]
                is_error = item["is_error"]

                target_area = self.log_area_1
                tag = 'ERROR' if is_error else ''
                
                if is_error:
                    formatted_log = f"[ERRO]: {line}"
                    self.log_area_buffer.insert(tk.END, formatted_log, tag)
                else:
                    try:
                        log_entry = json.loads(line)
                        source = log_entry.get('source', 'Desconhecido')
                        payload = log_entry.get('payload', {})
                        
                        if isinstance(payload, dict):
                            step = payload.get('step', 'info')
                            message = payload.get('message', '')
                            
                            detailed_message = message
                            if 'data' in payload:
                                detailed_message += f" (Valor: {payload['data']})"
                            formatted_log = f"[{step.upper()}]: {detailed_message}\n"
                            
                            buffer_log = f"[{source}]: {message}\n"
                        else:
                            formatted_log = f"[INFO]: {payload}\n"
                            buffer_log = formatted_log
                        
                        self.log_area_buffer.insert(tk.END, buffer_log)
                        self.log_area_buffer.see(tk.END)

                        # CORRIGIDO: Lógica de distribuição de logs mais robusta
                        dist_key_1 = self.process_labels[0].split()[-1].upper()
                        dist_key_2 = self.process_labels[1].split()[-1].upper()

                        if dist_key_1 in source.upper():
                            target_area = self.log_area_1
                        elif dist_key_2 in source.upper():
                            target_area = self.log_area_2
                        else:
                            formatted_log = f"[{source.upper()}]: {payload.get('message', payload)}\n"
                            
                    except json.JSONDecodeError:
                        formatted_log = f"[DADO BRUTO]: {line}"
                
                target_area.insert(tk.END, formatted_log, tag)
                target_area.see(tk.END)

        except queue.Empty:
            pass 

        if self.process and self.process.poll() is not None:
            if not self.process_finished_logged:
                # NOVO: Captura e exibe o código de saída do processo
                return_code = self.process.returncode
                final_message = f"[APP]: Processo backend finalizado. (Código de saída: {return_code})\n"
                tag = 'ERROR' if return_code != 0 else ''
                self.log_area_1.insert(tk.END, final_message, tag)
                self.log_area_buffer.insert(tk.END, final_message, tag) # Também no log central

                self.process_finished_logged = True
                self.start_button.config(state=tk.NORMAL)
                self.stop_button.config(state=tk.DISABLED)

        self.after(100, self.process_log_queue)

    def stop_process(self):
        if self.process and self.process.poll() is None:
            self.process.terminate()
            self.log_area_1.insert(tk.END, "[APP]: Sinal de término enviado ao processo backend.\n")
            self.stop_button.config(state=tk.DISABLED)

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Visualizador de IPC")
        self.root.geometry("1200x650")

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(pady=10, padx=10, expand=True, fill="both")

        pipes_tab = IPC_Tab(self.notebook, "pipes", ["Processo Pai", "Processo Filho"])
        self.notebook.add(pipes_tab, text="Pipes Anónimos")

        sockets_tab = IPC_Tab(self.notebook, "sockets", ["Servidor", "Cliente"])
        self.notebook.add(sockets_tab, text="Sockets")

        shared_mem_tab = IPC_Tab(self.notebook, "shared_memory", ["Processo 1", "Processo 2"])
        self.notebook.add(shared_mem_tab, text="Memória Partilhada")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()

