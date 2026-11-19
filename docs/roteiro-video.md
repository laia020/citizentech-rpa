# Roteiro RPA - até 3 minutos

**Estado: roteiro preparado; vídeo não gravado nem publicado.** A integração real já foi demonstrada no [run `44327757282`](https://github.com/laia020/citizentech-rpa/actions/runs/44327757282). Mostrar essa execução e suas evidências preservadas, identificando a data; não repetir inferência apenas para filmar. Screenshots, logs e PDF não substituem o vídeo.

**Mensagem central:** o RPA automatiza o processo em lote e utiliza o serviço de IA existente do mesmo produto. O vídeo desta disciplina demonstra validação, decisões, repetição, tratamento de exceções e auditoria. A entrega de IA explica o componente analítico separadamente. A importação no backend do Akona fica como evolução futura. [Narração pronta para ensaiar](narracao-video-rpa.md).

| Tempo | Fala e demonstração |
|---|---|
| 0:00–0:20 | “Akona Energy organiza relatos de iluminação. O RPA confere lotes fictícios, evita repetição e separa pendências.” Mostrar nome do produto e `examples/lote-real.json`, com `simulada: true`. |
| 0:20–0:45 | Mostrar o BPMN: leitura, validação, repetição sequencial, consulta e auditoria. Identificar que o destino final é revisão humana. |
| 0:45–1:20 | Abrir o run real concluído e o resumo: 4 entradas, 2 processadas, 1 duplicada, 1 pendência e 0 falhas. Mostrar que restaurou `44296159102`, sem criar estado novo, em runner Ubuntu hospedado. |
| 1:20–2:00 | Abrir os resultados: `RPA-LIVE-20261118-001` com análise preliminar e `RPA-LIVE-20261118-002` com informação insuficiente. Correlacionar os IDs e `request_id` com a auditoria HTTP 200. Explicar: dados fictícios, chamada real à IA; informação insuficiente é resposta válida. |
| 2:00–2:30 | Mostrar a duplicata com o mesmo `request_id`, sem outra consulta, e o registro incompleto sem API. Mostrar também o histórico 503, identificado como execução anterior, e as tentativas limitadas. O estado atual é `44327757282`; sucessos são preservados. |
| 2:30–2:55 | Mostrar GitHub e relatório atualizado. Explicar que não houve criação de chamado no Akona, reparo ou ganho municipal medido. O resultado exige revisão humana. |

## Material a deixar aberto

1. Repositório público e `examples/lote-real.json`.
2. BPMN macro e detalhado, ou as páginas correspondentes do PDF.
3. Run real `44327757282` e seu resumo.
4. `docs/evidencias/nuvem-real/resultados.json` e `auditoria.jsonl`, ou os artifacts do mesmo run. O `request_id` do ID `001` é `333fecbe-114f-4603-824e-43b7fa8dd2d6`; o do ID `002` é `5e25fa23-6c84-423e-87f8-9a1fb4e849d3`.
5. Histórico separado em `docs/evidencias/real-indisponibilidade/` e `real-retomada/`.
6. PDF revisado e CI histórica de 26 testes, identificada como suíte com rede simulada.

## Conferência antes e depois da gravação

- As evidências e esta revisão foram publicadas com autorização; ver `docs/evidencias/publicacao-revisao.json`. Conferir os links públicos antes de gravar. Mudanças futuras continuam sujeitas à autorização de publicação.
- Não apagar o banco, iniciar estado novo, mudar IDs para repetir consultas ou reexecutar sucessos para gravar. A gravação pode mostrar a execução concluída e os arquivos autênticos, identificando isso em voz e tela.
- Se uma nova execução for necessária por outro motivo legítimo, conferir o run mais recente e restaurar seu `rpa-state`. O último conhecido aqui é `44327757282`. Não usar o ancestral `44296159102`. Artifacts expiram; seguir as regras de reconciliação do README.
- O Windows não executa nativamente o RPA por causa de `fcntl`; não apresentar a geração local do PDF como execução do lote. O processamento real foi hospedado no GitHub.
- Gravar a demonstração verdadeira, com texto legível, sem segredos e duração final **≤ 3:00**. Cortes de espera devem ser identificados, preservando IDs e resultados.
- Publicar o vídeo e conferir acesso ao link. Inserir a URL verdadeira no README, em `docs/entrega.json` e no PDF; regenerar e revisar o relatório novamente.
- Alinhar a ficha comum com o grupo e preparar o envio por um integrante na tarefa de **RPA do Teams**, até **19/11/2026 às 23h55**. Não declarar o envio concluído antes da confirmação real.
