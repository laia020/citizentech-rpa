# PDD - Recepção e triagem de ocorrências fictícias em lote

Ficha Técnica comum: [abertura do README](../README.md). Produto: Akona Energy. Território: Osasco/SP demonstrativo, a alinhar com a equipe. Disciplina: Robotic Process Automation; Bruno Diniz e Cibele Ribeiro. Atividade: Do Processo Manual à Automação Inteligente.

## Processo manual (AS-IS)

Operador lê cada relato, confere informações, procura o ID em uma planilha, separa repetições e encaminha para triagem. O processo descrito é uma hipótese operacional da POC, sem observação de operação municipal real ou tempo cronometrado de atendimento.

## Processo automatizado (TO-BE)

Início: operador escolhe um lote fictício e dispara uma execução. Entradas: CSV UTF-8 ou JSON lista, até 100 itens e 1 MiB. O lote demonstrativo tem quatro entradas. Pré-condições: Python 3.12, dependências fixadas, diretório gravável e estado preservado; acesso à IA apenas em modo real.

1. Abrir auditoria e registrar execução e horário UTC com fuso.
2. Ler arquivo: arquivo ausente, formato, UTF-8, cabeçalho ou coleção inválida encerram com erro explícito, sem API.
3. Adquirir lock do estado. Outra execução com a mesma base é recusada com `estado_em_uso`.
4. Repetir sequencialmente para cada registro. Normalizar texto e defaults, validar campos e a restrição de dados fictícios.
5. Registro incompleto, desconhecido ou incoerente: registrar pendência. Não inferir dado ausente.
6. Consultar `(modo, ID)` e fingerprint: sucesso idêntico reutiliza resposta; divergência vira conflito; falha 429/503 só pode ser retomada explicitamente; envio interrompido ou resultado incerto exige revisão.
7. Registro novo ou falha retomável: gravar marcador antes do POST. Mapear apenas campos do contrato da IA. Em simulação, usar cliente fixo explicitamente identificado, sem rede.
8. Tratar status HTTP e validar corpo e correlação. Um 200 válido pode conter análise preliminar, informação insuficiente ou fora de escopo. Todos requerem pessoa responsável pelo encaminhamento.
9. Salvar o resultado do item no SQLite; registrar auditoria, preservar os outros resultados e seguir ao próximo item.
10. Gerar resultados, pendências e resumo em diretório novo. Fim: operador revisa pendências e evidências; nenhuma manutenção física é disparada.

## Decisões e saídas

| Situação | Status RPA / decisão |
|---|---|
| Válido + análise válida | `processado`; destino depende de `analise.status`. |
| IA informa dado insuficiente | `processado` / `complementar_informacoes`; não é falha técnica. |
| IA recusa fora de escopo | `processado` / `revisao_de_escopo`. |
| Sucesso anterior com mesmo ID e conteúdo | `duplicado`, preservando request e execução originais; zero nova chamada. |
| Mesmo ID, conteúdo diferente | `pendente` / `id_conflitante`, sem sobrescrever estado. |
| Incompleto ou campo extra | `pendente`, sem API nem armazenamento do conteúdo bruto inválido. |
| 429/503 após limite | `falha`, retomável por opção explícita. |
| 413/422/502 | `falha`, sem repetição automática; revisar entrada/serviço. |
| Timeout, resposta inválida ou envio interrompido | Falha/pendência de resultado incerto; revisão humana, sem replay automático. |

## Recuperação, monitoramento e responsabilidade

Preservar `state/` e `runs/`; retomar somente com a mesma base. O estado não é reconstruído a partir de prints. Para resultado incerto, consultar o responsável pela IA e correlacionar logs quando disponível; a API atual não oferece busca por ID nem garantia de idempotência remota. Não apagar/editar a base para mascarar falhas. Mudanças de conteúdo em ID já reservado precisam de decisão humana e uma nova versão/ID rastreável, preservando o original.

O operador monitora `resumo.json`, códigos de saída e `pendencias.json`. O workflow apresenta contagens e arquiva resultados inclusive em erro de API. Em infraestrutura interrompida, revisar itens com marcador `em_envio`; se houver falha de disco antes da exportação, resultados já confirmados permanecem na base, desde que o disco tenha preservado as gravações. Não há serviço de monitoramento permanente.

## BPMN

Fonte editável: [processo.bpmn](processo.bpmn). Vista macro: início/fim, tarefa de leitura, gateway exclusivo, subprocesso com múltiplas instâncias **sequenciais**, tratamento de arquivo e exportação. Vista detalhada: validação/estado, caminhos de pendência e duplicata, tarefa de serviço da IA, evento de erro de borda, persistência e mensagens entre participantes RPA e IA. A rotina de timeout/tentativas fica encapsulada na tarefa de serviço e descrita acima; não é um fluxograma renomeado.

## Critérios de aceite e limites

Testes de sucesso, decisão e falha devem passar e produzir evidência. Os 26 testes aprovados são o registro histórico da suíte, com rede simulada; a conferência documental local não os reexecutou. A CI roda na publicação. O consumo real pela IA foi demonstrado no [run `44327757282`](https://github.com/laia020/citizentech-rpa/actions/runs/44327757282), com duas respostas HTTP 200 validadas: análise preliminar e informação insuficiente. Foram 4 entradas, 2 processadas, 1 duplicada, 1 pendência e 0 falhas. A duplicata não repetiu a consulta. As falhas HTTP 503 anteriores foram preservadas.

O estado de referência é o desse run, sujeito à conferência de execuções posteriores. Não há importação pelo Akona, comprovação de reparo ou validação municipal. GitHub público, CI e workflows hospedados foram executados; as evidências novas e a revisão documental foram publicadas com autorização. Vídeo, alinhamento da ficha e envio ao Teams continuam pendentes.
