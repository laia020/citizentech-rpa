# Origem e justificativa dos dados fictícios

## Fonte e método

Os arquivos de `examples/` são exemplos autorais, escritos manualmente para testar regras do RPA e o contrato da IA. Não foram obtidos de prefeitura, moradores, sensores ou operações reais. A escolha de dados simulados atende à alternativa prevista na página 18 do enunciado, com esta geração documentada.

Não há gerador estatístico, amostragem de população ou distribuição estimada. As entradas são determinísticas: cada linha foi escolhida para exercitar um caminho do processo, permitindo reproduzir contagens e verificar a auditoria. Nenhum indicador de prevalência, economia ou impacto pode ser inferido desses lotes.

## Cenários e finalidade

| Arquivo | Construção | Finalidade |
|---|---|---|
| `examples/lote-demo.json` | Quatro entradas: uma ocorrência válida, repetição idêntica, mesmo ID com relato divergente e registro sem observação. | Exercitar sucesso simulado, duplicidade, conflito e pendência, sem rede de IA. |
| `examples/lote-demo.csv` | Três entradas: uma ocorrência válida, repetição e ausência de observação. Booleano fictício representado como `true`. | Verificar a leitura CSV e as mesmas regras operacionais. |
| `examples/lote-real.json` | Quatro entradas: relato fictício de luminária apagada, repetição idêntica, leitura fictícia ADC sem calibração e registro incompleto. | Consultar a IA existente com conteúdo fictício; demonstrar análise preliminar, informação insuficiente, deduplicação e pendência. |

O nome `lote-real` identifica a intenção de usar o cliente HTTP real; **o conteúdo continua fictício**, com `simulada: true`. A leitura ADC `83` é apenas um valor de teste. Ela não veio de dispositivo, não foi convertida em lux e não permite concluir conformidade ou causa elétrica.

## Território e identificadores

Osasco/SP é somente o território demonstrativo informado para a POC. Bairros e postes dos exemplos são fictícios e não representam infraestrutura municipal cadastrada. IDs são identificadores técnicos de demonstração, sem nome, e-mail ou documento de cidadão.

Os nomes e RMs da equipe são dados acadêmicos de identificação da entrega; não fazem parte das ocorrências enviadas à IA.

## Contrato e proteção

O RPA exige a declaração de dados fictícios, valida o esquema e limita tamanho e quantidade. Essa declaração não detecta dados pessoais automaticamente: o operador deve revisar qualquer novo lote. Campos desconhecidos geram pendência. Os metadados `tipo`, `bairro` e `ponto` ficam no RPA e não integram o payload da IA.

Os hashes dos lotes originais estão nos resumos de execução. Em um checkout Windows, LF pode ser convertido em CRLF pelo Git; a conferência documental registra essa equivalência sem alterar os resumos históricos.

## Limites da demonstração

O lote real de 18/11/2026 comprovou duas respostas HTTP 200 no run `44327757282`, sem criar chamados ou acionar reparos. O sucesso técnico não comprova qualidade de diagnóstico, impacto municipal ou integração de `resultados.json` ao backend do Akona. Não gerar novos IDs nem apagar estado para repetir sucessos apenas para filmar.
