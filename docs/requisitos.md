# Requisitos, evidências e estado

Ficha Técnica comum abre o [README](../README.md). Fonte original conferida: PDF FIAP “Desafio-FIAP-GS-CitizenTech 4ES”, páginas 45–50; requisitos comuns nas páginas 18–24. Hash e páginas em `evidencias/enunciado-origem.json`; [auditoria detalhada](auditoria-entrega.md). Professores: Bruno Diniz e Cibele Ribeiro. Prazo: **19/11/2026 às 23h55**, Teams da disciplina RPA. Rubrica: integração 1; documentação 2; desenvolvimento 5; vídeo 2 pontos. Não é promessa de nota.

## Matriz das oito etapas

| # | Requisito obrigatório | Evidência real | Estado |
|---|---|---|---|
| 1 | Mapeamento do processo | `PDD.md`, `processo.bpmn`, imagens e páginas BPMN no relatório. | **Concluído** |
| 2 | Desenvolvimento versionado no GitHub | [Repositório público](https://github.com/laia020/citizentech-rpa) com código versionado e [CI aprovada](https://github.com/laia020/citizentech-rpa/actions/runs/44296025620). | **Concluído** |
| 3 | Decisão e repetição | Lote simulado de 4 entradas: 1 processada, 1 duplicada, 2 pendências; laço sequencial e testes de recusa/conflito. | **Concluído** |
| 4 | Exceções e resiliência | Testes de arquivo, API, timeout, quota, conflito e interrupção; HTTP 503 real registrado. | **Concluído** |
| 5 | Logs e auditoria | `logs/*.jsonl` e resumos com UTC, referência do item, etapas, tentativas e códigos sanitizados. | **Concluído** |
| 6 | Consumo por outro componente | [Run real `44327757282`](https://github.com/laia020/citizentech-rpa/actions/runs/44327757282): duas respostas HTTP 200 validadas, com análise preliminar e informação insuficiente, IDs e `request_id` preservados em `evidencias/nuvem-real/`. Akona ainda não consumiu saída. | **Demonstrado via IA** |
| 7 | Testes sucesso/decisão/falha | 26 testes automatizados aprovados, clientes simulados; cenário de indisponibilidade real separado. | **Concluído** |
| 8 | Documentação e publicação | README, PDD, BPMN e código públicos; PDF atualizado com GitHub. Vídeo e link final ainda pendentes. | **Parcial** |

## Outros entregáveis

Escopo adotado: **automação em lote RPA integrada à IA existente**, com relatório, BPMN e vídeo específicos de RPA. O item 6 da página 48 permite API, banco ou arquivo estruturado e não impõe o backend do Akona nem o arquivo final. A evidência adotada é a ocorrência validada e normalizada pelo RPA, consumida pela API da IA. A importação do arquivo final pelo backend/interface do Akona fica como evolução futura. A aceitação acadêmica depende da avaliação; não há garantia de nota. [Justificativa e limites](auditoria-entrega.md#interpretação-explícita-da-integração).

Relatório técnico PDF atualizado com a integração real e revisado visualmente. O link real do GitHub foi inserido; o campo de vídeo permanece pendente, sem URL inventada. O arquivo não deve ser enviado como entrega final antes de inserir o vídeo e alinhar a ficha comum. As alterações documentais e as evidências novas foram publicadas com autorização; ver `evidencias/publicacao-revisao.json`.

Vídeo ≤ 3 min: **pendente**, apenas roteiro e sequência prontos. Workflow hospedado: **executado com sucesso em simulação e em modo real**, com [run real](https://github.com/laia020/citizentech-rpa/actions/runs/44327757282) e resultados preservados: 4 entradas, 2 processadas, 1 duplicada, 1 pendência e 0 falhas. As seis chamadas 503 iniciais continuam preservadas. O registro histórico da suíte tem 26 testes com rede simulada; a conferência local não os reexecutou. A [CI da publicação da revisão](https://github.com/laia020/citizentech-rpa/actions/runs/44437773380) também foi aprovada. Envio no Teams: **pendente**, por integrante da equipe.

Ficha Técnica: versão de componente produzida a partir do contexto existente; cidadão, território, indicadores e arquitetura comuns devem ser alinhados com o grupo. Nenhum ganho municipal, energético, financeiro ou de tempo foi medido.

## Condições para encerrar

1. Publicação autorizada e realizada: GitHub público, commit/push, CI e primeiro workflow simulado concluídos. Preservar os artifacts e usar o estado mais recente nas execuções seguintes.
2. Consumo bem-sucedido pela IA demonstrado no run `44327757282`, com evidências publicadas. Preservar respostas, correlação e estado, sem repetir inferência para filmar. A aceitação acadêmica depende da avaliação, sem promessa de nota.
3. Se houver integração adicional com Akona, obter repositório/contrato e autorização antes de enviar registros. Ela não é condição para desenvolver as partes independentes, nem deve ser inventada.
4. Alinhar ficha com o grupo; gravar/publicar vídeo ≤ 3 min, inserir links reais e regenerar o PDF.
5. Conferir acesso público durante o período de correção e enviar na tarefa RPA do Teams. Não confundir com pitch de BI ou relatório de IA.
