# 🚀 Ferramenta de Visualização de Comunicação Entre Processos (IPC)

## 📖 Descrição do Projeto

Este projeto, desenvolvido para a disciplina de Sistemas Computacionais, consiste em uma aplicação desktop para demonstrar e visualizar três mecanismos fundamentais de Comunicação Entre Processos (IPC): **Pipes Anônimos**, **Sockets Locais** e **Memória Compartilhada**.

A arquitetura da aplicação é construída inteiramente em **Python**, utilizando o módulo nativo `multiprocessing` para a lógica de IPC (backend) e a biblioteca `Tkinter` para a interface gráfica do usuário (frontend). Essa abordagem permite que a complexidade da comunicação interprocessos e a visualização sejam tratadas em uma única e coesa base de código.

## 👥 Equipe

* **Aluno A:** Eduardo Rodrigues Araújo de Oliveira - Coordenador, Módulo de Frontend (`tkinter`), Módulo de Memória Compartilhada (`backend/shared_memory`).
* **Aluno B:** Ricardo Hey - Módulo de Pipes (`backend/pipes`) e Módulo de Sockets (`backend/sockets`).

### Arquitetura Detalhada

#### Backend (`/backend`)
* **Responsabilidade:** Implementa a lógica para cada mecanismo de IPC. Cada módulo é um script Python separado que, ao ser iniciado pelo frontend, cria os processos necessários (ex: pai/filho, cliente/servidor) para demonstrar a comunicação.
* **Comunicação com o Frontend:** Para garantir a visualização em tempo real, todos os processos do backend enviam logs para a "saída padrão" (`stdout`) em um formato **JSON** estruturado. Isso permite que a interface gráfica capture e interprete os eventos de forma organizada.

#### Frontend (`/frontend`)
* **Responsabilidade:** Fornecer uma interface gráfica (`Tkinter`) para o usuário selecionar o mecanismo de IPC, inserir uma mensagem para ser enviada e visualizar os logs de comunicação dos processos em áreas de texto separadas.
* **Integração:** A interface gráfica inicia os scripts do backend como subprocessos, captura o `stdout` deles em uma thread separada para não travar a UI, e interpreta o JSON recebido para exibir as informações na tela de forma clara e cronológica.

## 📁 Estrutura de Pastas

```
projeto-ipc/
├── backend/            # Contém toda a lógica de IPC em Python
│   ├── pipes/
│   │   └── logic.py    # Lógica de comunicação com Pipes Anônimos
│   ├── sockets/
│   │   └── logic.py    # Lógica de comunicação com Sockets Locais
│   └── shared_memory/
│       └── logic.py    # Lógica de comunicação com Memória Compartilhada
│
├── frontend/           # Contém a interface do usuário
│   └── main_gui.py     # Script principal da aplicação com Tkinter
│
└── README.md           # Este arquivo
```

## 🛠️ Tecnologias Utilizadas

* **Linguagem Principal:** Python 3.13
* **Interface Gráfica (Frontend):**
    * **Tkinter:** A biblioteca padrão do Python para criação de interfaces gráficas desktop. Utiliza os módulos `tkinter.ttk` para widgets modernos e `tkinter.scrolledtext` para áreas de log com rolagem.
* **Lógica de IPC (Backend):**
    * **Módulo `multiprocessing`:** Utilizado para criar e gerenciar processos (`mp.Process`), além de fornecer os mecanismos de IPC:
        * `mp.Pipe` para Pipes Anônimos.
        * `mp.Array` para Memória Compartilhada.
        * `mp.Event` para sincronização na Memória Compartilhada.
    * **Módulo `socket`:** Utilizado para a comunicação cliente-servidor com Sockets TCP/IP em `localhost`.
* **Sincronização e Concorrência:**
    * **Módulo `threading` e `queue`:** Usados no frontend para capturar a saída do backend em segundo plano sem congelar a interface do usuário.
* **Formato de Dados:**
    * **JSON:** Utilizado como o "protocolo" de comunicação entre o backend e o frontend, garantindo que os logs sejam estruturados e fáceis de interpretar.

## 🚀 Como Compilar e Executar

Este projeto não requer compilação. Siga os passos abaixo para configurar o ambiente e executar a aplicação em Windows ou Linux.

### Pré-requisitos

* **Git (Opcional):** Recomendado para baixar o projeto.
* **Python 3.13:** Essencial para rodar o código. Certifique-se de que o comando `python3.13` (ou um similar) esteja acessível no seu PATH.

### Passo 1: Obter o Projeto

Abra um terminal (CMD, PowerShell, Git Bash, ou Terminal do Linux) e clone o repositório:
```bash
git clone [https://github.com/EduardoRTonks/Comunicacao_Entre_Processos_IPC.git](https://github.com/EduardoRTonks/Comunicacao_Entre_Processos_IPC.git)
cd Comunicacao_Entre_Processos_IPC
```

### Passo 2: Instalar Dependências do Sistema (Apenas Linux)

O Tkinter, apesar de ser uma biblioteca padrão, precisa de um pacote de sistema no Linux para funcionar. Se você estiver no Windows, pule para o próximo passo.

Para sistemas baseados em **Ubuntu/Debian**:
```bash
sudo apt update
sudo apt install python3.13-tk
```
*(Nota: se o pacote `python3.13-tk` não estiver disponível, tente o mais genérico `python3-tk`)*

### Passo 3: Configurar o Ambiente Virtual (venv)

Usar um ambiente virtual é uma boa prática para isolar as dependências do projeto.

1.  **Crie o ambiente virtual:**
    ```bash
    python3.13 -m venv .venv
    ```

2.  **Ative o ambiente virtual:**
    * **No Windows (PowerShell):**
        ```powershell
        .venv\Scripts\Activate.ps1
        ```
    * **No Windows (CMD):**
        ```cmd
        .venv\Scripts\activate.bat
        ```
    * **No Linux / macOS:**
        ```bash
        source .venv/bin/activate
        ```
    *(Após a ativação, você deverá ver `(.venv)` no início do seu prompt do terminal)*

### Passo 4: Executar a Aplicação

Com o ambiente virtual ativado, execute o arquivo da interface gráfica:
```bash
python3.13 frontend/main_gui.py
```
*(Nota: Dentro de um venv ativado, o comando `python` geralmente já aponta para a versão correta, então `python frontend/main_gui.py` também deve funcionar.)*

#### Atenção: Permissão de Firewall (Windows)
Na primeira vez que você rodar a demonstração com **Sockets**, o Firewall do Windows provavelmente pedirá permissão para a aplicação. Clique em **"Permitir acesso"** para que a comunicação local funcione corretamente.

E é isso! A interface gráfica da aplicação deverá abrir, e você poderá testar os diferentes mecanismos de IPC.