[Home](index.md) | [Especificação](specification.md) | [Exemplos](examples.md) | [Guia MCP do n8n](n8n_mcp_server_guide.md) | [Contribuir](contributing.md) | [Multilíngue](multilingual.md) | [Histórico de Alterações](changelog.md) | [Licença](license.md)

**Idiomas:** [English (en)](../en/index.md) | [Español (es)](../es/index.md) | [Português (pt)](index.md)

## 🚀 Início rápido

1. **Escolha o esquema certo**
   - 1.x básico (`schema/atdf_schema.json`): descrições essenciais com `tool_id`, `description`, `when_to_use` e `how_to_use`.
   - 2.x avançado (`schema/enhanced_atdf_schema.json`): acrescenta `metadata`, `localization`, `prerequisites`, `examples` e `feedback`.
   Consulte a [Compatibilidade de Versões](../web/versions.html) em caso de dúvida.

2. **Escreva o descritor**

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

Para um descritor 1.x defina `schema_version` = "1.0.0" e omita campos opcionais como `metadata` e `examples`.

3. **Valide e teste**

```bash
python tools/validator.py sua_tool.json --schema schema/atdf_schema.json
python tools/validate_enhanced.py sua_tool.json
python tests/run_all_tests.py
```

Consulte o [Guia de Respostas Enriquecidas](enriched_responses_guide.md) para estruturar erros detalhados.

## 📚 Documentação principal
- **[Especificação ATDF](../docs/ATDF_SPECIFICATION.md)** – Referência completa do formato
- **[Conceitos Fundamentais](../docs/CONCEPTS.md)** – Explicação dos conceitos-chave
- **[Exemplos de Implementação](../docs/examples.md)** – Casos em múltiplas linguagens e frameworks
- **[Guia de Implementação](IMPLEMENTATION_GUIDE.md)** – Como integrar ATDF às suas ferramentas
- **[Melhores Práticas](BEST_PRACTICES.md)** – Recomendações e padrões comprovados
- **[Fluxo ATDF + MCP + n8n](n8n_mcp_fluxo_integracao.md)** – Arquitetura e cenários de integração

### Recursos visuais
- **[Diagramas Mermaid](../MERMAID_DIAGRAMS.md)** – Diagramas de fluxo e arquitetura do ATDF

## 🔌 Integrações em destaque
- **n8n + MCP + ATDF**: siga o [guia de integração](n8n_mcp_fluxo_integracao.md) para conectar o bridge ATDF-MCP e executar ferramentas no n8n (nós nativos ou personalizados).
- **API REST e Autenticação do n8n**: `../../n8n_setup_complete.md` — como autenticar e importar workflows via REST.
- **Workflow Code v3 (n8n)**: `../../n8n-workflows/README.md` — reserva completa de viagem usando MCP Bridge.
- **Guia rápido (ES)**: `../../GUIA_INTEGRACION_N8N.md` — configuração ATDF + MCP + n8n.
- **Índice central n8n + MCP + ATDF**: `../n8n_mcp_atdf_index.md` — mapa unificado da documentação.
- **Bridge ATDF-MCP local**:
  ```bash
  python examples/fastapi_mcp_integration.py
  python examples/mcp_atdf_bridge.py --port 8001 --atdf-server http://localhost:8000
  ```

## ⭐ Funcionalidades chave
- **Erros enriquecidos**: contexto completo (`expected`, soluções, valores sugeridos).
- **Suporte multilíngue**: localização integrada para descrições e erros.
- **Validação automática**: detecção de versão de esquema e validação de entradas/saídas.
- **Interoperabilidade**: SDKs Python/JavaScript, conversores MCP e nós para n8n.

## 📦 Casos de uso
- **Agentes de IA** que precisam descobrir ferramentas por função e contexto.
- **APIs e microserviços** que exigem respostas de erro consistentes.
- **Workflows low-code/no-code** (n8n, Zapier) que consomem metadados declarativos.
- **Marketplaces de ferramentas** com catálogos multilíngues e permissões granulares.

## 🤝 Como contribuir
- Confira o [guia de contribuição](contributing.md) para fluxo de trabalho, checklist de PR e estilo.
- Execute `python tests/run_all_tests.py` e `npm test` (em `js/`) antes de abrir um PR.
- Mantenha as traduções sincronizadas em `docs/en`, `docs/es` e `docs/pt`.

## 📄 Licença
O ATDF é distribuído sob a licença MIT. Consulte [License](license.md) para mais detalhes.

---

**ATDF v2.0.0** – Formato padrão para descrever ferramentas de forma funcional, habilitando agentes mais inteligentes, fluxos multilíngues e respostas de erro enriquecidas.
