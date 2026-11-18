# Diagramas e evidências visuais

- `bpmn-macro.svg` e `bpmn-item.svg`: vistas vetoriais geradas da definição BPMN editável em `docs/processo.bpmn`. A imagem do subprocesso é detalhamento do item repetido sequencialmente na vista macro.
- `bpmn-macro.png` e `bpmn-item.png`: versões raster para consulta e relatório.
- `execucao-evidencia.png`: painel **gerado dos JSON/logs de execuções reais**, com simulação e comunicação HTTP 503 identificadas. Não é screenshot do site Akona nem prova de criação de chamado.

Fontes BPMN: eventos de início/fim, gateways exclusivos, tarefas, subprocesso de múltiplas instâncias sequenciais, evento de erro de borda e fluxos de mensagem entre participantes. Layout e XML são gerados por `scripts/gerar_bpmn.py`; ao editar, manter consistência entre fonte, imagens e relatório.
