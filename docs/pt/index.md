[Home](index.md) | [Especificação](specification.md) | [Exemplos](examples.md) | [Guia MCP do n8n](n8n_mcp_server_guide.md) | [Contribuir](contributing.md) | [Multilíngue](multilingual.md) | [Histórico de Alterações](changelog.md) | [Licença](license.md)

**Idiomas:** [English (en)](../en/index.md) | [Español (es)](../es/index.md) | [Português (pt)](index.md)

## 📚 Documentação ATDF

### 📖 **Documentos Principais**
- **[README](../../README.md)** - Introdução e guia rápida
- **[Especificação ATDF](./specification.md)** - Especificação completa do formato
- **[Conceitos Fundamentais](./CONCEPTS.md)** - Explicação de conceitos-chave
- **[Exemplos de Implementação](./examples.md)** - Exemplos em múltiplas linguagens e ferramentas
- **[Guia de Implementação](./IMPLEMENTATION_GUIDE.md)** - Como implementar ATDF
- **[Melhores Práticas](./BEST_PRACTICES.md)** - Recomendações para implementações robustas

### 📊 **Recursos Visuais**
- **[Diagramas Mermaid](../MERMAID_DIAGRAMS.md)** - Diagramas de fluxo e arquitetura ATDF

# Formato de Descrição de Ferramentas para Agentes (ATDF)

Bem-vindo à documentação do **Formato de Descrição de Ferramentas para Agentes (ATDF)**, um protocolo aberto para descrever ferramentas funcionalmente para permitir que agentes de IA as selecionem e usem com base no propósito, contexto e operação, sem depender de detalhes específicos de implementação.

## Versão Atual

**Versão atual: 0.2.0** - Consulte o [histórico de alterações](changelog.md) para detalhes sobre as últimas atualizações.

## Introdução

O ATDF foi projetado para resolver o problema de integração de ferramentas para agentes de IA. Em vez de exigir nomes de ferramentas codificados ou APIs técnicas complexas, o ATDF fornece uma maneira padronizada de descrever ferramentas com base em:

1.  **O que** a ferramenta faz
2.  **Quando** deve ser usada
3.  **Como** é usada

Essa abordagem funcional permite que os agentes de IA selecionem ferramentas com base na tarefa em mãos, em vez de exigir conhecimento específico sobre nomes de ferramentas ou APIs.

## Funcionalidades Principais

### Funcionalidades Base (v0.1.0)
- **Formato Simples e Legível por Humanos**: Estrutura JSON/YAML fácil de entender.
- **Agnóstico ao Modelo**: Funciona com qualquer modelo de agente de IA.
- **Agnóstico à Ferramenta**: Descreve tanto ferramentas físicas (ex., furadeiras) quanto ferramentas digitais (ex., APIs).
- **Agnóstico ao Prompt**: Seleção de ferramentas baseada na função, não em nomes específicos.
- **Validação de Esquema**: Esquema JSON para validar descrições de ferramentas.

### Funcionalidades Aprimoradas (v0.2.0)
- **Suporte a Metadados**: Organize ferramentas com informações de versão, autor, tags e categoria.
- **Suporte Multilíngue Rico**: Localização integrada para múltiplos idiomas.
- **Pré-requisitos e Dependências**: Especifique ferramentas, condições e permissões necessárias.
- **Mecanismos de Feedback**: Indicadores de progresso e sinais de conclusão.
- **Exemplos de Uso**: Exemplos do mundo real com entradas e saídas esperadas.
- **Tipos de Entrada Complexos**: Suporte para objetos aninhados e esquemas avançados.

## Links Rápidos

- [Especificação](specification.md): Especificação técnica detalhada do protocolo ATDF.
- [Exemplos](examples.md): Descrições de ferramentas de exemplo e como criar as suas.
- [Suporte Multilíngue](multilingual.md): Informações sobre o uso de múltiplos idiomas.
- [Contribuir](contributing.md): Diretrizes para contribuir com o ATDF.
- [Histórico de Alterações](changelog.md): Histórico de versões e alterações do ATDF.

## Primeiros Passos

Para começar a usar o ATDF, você pode:

1.  **Explorar Exemplos**: Confira as [descrições de ferramentas de exemplo](examples.md) para entender o formato.
2.  **Criar as Suas**: Siga a [especificação](specification.md) para criar descrições de ferramentas.
3.  **Validar Ferramentas**: Use o validador para garantir que suas descrições de ferramentas sejam válidas:
    ```bash
    python tools/validator.py caminho/para/sua/ferramenta.json
    ```
4.  **Experimentar a Demo**: Execute os agentes de demonstração para ver o ATDF em ação:
    ```bash
    python tools/demo/atdf_showcase.py
    ```
    (Nota: estes scripts podem precisar existir ou ser adaptados)

## Casos de Uso

O ATDF é projetado para uma ampla gama de aplicações, incluindo:

- **Agentes de IA**: Ajudar sistemas de IA a selecionar e usar ferramentas apropriadamente.
- **Robótica**: Descrever ferramentas físicas para sistemas robóticos.
- **Integração de API**: Padronizar descrições de APIs e serviços web.
- **Aplicações Multimodais**: Unificar diferentes tipos de ferramentas em um formato comum.
- **Sistemas Multilíngues**: Suportar descrições de ferramentas em diferentes idiomas.

## Licença

O ATDF é licenciado sob a Licença MIT. Consulte o arquivo [LICENSE](license.md) para mais detalhes.

---

[Repositório GitHub](https://github.com/MauricioPerera/agent-tool-description-format) | [Histórico de Alterações](changelog.md) 