# Roteiro RPA - até 3 minutos

**Estado: roteiro preparado; vídeo real não gravado nem publicado.** Screenshots, log e PDF não substituem o vídeo. A integração com análise 200 precisa ser demonstrada quando o serviço estiver disponível; se continuar 503, explicar a limitação e não apresentar simulação como consumo real.

| Tempo | Fala e demonstração |
|---|---|
| 0:00–0:20 | “Akona Energy organiza relatos de iluminação. Esta POC automatiza a conferência de lotes fictícios, evitando repetição e separando pendências.” Mostrar nome do produto e quatro registros. |
| 0:20–0:45 | Mostrar o BPMN: leitura, validação, repetição sequencial, consulta e auditoria. Identificar que o destino final é revisão humana. |
| 0:45–1:25 | Disparar o workflow hospedado autorizado, com lote fictício pequeno. Mostrar o modo escolhido. Abrir resultados: registro válido, duplicata, conflito ou incompleto. Em modo simulado, declarar isso em voz e tela. |
| 1:25–2:05 | Mostrar execução real RPA–IA, payload mapeado e `request_id`/análise quando 200. Evidenciar correlação do ID. Se 503, mostrar a falha real e informar que o consumo com análise permanece pendente. Não afirmar criação de chamado no Akona. |
| 2:05–2:35 | Mostrar auditoria, tentativas limitadas, retorno de erro e preservação dos outros itens. Pode usar a falha HTTP 503 já observada ou teste automatizado claramente identificado. Reexecutar com o mesmo estado para mostrar idempotência, sem repetir sucesso na IA. |
| 2:35–2:55 | Mostrar resumo, GitHub público e relatório. Explicar dados fictícios, revisão humana e independência do Mac, somente se o workflow hospedado tiver sido executado. |

## Sequência reproduzível

1. Antes de gravar: publicar com autorização, executar CI, conferir artefatos e links, obter resposta 200 real se disponível. Preparar as abas de workflow, lote, resultados e relatório. Não apagar estado de demonstração anterior. Usar um novo lote/ID rastreável apenas quando for uma execução nova legítima; não contornar rejeições.
2. Primeiro use `lote-demo.json`, modo `simulado`, estado preservado. A expectativa com estado novo é 1 processado, 1 duplicado, 2 pendências. Depois repita com o mesmo estado: 0 processados, 2 duplicados, 2 pendências.
3. Para a integração, use `lote-real.json`, modo `real`. Se o estado contém 429/503, indique retomada explícita. Se já contém sucesso, mostre o resultado original e a duplicata atual; não repita a API apenas para filmar.
4. Para erro de arquivo local, opcional: `citizentech-rpa examples/nao-existe.json --modo simulado`. O arquivo não precisa existir: auditoria deve registrar `arquivo_ausente`, exit 2 e zero chamadas.
5. Grave a execução verdadeira. Se for necessário condensar a espera, use corte identificado e preserve os mesmos IDs antes/depois. Não montar uma interface falsa ou misturar resposta simulada com execução real.
6. Conferir duração final ≤ 3:00, texto legível, ausência de segredos e acesso ao link. Inserir URL do vídeo e do GitHub no README e no PDF; regenerar e revisar o relatório. Um integrante envia na tarefa de RPA no Teams.
