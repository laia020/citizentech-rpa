# Evidências preservadas

- `enunciado-origem.json`: identificação e SHA-256 do PDF original conferido em Downloads, com páginas e critérios. O PDF de terceiros não foi copiado para o repositório.
- `auditoria-criterios.json`: registro da conferência contra o original, evidências técnicas e pendências externas; complemento da [auditoria legível](../auditoria-entrega.md).

- `tdd-inicial.txt`: primeira execução dos testes de API/pipeline antes da implementação, falhando por módulo ausente. Evidência local, sem commit anterior.
- `tdd-cloud-inicial.txt`: testes do ponto de entrada da nuvem antes do script correspondente.
- `testes.json` e `testes.txt`: execução final automatizada; transporte de IA simulado. Nenhum teste destrutivo no serviço público.
- `simulado/`: execução real do **simulador**, 4 entradas, 1 processada, 1 duplicada e 2 pendências. Não houve inferência.
- `real-indisponibilidade/`: execução contra API pública, HTTP 503 nas quatro tentativas, 2 IDs válidos; sem análise bem-sucedida. Repetição idêntica cujo original falhou fica pendente para revisão, por isso não há duplicado de sucesso.
- `real-retomada/`: retomada controlada dez minutos depois, mesma base e lote; duas chamadas, ambas HTTP 503. Sem chamadas adicionais para a duplicata interna ao lote.
- `simulado-repeticao/`: reaproveitamento do mesmo estado; 0 novas análises, 2 duplicatas de sucesso, 2 pendências.
- `csv-simulado/` e `arquivo-ausente/`: execução CLI em CSV e falha real de leitura local, ambas sem rede de IA.
- `cloud-entrada-local.txt`: smoke test local do script de workflow; **não é execução hospedada**.
- `contrato-origem.json`: origem, data UTC e SHA-256 do OpenAPI coletado.
- `validacao-artefatos.json`: inspeção do PDF, links, fonte BPMN e integridade das evidências. Não substitui avaliação funcional do grupo.

Os arquivos em `logs/` são cópias sanitizadas das auditorias dessas execuções. São exemplos pequenos com dados fictícios. Resultados históricos são preservados; não substituir uma execução que falhou por um sucesso simulado. O resumo contém SHA-256 do lote para vincular aos arquivos de `examples/`.

Na verificação inicial, os links do MVP, repositório da IA, demonstração, API/OpenAPI e GitHub Docs retornaram HTTP 200. Na revalidação durante a publicação, o HEAD do MVP apresentou falha de rede; o resultado atual é preservado em `validacao-artefatos.json`, sem inferir a causa ou alterar o serviço. A documentação oficial do uv retornou HTTP 403 ao HEAD deste ambiente; seu conteúdo foi consultado pela ferramenta web. Essa restrição de acesso é registrada, sem afirmar que todos os links responderam 200. O GitHub do RPA foi publicado com autorização e sua URL foi inserida no relatório. A URL de vídeo permanece pendente, sem ser inventada.

- `nuvem-simulado/`: primeiro lote no executor hospedado do GitHub, modo simulado, 4 entradas, 1 processada, 1 duplicada e 2 pendências. `github-run.json` vincula os arquivos ao run público e ao commit executado. Não houve inferência de IA.
- `nuvem-repeticao/`: segundo run hospedado restaurou o artifact de estado do primeiro, com 0 novos processamentos e 2 duplicatas. Modo simulado, sem rede de IA.
- `publicacao.json`: repositório público verificado sem credenciais, SHA executado, CI com 26 testes aprovados e links dos dois runs hospedados.
- `nuvem-real/`: [run `44327757282`](https://github.com/laia020/citizentech-rpa/actions/runs/44327757282), restaurando `44296159102`, com duas respostas HTTP 200 validadas, 2 processadas, 1 duplicada, 1 pendência e 0 falhas. Preserva análise preliminar e informação insuficiente, IDs e `request_id`. `github-run.json` registra a origem e os hashes dos artifacts. As cópias locais e a revisão documental aguardam commit/push autorizado.
- `validacao-atual.json`: conferência documental da revisão com integração bem-sucedida, sem nova inferência nem execução da suíte. Inclui validação das respostas preservadas, hashes, contagens, equipe e PDF. Reconhece equivalência LF/CRLF nos hashes textuais e registra quando ela foi usada. Não substitui `validacao-artefatos.json`, que permanece como histórico da revisão anterior.

O estado de referência após a integração é o run **44327757282**; verificar se houve runs posteriores antes de executar outro lote. ZIPs originais e backup desse estado permanecem em `tmp/nuvem-real-20261118-114522/`, fora do Git. São oito chamadas reais documentadas: seis HTTP 503 iniciais e duas HTTP 200 posteriores. Não houve reexecução da suíte de 26 testes durante esta revisão.
