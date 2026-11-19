# Contratos e fronteiras de integração

Ficha Técnica: [README](../README.md). API confirmada em 18/11/2026 por HTTP GET de `/openapi.json`; o snapshot está empacotado com o RPA e seu SHA-256 consta em `evidencias/contrato-origem.json`.

## Escopo adotado para a demonstração

A entrega de RPA demonstra a automação em lote integrada ao serviço de IA existente do mesmo produto. O RPA é responsável por validação, decisões, repetição, estado e auditoria; a IA recebe o payload normalizado e produz a análise. O backend/interface do Akona não participa deste fluxo demonstrado; sua importação fica como evolução futura.

Há duas fronteiras diferentes: **a ocorrência resultante da validação e normalização do RPA, enviada à IA**, já foi consumida com sucesso; **a importação do arquivo final `resultados.json` pelo Akona** não foi implementada. O original foi conferido: a página 48 exige que outro componente consuma o resultado via API, banco ou arquivo estruturado; não determina um backend ou um arquivo final específico. A justificativa desta entrega usa a primeira fronteira, comprovada por contrato e respostas reais. O enquadramento acadêmico segue sujeito à avaliação, sem declarar consumo inexistente na segunda fronteira. Fonte e conferência em [auditoria da entrega](auditoria-entrega.md).

As duas disciplinas podem demonstrar o mesmo serviço com focos distintos: a entrega de IA explica o componente analítico; a entrega de RPA explica o processo automatizado que o utiliza. Código, relatório e vídeo de RPA permanecem próprios, sem alegar que o RPA treinou ou modificou o modelo.

## RPA → IA existente

Endpoint fixo: `POST https://laia020-citizentech-iluminacao-ia.hf.space/v1/analisar`. Corpo é construído por whitelist a partir do esquema `Occurrence`. `tipo`, `bairro` e `ponto` ficam apenas no RPA. A API recebe somente dados fictícios marcados `simulada: true` e alguma observação. A saída é validada contra `AnalysisResponse`, incluindo correspondência de `ocorrencia_id` e `request_id` não vazio.

O status operacional fica em `status_rpa`; o status de negócio da IA em `status_ia`. Uma recusa válida não vira erro HTTP fictício. A resposta integral válida fica em `ia`, sem reparar JSON nem reconstruir trechos faltantes. Todos os encaminhamentos requerem revisão humana.

**Evidência atual:** o [run hospedado `44327757282`](https://github.com/laia020/citizentech-rpa/actions/runs/44327757282), execução `dd5f0bb6ea1f4cd6bd39db4fa78b0385`, concluiu em modo real em 18/11/2026 às 11:45 (Brasília). Restaurou o estado do run `44296159102`, sem inicializar uma base nova. As duas chamadas retornaram HTTP 200 e passaram pela validação de contrato e correlação. Contagens: 4 entradas, 2 processadas, 1 duplicada, 1 pendência, 0 falhas. [Resultados](evidencias/nuvem-real/resultados.json), [auditoria](evidencias/nuvem-real/auditoria.jsonl) e [proveniência](evidencias/nuvem-real/github-run.json).

| Ocorrência fictícia | Status da IA | `request_id` |
|---|---|---|
| `RPA-LIVE-20261118-001` | `analise_preliminar` | `333fecbe-114f-4603-824e-43b7fa8dd2d6` |
| `RPA-LIVE-20261118-002` | `informacao_insuficiente` | `5e25fa23-6c84-423e-87f8-9a1fb4e849d3` |

A repetição da primeira ocorrência reutilizou o mesmo resultado e `request_id`, sem nova consulta. O registro sem observação foi separado para revisão, sem API. A informação insuficiente é uma resposta de negócio válida e processada, com destino `complementar_informacoes`. O consumo bem-sucedido pelo componente de IA está demonstrado; o backend/interface do Akona continua sem consumo. As cópias novas de evidência foram publicadas com autorização; a origem e a verificação pública constam em [publicacao-revisao.json](evidencias/publicacao-revisao.json).

**Histórico preservado:** a execução `0ec3479a81ff41908c7d6529429ff274` recebeu HTTP 503 nas duas tentativas de cada um dos dois IDs válidos. Não houve resposta 200 naquela execução. `/ready` retornou `pronto: true` antes do teste; prontidão não comprova disponibilidade efetiva de inferência. Não foi determinada a causa exata do 503.

Não foram alterados serviço, pesos, dependências, prompts, corpus ou treinamento da IA para realizar o RPA. Os testes automatizados usam transportes/retornos simulados, sem tocar o serviço público. O simulador de demonstração é sempre marcado e não comprova integração.

Retomada controlada `57dd12eb306d4501a9e22abb3427c539`, cerca de dez minutos depois: uma tentativa por ID, novamente HTTP 503, com mesmo lote e mesma base. Nenhum item já bem-sucedido foi repetido. As duas execuções iniciais somam seis chamadas 503; o lote hospedado acrescentou duas chamadas 200, totalizando oito. Nenhum 502 foi repetido para procurar resposta conveniente. O sucesso posterior não determina a causa das falhas anteriores.

O estado mais recente desta verificação é o run **44327757282**, com dois sucessos reais e um simulado. Conferir runs posteriores antes de continuar. Os artifacts são temporários, com expiração informada em 02/12/2026 às 11:45 (Brasília). O backup local do estado desse run está em `tmp/nuvem-real-20261118-114522/rpa-state-44327757282.zip`; seu SHA-256 consta em [github-run.json](evidencias/nuvem-real/github-run.json). `tmp/` fica fora do Git. Não repetir sucessos para filmar nem restaurar estado ancestral.

## Saída do RPA, versão 1.0

`resultados.json` é uma lista, um objeto por entrada. Campos comuns: `execucao_id`, `linha` (índice 1-based de registro, não número físico da linha CSV) e `integracao` (`simulada`/`real` identifica o cliente utilizado, **não garante sucesso**). `status_rpa`: `processado`, `duplicado`, `pendente`, `falha`; `codigo` é enum operacional sanitizado.

Quando a validação permite: `ocorrencia_id`, `item_ref` (prefixo SHA-256 do ID), `fingerprint` (registro canônico), `entrada` padronizada. Rejeições locais não preservam o corpo bruto. Um sucesso contém `request_id`, `status_ia`, `destino`, `ia` completa. Uma duplicata aponta para `execucao_original` e reaproveita a análise. Uma falha informa `repetivel` e `resultado_incerto` quando aplicável. A primeira evidência real foi gerada antes da inclusão de `entrada` nos resultados de falha; o lote original continua reproduzível em `examples/lote-real.json` e seu hash está no resumo.

Um consumidor deverá correlacionar por execução/ID/fingerprint, tratar pendências, não assumir que `integracao: real` significa HTTP 200 e validar a versão do contrato. Não há prazo, custo, causa elétrica ou prioridade de atendimento inventados na saída.

## Akona: o que falta do grupo

Nenhum endpoint de importação foi confirmado. Os nomes de campo do formulário informados no contexto não comprovam API. Nenhum registro foi enviado ao site publicado.

Precisamos do repositório e contrato real do backend para decidir:

- Campo/enum de `tipo`, obrigatoriedade e IDs de bairro/ponto e identificador externo.
- Mecanismo autorizado de integração (API, banco ou importação) e credenciais por segredo de ambiente, se necessárias.
- Semântica de criação, atualização, conflito, retorno de protocolo e vínculo com a triagem humana.
- Onde o Akona consumirá registros/análises/recusas e como apresentará indisponibilidade.
- Persistência na infraestrutura do grupo, permissões, retenção e ambiente para teste fictício.

Após disponibilização e autorização, implementar o adaptador correspondente e executar um teste rastreável de consumo no componente do grupo. Não fabricar esse consumidor neste projeto para satisfazer a rubrica.
