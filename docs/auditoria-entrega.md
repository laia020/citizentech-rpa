# Auditoria da entrega de RPA

Conferência em **18/11/2026**, comparando a cópia local com o enunciado original **Desafio-FIAP-GS-CitizenTech 4ES.pdf**, encontrado em Downloads. SHA-256 da fonte: `236c35530bc23f3f6c48211f022862ff5d1458f17ad2d813e1f9d5130b696c87`. Páginas de RPA: 45–50; regras comuns: 18–24. O PDF original não foi copiado para o repositório.

## Resultado da conferência

A implementação e as evidências disponíveis cobrem mapeamento, desenvolvimento em Python, decisões e repetição, falhas, logs e testes. A integração RPA–IA por API está comprovada. A revisão documental atual está local; **a entrega ainda não está pronta para envio**, pois faltam o vídeo, seu link no PDF, a confirmação da ficha comum e a publicação autorizada da revisão.

Não houve nova inferência, execução da aplicação no Windows ou reexecução da suíte durante esta auditoria. Os fontes atuais são comparados aos hashes do registro histórico; os 26 testes e a CI são evidências existentes, sem serem apresentados como testes novos.

## Oito etapas obrigatórias

| Etapa | Página da fonte | Evidência conferida | Estado |
|---|---:|---|---|
| 1. Mapeamento do processo | 47 | `docs/PDD.md`, `docs/processo.bpmn`, imagens e páginas 3–4 do relatório. | Preparado |
| 2. Desenvolvimento | 47 | `src/citizentech_rpa/`, Python, `pyproject.toml`, `uv.lock` e repositório público. | Implementado e publicado; revisão documental local |
| 3. Lógica de negócio e lote | 47 | Laço sequencial, validação, duplicidade, conflito, pendências e separação de `status_rpa`/`status_ia`. Lotes demonstrativos preservados. | Comprovado |
| 4. Exceções e resiliência | 47 | Histórico real HTTP 503; testes de indisponibilidade, arquivo ausente/inválido, limites, timeout e recuperação. | Comprovado no escopo registrado |
| 5. Logs e auditoria | 48 | `auditoria.jsonl`, resumos, horários UTC, contagens, tentativas e códigos sanitizados. | Comprovado |
| 6. Integração com o MVP | 48 | Resultado da normalização do RPA enviado à API da IA existente; dois HTTP 200 e correlação de IDs no run `44327757282`. | Integração técnica por API demonstrada; enquadramento acadêmico descrito abaixo |
| 7. Testes e validação | 48 | `docs/evidencias/testes.json`, `testes.txt`, CI `44296622327` e nove cenários preservados. | Evidência histórica conferida; suíte não reexecutada |
| 8. Documentação e publicação | 48 | Estrutura, README, documentos, PDF e exemplos existentes. Evidências novas e revisão aguardam commit/push. | Parcial |

## Interpretação explícita da integração

O item 6 diz: **“O resultado deve ser consumido por outro componente da CitizenTech”**, permitindo API, banco ou arquivo estruturado. O texto não exige por nome o backend do Akona, nem especifica que o único resultado aceito seja o arquivo final `resultados.json`.

A justificativa adotada é: o RPA lê, valida e normaliza a ocorrência; esse resultado estruturado é consumido via API pelo componente de IA existente do mesmo produto. A resposta devolvida é validada e correlacionada ao ID, preservando os resultados da análise. Esse fluxo foi executado em nuvem e tem evidência real, não apenas diagramas ou respostas simuladas.

Essa é a interpretação técnica usada na entrega, sujeita à avaliação dos professores. **A importação da saída final no backend/interface do Akona não foi implementada.** Também não houve confirmação documental da arquitetura comum do grupo nesta auditoria. Não apresentar essa fronteira adicional como concluída nem prometer a pontuação de integração.

## Repositório exigido na página 49

| Item | Local | Estado |
|---|---|---|
| Descrição, integrantes, arquitetura, instruções e links | `README.md` | Preparado; link de vídeo pendente |
| Código Python | `src/` | Existente e publicado |
| PDD e fluxo | `docs/PDD.md`, `docs/processo.bpmn` | Preparado |
| Imagens e evidências | `assets/`, `docs/evidencias/` | Preparado; evidência nova ainda local |
| Logs sem dados sensíveis | `logs/`, auditorias dos cenários | Amostras fictícias existentes |
| Testes e instruções | `tests/`, README e registros de CI | Existentes |
| UiPath/Power Automate | Não utilizados | Não se aplica à implementação em Python |

## Conteúdo do relatório técnico exigido na página 49

| Exigência | Páginas do relatório | Estado |
|---|---|---|
| Nome completo e RM de todos | 1 | Conferido |
| CitizenTech e problema | 1–2 | Presente; território e ficha sujeitos ao alinhamento comum |
| Objetivo e benefício ao cidadão | 1–2 | Presente como benefício proposto, sem impacto inventado |
| Processo e fluxo | 2–4 | Presente, com fonte BPMN editável |
| Tecnologias e justificativa | 2 e 7 | Presente |
| Regras, decisões e processamento | 2 e 4–6 | Presente |
| Exceções e recuperação | 4, 6–7 | Presente |
| Logs e auditoria | 5–6 | Presente |
| Descrição e evidências da integração | 5 e 8 | RPA–IA comprovada; limites declarados |
| Testes de sucesso, decisão e falha | 6 | Registros históricos identificados |
| Segurança e LGPD | 7 | Presente com limites da POC |
| Link do GitHub e link do vídeo | 8 | GitHub presente; vídeo pendente |

## Vídeo e envio

O vídeo precisa ter até **3 minutos**, apresentar problema/papel, mostrar o processo de ponta a ponta e demonstrar decisão, integração e falhas (página 49). Existem [roteiro](roteiro-video.md) e [narração](narracao-video-rpa.md), mas **não existe gravação ou URL informada**. A duração do vídeo não foi medida.

Usar os registros autênticos do run concluído, identificando sua data. Não repetir inferência nem apagar estado para filmar. A narração deve acompanhar uma demonstração das telas e dos arquivos, não apenas a leitura de um texto. Se o professor exigir uma nova execução durante a gravação, ela deve ser planejada com o estado mais recente e sem reenvio dos sucessos.

O envio é feito por um integrante na tarefa de RPA do Teams, até **19/11/2026 às 23h55** (páginas 24 e 46). Repositórios, aplicações e vídeo devem ficar públicos e funcionando durante a correção, prevista em até uma semana após o encerramento. Não houve envio ao Teams nesta auditoria.

## O que falta para liberar o envio

- [ ] Confirmar a ficha comum com o grupo, especialmente território, arquitetura e indicadores; não marcar alinhamento sem confirmação.
- [ ] Gravar o vídeo e medir duração de até 3:00.
- [ ] Publicar o vídeo e conferir acesso ao link.
- [ ] Informar URL e duração em `docs/entrega.json`, inserir o link no README, regenerar e revisar o PDF.
- [ ] Autorizar e executar commit/push da revisão, conferindo a publicação dos documentos e evidências.
- [ ] Executar a conferência final: `uv run --no-sync python scripts/validar_entrega.py --online --final`.
- [ ] Revisar a seleção de arquivos e enviar na tarefa RPA do Teams; conferir o comprovante.

`validar_entrega.py` confere artifacts preservados e documentação. O modo `--final` deve recusar prontidão enquanto houver itens obrigatórios faltantes; não grava vídeo, publica alterações ou envia ao Teams.

Rubrica da página 50: integração **1 ponto**, documentação **2**, desenvolvimento **5**, vídeo **2**. Esta auditoria não atribui nota nem substitui a avaliação.
