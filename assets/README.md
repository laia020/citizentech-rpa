# Diagramas e evidências visuais

- `bpmn-macro.svg` e `bpmn-item.svg`: vistas vetoriais geradas da definição BPMN editável em `docs/processo.bpmn`. A imagem do subprocesso é detalhamento do item repetido sequencialmente na vista macro.
- `bpmn-macro.png` e `bpmn-item.png`: versões raster para consulta e relatório.
- `execucao-evidencia.png`: painel **gerado dos JSON/logs preservados**, com simulação, histórico HTTP 503 e integração real HTTP 200 identificados. A linha de sucesso vem do run `44327757282`: 2 processadas, 1 duplicada, 1 pendência e 0 falhas. Não é screenshot do site Akona nem prova de criação de chamado.

Fontes BPMN: eventos de início/fim, gateways exclusivos, tarefas, subprocesso de múltiplas instâncias sequenciais, evento de erro de borda e fluxos de mensagem entre participantes. Layout e XML são gerados por `scripts/gerar_bpmn.py`; ao editar, manter consistência entre fonte, imagens e relatório.
