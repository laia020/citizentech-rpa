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

## Continuidade no Windows e integração real

Em 18/11/2026, após nova autorização para continuar, inspecionamos a cópia Windows e preservamos o projeto. Python 3.12.10 e uv já estavam instalados. O uso de `fcntl` impede execução nativa da aplicação; usamos o runner Ubuntu existente, sem alterar o armazenamento ou a IA.

O [run `44327757282`](https://github.com/laia020/citizentech-rpa/actions/runs/44327757282) restaurou o estado `44296159102` e concluiu o lote real: 2 processadas, 1 duplicada, 1 pendência e 0 falhas, com duas chamadas HTTP 200. Respostas, auditoria e proveniência estão em `evidencias/nuvem-real/`. Os seis HTTP 503 anteriores foram preservados. A API foi acionada uma vez para disparar o workflow; acompanhamento e download foram feitos pelo MCP. Não houve mudança de código da aplicação, commit, push ou deploy.

A revisão documental preservou backup datado em `tmp/backups/documentacao-20261118-140547/`. Uma `.venv` nova foi criada com Python 3.12.10 e `uv sync --locked --group docs`, exclusivamente para geração e conferência documental; ambientes externos foram preservados. Nenhuma suíte ou nova inferência foi executada nessa revisão. PDF, painel e validação documental são gerados dos registros existentes.

Próximos passos: alinhar ficha com o grupo, gravar/publicar vídeo de até 3 minutos, inserir o link e revisar novamente o PDF, conferir a publicação das alterações finais e enviar na tarefa RPA do Teams. O estado de referência é `44327757282`, sempre conferindo se houve run posterior. Evidências em `docs/evidencias/nuvem-real/`; backup local do estado em `tmp/nuvem-real-20261118-114522/rpa-state-44327757282.zip`, fora do Git.

## Publicação da revisão com evidências reais

Após autorização explícita do usuário para commit e push, a revisão foi publicada na `main` a partir do commit `6b6a2061480c6ca633ed0a408e0d13dfedd75da3`. README, respostas reais preservadas e PDF foram conferidos por acesso público, sem credenciais; registro em `evidencias/publicacao-revisao.json`. Os históricos de falha e as auditorias anteriores foram mantidos. Código da aplicação e projeto de IA não foram alterados. Vídeo, ficha comum e envio ao Teams permanecem pendentes.
