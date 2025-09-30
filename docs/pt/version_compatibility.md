[Home](index.md) | [Especificação](specification.md) | [Exemplos](examples.md) | [Contribuir](contributing.md) | [Multilíngue](multilingual.md) | [Histórico de Alterações](changelog.md) | [Licença](license.md)

**Idiomas:** [English (en)](../en/version_compatibility.md) | [Español (es)](../es/version_compatibility.md) | [Português (pt)](version_compatibility.md)

# Compatibilidade de Versões ATDF

Este guia resume como as versões históricas do ATDF se relacionam com os esquemas JSON atuais e seus recursos.

## Matriz de esquemas e funcionalidades

| Versão do esquema | Nome legado | Recursos principais | Uso recomendado |
| ------------------ | ----------- | ------------------- | --------------- |
| 1.x (`schema/atdf_schema.json`) | ATDF v0.1 Básico | Metadados essenciais (`tool_id/id`, `description`, `when_to_use`, `how_to_use.inputs/outputs`) e lista simples de erros | Agentes que precisam apenas de invocações declarativas |
| 2.x (`schema/enhanced_atdf_schema.json`) | ATDF v0.2 Avançado | Adiciona `metadata`, `localization`, `prerequisites`, `examples` e campos estruturados de `feedback` | Assistentes multilíngues, marketplaces e integrações ricas |
| Esquema de respostas enriquecidas (`schema/enriched_response_schema.json`) | ATDF v2.0 Error Envelope | Payload canônico com `expected`, `solution` e blocos de contexto | Qualquer ferramenta que entregue instruções corretivas |

## Notas de compatibilidade

- O esquema 2.x é um superconjunto do 1.x; descrições básicas permanecem válidas.
- Descrições aprimoradas devem declarar `schema_version` = "2.0.0" (ou superior) para que os validadores selecionem o esquema correto.
- As respostas de erro enriquecidas podem ser adotadas de forma independente desde que respeitem `enriched_response_schema.json`.
- Documentos legados escritos para ATDF v0.1/v0.2 correspondem diretamente aos esquemas 1.x/2.x acima. Atualize as referências para usar os caminhos de esquema quando possível.

## Checklist de migração

1. Confirme qual esquema a descrição deve usar e declare `schema_version` explicitamente.
2. Valide com `python tools/validator.py ... --schema schema/atdf_schema.json` para 1.x ou `python tools/validate_enhanced.py ...` para 2.x.
3. Ao migrar para 2.x, adicione as novas seções gradualmente: comece com `metadata.version`, depois localização e pré-requisitos.
4. Adote o esquema de erros enriquecidos junto com a atualização da ferramenta para fornecer diagnósticos consistentes.
