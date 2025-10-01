[Home](index.md) | [Especificação](specification.md) | [Exemplos](examples.md) | [Guia MCP do n8n](n8n_mcp_server_guide.md) | [Contribuir](contributing.md) | [Multilíngue](multilingual.md) | [Histórico de Alterações](changelog.md) | [Licença](license.md)

**Idiomas:** [English (en)](../en/index.md) | [Español (es)](../es/index.md) | [Português (pt)](index.md)

## 📚 Documentação Principal

- **[Especificação ATDF](../docs/ATDF_SPECIFICATION.md)** - Especificação completa do formato
- **[Conceitos Fundamentais](../docs/CONCEPTS.md)** - Explicação de conceitos-chave
- **[Exemplos de Implementação](../docs/examples.md)** - Exemplos em múltiplas linguagens e ferramentas
- **[Guia de Implementação](./IMPLEMENTATION_GUIDE.md)** - Como implementar ATDF
- **[Melhores Práticas](./BEST_PRACTICES.md)** - Recomendações para implementação

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
- [Compatibilidade de Versões](version_compatibility.md): Tabela que relaciona rótulos antigos aos esquemas atuais.
- [Exemplos](examples.md): Descrições de ferramentas de exemplo e como criar as suas.
- [Suporte Multilíngue](multilingual.md): Informações sobre o uso de múltiplos idiomas.
- [Contribuir](contributing.md): Diretrizes para contribuir com o ATDF.
- [Fluxo ATDF + MCP + n8n](n8n_mcp_fluxo_integracao.md): Arquitetura e cenários de integração.
- [Guia de Redesign](redesign_guidelines.md): Considerações centrais para evoluir o protocolo.
- [Histórico de Alterações](changelog.md): Histórico de versões e alterações do ATDF.

## Primeiros Passos

1. **Escolha o esquema certo**
   - 1.x básico (`schema/atdf_schema.json`): descrições essenciais com `tool_id`, `description`, `when_to_use` e `how_to_use`.
   - 2.x avançado (`schema/enhanced_atdf_schema.json`): acrescenta `metadata`, `localization`, `prerequisites`, `examples` e `feedback`.
   Consulte [Compatibilidade de Versões](version_compatibility.md) em caso de dúvida.

2. **Escreva a descrição**

```json
{
  "schema_version": "2.0.0",
  "tool_id": "validador_datas",
  "description": "Valida intervalos de datas e sugere correções",
  "when_to_use": "Use quando precisar detalhar por que um intervalo de datas é inválido",
  "how_to_use": {
    "inputs": [
      {"name": "data_inicial", "type": "string", "description": "Data inicial ISO 8601", "required": true},
      {"name": "data_final", "type": "string", "description": "Data final ISO 8601", "required": true}
    ],
    "outputs": {
      "success": "Intervalo válido",
      "failure": [
        {"code": "INVALID_DATE_RANGE", "description": "A data inicial deve ser menor que a final"}
      ]
    }
  }
}
```

Para um descriptor 1.x use `schema_version` = "1.0.0" e omita campos opcionais como `metadata` e `examples`.

3. **Valide e teste**

```bash
python tools/validator.py sua_tool.json --schema schema/atdf_schema.json
python tools/validate_enhanced.py sua_tool.json
python tests/run_all_tests.py
```

Veja a [Guia de Respostas Enriquecidas](enriched_responses_guide.md) para a estrutura de erros detalhados.
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
