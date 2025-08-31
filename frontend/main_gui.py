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

        # Frame de botões
        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)
        self.start_button = tk.Button(button_frame, text=f"Iniciar {backend_module_name.capitalize()}", command=self.start_process)
        self.start_button.pack(side=tk.LEFT, padx=5)
        self.stop_button = tk.Button(button_frame, text="Parar", command=self.stop_process, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        # Frame de logs
        log_frame = tk.Frame(self)
        log_frame.pack(pady=10, padx=10, expand=True, fill=tk.BOTH)
        log_frame.grid_columnconfigure(0, weight=1)
        log_frame.grid_columnconfigure(1, weight=1)
        log_frame.grid_rowconfigure(1, weight=1)

        # Caixas de texto
        ttk.Label(log_frame, text=process_labels[0], font=("Helvetica", 12, "bold")).grid(row=0, column=0, pady=(0,5))
        self.log_area_1 = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, width=45, height=20, bg="#f0f0f0")
        self.log_area_1.grid(row=1, column=0, sticky="nsew", padx=(0, 5))

        ttk.Label(log_frame, text=process_labels[1], font=("Helvetica", 12, "bold")).grid(row=0, column=1, pady=(0,5))
        self.log_area_2 = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, width=45, height=20, bg="#f0f0f0")
        self.log_area_2.grid(row=1, column=1, sticky="nsew", padx=(5, 0))

        self.process_labels = process_labels
        self.after(100, self.process_log_queue)

    def start_process(self):
        self.log_area_1.delete('1.0', tk.END)
        self.log_area_2.delete('1.0', tk.END)
        
        command = ["python3", "-m", f"backend.{self.backend_module}.logic"]
        
        try:
            self.process = subprocess.Popen(
                command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, bufsize=1, universal_newlines=True, encoding='utf-8'
            )
        except FileNotFoundError:
            self.log_area_1.insert(tk.END, "ERRO: O interpretador 'python3' não foi encontrado.")
            return

        threading.Thread(target=self.read_output, args=(self.process.stdout,), daemon=True).start()
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

    def read_output(self, pipe):
        for line in iter(pipe.readline, ''):
            if line: self.log_queue.put(line)
        pipe.close()
        self.log_queue.put(json.dumps({"source": "App", "type": "status", "payload": {"message": "Processo backend finalizado."}}))

    def process_log_queue(self):
        try:
            while True:
                line = self.log_queue.get_nowait()
                try:
                    log_entry = json.loads(line)
                    source = log_entry.get('source', 'Desconhecido')
                    payload = log_entry.get('payload', {})
                    
                    if isinstance(payload, dict):
                        step = payload.get('step', 'info')
                        message = payload.get('message', '')
                        data_info = ""
                        if 'data' in payload:
                            data_info = f" (data: '{payload['data']}', size: {payload.get('size_bytes', 0)} bytes)"
                        formatted_log = f"[{step.upper()}]: {message}{data_info}\n"
                    else:
                        formatted_log = f"[INFO]: {payload}\n"
                    
                    # Direciona o log para a caixa de texto correta baseado nos rótulos
                    if self.process_labels[0].upper() in source.upper():
                        self.log_area_1.insert(tk.END, formatted_log)
                        self.log_area_1.see(tk.END)
                    elif self.process_labels[1].upper() in source.upper():
                        self.log_area_2.insert(tk.END, formatted_log)
                        self.log_area_2.see(tk.END)
                    else:
                        self.log_area_1.insert(tk.END, f"[{source.upper()}]: {payload.get('message', '')}\n")
                        self.log_area_1.see(tk.END)

                except json.JSONDecodeError:
                    self.log_area_1.insert(tk.END, f"[ERRO BRUTO]: {line}")
        except queue.Empty:
            pass 

        if self.process and self.process.poll() is not None:
             self.start_button.config(state=tk.NORMAL)
             self.stop_button.config(state=tk.DISABLED)

        self.after(100, self.process_log_queue)

    def stop_process(self):
        if self.process:
            self.process.terminate()
            self.log_area_1.insert(tk.END, "[APP]: Sinal de término enviado ao processo backend.\n")
            self.stop_button.config(state=tk.DISABLED)

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Visualizador de IPC")
        self.root.geometry("950x600")

        # Cria o Notebook (gerenciador de abas)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(pady=10, padx=10, expand=True, fill="both")

        # Cria a aba de Pipes
        pipes_tab = IPC_Tab(self.notebook, "pipes", ["Processo Pai", "Processo Filho"])
        self.notebook.add(pipes_tab, text="Pipes Anônimos")

        # Cria a aba de Sockets
        sockets_tab = IPC_Tab(self.notebook, "sockets", ["Servidor", "Cliente"])
        self.notebook.add(sockets_tab, text="Sockets")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()

