# Visualizador de Comunicação entre Processos (IPC)

Este projeto é uma ferramenta visual simples para entender como diferentes programas de computador conseguem "conversar" uns com os outros, mesmo sendo processos separados.

## Como Executar o Programa

1.  Certifique-se de que você tem Python instalado no seu computador.
2.  Abra um terminal ou prompt de comando na pasta do projeto.
3.  Execute o seguinte comando:

    ```bash
    python -m main_gui
    ```

4.  A interface gráfica irá aparecer. Você pode escolher um método de IPC, digitar uma mensagem e clicar em "Iniciar Comunicação" para ver a mágica acontecer!

## O que é Comunicação entre Processos (IPC)? (A Explicação Simples)

Imagine que seu computador é um grande escritório. Cada programa que você abre (como o navegador, um jogo, ou este próprio visualizador) é como uma pessoa trabalhando em sua própria sala, com a porta fechada.

Essa pessoa (o programa) tem sua própria memória, suas próprias ferramentas e trabalha de forma independente.

Mas e se a pessoa da Sala A precisar de uma informação que está com a pessoa da Sala B? Elas não podem simplesmente gritar, pois as salas são isoladas. Elas precisam de uma forma organizada para se comunicar.

**IPC (Inter-Process Communication)** é exatamente isso: um conjunto de regras e ferramentas que o sistema operacional oferece para que essas "pessoas" (programas) em salas diferentes possam trocar mensagens e dados de forma segura e organizada.

Nosso projeto demonstra 3 dessas ferramentas.

---

## Os Métodos de IPC Explicados (Para Leigos)

Abaixo, cada método é explicado com uma analogia do mundo real.

### 1. Pipes (Canos ou Tubos)

* **Analogia do Mundo Real:** Pense em um **telefone de latinha**. Duas latinhas conectadas por um barbante.

![Telefone de Latinha](https://i.imgur.com/2s71G5E.png)

* **Como Funciona:**
    * É uma conexão direta e exclusiva entre **dois** processos. Geralmente um processo "pai" que cria um processo "filho".
    * O que um processo fala (envia) em uma ponta do "cano", o outro escuta (recebe) na outra ponta.
    * A comunicação pode ser de mão dupla: o filho também pode responder para o pai pelo mesmo cano.

* **Como Vemos no Código:**
    * A linha `mp.Pipe()` cria o "telefone de latinha", dando uma ponta para o pai e outra para o filho.
    * O pai usa `conn_pai.send()` para "falar" e `conn_pai.recv()` para "ouvir". O filho faz o mesmo com a `conn_filho`.

* **Quando Usar?** É ótimo para uma comunicação simples e direta entre processos que têm uma relação próxima (como um processo que acabou de criar o outro), e que estão rodando no **mesmo computador**.

### 2. Shared Memory (Memória Compartilhada)

* **Analogia do Mundo Real:** Pense em um **quadro branco em uma sala de reuniões**.

![Quadro Branco](https://i.imgur.com/uSj4E2L.png)

* **Como Funciona:**
    * Em vez de enviar uma mensagem, o sistema operacional reserva um pequeno pedaço da memória do computador (o "quadro branco") que pode ser acessado por múltiplos processos.
    * Um processo vai até o quadro e **escreve** uma informação.
    * O outro processo vai até o **mesmo** quadro e **lê** a informação que está lá.
    * **Problema:** Como o segundo processo sabe *quando* a mensagem está pronta no quadro? E como evitar que os dois escrevam ao mesmo tempo e virem uma bagunça? Para isso, usamos "sinais" (no nosso código, um `Event`), que funciona como alguém levantando uma bandeira e dizendo: "Ei, acabei de escrever, pode vir ler!".

* **Como Vemos no Código:**
    * `mp.Array('c', 1024)` cria o nosso "quadro branco" de 1024 bytes.
    * `mp.Event()` cria a "bandeira de sinalização".
    * O processo Escritor escreve no `Array` e depois chama `evento.set()` para levantar a bandeira.
    * O processo Leitor fica parado em `evento.wait()`, esperando a bandeira levantar para poder ler a mensagem.

* **Quando Usar?** É o método **mais rápido** de todos, porque os dados não são copiados de um lugar para o outro. É ideal quando a velocidade é crucial e múltiplos processos precisam acessar os mesmos dados com frequência. Exige mais cuidado para não causar "acidentes".

### 3. Sockets

* **Analogia do Mundo Real:** Pense no **serviço de Correios ou em uma ligação telefônica**.

![Correios](https://i.imgur.com/Q2y1yNm.png)

* **Como Funciona:**
    * Este método é mais formal e poderoso. Ele funciona com base em **endereços**, assim como os Correios.
    * Um processo age como o **Servidor**: ele "abre uma agência dos Correios" em um endereço específico (um "endereço IP" e um número de "Porta") e fica esperando por cartas.
    * O outro processo age como o **Cliente**: ele escreve uma carta, coloca o endereço da "agência" do servidor e a envia.
    * O servidor recebe a carta, pode processá-la e enviar uma resposta de volta para o cliente.

* **Como Vemos no Código:**
    * O **Servidor** usa `socket.bind()` para "abrir sua agência" em um endereço e `socket.listen()` para começar a "esperar por cartas".
    * O **Cliente** usa `socket.connect()` para "enviar sua carta" para o endereço do servidor.
    * Ambos usam `sendall()` e `recv()` para enviar e receber os dados.

* **Quando Usar?** É o método mais flexível. Ele não só funciona para processos no mesmo computador, mas é a base de **toda a internet**! Você pode ter um cliente rodando no Brasil e um servidor no Japão, e eles conversarão via Sockets. É perfeito para qualquer aplicação de rede.

## Estrutura do Projeto

```
.
├── backend/
│   ├── pipes/
│   │   └── logic.py    # Lógica para comunicação com Pipes
│   ├── shared_memory/
│   │   └── logic.py    # Lógica para Memória Compartilhada
│   └── sockets/
│       └── logic.py    # Lógica para Sockets
│
├── main_gui.py         # Arquivo principal da Interface Gráfica
└── README.md           # Este arquivo
```