# Plano enxuto e decisões

Fonte: enunciado FIAP CitizenTech 4ES, páginas 18–24 e 45–50, lido do PDF local em 18/11/2026. O arquivo é fonte de requisitos, não autorização para publicar, enviar mensagens ou alterar sistemas.

1. Inspecionar ambiente e contrato público. Diretório não existia; Python 3.12.16 e uv 0.13.6 já estavam instalados. Sem requisitos preexistentes conflitantes. Consultadas as notas de continuidade do Mac.
2. Escrever testes antes do código. Primeira execução registrada em `evidencias/tdd-inicial.txt`; testes de restauração escritos antes do ponto de entrada da nuvem, em `tdd-cloud-inicial.txt`.
3. Implementar CLI em Python, sem servidor e sem bibliotecas de IA. JSON Schema usa o OpenAPI congelado; SQLite oferece persistência proporcional à POC; arquivos por UUID evitam sobrescrita.
4. Usar simulação explicitamente identificada na suíte e realizar um pequeno lote real. HTTP 503 observado, sem consumo bem-sucedido por IA nessa execução. Preservar a falha em vez de transformar simulação em prova de integração.
5. Preparar workflow hospedado, PDD, BPMN, PDF e roteiro. Revisar resultados antes de solicitar publicação. Nenhum commit, push ou deploy nesta etapa.

## O que é obrigatório e o que é escolha técnica

Obrigatórios: os oito requisitos da matriz, código Python público/versionado, relatório PDF com BPMN, equipe e links, vídeo até 3 min, entrega RPA no Teams.

Escolhas desta POC: CSV/JSON, lote fictício de iluminação, Python 3.12, uv, jsonschema, SQLite, integração opcional RPA–IA e GitHub Actions manual. O PDF não exige simultaneamente Python, UiPath, n8n e Power Automate, tarefa agendada permanente ou importação no Akona por endpoint inventado.

## Fronteiras

Não alterar o projeto de IA, seus pesos, corpus, prompts, treinamento, ambiente ou implantação. Não instalar bibliotecas de IA. Não enviar chamados ao Akona publicado. Não contatar terceiros. Não confundir comunicação HTTP com análise remota bem-sucedida ou importação no MVP. Repositório do Akona e alinhamento da ficha técnica dependem do grupo.

## Publicação autorizada em 18/11/2026

Após a revisão da POC, o usuário autorizou subir o projeto ao Git. Código publicado em https://github.com/laia020/citizentech-rpa, preservando a etapa local acima como histórico. A CI foi aprovada e o primeiro workflow de lote foi executado com sucesso em runner hospedado, modo simulado. Não foi feita nova chamada real à IA nem alteração no Akona publicado.
