# Narração do vídeo de RPA

Texto para ensaio, com janelas planejadas de 2min55s. **A duração precisa ser medida na gravação**; não há vídeo gravado ou publicado. Mostrar a execução concluída de 18/11/2026 e seus arquivos autênticos. Não disparar outra inferência para filmar.

## 0:00–0:20 — Produto e papel do RPA

Na tela: README e `examples/lote-real.json`.

> Este é o componente de RPA do Akona Energy. Ele recebe ocorrências fictícias de iluminação pública em lote e organiza a triagem. O RPA cuida da automação do processo e utiliza o serviço de IA existente do mesmo produto para analisar os registros válidos.

## 0:20–0:45 — Processo e decisões

Na tela: BPMN, páginas 3 e 4 do relatório.

> O processo começa pela leitura de CSV ou JSON. Cada registro passa por validação e consulta ao estado. Informações incompletas ficam pendentes; sucessos repetidos são reutilizados; um mesmo ID com conteúdo diferente gera conflito. Os registros aptos seguem sequencialmente para a IA, e o resultado fica disponível para revisão humana.

## 0:45–1:20 — Execução hospedada comprovada

Na tela: [run `44327757282`](https://github.com/laia020/citizentech-rpa/actions/runs/44327757282) e `docs/evidencias/nuvem-real/resumo.json`.

> Esta é a execução real concluída em 18 de novembro, no GitHub Actions, em um runner Ubuntu hospedado. Ela restaurou o estado da execução anterior. O lote teve quatro entradas: duas processadas, uma duplicada, uma pendência e nenhuma falha. Os dados são fictícios, mas as chamadas ao serviço de IA foram reais. Não estou disparando uma nova consulta nesta gravação.

## 1:20–2:00 — Integração e rastreabilidade

Na tela: `resultados.json` e `auditoria.jsonl` em `docs/evidencias/nuvem-real/`. Destacar as linhas dos IDs terminados em `001` e `002`, seus `request_id` e os dois HTTP 200.

> A primeira ocorrência recebeu uma análise preliminar. A segunda recebeu informação insuficiente, pois uma leitura ADC sem referência de calibração não permite concluir um valor em lux. Essa resposta é um sucesso operacional, com encaminhamento para complementação. As duas consultas retornaram HTTP 200. O RPA validou o contrato e a correspondência dos IDs; os identificadores de requisição ligam os resultados à auditoria.

## 2:00–2:30 — Duplicatas, pendências e falhas

Na tela: duplicata do ID `001`, pendência `observacao_ausente` e auditoria histórica em `docs/evidencias/real-retomada/`.

> A ocorrência duplicada reutilizou a mesma resposta, sem outra consulta. O registro sem observação foi separado antes da IA. As falhas HTTP 503 anteriores também foram preservadas: o cliente limita tentativas, e resultados incertos exigem revisão. O SQLite mantém o estado; ele não deve ser apagado para repetir a demonstração.

## 2:30–2:55 — Entregáveis e limite

Na tela: repositório e relatório técnico, páginas 5 e 8.

> A entrega de RPA inclui código, BPMN, testes históricos e evidências da integração com IA. O componente de IA produz a análise; aqui demonstramos o processo que o utiliza. A importação no backend do Akona fica como evolução futura. Nenhum chamado ou reparo foi acionado, e o encaminhamento final depende de revisão humana.

## Preparação e conferência

- Deixar os arquivos locais e as páginas do run abertos antes de gravar; mostrar trechos legíveis, evitando rolagem longa. Não é necessário ler os UUIDs completos em voz alta.
- Identificar as falhas 503 como histórico anterior e o sucesso como a execução de 18/11/2026. A suíte de 26 testes usa clientes simulados; não apresentá-la como uma nova execução contra a IA.
- Medir a duração no ensaio. Se ultrapassar três minutos, reduzir as pausas e encurtar a explicação do BPMN, mantendo a identificação da chamada real e os limites.
- Não afirmar que outro sistema importou `resultados.json`, que houve criação de chamado, reparo, impacto municipal medido ou garantia de nota.
- Após gravar e publicar, conferir o acesso à URL real, inseri-la nos documentos e revisar o PDF final. A publicação das mudanças do repositório continua sujeita à autorização do usuário.
