# Contratos e fronteiras de integração

Ficha Técnica: [README](../README.md). API confirmada em 18/11/2026 por HTTP GET de `/openapi.json`; o snapshot está empacotado com o RPA e seu SHA-256 consta em `evidencias/contrato-origem.json`.

## RPA → IA existente

Endpoint fixo: `POST https://laia020-citizentech-iluminacao-ia.hf.space/v1/analisar`. Corpo é construído por whitelist a partir do esquema `Occurrence`. `tipo`, `bairro` e `ponto` ficam apenas no RPA. A API recebe somente dados fictícios marcados `simulada: true` e alguma observação. A saída é validada contra `AnalysisResponse`, incluindo correspondência de `ocorrencia_id` e `request_id` não vazio.

O status operacional fica em `status_rpa`; o status de negócio da IA em `status_ia`. Uma recusa válida não vira erro HTTP fictício. A resposta integral válida fica em `ia`, sem reparar JSON nem reconstruir trechos faltantes. Todos os encaminhamentos requerem revisão humana.

**Evidência atual:** a execução `0ec3479a81ff41908c7d6529429ff274` recebeu HTTP 503 nas duas tentativas de cada um dos dois IDs válidos. A comunicação HTTP foi real, mas não houve resposta 200 e não foi demonstrado consumo com análise bem-sucedida. `/ready` retornou `pronto: true` antes do teste; prontidão não comprova disponibilidade efetiva de GPU/fila/cota. Não foi determinada a causa exata do 503.

Não foram alterados serviço, pesos, dependências, prompts, corpus ou treinamento da IA para realizar o RPA. Os testes automatizados usam transportes/retornos simulados, sem tocar o serviço público. O simulador de demonstração é sempre marcado e não comprova integração.

Retomada controlada `57dd12eb306d4501a9e22abb3427c539`, cerca de dez minutos depois: uma tentativa por ID, novamente HTTP 503, com mesmo lote e mesma base. Nenhum item já bem-sucedido foi repetido. As duas execuções reais somam seis chamadas; nenhum 502 foi repetido para procurar resposta conveniente.

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
