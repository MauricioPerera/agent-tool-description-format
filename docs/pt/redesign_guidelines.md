# Guia de Redesign do ATDF

## Propósito
Orientações para definir uma nova geração do Agent Tool Description Format (ATDF) sem comprometer a interoperabilidade com os ecossistemas de agentes existentes.

## Tópicos a cobrir
- **Escopo do protocolo**: Problema endereçado, cenários suportados, relação com padrões existentes (JSON Schema, OpenAPI, MCP etc.).
- **Modelo de dados**: Campos obrigatórios, extensões opcionais, aliases, regras de tipagem, esquemas de parâmetros, entradas condicionais.
- **Semântica de uso**: when_to_use, how_to_use, convenções de entrada/saída, negociação de versão, descoberta de capacidades.
- **Modelo de erros**: Estrutura padrão de payloads, contexto diagnóstico, dicas de remediação, mapeamento para erros de transporte ou execução.
- **Ciclo de vida e versionamento**: Fluxo de publicação, política de versionamento semântico, cronogramas de depreciação, expectativas de compatibilidade.
- **Segurança e permissões**: Indicadores de escopos necessários, limites de uso, nível de risco, prompts de consentimento.
- **Extensibilidade**: Mecanismos para metadados específicos de fornecedores, regras de namespacing, processo de registro para extensões da comunidade.
- **Ferramentas e suporte**: Validadores, SDKs, exemplos, servidores de referência, suites de conformidade.
- **Governança**: Processo decisório, controle de mudanças, obrigações de documentação, requisitos multilíngues.

## Armadilhas a evitar
- **Superespecificação**: Incorporar suposições sobre runtimes ou camadas de transporte que limitem a adoção.
- **Subespecificação**: Deixar comportamentos essenciais ambíguos, principalmente em campos opcionais ou valores padrão.
- **Quebras sem migração**: Remover ou renomear campos sem aliases ou ignorar o versionamento semântico.
- **Lógica de negócio embutida**: Permitir lógica executável ou estado dinâmico dentro das descrições em vez de metadados declarativos.
- **Campos redundantes ou conflitantes**: Introduzir conceitos sobrepostos que confundem as implementações de agentes.
- **Negligenciar validação**: Publicar sem ferramentas de linting, validação de esquemas ou suites de conformidade.
- **Ignorar localização**: Não definir como devem ser fornecidas traduções de descrições e orientações.
- **Lacunas de segurança**: Omitir formas de expressar permissões, necessidades de auditoria ou considerações de privacidade.

## Processo recomendado
1. Elabore um modelo de referência que cubra os tópicos acima e colete feedback de integradores.
2. Prototipe as atualizações de esquema e atualize validadores, SDKs e documentação em paralelo.
3. Forneça guias de migração, exemplos práticos e testes automatizados antes de declarar o redesign estável.
4. Estabeleça artefatos de governança (roadmap, processo de RFC, changelog) para orientar revisões futuras.
