# Guia para Pessoas Recém-Chegadas ao Projeto

## Resumo rápido
Agent Tool Description Format (ATDF) é uma especificação independente de implementação que padroniza como agentes de IA descobrem e operam ferramentas externas. Ela define esquemas JSON para catálogos de ferramentas e respostas de erro enriquecidas, permitindo que os agentes decidam quando e como acionar cada capacidade disponível.

## Status atual
⚠️ Este trilho de onboarding ainda está pendente de implementação. Considere o roteiro abaixo como uma lista preliminar até que a equipe designe responsáveis e produza os materiais de suporte.

## Estrutura do repositório
- **Esquemas (`schema/`)** – Documentos JSON Schema oficiais para os descritores ATDF clássicos (1.x) e aprimorados (2.x), além do envelope de erros enriquecidos.
- **Ferramentas em Python (`tools/`, `sdk/`)** – Validadores de linha de comando, utilitários de conversão e um SDK em Python (`ATDFTool`, carregadores de catálogos, busca multilíngue, auto-seleção) que interpretam descritores e executam consultas de catálogo programaticamente.
- **SDK JavaScript (`js/`)** – Utilitários para Node.js/navegador que espelham os recursos do SDK em Python, incluindo busca vetorial opcional, assistentes de localização e conversores MCP→ATDF.
- **Exemplos (`examples/`)** – Aplicação de referência em FastAPI, demonstrações de cenários e testes de integração que exibem o tratamento de erros ATDF ponta a ponta, fluxos de reserva e integração com o Model Context Protocol (MCP).
- **Documentação (`docs/`)** – Especificações, guias de implementação, tutoriais de integração (FastAPI, n8n, monitoramento) e conteúdo multilíngue sincronizado entre inglês/espanhol/português.
- **Automação e fluxos (`n8n-*`, `monitoring/`, `scripts/`)** – Workflows prontos para importar no n8n, painéis de monitoramento e scripts auxiliares para levantar ambientes de demonstração.

## Conceitos fundamentais para aprender primeiro
1. **Descritores de ferramentas** – Entenda os campos obrigatórios e opcionais nos esquemas ATDF clássico e aprimorado, incluindo metadados de localização, pré-requisitos e exemplos guiados.
2. **Respostas de erro enriquecidas** – Estude o envelope de erro compartilhado (`schema/enriched_response_schema.json`) para que seus serviços entreguem sugestões de correção acionáveis aos agentes.
3. **Padrões de uso dos SDKs** – Observe como os SDKs de Python e JavaScript carregam catálogos, realizam busca textual/vetorial e auto-selecionam ferramentas para evitar reimplementar lógica de parsing.
4. **Ponte FastAPI MCP** – Utilize o aplicativo de exemplo em `examples/` como implementação de referência e ambiente de testes ao integrar ATDF em novos runtimes.

## Boas práticas ao colaborar no repositório
- Valide descritores desde cedo com `tools/validator.py` ou `tools/validate_enhanced.py` antes de distribuí-los.
- Execute as suítes de testes em Python e JavaScript (`python tests/run_all_tests.py`, `npm test` dentro de `js/`) para detectar regressões nos SDKs.
- Use os workflows FastAPI + n8n como testes de sistema ao ajustar a lógica do servidor ou integrações MCP.
- Mantenha a documentação localizada: quaisquer mudanças em `docs/en` devem ser refletidas em `docs/es` e `docs/pt`.

## Próximos passos para o onboarding
1. Leia o **Guia de Implementação** (`docs/IMPLEMENTATION_GUIDE.md`) para entender padrões arquiteturais, estratégia de validação e considerações de implantação.
2. Explore os **exemplos dos SDKs** em `sdk/` e `js/` para ver carga de catálogos, manipulação de metadados multilíngues e extração de esquemas na prática.
3. Siga os **tutoriais n8n + MCP** (`docs/*n8n*`) para compreender a orquestração ponta a ponta e o tratamento de erros em fluxos de automação.
4. Revise os **roteiros de monitoramento** (`monitoring/`) para aprender como implantações em produção acompanham métricas de erro ATDF e saúde operacional.
