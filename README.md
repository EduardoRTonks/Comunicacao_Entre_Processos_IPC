🚀 Ferramenta de Visualização de Comunicação Entre Processos (IPC)
📖 Descrição do Projeto
Este projeto, desenvolvido para a disciplina de Sistemas Computacionais (Sistemas Operacionais), consiste em uma aplicação para demonstrar visualmente três mecanismos de Comunicação Entre Processos (IPC): Pipes Anônimos, Sockets Locais e Memória Compartilhada.

A arquitetura separa a lógica principal (backend), implementada em C++, da interface do usuário (frontend), desenvolvida com HTML, CSS e JavaScript. Essa abordagem permite que a complexidade da comunicação interprocessos seja tratada em uma linguagem de sistema, enquanto a visualização é feita com tecnologias web leves e modernas.

👥 Equipe (Exemplo)
Aluno A: Eduardo Rodrigues Araújo de Oliveira - Coordenador e Módulo de Pipes, Módulo de Memória Compartilhada

Aluno B: Ricardo Hey - Módulo de Sockets, Frontend e Integração

🏛️ Arquitetura e Tecnologias
O projeto é dividido em duas partes principais:

Backend (C++):

Linguagem: C++23 (ou C/Rust, conforme especificado).

Responsabilidade: Implementa a lógica para cada mecanismo de IPC. Cada módulo de IPC é um executável separado que, ao ser iniciado pelo frontend, começa a se comunicar com seu processo par.

Comunicação com o Frontend: Os processos em C++ enviam informações para a "saída padrão" (stdout) em formato JSON. O frontend captura essa saída para atualizar a interface em tempo real.

Build System: CMake é utilizado para gerenciar a compilação do código C++, garantindo que funcione em diferentes sistemas operacionais (Linux, Windows, macOS).

Frontend (HTML/JS):

Tecnologias: HTML5, CSS3, JavaScript (Vanilla - sem frameworks).

Responsabilidade: Fornecer uma interface gráfica para o usuário selecionar o mecanismo de IPC, enviar mensagens e visualizar os logs de comunicação.

Integração: O JavaScript será responsável por iniciar os processos do backend em background, ler o stdout deles e interpretar o JSON para exibir as informações na tela de forma clara.

📁 Estrutura de Pastas
O repositório está organizado da seguinte forma para minimizar conflitos e manter o código modular:

projeto-ipc/
├── backend/                # Contém todo o código C++
│   ├── pipes/              # Lógica de comunicação com Pipes Anônimos
│   ├── sockets/            # Lógica de comunicação com Sockets Locais
│   └── shared_memory/      # Lógica de comunicação com Memória Compartilhada
│
├── frontend/               # Contém a interface do usuário
│   ├── index.html          # Estrutura principal da página
│   ├── style.css           # Estilização
│   └── script.js           # Lógica de interação e comunicação com o backend
│
├── docs/                   # Documentação adicional, diagramas, etc.
│
├── tests/                  # Testes unitários para o backend
│
└── README.md               # Este arquivo

🔧 Como Compilar e Executar
Siga os passos abaixo para configurar e rodar o projeto.

Pré-requisitos
Um compilador C++ moderno (GCC, Clang ou MSVC)

CMake (versão 3.10 ou superior)

Git

1. Compilando o Backend (C++)
Clone o repositório:

git clone [URL-DO-SEU-REPOSITORIO-NO-GITHUB]
cd projeto-ipc

Crie uma pasta para a compilação:

mkdir build
cd build

Use o CMake para gerar os arquivos de build e compile:

cmake ../backend
cmake --build .

Após a compilação, os executáveis (pipes_main, sockets_main, shared_memory_main) estarão dentro da pasta build.

2. Executando o Frontend
Navegue até a pasta do frontend:

cd ../frontend

Abra o arquivo index.html em um navegador web.

A interface gráfica será carregada. As ações na interface (como clicar em "Iniciar") irão executar os programas C++ compilados que estão na pasta build.

🔄 Protocolo de Comunicação (Backend -> Frontend)
Para que o frontend entenda o que está acontecendo no backend, os programas C++ enviarão objetos JSON pela saída padrão (stdout). Cada linha será um JSON independente.

Exemplo de log de mensagem:

{
  "timestamp": "2024-10-27T10:00:01Z",
  "source": "Processo Pai (Pipe)",
  "type": "log",
  "message": "Enviando mensagem: 'Olá, mundo!'"
}

Exemplo de atualização de estado:

{
  "timestamp": "2024-10-27T10:00:02Z",
  "source": "Memória Compartilhada",
  "type": "state",
  "content": "O conteúdo atual da memória é: 'Olá, mundo!'"
}

Exemplo de erro:

{
  "timestamp": "2024-10-27T10:00:03Z",
  "source": "Socket Servidor",
  "type": "error",
  "message": "Falha ao conectar: o cliente foi desconectado."
}

O JavaScript no frontend irá ler essas linhas, fazer o "parse" do JSON e adicionar as informações dinamicamente nos elementos HTML correspondentes (área de log, visualizador de estado, etc.).

✅ Divisão de Tarefas
Aluno A (Pipes & Coordenação): Implementar a lógica em backend/pipes. Coordenar o repositório no GitHub.

Aluno B (Sockets): Implementar a lógica cliente-servidor em backend/sockets.

Aluno C (Memória Compartilhada): Implementar a lógica de acesso e sincronização (com semáforos/mutex) em backend/shared_memory.

Aluno D (Frontend): Desenvolver os arquivos em frontend/ e implementar a lógica em script.js para chamar os executáveis do backend e processar a saída JSON.