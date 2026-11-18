# Requisitos, evidências e estado

Ficha Técnica comum abre o [README](../README.md). Fonte: PDF FIAP “Desafio-FIAP-GS-CitizenTech 4ES”, páginas 45–50; requisitos comuns nas páginas 18–24. Professores: Bruno Diniz e Cibele Ribeiro. Prazo: **19/11/2026 às 23h55**, Teams da disciplina RPA. Rubrica: integração 1; documentação 2; desenvolvimento 5; vídeo 2 pontos. Não é promessa de nota.

## Matriz das oito etapas

| # | Requisito obrigatório | Evidência real | Estado |
|---|---|---|---|
| 1 | Mapeamento do processo | `PDD.md`, `processo.bpmn`, imagens e páginas BPMN no relatório. | **Concluído** |
| 2 | Desenvolvimento versionado no GitHub | [Repositório público](https://github.com/laia020/citizentech-rpa) com código versionado e [CI aprovada](https://github.com/laia020/citizentech-rpa/actions/runs/44296025620). | **Concluído** |
| 3 | Decisão e repetição | Lote simulado de 4 entradas: 1 processada, 1 duplicada, 2 pendências; laço sequencial e testes de recusa/conflito. | **Concluído** |
| 4 | Exceções e resiliência | Testes de arquivo, API, timeout, quota, conflito e interrupção; HTTP 503 real registrado. | **Concluído** |
| 5 | Logs e auditoria | `logs/*.jsonl` e resumos com UTC, referência do item, etapas, tentativas e códigos sanitizados. | **Concluído** |
| 6 | Consumo por outro componente | Chamadas reais à IA retornaram 503; não houve análise 200. Akona ainda não consumiu saída. | **Parcial** |
| 7 | Testes sucesso/decisão/falha | 26 testes automatizados aprovados, clientes simulados; cenário de indisponibilidade real separado. | **Concluído** |
| 8 | Documentação e publicação | README, PDD, BPMN e código públicos; PDF atualizado com GitHub. Vídeo e link final ainda pendentes. | **Parcial** |

## Outros entregáveis

Relatório técnico PDF gerado e conferido visualmente. O link real do GitHub foi inserido; o campo de vídeo permanece pendente, sem URL inventada. O arquivo não deve ser enviado como entrega final antes de resolver esses campos e as limitações de integração.

Vídeo ≤ 3 min: **pendente**, apenas roteiro e sequência prontos. Workflow hospedado: **executado com sucesso em modo simulado**, com [run público](https://github.com/laia020/citizentech-rpa/actions/runs/44296057126) e resultados preservados. Não houve consulta à IA neste teste. Envio no Teams: **pendente**, por integrante da equipe.

Ficha Técnica: versão de componente produzida a partir do contexto existente; cidadão, território, indicadores e arquitetura comuns devem ser alinhados com o grupo. Nenhum ganho municipal, energético, financeiro ou de tempo foi medido.

## Condições para encerrar

1. Publicação autorizada e realizada: GitHub público, commit/push, CI e primeiro workflow simulado concluídos. Preservar os artifacts e usar o estado mais recente nas execuções seguintes.
2. Obter uma execução real com consumo bem-sucedido da entrada normalizada pela IA, preservando resposta e correlação; ou implementar e comprovar outro consumidor real autorizado do grupo.
3. Se houver integração adicional com Akona, obter repositório/contrato e autorização antes de enviar registros. Ela não é condição para desenvolver as partes independentes, nem deve ser inventada.
4. Alinhar ficha com o grupo; gravar/publicar vídeo ≤ 3 min, inserir links reais e regenerar o PDF.
5. Conferir acesso público durante o período de correção e enviar na tarefa RPA do Teams. Não confundir com pitch de BI ou relatório de IA.
