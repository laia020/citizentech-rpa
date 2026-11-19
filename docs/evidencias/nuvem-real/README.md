# Integracao real hospedada em 18/11/2026

Run: https://github.com/laia020/citizentech-rpa/actions/runs/44327757282

O workflow restaurou o estado do run 44296159102 e consultou a IA publica com dados ficticios. Foram 4 entradas: 2 processadas, 1 duplicada, 1 pendencia e 0 falhas. Duas chamadas retornaram HTTP 200; uma analise preliminar e uma resposta de informacao insuficiente. Os IDs e request_id estao correlacionados em resultados.json e auditoria.jsonl. O RPA executado valida as respostas contra o contrato congelado antes de marcar processado.

O novo estado de referencia e o run 44327757282. Nao repetir sucessos para demonstracao. ZIPs originais e backup do SQLite permanecem em tmp/nuvem-real-20261118-114522/, fora do Git. As evidencias historicas de HTTP 503 foram preservadas. Esta pasta ainda nao foi publicada por commit/push.

Esta verificacao nao executou novamente a suite automatizada. A integracao com o backend/interface do Akona, o alinhamento da ficha, o video e o envio ao Teams continuam pendentes. O PDF e os documentos de status foram atualizados localmente para incorporar esta evidencia; a publicacao da revisao aguarda autorizacao.
