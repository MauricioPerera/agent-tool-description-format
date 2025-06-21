# Índice

- [Guia do Servidor MCP do n8n](#guia-do-servidor-mcp-do-n8n)
- [Introdução e Objetivos](#introdução-e-objetivos)
- [Conceitos Básicos](#conceitos-básicos)
  - [MCP Server Trigger](#mcp-server-trigger)
  - [Subfluxos (Subworkflows)](#subfluxos-subworkflows)
  - [Nó toolWorkflow (toolWorkflow Node)](#nó-toolworkflow-toolworkflow-node)
- [Boas Práticas MCP](#boas-práticas-mcp)
  - [Arquitetura](#arquitetura)
  - [Nomenclatura (Convenções de Nomes)](#nomenclatura-convenções-de-nomes)
  - [Saída Padrão](#saída-padrão)
  - [Validação](#validação)
  - [Segurança](#segurança)
  - [Documentação](#documentação)
  - [Versionamento](#versionamento)
  - [Princípios Chave para a Robustez de Fluxos de Trabalho](#princípios-chave-para-a-robustez-de-fluxos-de-trabalho)
- [Arquitetura Geral](#arquitetura-geral)
  - [Estrutura Básica](#estrutura-básica)
  - [Vantagens do Uso de Subfluxos](#vantagens-do-uso-de-subfluxos)
- [Design de Ferramentas MCP (Subfluxos)](#design-de-ferramentas-mcp-subfluxos)
  - [Formato Padrão de Saída](#formato-padrão-de-saída)
  - [Validação de Entradas e Erros Uniformes](#validação-de-entradas-e-erros-uniformes)
- [Template Visual Base para Subfluxos (Ferramentas)](#template-visual-base-para-subfluxos-ferramentas)
- [Exemplo de Fluxo Principal (Servidor MCP)](#exemplo-de-fluxo-principal-servidor-mcp)
- [Considerações Gerais](#considerações-gerais)
- [Integração do Formato ATDF (Automatic Tool Definition Format)](#integração-do-formato-atdf-automatic-tool-definition-format)
  - [Como Integrá-lo](#como-integrá-lo)
  - [Campos Recomendados para ATDF](#campos-recomendados-para-atdf)
  - [Exemplo de Bloco ATDF (YAML)](#exemplo-de-bloco-atdf-yaml)
  - [Mini-Template ATDF Comentado (YAML)](#mini-template-atdf-comentado-yaml)
  - [Validação da Sintaxe ATDF (YAML)](#validação-da-sintaxe-atdf-yaml)
- [Uso de Subservidores MCP como Ferramentas](#uso-de-subservidores-mcp-como-ferramentas)
  - [Configuração](#configuração)
  - [Vantagens](#vantagens)
  - [Exemplo Visual (Diagrama de Fluxo)](#exemplo-visual-diagrama-de-fluxo)
- [Considerações sobre a Descrição de Ferramentas Externas (via MCP Client)](#considerações-sobre-a-descrição-de-ferramentas-externas-via-mcp-client)
- [Perguntas Frequentes (FAQ)](#perguntas-frequentes-faq)
- [Testes e Depuração](#testes-e-depuração)
- [Guia de Exportação/Importação e Versionamento com Git](#guia-de-exportaçãoimportação-e-versionamento-com-git)
- [Uso de Etiquetas (Tags) nos Fluxos de Trabalho do n8n](#uso-de-etiquetas-tags-nos-fluxos-de-trabalho-do-n8n)
- [Tratamento Global de Erros no Fluxo Principal do Servidor MCP](#tratamento-global-de-erros-no-fluxo-principal-do-servidor-mcp)

# Guia do Servidor MCP do n8n

## Introdução e Objetivos

Este guia descreve as melhores práticas e a arquitetura para construir e manter Servidores de Processos Comuns (MCP) utilizando n8n. O objetivo é promover a modularidade, a reutilização e a manutenibilidade dos fluxos de trabalho.

## Conceitos Básicos

### MCP Server Trigger
O **MCP Server Trigger** (tipo de nó: `@n8n/n8n-nodes-langchain.mcpTrigger`) é um nó especializado no n8n que atua como ponto de entrada para as solicitações ao servidor MCP. Permite definir a interface de entrada e saída do servidor, e é ele que recebe as requisições externas para executar uma ou várias ferramentas.

### Subfluxos (Subworkflows)
Os **Subfluxos** (fluxos de trabalho secundários) são fluxos de trabalho do n8n que podem ser chamados a partir de outros fluxos de trabalho. São fundamentais para a modularidade na arquitetura MCP, permitindo encapsular lógica específica em unidades reutilizáveis. Estes subfluxos implementam a lógica de uma ferramenta específica.

### Nó toolWorkflow (toolWorkflow Node)
O nó **toolWorkflow** (tipo de nó: `@n8n/n8n-nodes-langchain.toolWorkflow`) é utilizado no fluxo principal do servidor MCP para chamar um subfluxo (ferramenta). Atua como uma ponte, configurando como o subfluxo é chamado e como suas entradas e saídas são mapeadas. A descrição ATDF da ferramenta é colocada neste nó.

## Boas Práticas MCP

### Arquitetura
*   Projetar uma arquitetura modular utilizando subfluxos para cada ferramenta ou processo discreto.
*   O servidor MCP principal utiliza um `@n8n/n8n-nodes-langchain.mcpTrigger` e chama os subfluxos (ferramentas) através de nós `@n8n/n8n-nodes-langchain.toolWorkflow`.

### Nomenclatura (Convenções de Nomes)
*   Utilizar nomes claros e consistentes para fluxos de trabalho, subfluxos, nós e variáveis.
*   Prefixar os subfluxos com `SWF_` para identificá-los facilmente (ex: `SWF_Valida_Intervalo_Datas`).
*   Prefixar as variáveis de ambiente com `ENV_`.
*   Utilizar snake_case para nomes de variáveis e parâmetros.
*   Para nomes de ferramentas (configurados no nó `toolWorkflow`), seguir o formato: `tool.<acao>_<entidade>` (ex: `tool.get_user`, `tool.create_invoice`).

### Saída Padrão
*   Definir um formato de saída padrão para todos los subfluxos (ferramentas), tanto para respostas bem-sucedidas como para erros. O campo `status` deve ser estritamente `"success"` ou `"error"`. (Ver "Design de Ferramentas MCP (Subfluxos) > Formato Padrão de Saída").

### Validação
*   Validar as entradas em cada subfluxo para assegurar a integridade dos dados.
*   Fornecer mensagens de erro claras e uniformes seguindo o formato de erro padrão. (Ver "Design de Ferramentas MCP (Subfluxos) > Validação de Entradas e Erros Uniformes").

### Segurança
*   Proteger os endpoints do `@n8n/n8n-nodes-langchain.mcpTrigger` utilizando mecanismos de autenticação e autorização do n8n.
*   Gerenciar as credenciais de forma segura utilizando o gerenciador de credenciais do n8n.
*   Evitar expor informação sensível nos logs.

### Documentação
*   Documentar cada ferramenta (subfluxo), incluindo seu propósito, parâmetros de entrada, formato de saída e quaisquer dependências. O bloco ATDF é incluído na descrição do nó `@n8n/n8n-nodes-langchain.toolWorkflow` que o chama.
*   Manter atualizada a documentação da arquitetura geral do MCP.

### Versionamento
*   Versionar os subfluxos e o servidor MCP para gerenciar as mudanças e evitar quebrar integrações existentes.
*   Utilizar um sistema de controle de versões como Git para o versionamento dos fluxos de trabalho exportados. (Ver "Guia de Exportação/Importação e Versionamento com Git").

### Princípios Chave para a Robustez de Fluxos de Trabalho
Para assegurar que os servidores MCP e suas ferramentas (subfluxos) sejam confiáveis e fáceis de depurar, devem-se seguir estes princípios fundamentais:
1.  **Aderência ao Formato de Saída Padrão:** Todo subfluxo (ferramenta) deve devolver consistentemente o [Formato Padrão de Saída](#formato-padrão-de-saída) JSON, seja para sucesso (`status: "success"`) ou erro (`status: "error"`), incluindo os campos `data` e `meta` apropriados.
2.  **Validação Exaustiva de Entradas:** Cada subfluxo deve validar rigorosamente seus parâmetros de entrada no início. Ver a seção [Validação de Entradas e Erros Uniformes](#validação-de-entradas-e-erros-uniformes).
3.  **Tratamento Explícito de Erros em Nós Críticos:** Para nós que realizam operações suscetíveis a falhas (ex: chamadas a APIs externas com `HTTP Request`, interações com serviços como `Google Calendar`), configurar explicitamente o tratamento de erros. Isso pode ser feito usando a opção "Configurações" > "Continue On Fail" no nó, seguido de um nó `IF` para verificar se `$json.error` existe e assim dirigir o fluxo para a preparação de uma resposta de erro padrão. Alternativamente, pode-se usar a opção "Error Workflow" do nó para dirigir a falha a um fluxo de trabalho de tratamento de erros dedicado.
4.  **Cobertura de Todas as Rotas Lógicas:** Assegurar que todas as ramificações possíveis dentro de um fluxo de trabalho (ex: em nós `IF` ou `Switch`) terminem explicitamente num nó que gere uma saída padrão (sucesso ou erro). Evitar "caminhos mortos" onde uma ramificação não produz uma resposta formatada, o que poderia levar a erros silenciosos ou respostas inesperadas.
5.  **Uso Estratégico de "Error Workflows" do n8n:**
    *   **Nível de Nó:** Para nós críticos ou complexos como `@n8n/n8n-nodes-langchain.toolWorkflow`, configurar um "Error Workflow" específico na aba "Configurações" do nó pode proporcionar um tratamento de falhas granular.
    *   **Nível de Instância (Global):** Configurar um "Error Workflow" global para a instância do n8n (a partir de "Settings" / "Configurações" do n8n) serve como uma rede de segurança final para capturar e tratar quaisquer erros não controlados que possam ocorrer em qualquer fluxo de trabalho.
6.  **Registro (Logging) Significativo:** Implementar o registro de eventos importantes, parâmetros de entrada chave e erros em pontos críticos dos fluxos de trabalho. Utilizar o nó `n8n-nodes-base.logMessage` ou ferramentas de observabilidade externas. Isto é crucial para a depuração e o monitoramento. (Ver "Testes e Depuração > Interpretação de Logs").

O cumprimento destes princípios é fundamental e é detalhado ou exemplificado em seções posteriores como [Testes e Depuração](#testes-e-depuração) e [Tratamento Global de Erros no Fluxo Principal do Servidor MCP](#tratamento-global-de-erros-no-fluxo-principal-do-servidor-mcp).

## Arquitetura Geral

### Estrutura Básica
A arquitetura MCP baseia-se num fluxo principal (o servidor MCP) que utiliza um `@n8n/n8n-nodes-langchain.mcpTrigger` como ponto de entrada. Este fluxo orquestra a execução de subfluxos (ferramentas) através de nós `@n8n/n8n-nodes-langchain.toolWorkflow`.

```mermaid
graph TD
    A[@n8n/n8n-nodes-langchain.mcpTrigger] --> B{Nó Switch (Roteador baseado no nome da ferramenta do Agente AI)};
    B -- nome_ferramenta_A --> C1["@n8n/n8n-nodes-langchain.toolWorkflow (configurado para SWF_Ferramenta_A)"];
    B -- nome_ferramenta_B --> C2["@n8n/n8n-nodes-langchain.toolWorkflow (configurado para SWF_Ferramenta_B)"];
    C1 --> D[Tratamento de Resposta / Preparação para Agente AI];
    C2 --> D;
```
O `mcpTrigger` recebe uma solicitação, um nó `Switch` (ou lógica similar) determina qual ferramenta executar, e um nó `toolWorkflow` específico chama o subfluxo correspondente.

### Vantagens do Uso de Subfluxos
*   **Modularidade:** Decompor problemas complexos em partes menores e gerenciáveis.
*   **Reutilização:** Utilizar a mesma lógica em diferentes partes do sistema ou em diferentes servidores MCP.
*   **Manutenibilidade:** Facilitar a atualização e correção de erros ao isolar a lógica em unidades independentes.
*   **Testabilidade:** Testar cada subfluxo (ferramenta) de forma isolada.

## Design de Ferramentas MCP (Subfluxos)

### Formato Padrão de Saída

#### Sucesso
O campo `status` será sempre `"success"`. O campo `data` contém o resultado útil da ferramenta.

```json
{
  "status": "success",
  "data": {
    "resultado_especifico": "valor",
    "outro_dado": 123
  },
  "meta": {
    "timestamp": "2023-10-27T10:30:00Z"
  }
}
```
*(Nota: `meta.timestamp` pode ser gerado com `{{ $now }}` num nó `Set`)*.

#### Erro
O campo `status` será sempre `"error"`. O campo `data` contém detalhes do erro. O campo `message` ou `text` dentro de `data` fornece uma mensagem legível.

```json
{
  "status": "error",
  "data": {
    "code": "CODIGO_ERRO_UNICO",
    "message": "Descrição legível do erro.",
    "text": "Descrição legível do erro (alternativa se 'text' for usado).",
    "details": {
      "field": "nome_do_campo_com_erro",
      "expected": "tipo_ou_formato_esperado",
      "solution": "Como solucionar o problema ou o que se espera."
    }
  },
  "meta": {
    "timestamp": "2023-10-27T10:35:00Z"
  }
}
```
*(Preferir `message` ou `text` consistentemente. Se os exemplos usam `text`, usar `text`. Assegurar que os códigos de erro como `CODIGO_ERRO_UNICO` estejam em maiúsculas e entre crases se referenciados no texto.)*.

### Validação de Entradas e Erros Uniformes
*   Utilizar nós `n8n-nodes-base.if` ou `n8n-nodes-base.switch` no início dos subfluxos para validar os parâmetros de entrada.
*   Se a validação falhar, deve-se construir uma resposta de erro utilizando a estrutura definida anteriormente. Por exemplo, se um campo `user_id` é requerido mas não é fornecido:

```json
{
  "status": "error",
  "data": {
    "code": "VALIDATION_ERROR",
    "message": "Parâmetros de entrada inválidos.",
    "details": {
      "field": "user_id",
      "expected": "string, non-empty",
      "solution": "Fornecer um user_id válido."
    }
  },
  "meta": {
    "timestamp": "2023-10-27T10:40:00Z"
  }
}
```
*   Utilizar códigos de erro únicos e descritivos (ex: `VALIDATION_ERROR`) para facilitar a depuração e o monitoramento.

## Template Visual Base para Subfluxos (Ferramentas)

Os subfluxos que atuam como ferramentas são tipicamente iniciados por um `n8n-nodes-base.executeWorkflowTrigger` (gatilho de execução de fluxo de trabalho) quando são chamados desde o fluxo principal (através de um `@n8n/n8n-nodes-langchain.toolWorkflow`). É crucial seguir os [Princípios Chave para a Robustez de Fluxos de Trabalho](#princípios-chave-para-a-robustez-de-fluxos-de-trabalho) ao desenhar estes templates.

**Exemplo: Subfluxo "SWF_Valida_Intervalo_Datas"**

1.  **Início (Gatilho):** Nó `n8n-nodes-base.executeWorkflowTrigger`. Recebe parâmetros como `Start` (data de início) e `End` (data de fim) do nó `toolWorkflow` no fluxo principal.
2.  **Validação de Entradas:** Nó `n8n-nodes-base.if` (ex: "Validar datas"). Verifica se as datas são válidas, se `Start` é anterior a `End`, etc. (Princípio de Robustez #2).
    *   Se a validação falhar, uma ramificação (FALSE) leva a um nó `n8n-nodes-base.set` (ex: "Erro: Datas Inválidas") para construir o JSON de erro padrão (Princípio de Robustez #1).
3.  **Lógica Principal (se a validação estiver correta):** Pode incluir outros nós para processar as datas, se necessário. Neste exemplo, a própria validação é a lógica principal.
4.  **Saída Bem-sucedida:** Nó `n8n-nodes-base.set` (ex: "Sucesso: Intervalo Válido"). Prepara o JSON de resposta bem-sucedida padrão (Princípio de Robustez #1).
    ```json
    {
      "status": "success",
      "data": {
        "message": "O intervalo de datas é válido.",
        "start_date": "{{ $json.Start }}",
        "end_date": "{{ $json.End }}"
      },
      "meta": {
        "timestamp": "{{ $now.toJSON() }}"
      }
    }
    ```
5.  **Saída de Erro (da validação ou lógica principal):** Nó `n8n-nodes-base.set` (ex: "Erro: Datas Inválidas"). Prepara o JSON de resposta de erro padrão (Princípio de Robustez #1).
    ```json
    {
      "status": "error",
      "data": {
        "code": "INVALID_DATE_RANGE",
        "text": "A data de início deve ser anterior à data de fim.",
        "details": {
          "field_start": "{{ $json.Start }}",
          "field_end": "{{ $json.End }}",
          "condition": "Start < End"
        }
      },
      "meta": {
        "timestamp": "{{ $now.toJSON() }}"
      }
    }
    ```
    *(Nota: O exemplo "Valida_Intervalo_Datas" usa `data.text` para a mensagem, por isso reflete-se aqui. O código de erro `INVALID_DATE_RANGE` está em maiúsculas.)*
6.  **Fim do Subfluxo:** O subfluxo termina. Os dados preparados no nó `Set` da ramificação executada (sucesso ou erro) são devolvidos implicitamente ao fluxo chamador (ao nó `toolWorkflow`). Assegurar a cobertura de todas as rotas lógicas (Princípio de Robustez #4).

```mermaid
graph TD
    A[n8n-nodes-base.executeWorkflowTrigger <br> (Recebe: Start, End)] --> B{n8n-nodes-base.if <br> (Validar Datas: Start < End?)};
    B -- TRUE (Válido) --> S_PREP[n8n-nodes-base.set <br> (Prepara JSON Sucesso: status=success, data={message, dates}, meta)];
    S_PREP --> Z[Fim do Subfluxo <br> (Retorna JSON de S_PREP)];
    B -- FALSE (Inválido) --> E_PREP[n8n-nodes-base.set <br> (Prepara JSON Erro: status=error, data={code, text, details}, meta)];
    E_PREP --> Z;
```

## Exemplo de Fluxo Principal (Servidor MCP)

O fluxo principal utiliza um `@n8n/n8n-nodes-langchain.mcpTrigger` como ponto de entrada.

1.  **MCP Server Trigger:** Nó `@n8n/n8n-nodes-langchain.mcpTrigger`. Define o endpoint, e é onde o Agente AI (Langchain) envia as solicitações para executar ferramentas.
2.  **Validação de Solicitação (Opcional, delegada ao mcpTrigger):** O `mcpTrigger` trata parte da validação da solicitação do agente.
3.  **Roteador/Dispatcher (Nó Switch):** Um nó `n8n-nodes-base.switch` dirige a execução com base no nome da ferramenta solicitada pelo agente AI (ex: `{{ $json.tool_name }}`). Cada saída do `Switch` conecta-se a um nó `@n8n/n8n-nodes-langchain.toolWorkflow` específico. (Ver "Tratamento Global de Erros no Fluxo Principal do Servidor MCP" para erros de roteamento).
4.  **Chamada a Subfluxo (Ferramenta):** O nó `@n8n/n8n-nodes-langchain.toolWorkflow` é responsável por:
    *   Identificar o subfluxo a executar (configurado nos seus parâmetros).
    *   Mapear as entradas para o subfluxo (ex: usando expressões como `{{ $fromAI("user_id") }}` para obter parâmetros da solicitação do agente AI).
    *   Executar o subfluxo.
    *   Receber a resposta (JSON de sucesso/erro) do subfluxo. (Ver "Tratamento Global de Erros no Fluxo Principal do Servidor MCP" para falhas do `toolWorkflow` ou respostas inválidas).
5.  **Tratamento da Resposta do Subfluxo:** A saída do `toolWorkflow` (que é a saída do subfluxo) pode ser processada adicionalmente, se necessário, antes de ser devolvida ao `mcpTrigger`.
6.  **Resposta ao Agente AI:** O `mcpTrigger` encarrega-se de enviar a resposta de volta ao agente AI.

## Considerações Gerais

*   **Seguir convenções de nomes:** Crucial para a legibilidade e manutenção.
*   **Etiquetar e nomear claramente cada ferramenta:** O nome da ferramenta é definido no nó `@n8n/n8n-nodes-langchain.toolWorkflow`.
*   **Testar cada subfluxo de forma isolada:** Assegura que cada componente funciona corretamente antes de o integrar. (Ver "Testes e Depuração").
*   **Versionar ferramentas:** A descrição ATDF no nó `toolWorkflow` deve refletir a versão da ferramenta/subfluxo que chama.
*   **Documentar cada versão:** Incluir alterações na descrição ATDF.

## Integração do Formato ATDF (Automatic Tool Definition Format)

### Como Integrá-lo
O bloco de descrição ATDF (em formato YAML) deve ser incluído diretamente no **parâmetro `description` do nó `@n8n/n8n-nodes-langchain.toolWorkflow`** que chama o subfluxo correspondente. Este nó `toolWorkflow` atua como a representação da ferramenta dentro do servidor MCP principal e é o que o agente AI "vê".

### Campos Recomendados para ATDF
*   `description`: Descrição concisa do que a ferramenta faz.
*   `how_to_use`: Detalhes sobre como interagir com a ferramenta, incluindo:
    *   `inputs`: Lista de parâmetros de entrada (nome, tipo, se é requerido, descrição).
    *   `outputs`: Descrição da estrutura de saída esperada (campos `status`, `data` com os seus subcampos, `meta`).
*   `when_to_use`: Casos de uso ou situações onde esta ferramenta é apropriada.

### Exemplo de Bloco ATDF (YAML)

Este bloco seria colocado no campo "Description" de um nó `@n8n/n8n-nodes-langchain.toolWorkflow` que está configurado para chamar o subfluxo `SWF_Get_User_Profile`.

```yaml
---
description: Obtém o perfil de um utilizador a partir do seu ID.
how_to_use:
  inputs:
    - name: user_id # Este 'name' é o que o Agente AI usará
      type: string
      required: true
      description: Identificador único do utilizador.
  outputs:
    status: string (success/error)
    data: (se status for success)
      name: string
      email: string
    data: (se status for error)
      code: string
      text: string # ou message, ser consistente
      details: object
    meta:
      timestamp: string (ISO 8601)
when_to_use: Quando é necessária informação detalhada de um utilizador específico.
---
```

### Mini-Template ATDF Comentado (YAML)

```yaml
---
# Nome descritivo da ferramenta, visível para o agente AI.
# name: tool.minha_acao.minha_entidade
# (O 'name' é geralmente tratado pelo MCP Trigger ou ToolWorkflow,
#  esta seção ATDF vai no campo 'description' desse nó)

# Descrição concisa do que a ferramenta faz.
description: Realiza uma ação específica sobre uma entidade.

# Instruções sobre como usar a ferramenta, incluindo entradas e saídas.
how_to_use:
  inputs:
    # Lista de parâmetros de entrada que a ferramenta espera.
    - name: parametro_requerido
      type: string # Tipos comuns: string, number, boolean, object, array
      required: true # true se o parâmetro for obrigatório, false se opcional.
      description: Descrição detalhada deste parâmetro e seu propósito.
                  # Incluir exemplos de valores, se útil.
    - name: parametro_opcional
      type: number
      required: false
      description: Parâmetro que não é estritamente necessário.
      default: 10 # Valor padrão se não fornecido (informativo para o ATDF).

  outputs:
    # Descrição da estrutura de saída que a ferramenta devolve.
    # Isto deve alinhar-se com o Formato Padrão de Saída do guia.
    status: string # Sempre "success" ou "error".
    data: object # Contentor para os dados da resposta.
      # Subcampos de 'data' se status for "success":
      # resultado_sucesso: string
      # outro_dado: number
      # Subcampos de 'data' se status for "error":
      # code: string
      # message: string (ou text)
      # details: object (com campos field, expected, solution)
    meta: object # Metadados da resposta.
      # timestamp: string # Data e hora em formato ISO 8601.

# Quando esta ferramenta deve ser usada. Descreve os casos de uso apropriados.
when_to_use: Ideal para quando é necessário [descrever o cenário de uso].
             Não usar se [descrever contraindicações ou alternativas].
---
```

### Validação da Sintaxe ATDF (YAML)
O ATDF é escrito em YAML. Para assegurar que a sintaxe da sua descrição ATDF está correta antes de a colar no campo de descrição de um nó n8n, é altamente recomendável validá-la. Pode usar:
- **Editores de Código Modernos:** Muitos editores como o VS Code (com extensões para YAML) realçam erros de sintaxe YAML em tempo real.
- **Validadores de YAML Online:** Existem inúmeras ferramentas web onde pode colar o seu YAML para verificar a sua validade (procure por "yaml linter online").
- **Integração Contínua (CI):** Num ambiente de desenvolvimento mais avançado com Git, pode integrar um validador de YAML no seu processo de CI/CD para verificar automaticamente os arquivos ATDF se os gerir como arquivos separados antes de os copiar para o n8n.

## Uso de Subservidores MCP como Ferramentas

Um servidor MCP (principal) pode utilizar ferramentas expostas por outros servidores MCP (subservidores) através do nó `@n8n/n8n-nodes-langchain.mcpClient`.

### Configuração
*   No fluxo do servidor MCP principal, utiliza-se um nó `@n8n/n8n-nodes-langchain.mcpClient`.
*   Configura-se o `sseEndpoint` do nó `mcpClient` para que aponte para o URL do endpoint do `@n8n/n8n-nodes-langchain.mcpTrigger` do subservidor MCP.
*   Podem-se usar as opções `includeTools` ou `excludeTools` no nó `mcpClient` para filtrar quais ferramentas do subservidor se querem expor ou utilizar.
*   As credenciais para aceder ao subservidor configuram-se no nó `mcpClient`.

### Vantagens
*   **Maior Modularidade e Desacoplamento.**
*   **Escalabilidade Independente.**
*   **Equipas Diferentes.**
*   **Reutilização Segura.**

### Exemplo Visual (Diagrama de Fluxo)

```mermaid
flowchart LR
  A[Agente MCP Principal] --> B("@n8n/n8n-nodes-langchain.mcpClient");
  B -- sseEndpoint: http://github-mcp/sse --> C[Subservidor MCP GitHub (@mcpTrigger)];
  B -- sseEndpoint: http://docs-mcp/sse --> D[Subservidor MCP Documentação (@mcpTrigger)];
  B -- sseEndpoint: http://code-mcp/sse --> E[Subservidor MCP Código (@mcpTrigger)];
```
O nó `mcpClient` (B) no Agente MCP Principal conecta-se a vários subservidores MCP (C, D, E), cada um com o seu próprio `@n8n/n8n-nodes-langchain.mcpTrigger`.

## Considerações sobre a Descrição de Ferramentas Externas (via MCP Client)

Quando um servidor MCP principal utiliza ferramentas de um subservidor MCP através do nó `@n8n/n8n-nodes-langchain.mcpClient`:

*   **Propagação de ATDF:** O `mcpClient` obtém as descrições ATDF das ferramentas diretamente do parâmetro `description` dos nós `@n8n/n8n-nodes-langchain.toolWorkflow` (ou equivalentes) no subservidor.
*   **Visualização no Cliente:** Se o subservidor MCP fornecer descrições ATDF, o `mcpClient` irá mostrá-las.
*   **Descrições Genéricas:** Se o subservidor não fornecer ATDF, o `mcpClient` poderá mostrar uma descrição genérica.
*   **Imutabilidade do Lado do Cliente:** As descrições das ferramentas dos subservidores não podem ser editadas a partir do `mcpClient`. A fonte da verdade é o subservidor.
*   **Interoperabilidade:** Este mecanismo assegura que o servidor principal consome as ferramentas tal como definidas e documentadas pelo subservidor.

## Perguntas Frequentes (FAQ)

**1. O que acontece se um subfluxo (ferramenta) falhar inesperadamente?**
   - O nó `@n8n/n8n-nodes-langchain.toolWorkflow` que chama o subfluxo deveria, idealmente, capturar esta falha.
   - Um subfluxo bem desenhado, seguindo os [Princípios Chave para a Robustez de Fluxos de Trabalho](#princípios-chave-para-a-robustez-de-fluxos-de-trabalho), devolverá um JSON de erro padrão.
   - Se o subfluxo falhar catastroficamente (um nó falhar sem aplicar o Princípio de Robustez #3 ou #4), o `toolWorkflow` poderá receber um erro genérico. Neste caso, é crucial o Princípio de Robustez #5 (uso de "Error Workflows" de nó ou globais).
   - Para nós críticos dentro do subfluxo (ex: chamadas a APIs externas), deve-se aplicar o Princípio de Robustez #3.

**2. Pode-se ter um subfluxo que invoque outro subfluxo?**
   - Sim, absolutamente. Esta é uma prática recomendada para a composição de ferramentas e a reutilização de lógica.
   - Um subfluxo (ex: "Ferramenta Complexa A") pode usar um nó `n8n-nodes-base.executeWorkflow` para chamar outro subfluxo mais simples (ex: "Sub-Ferramenta B").
   - O subfluxo chamador ("Ferramenta Complexa A") deveria tratar a resposta (sucesso ou erro) do subfluxo chamado ("Sub-Ferramenta B") e depois formatar a sua própria resposta padrão (Princípio de Robustez #1) para o `toolWorkflow` que o chamou originalmente. O exemplo "Valida disponibilidade" que chama "Valida intervalo de datas" ilustra este padrão.

**3. Como versionar corretamente os subfluxos e manter a compatibilidade?**
   - **Nomenclatura:** Incluir um número de versão no nome do subfluxo (ex: `SWF_MinhaFerramenta_v1`, `SWF_MinhaFerramenta_v2`).
   - **ATDF:** A descrição ATDF no nó `@n8n/n8n-nodes-langchain.toolWorkflow` que chama o subfluxo deve refletir claramente a versão da ferramenta que está a expor e os parâmetros/saídas esperados para essa versão. Qualquer desvio deve ser considerado um erro pelo subfluxo (Princípio de Robustez #2).
   - **Alterações Não Disruptivas:** Se adicionar nova funcionalidade opcional ou campos não obrigatórios à saída, pode manter a mesma versão principal e atualizar uma menor (ex: v1.1). Assegure-se de que o ATDF é atualizado.
   - **Alterações Disruptivas:** Se alterar nomes de parâmetros, tipos de dados, eliminar campos da saída, ou alterar a lógica fundamental de uma maneira que não seja compatível com versões anteriores, deve criar uma nova versão do subfluxo (ex: `SWF_MinhaFerramenta_v2`). O fluxo principal do servidor MCP deveria então usar um novo nó `@n8n/n8n-nodes-langchain.toolWorkflow` para expor esta nova versão (ex: `tool.minha_ferramenta_v2`).
   - **Git:** Utilize um sistema de controle de versões como Git para guardar as exportações JSON dos seus fluxos de trabalho. Ramos (branches) ou `tags` podem ajudar a gerir as versões.
   - **Depreciação:** Considere manter versões antigas por um tempo e marcá-las como depreciadas no seu ATDF, indicando qual é a nova versão a utilizar.

## Testes e Depuração

Esta seção foca-se em como verificar a implementação dos [Princípios Chave para a Robustez de Fluxos de Trabalho](#princípios-chave-para-a-robustez-de-fluxos-de-trabalho) e depurar problemas.

**1. Testes de Subfluxos (Ferramentas) de Forma Isolada**
   - **Ambiente de Teste:** Considere ter um fluxo de trabalho do n8n dedicado para testar os seus subfluxos individualmente antes de os integrar no servidor MCP principal.
   - **Gatilho Manual:** Neste fluxo de trabalho de teste, pode usar um nó `n8n-nodes-base.manualTrigger` (ou simplesmente o botão "Execute Workflow" com dados de entrada fixos se o subfluxo começar com `n8n-nodes-base.executeWorkflowTrigger`) para iniciar a execução.
   - **Dados de Entrada:** Prepare um nó `n8n-nodes-base.set` ou `n8n-nodes-base.function` para simular os dados de entrada (parâmetros) que o subfluxo esperaria receber do nó `@n8n/n8n-nodes-langchain.toolWorkflow`.
   - **Chamada ao Subfluxo:** Utilize um nó `n8n-nodes-base.executeWorkflow` para chamar o subfluxo que quer testar, passando os dados de entrada simulados.
   - **Verificação da Saída:** Observe a saída do nó `Execute Workflow`. Verifique que:
     - Para casos de sucesso, o JSON de saída coincida com o [Formato Padrão de Saída](#formato-padrão-de-saída) com `status: "success"`.
     - Para casos de erro conhecidos (ex: parâmetros inválidos), o JSON de saída coincida com o [Formato Padrão de Saída](#formato-padrão-de-saída) com `status: "error"` e um `data.code` apropriado.
     - Os dados dentro de `data` e `meta` sejam os corretos para cada caso de teste.
   - **Casos de Teste:** Desenhe múltiplos casos de teste, incluindo:
     - Entradas válidas (caminho feliz) (Verifica Princípio de Robustez #1 e #2).
     - Entradas inválidas (ex: campos em falta, formatos incorretos, valores fora do intervalo) (Verifica Princípio de Robustez #2).
     - Casos limite.
     - Erros esperados de serviços externos (se o subfluxo chamar outras APIs, verifica Princípio de Robustez #3).

**2. Interpretação de Logs**
   (Ver Princípio de Robustez #6 sobre a importância do logging)
   - **Logs do `@n8n/n8n-nodes-langchain.mcpTrigger`:**
     - Mostrará a solicitação completa recebida do agente AI (Langchain), incluindo o nome da ferramenta e os parâmetros.
     - Registrará a resposta final enviada de volta ao agente AI depois que o `toolWorkflow` e o subfluxo tiverem sido executados.
     - Os erros que ocorram diretamente no `mcpTrigger` ou se um `toolWorkflow` não devolver uma resposta válida podem aparecer aqui.
   - **Logs do `@n8n/n8n-nodes-langchain.toolWorkflow`:**
     - Mostrará os parâmetros que recebeu (potencialmente transformados da entrada do `mcpTrigger`, ex: por `$fromAI()`).
     - Indicará qual subfluxo está a chamar.
     - Registrará a resposta JSON completa que recebeu do subfluxo.
     - Se o próprio `toolWorkflow` falhar (ex: não consegue encontrar o subfluxo especificado, ou há um erro na configuração do mapeamento de entradas), o erro será visto neste nó.
   - **Logs do Subfluxo (durante testes isolados):**
     - Ao testar com `Execute Workflow`, pode ver os dados de entrada que o subfluxo recebeu e a saída de cada nó dentro dele. Isto é crucial para depurar a lógica interna.
     - Utilize o painel "Execution Log" no n8n para rastrear o fluxo de dados e os erros em cada passo do subfluxo.

**3. Captura de Erros Silenciosos ou Inesperados**
   - **Design Robusto de Subfluxos (Princípio de Robustez #4):** A causa mais comum de "erros silenciosos" é um subfluxo que não trata todas as suas rotas de erro.
   - **Rever Ramificações de `IF`/`Switch` (Princípio de Robustez #4):** Assegure-se de que todas as possíveis ramificações dos seus nós `IF` ou `Switch` terminem num nó `Set` que produza a estrutura de saída padrão (sucesso ou erro).
   - **Tratamento de Erros em Nós Críticos (Princípio de Robustez #3):** Para nós que podem falhar (ex: `HTTP Request`, `Google Calendar`):
     - Utilize a aba "Configurações" > "Continue On Fail" ou configure um "Error Workflow" para esse nó.
     - Se usar "Continue On Fail", o nó seguinte deve ser um `IF` que verifique se o nó anterior produziu um erro (normalmente `$json.error` estará presente) e redirecione adequadamente.
   - **Error Workflow Global do n8n (Princípio de Robustez #5):** Configure um "Error Workflow" global na sua instância n8n como último recurso.
   - **Validação da Saída do Subfluxo (Avançado):** No fluxo principal, após o nó `@n8n/n8n-nodes-langchain.toolWorkflow`, poderia adicionar um nó `IF` ou `Function` para verificar a estrutura da resposta. Isto é descrito em [Tratamento Global de Erros no Fluxo Principal do Servidor MCP](#tratamento-global-de-erros-no-fluxo-principal-do-servidor-mcp).

## Guia de Exportação/Importação e Versionamento com Git

**1. Exportação e Importação de Fluxos de Trabalho no n8n**
   - **Formato de Exportação:** O n8n permite exportar fluxos de trabalho em formato JSON.
     - Para exportar um fluxo de trabalho, abra-o, clique no menu de três pontos (⋮) no canto superior direito e selecione "Baixar".
     - Recomenda-se guardar o JSON **não compactado (formatado para legibilidade)**. Embora o arquivo seja maior, é muito mais fácil de ler e rever diferenças (`diffs`) no Git. Se o n8n exportar por defeito em formato compacto, pode usar ferramentas externas (como `jq` na linha de comando ou um editor de código) para "embelezar" o JSON antes de o confirmar no Git: `jq . fluxo_compacto.json > fluxo_legivel.json`.
   - **Importação:** Para importar um fluxo de trabalho, a partir do ecrã principal de "Workflows" no n8n, clique em "Novo" e depois selecione "Importar de arquivo" (ou "Importar de URL" se o JSON estiver alojado numa URL).

**2. Estratégia de Versionamento com Git**
   - **Benefícios do Git:**
     - **Histórico de Alterações:** Rastreia cada alteração feita aos seus fluxos de trabalho.
     - **Colaboração:** Permite que múltiplos programadores trabalhem nos mesmos fluxos de trabalho.
     - **Ramificação (`Branching`):** Desenvolva novas funcionalidades ou corrija erros em ramos separados sem afetar a versão principal.
     - **Reversão:** Facilita reverter para versões anteriores se algo correr mal.
     - **Revisão de Código:** Permite rever as alterações (`diffs` no JSON) antes de as fundir.
   - **O que incluir no Repositório?**
     - Os arquivos JSON exportados dos seus fluxos de trabalho do n8n.
     - Potencialmente, scripts utilitários (ex: para formatar JSON, para implantações).
     - Documentação adicional se não estiver toda dentro dos ATDF dos nós.

**3. Organização do Repositório (Sugestões)**
   - Não há uma única forma correta, mas aqui ficam algumas estruturas comuns:
     - **Por Tipo de Fluxo de Trabalho:**
       ```
       /raiz-do-repositorio
       ├── mcp_servers/
       │   ├── auth_server_main.json
       │   └── user_management_server_main.json
       ├── tools/  (ou subworkflows/)
       │   ├── SWF_GetUserProfile_v1.json
       │   ├── SWF_UpdateUserProfile_v1.json
       │   ├── SWF_ValidateDateRange_v1.json
       ├── utilities/ (subfluxos não expostos como ferramentas diretas)
       │   └── SWF_FormatAddress_v1.json
       └── README.md
       ```
     - **Por Domínio ou Projeto:**
       ```
       /raiz-do-repositorio
       ├── projeto_alfa/
       │   ├── mcp_server_alfa.json
       │   ├── tools/
       │   │   └── SWF_AlphaTool1_v1.json
       │   └── subworkflows_internos/
       │       └── SWF_AlphaHelper_v1.json
       ├── projeto_beta/
       │   ├── mcp_server_beta.json
       │   └── tools/
       │       └── SWF_BetaTool1_v1.json
       └── shared_tools/
           └── SWF_CommonUtil_v1.json
       ```
   - **Consistência:** Escolha uma estrutura e seja consistente.
   - **Nomes dos Arquivos:** Use nomes de arquivo descritivos, idealmente incluindo o nome do fluxo de trabalho e a sua versão (ex: `SWF_GetUserProfile_v2.json`). Isto ajuda mesmo antes de abrir o arquivo.
   - **Arquivos `.gitattributes` (Avançado):** Para melhorar os `diffs` de JSON no Git, pode adicionar um arquivo `.gitattributes` na raiz do seu repositório com o seguinte conteúdo para que o Git trate os JSON de maneira mais inteligente para os `diffs` (pode requerer configuração adicional ou não ser suportado por todas as interfaces Git):
     ```
     *.json diff=json
     ```

**4. Fluxo de Trabalho Básico com Git**
   - **Clonar:** `git clone <url_do_repositorio>`
   - **Criar Ramo (Branch):** `git checkout -b minha_nova_funcionalidade`
   - **Modificar Fluxos de Trabalho:** Faça alterações no n8n, exporte o JSON, substitua o arquivo antigo na sua cópia local do repositório.
   - **Rever Alterações:** `git diff nome_do_workflow.json` (para ver o que mudou no JSON).
   - **Adicionar e Confirmar:**
     ```bash
     git add nome_do_workflow.json
     git commit -m "feat: Adicionada validação de entrada a SWF_GetUserProfile_v1"
     ```
     (Siga uma convenção para as mensagens de `commit`, ex: Conventional Commits).
   - **Enviar Alterações:** `git push origin minha_nova_funcionalidade`
   - **Pull Request / Merge Request:** Crie um Pull Request (ou Merge Request) na sua plataforma Git (GitHub, GitLab, etc.) para fundir as alterações no ramo principal (ex: `main` ou `develop`).

## Uso de Etiquetas (Tags) nos Fluxos de Trabalho do n8n

**1. Benefícios do Uso de Etiquetas**
   - Em ambientes n8n com uma grande quantidade de fluxos de trabalho, as etiquetas (`tags`) são uma ferramenta poderosa para organizar, filtrar e encontrar fluxos de trabalho rapidamente.
   - Permitem categorizar os fluxos de trabalho por diversos critérios, como a sua função, estado, versão, ou o projeto a que pertencem.
   - Facilitam a gestão e a manutenção, especialmente em equipas grandes ou com múltiplos projetos.

**2. Como Usar Etiquetas no n8n**
   - Para adicionar ou editar etiquetas de um fluxo de trabalho, pode fazê-lo a partir da vista de lista de "Workflows":
     - Passe o cursor sobre o fluxo de trabalho.
     - Clique no ícone de etiqueta (`tag`) que aparece.
     - Escreva o nome da etiqueta e pressione Enter. Pode adicionar múltiplas etiquetas.
   - Também pode gerir etiquetas ao editar um fluxo de trabalho, usualmente num painel de configuração do próprio fluxo de trabalho (a localização exata pode variar ligeiramente com as versões do n8n).

**3. Estratégias de Etiquetagem Sugeridas para Servidores MCP e Ferramentas**
   - **Tipo de Fluxo de Trabalho:**
     - `mcp-server`: Para o fluxo de trabalho principal que atua como servidor MCP (o que contém o `@n8n/n8n-nodes-langchain.mcpTrigger`).
     - `mcp-tool`: Para subfluxos que representam uma ferramenta específica e são chamados por um `@n8n/n8n-nodes-langchain.toolWorkflow`.
     - `subworkflow-helper`: Para subfluxos internos que não são ferramentas diretas mas são reutilizados por outros (ex: uma utilidade de formatação).
   - **Domínio/Funcionalidade da Ferramenta:**
     - `tool:user-management`
     - `tool:document-processing`
     - `tool:calendar-operations`
     - `module:authentication`
   - **Versão:**
     - `v1.0`
     - `v1.1`
     - `v2.0-beta`
     - `tool-version:1.2` (se quiser ser mais específico para diferenciar da versão do servidor MCP)
   - **Estado:**
     - `status:active`
     - `status:development`
     - `status:deprecated` (para ferramentas ou servidores que serão substituídos)
     - `status:experimental`
   - **Projeto ou Cliente (se aplicável):**
     - `project:alpha`
     - `client:acme-corp`
   - **Prioridade ou Criticidade (opcional):**
     - `priority:high`
     - `critical`

**4. Exemplos Combinados**
   - Um fluxo de trabalho servidor MCP para utilizadores poderia ter as etiquetas: `mcp-server`, `module:user-management`, `v1.0`, `status:active`.
   - Um subfluxo que é uma ferramenta para obter perfis de utilizador: `mcp-tool`, `tool:user-management`, `tool-version:1.0`, `status:active`.
   - Um subfluxo utilitário para validar datas usado por várias ferramentas: `subworkflow-helper`, `module:utils`, `v1.0`, `status:active`.

**5. Filtragem por Etiquetas**
   - Na vista de lista de "Workflows" do n8n, usualmente há uma barra de pesquisa ou um controlo de filtro que permite escrever nomes de etiquetas para mostrar apenas os fluxos de trabalho que as contenham. Isto agiliza enormemente a localização de fluxos de trabalho específicos.

**Recomendação:** Defina uma convenção de etiquetagem para a sua equipa ou organização e seja consistente na sua aplicação. Um bom sistema de etiquetagem é inestimável à medida que a sua instância n8n cresce.

## Tratamento Global de Erros no Fluxo Principal do Servidor MCP

Esta seção aborda como o fluxo principal do servidor MCP deve tratar falhas relacionadas com a orquestração de ferramentas, complementando os [Princípios Chave para a Robustez de Fluxos de Trabalho](#princípios-chave-para-a-robustez-de-fluxos-de-trabalho) que se aplicam a cada subfluxo.

**1. Importância do Tratamento de Erros ao Nível do Servidor Principal**
   - Assegura que o agente AI que consome o servidor MCP receba uma resposta coerente (Princípio de Robustez #1) mesmo que ocorram problemas inesperados na orquestração das ferramentas antes que um subfluxo específico seja invocado ou depois que este (supostamente) tenha completado a sua execução.

**2. Cenários de Erro no Fluxo Principal e Como Tratá-los**

   **a. Falha do Nó `@n8n/n8n-nodes-langchain.toolWorkflow`**
      - **Causa Possível:** O subfluxo especificado no nó `toolWorkflow` não existe (ex: ID incorreto, não importado), ou há um problema crítico com a configuração do próprio nó `toolWorkflow` que impede que sequer tente executar o subfluxo.
      - **Tratamento:**
        - Aplicar o Princípio de Robustez #5: Configurar a aba "Configurações" > "Error Workflow" para o nó `@n8n/n8n-nodes-langchain.toolWorkflow`. Este Error Workflow dedicado pode então gerar uma resposta JSON padrão (ex: com `status: "error"`, `data.code: "TOOL_EXECUTION_FAILED"`, e uma mensagem apropriada).
        - Um "Error Workflow" global para a instância n8n (Princípio de Robustez #5) também atuaria como uma salvaguarda.

   **b. Subfluxo Devolve uma Resposta Estruturalmente Inválida**
      - **Causa Possível:** Um subfluxo (ferramenta) termina e devolve dados, mas estes não se ajustam ao formato esperado (ex: falta o campo `status`, ou `status` não é nem `"success"` nem `"error"`). Isto indica um incumprimento do Princípio de Robustez #1 por parte do subfluxo.
      - **Tratamento:**
        - Após cada nó `@n8n/n8n-nodes-langchain.toolWorkflow` no fluxo principal (ou após um nó `Switch` que encaminha para vários `toolWorkflows`), adicionar um nó `n8n-nodes-base.if` para validar a estrutura da resposta.
        - **Condições do `IF`:** Verificar se o campo `status` existe e se é `"success"` OU `"error"`.
        - **Ramificação FALSE do `IF` (Resposta Inválida):**
          - Conectar a um nó `n8n-nodes-base.set` que construa uma resposta de erro padrão.
          - Exemplo de JSON de erro:
            ```json
            {
              "status": "error",
              "data": {
                "code": "INVALID_TOOL_RESPONSE_STRUCTURE",
                "message": "A ferramenta devolveu uma resposta com uma estrutura inesperada.",
                "details": {
                  "tool_name": "{{ $json.tool_name_if_available }}",
                  "received_response_preview": "{{ JSON.stringify($json).slice(0, 200) }}"
                }
              },
              "meta": {
                "timestamp": "{{ $now.toJSON() }}"
              }
            }
            ```
        - **Ramificação TRUE do `IF` (Resposta Válida):** Continuar o fluxo normalmente.

   **c. Erro no Roteador (ex. Nó `Switch`)**
      - **Causa Possível:** O nome da ferramenta fornecido pelo agente AI não coincide com nenhuma das rotas definidas no nó `Switch`.
      - **Tratamento:**
        - O nó `Switch` no n8n tem uma saída "Default" ou "Fallback". Conectar esta saída a um nó `n8n-nodes-base.set`.
        - Este nó `Set` deve gerar uma resposta de erro padrão (Princípio de Robustez #1) indicando que a ferramenta não foi encontrada.
        - Exemplo de JSON de erro:
          ```json
          {
            "status": "error",
            "data": {
              "code": "TOOL_NOT_FOUND",
              "message": "A ferramenta solicitada não está disponível ou não é reconhecida.",
              "details": {
                "requested_tool_name": "{{ $json.tool_name_from_ai_if_available }}"
              }
            },
            "meta": {
              "timestamp": "{{ $now.toJSON() }}"
            }
          }
          ```

**3. Considerações Adicionais**
   - **Consistência:** Todos os erros gerados pelo fluxo principal devem também seguir o formato JSON padrão (Princípio de Robustez #1).
   - **Logging (Registro) (Princípio de Robustez #6):** Considere adicionar nós de log (ex: `n8n-nodes-base.logMessage`) nestas rotas de erro globais para facilitar a depuração de problemas ao nível da orquestração.
   - **Error Workflow Global do n8n (Princípio de Robustez #5):** Um Error Workflow global é uma rede de segurança crucial.

Um tratamento de erros robusto ao nível do fluxo principal do servidor MCP complementa o tratamento de erros dentro de cada subfluxo, criando um sistema mais resiliente e previsível.
