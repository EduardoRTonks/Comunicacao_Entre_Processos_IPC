# 📝 Relatório de Execução de Testes - Ferramenta de Visualização de IPC

## 1. Informações Gerais

* **Data da Execução:** 07 de setembro de 2025
* **Executor do Teste:** Eduardo Rodrigues Araújo de Oliveira, Ricardo Hey
* **Ambiente de Teste:**
    * **Sistema Operacional:** Linux (distribuição baseada em Ubuntu/Debian)
    * **Versão do Python:** 3.13
    * **Hardware:** (Preencher com as especificações da máquina, se necessário)

## 2. Resumo dos Testes

O objetivo desta sessão de testes foi validar a funcionalidade principal de cada mecanismo de IPC, bem como a robustez da aplicação em cenários de interrupção e reexecução.

A funcionalidade principal ("caminho feliz") de todos os três módulos (**Pipes**, **Sockets** e **Memória Compartilhada**) foi validada com sucesso.

No entanto, foram identificados **dois problemas críticos** que ocorrem em cenários específicos:
1.  **Falha no Encerramento Gracioso:** Ao interromper um processo manualmente através do botão "Parar", a interface exibe logs de erro brutos do sistema, poluindo a visualização.
2.  **Falha de Reexecução (Sockets):** O módulo de Sockets não pode ser executado duas vezes seguidas, falhando na segunda tentativa com um erro de "Endereço já em uso".

## 3. Casos de Teste Executados

| ID do Teste | Cenário de Teste | Passos para Reproduzir | Resultado Esperado | Resultado Obtido | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **TC-01** | Funcionalidade: Pipes | 1. Selecionar "Pipes". <br> 2. Manter a mensagem padrão. <br> 3. Clicar em "Iniciar". | Os logs de "Processo Pai" e "Processo Filho" mostram a troca de mensagens e a finalização correta. | Conforme esperado. | ✅ **Sucesso** |
| **TC-02** | Funcionalidade: Sockets | 1. Selecionar "Sockets". <br> 2. Manter a mensagem padrão. <br> 3. Clicar em "Iniciar". | Os logs de "Servidor" e "Cliente" mostram a conexão, a troca de mensagens e a finalização correta. | Conforme esperado. | ✅ **Sucesso** |
| **TC-03** | Funcionalidade: Shared Memory | 1. Selecionar "Shared Memory". <br> 2. Manter a mensagem padrão. <br> 3. Clicar em "Iniciar". | Os logs de "Processo Escritor" e "Processo Leitor" mostram a escrita, o sinal e a leitura correta dos dados. | Conforme esperado. | ✅ **Sucesso** |
| **TC-04** | Robustez: Interrupção Manual | 1. Iniciar a comunicação de qualquer um dos três módulos. <br> 2. Durante a execução, clicar no botão "Parar". | O processo de backend é encerrado. A interface exibe uma mensagem limpa, como "Processo finalizado pelo usuário". | O processo é encerrado, porém a interface exibe um traceback de erro bruto (`[LOG BRUTO]`). | ❌ **Falha** |
| **TC-05** | Robustez: Reexecução de Sockets | 1. Executar o teste **TC-02** (Sockets) e esperar finalizar. <br> 2. Imediatamente após, clicar em "Iniciar" novamente para rodar o Sockets pela segunda vez. | A comunicação via Sockets deve funcionar corretamente na segunda execução, assim como na primeira. | A segunda execução falha. O servidor não consegue iniciar devido a um erro `OSError: [Errno 98] Address already in use`. | ❌ **Falha** |

## 4. Análise Detalhada dos Problemas Encontrados

### P-01: Exibição de Erros Brutos na Interrupção Manual (TC-04)

Ao forçar o encerramento de um processo com o botão "Parar", a chamada `terminate()` causa uma interrupção abrupta no script de backend. Isso gera erros de sistema (como `BrokenPipeError`) que são capturados pela thread de leitura do `stderr`. Como esses erros não estão no formato JSON esperado, eles são exibidos como "[LOG BRUTO]", poluindo a interface e confundindo o usuário.

**Evidência:**

![Screenshot do erro de interrupção manual](images/erro_interrupcao.png)

### P-02: Falha na Reexecução do Módulo Sockets (TC-05)

Após a primeira execução do módulo Sockets, o sistema operacional mantém a porta `65432` em um estado temporário de `TIME_WAIT`. Ao tentar executar o módulo novamente, o novo processo servidor tenta se vincular (`bind`) a essa porta, mas o sistema operacional nega o pedido, pois considera que ela ainda está em uso. Isso causa o erro `OSError: [Errno 98] Address already in use`.

**Evidência:**

![Screenshot do erro de reuso de endereço no Socket](images/erro_socket_reuso.png)

## 5. Recomendações e Próximos Passos

Para corrigir os problemas encontrados e aumentar a robustez da aplicação, as seguintes ações são recomendadas:

1.  **Para o problema P-01:** Implementar uma "flag" (bandeira) de controle na GUI. Quando o usuário clicar em "Parar", a flag é ativada. O código que exibe os logs brutos deve então verificar essa flag e, se ela estiver ativa, ignorar os erros de sistema esperados durante o encerramento manual.
2.  **Para o problema P-02:** Adicionar a opção de socket `SO_REUSEADDR` no script `backend/sockets/logic.py`. Esta opção deve ser configurada no socket do servidor antes da chamada `bind()`, instruindo o sistema operacional a permitir a reutilização imediata do endereço e da porta.

