# Akona Energy - Ficha Técnica CitizenTech

| Campo | Descrição |
|---|---|
| Produto | **Akona Energy**, componente de Robotic Process Automation da GS FIAP 4ES 2026.2. |
| Cidadão e território | Pessoas que relatam problemas de iluminação e equipes de triagem. Osasco/SP é território **demonstrativo**, sujeito ao alinhamento da ficha com o grupo. Sem operação municipal comprovada. |
| Problema | Receber ocorrências uma a uma exige validar campos, conferir repetições e organizar encaminhamentos manualmente. |
| Proposta de valor | Organizar lotes fictícios, separar pendências e manter rastreabilidade até a triagem humana; benefício proposto, sem redução de tempo ou custo medida em campo. |
| Arquitetura | CSV/JSON → Python RPA → validação + SQLite → cliente da IA → resultados JSON + auditoria → revisão humana. GitHub Actions executado em nuvem em simulação e em integração real com a IA. Consumo pelo backend/interface do Akona ainda pendente. |
| Fontes de dados | Exemplos autorais fictícios em `examples/`; contrato OpenAPI público da IA. Não usa base municipal, cidadãos reais ou sensor conectado. |
| Modelos de IA | Serviço existente: Qwen2.5-1.5B-Instruct, RAG e LoRA r1, implantação PyTorch FP32 informada pelo projeto de IA. O RPA não instala modelo, baixa pesos ou treina. O simulador não executa IA. |
| URLs | [MVP informado](https://ca-akona-energy-prod.salmoncoast-770d275b.eastus2.azurecontainerapps.io/), [IA pública](https://laia020-citizentech-iluminacao-ia.hf.space/demo), [API](https://laia020-citizentech-iluminacao-ia.hf.space/docs), [repositório da IA](https://github.com/laia020/citizentech-iluminacao-ia). [Repositório público do RPA](https://github.com/laia020/citizentech-rpa). [Vídeo demonstrativo de RPA](https://drive.google.com/file/d/1XqlXo0q4_SXJLDD0udv1aNUygJ99lG5k/view?usp=sharing). [Apresentação e evidências de RPA](https://laia020-citizentech-iluminacao-ia.hf.space/rpa). Repositório do Akona não fornecido. |
| Indicadores | Medidos nesta POC: contagens operacionais nos arquivos de execução e resultados dos testes. Propostos para estudo futuro: tempo de triagem, completude e encaminhamentos revisados. Não há medição de impacto de campo. |
| ODS | ODS 11: organização de relatos sobre infraestrutura urbana; ODS 7: apoio proposto à gestão da iluminação. Não demonstra economia de energia ou cumprimento de metas. |

## Escopo da entrega de RPA

A demonstração desta disciplina apresenta **o RPA integrado ao serviço de IA existente do Akona Energy**: lote fictício → validação e deduplicação → consulta real à IA → resultados, pendências e auditoria → revisão humana.

| Componente | Papel no fluxo demonstrado |
|---|---|
| RPA, foco desta entrega | Lê o lote, valida, percorre registros, decide o encaminhamento, preserva estado, evita consultas repetidas e exporta evidências. |
| IA existente | Recebe a ocorrência normalizada e devolve análise ou informação insuficiente. O RPA valida e preserva a resposta. |
| Backend/interface do Akona | Importação não implementada; evolução futura fora do fluxo demonstrado. |

As entregas de IA e RPA são distintas e compartilham um componente real do mesmo produto. Este relatório, BPMN e vídeo específico documentam a automação; treinamento e avaliação do modelo pertencem à entrega de IA. O serviço remoto foi reutilizado sem alterações. [Roteiro de gravação](docs/roteiro-video.md) e [narração preparada](docs/narracao-video-rpa.md).

A integração técnica RPA–IA está comprovada. A página 48 do enunciado original permite consumo do resultado por outro componente via API, banco ou arquivo estruturado; não especifica o backend do Akona nem obriga o uso do arquivo final. Nossa evidência é o resultado da validação e normalização consumido pela IA via API, com resposta correlacionada. A interpretação e os limites estão na [auditoria da entrega](docs/auditoria-entrega.md), sujeitos à avaliação dos professores. Não houve importação de `resultados.json` no backend do Akona.

Os lotes são autorais, determinísticos e fictícios, escolhidos para exercitar sucesso, decisão e falha. A [origem e justificativa dos dados](docs/dados-demonstracao.md) documenta a alternativa de dados simulados permitida na página 18 do enunciado.

## Equipe

| Nome completo | RM |
|---|---|
| Lucas Laia Manentti | 97709 |
| Guilherme Faustino Vargas | 98278 |
| Ryan Perez Pacheco | 98782 |
| João Lucas Yudi Redi Handa | 98458 |
| Guilherme Dal Posolo Matheus | 98694 |

## Resultado verificável em 18/11/2026

- Implementação e **26 testes automatizados aprovados**, todos com rede de IA simulada. [Registro](docs/evidencias/testes.json), [saída completa](docs/evidencias/testes.txt) e [primeira execução antes do código](docs/evidencias/tdd-inicial.txt).
- Lote simulado: 4 entradas, 1 processada, 1 duplicada e 2 pendências. Não demonstra análise por IA. [Resultados](docs/evidencias/simulado/resultados.json).
- Lote real: a API pública retornou **HTTP 503** para as duas ocorrências válidas. 4 entradas, 0 processadas, 0 duplicadas, 2 pendências e 2 falhas. Quatro tentativas HTTP no total, contadas separadamente dos itens. [Auditoria real](docs/evidencias/real-indisponibilidade/auditoria.jsonl).
- Uma retomada controlada, cerca de dez minutos depois, usou uma tentativa por ID e também recebeu 503: [segunda auditoria real](docs/evidencias/real-retomada/auditoria.jsonl). Foram seis chamadas reais no total das duas execuções, sem testes de carga nem repetição de 502.
- **Integração funcional RPA–IA demonstrada:** o [lote real hospedado](https://github.com/laia020/citizentech-rpa/actions/runs/44327757282), em 18/11 às 11:45 (Brasília), restaurou o estado `44296159102` e recebeu **duas respostas HTTP 200**, validadas pelo RPA. Foram 4 entradas, **2 processadas, 1 duplicada, 1 pendência e 0 falhas**, com duas chamadas no total. Uma resposta contém análise preliminar; a outra, `informacao_insuficiente`, é sucesso operacional com encaminhamento para complementação. A duplicata reaproveitou o mesmo `request_id`, sem outra consulta. [Respostas e correlação](docs/evidencias/nuvem-real/resultados.json), [auditoria](docs/evidencias/nuvem-real/auditoria.jsonl) e [origem dos artifacts](docs/evidencias/nuvem-real/github-run.json). O backend e a interface do Akona não consumiram a saída.
- [Código publicado no GitHub](https://github.com/laia020/citizentech-rpa), com [CI aprovada em Ubuntu](https://github.com/laia020/citizentech-rpa/actions/runs/44296025620). O [primeiro lote hospedado](https://github.com/laia020/citizentech-rpa/actions/runs/44296057126) concluiu em modo **simulado**: 4 entradas, 1 processada, 1 duplicada e 2 pendências, sem depender do Mac. Não comprova consumo pela IA. Vídeo e envio ao Teams permanecem pendentes; o projeto de IA não foi alterado.
- [Segunda execução hospedada](https://github.com/laia020/citizentech-rpa/actions/runs/44296159102) restaurou o estado do primeiro run: 0 novos processamentos, 2 duplicatas e 2 pendências. Restauração e idempotência foram verificadas fora do Mac, sem rede de IA. [Registro da publicação](docs/evidencias/publicacao.json).

As seis chamadas HTTP 503 anteriores foram preservadas como histórico; com o lote novo, são oito chamadas reais documentadas, duas bem-sucedidas. A conferência documental local não reexecutou a suíte; a CI do GitHub executa os testes a cada publicação. As evidências de `nuvem-real/` e a revisão documental foram publicadas com autorização, com [verificação pública dos arquivos](docs/evidencias/publicacao-revisao.json). O link do vídeo foi fornecido em 19/11/2026 e incluído no README e no PDF desta revisão. Ficha comum e envio ao Teams continuam pendentes. O autor autorizou a publicação desta atualização documental; roteiro, áudios e MP4 permanecem fora do Git.

## Executar localmente

Mac/Linux, Python **3.12** e uv. A aplicação usa apenas `jsonschema` como dependência direta de execução; as dependências de PDF ficam no grupo opcional `docs`. Não necessita GPU, bibliotecas de IA nem servidor permanente.

**Windows:** o lock usa `fcntl` e a execução nativa da aplicação não é suportada. Use o workflow Ubuntu hospedado para processar lotes. Os scripts de documentação podem rodar no Windows com Python 3.12 e o grupo `docs`; isso não comprova compatibilidade do RPA com Windows.

Em uma cópia nova, sem `.venv`:

```sh
cd ~/Projects/citizentech-rpa
uv venv --python 3.12 --prompt "venv-citizentech-rpa"
uv sync --locked --no-default-groups
source .venv/bin/activate
python -m unittest discover -s tests -v
citizentech-rpa examples/lote-demo.json --modo simulado
```

Se a `.venv` já existe, confira `.venv/pyvenv.cfg`, `.venv/bin/python --version` e `uv pip list --python .venv/bin/python` antes de sincronizar. Não recrie o ambiente. No Mac de desenvolvimento foi criada uma `.venv` exclusiva com Python 3.12.16 e prompt `(venv-citizentech-rpa)`. As dependências de outros projetos foram preservadas.

Modo real, intencional e sequencial, **somente com dados fictícios**:

```sh
citizentech-rpa examples/lote-real.json --modo real
```

A API tem cotas/filas. Esta execução pode retornar erro e não possui fallback local. Para retomar apenas falhas HTTP 429/503, preservando a mesma base:

```sh
citizentech-rpa examples/lote-real.json --modo real --retomar-falhas
```

Não use retomada em laço. Resultados concluídos são reaproveitados. Timeout, resposta inválida, interrupção durante envio e rejeição HTTP 502 exigem revisão; não são repetidos por esse argumento. Sem API de consulta por chave idempotente no serviço remoto, um timeout não permite garantir se a análise terminou lá.

## Entradas, saídas e decisões

CSV UTF-8 com vírgulas e cabeçalho, ou JSON contendo uma lista. Limites: **1 MiB e 100 registros**. A demonstração usa 4 itens e somente 2 IDs aptos a consulta. CSV usa `true`/`false`; sensores e observações visuais, quando usados em CSV, devem ser arrays JSON corretamente escapados.

Campos obrigatórios: `ocorrencia_id`, `pergunta`, `simulada: true`, mais alguma observação em `relato`, `sensores` ou `observacoes_visuais`. IDs aceitam letras ASCII, dígitos, `_`, `-` e `.`; não coloque nome, e-mail ou documento no identificador. Datas precisam de fuso. Calibração declarada exige referência, sem certificar a informação. Não há conversão ADC/lux nem diagnóstico elétrico.

Metadados opcionais `tipo`, `bairro`, `ponto` são preservados pelo RPA e **não enviados à IA**. Não são suficientes para afirmar compatibilidade de importação com o Akona. Campos desconhecidos geram pendência; não são encaminhados à API nem copiados para logs. O esquema público completo fica em [contrato congelado](src/citizentech_rpa/contracts/ia.openapi.json), com [origem e hash](docs/evidencias/contrato-origem.json).

Cada execução cria um diretório novo `runs/<execucao_id>/`:

| Arquivo | Uso |
|---|---|
| `resultados.json` | Um resultado por entrada, com `linha`, status operacional, decisão e, quando houver, análise e `request_id`. |
| `pendencias.json` | Pendências e falhas para revisão; registros inválidos não incluem conteúdo bruto. |
| `resumo.json` | SHA-256 da entrada, contagens, modo, situação, início/fim e código de saída. |
| `auditoria.jsonl` | Eventos com fuso UTC, execução, linha, referência hash do item, etapa, resultado, tentativa e códigos sanitizados. |

Um registro válido é normalizado (NFC, espaços externos e defaults), sem inventar localização ou dados ausentes. Duplicata de sucesso não repete análise; mesmo ID com conteúdo divergente vira conflito e não substitui o original. Registro incompleto fica pendente e o lote continua. A IA pode devolver `informacao_insuficiente` ou `fora_escopo`: são resultados de negócio **processados**, com encaminhamento humano distinto do status do RPA.

Contagens exclusivas: entradas = processados + duplicados + pendências + falhas em uma execução completa. Tentativas não são itens. Se uma infraestrutura impedir o processamento do lote, `erro_execucao` indica interrupção e as contagens podem abranger somente os itens finalizados. Códigos de saída: `0` lote concluído, inclusive pendências de negócio; `1` falha em item; `2` arquivo/infraestrutura inválido. **Exit 0 não certifica ausência de pendências.**

## Persistência e resiliência

O SQLite fica em `state/ocorrencias.sqlite3`, fora do Git, com chave `(modo, ocorrencia_id)` e fingerprint SHA-256 do registro padronizado completo, incluindo metadados. Simulação e integração real têm namespaces separados. O lock de arquivo impede acesso simultâneo pela aplicação no Mac/Linux; esse mecanismo não oferece suporte nativo a Windows.

O estado sobrevive à reinicialização **se o mesmo arquivo for preservado**. Antes do POST, grava `em_envio`. Ao reiniciar após uma interrupção nesse intervalo, marca a entrada para revisão e não repete o POST. O servidor remoto não oferece mecanismo que permita garantir exatamente uma execução após uma falha de rede. A base e as evidências devem ser preservadas; não apague o estado para fazer o exemplo passar.

HTTP 429/503: até 2 tentativas por padrão (máximo configurável 3), espera progressiva ou `Retry-After`, até 15 s por espera. Se `Retry-After` exceder esse limite, encerra o item sem antecipar a chamada. HTTP 413/422/502 e respostas inválidas não são reparados nem repetidos. Timeout padrão 120 s; resultado incerto fica para revisão. Arquivo inválido/ausente gera auditoria e resumo, sem chamadas de rede.

## Execução em nuvem

[Workflow manual](.github/workflows/rpa.yml) validado em `ubuntu-latest`, executor hospedado do GitHub. A [execução simulada](https://github.com/laia020/citizentech-rpa/actions/runs/44296057126) não consultou a IA. O [lote real posterior](https://github.com/laia020/citizentech-rpa/actions/runs/44327757282) obteve dois HTTP 200; [resumo preservado](docs/evidencias/nuvem-real/resumo.json). Nenhum computador pessoal foi usado como runner.

Para reproduzir no repositório publicado:

1. Abra [Actions → Lote CitizenTech RPA](https://github.com/laia020/citizentech-rpa/actions/workflows/rpa.yml) e clique em **Run workflow**. Comece em `simulado`.
2. O estado deste repositório já foi inicializado. Para continuar, restaure o run **mais recente** com `rpa-state`. Somente em outra cópia nova, sem histórico a preservar: deixe `estado_run_id` vazio e confirme `iniciar_estado`.
3. Nas próximas execuções, informe o ID do run **mais recente** que contém `rpa-state`, inclusive se houve falha na API. Último run de lote desta validação: **44327757282**. Desmarque `iniciar_estado`. Não reutilize um ancestral mais antigo; confira se houve execuções posteriores.
4. O lote `lote-real.json` já tem dois sucessos reais nesse estado. Preserve-os; não repita a inferência só para demonstrar. Retomada de 429/503 é explícita, após revisão, sem laço.
5. Baixe `rpa-resultados` e `rpa-state`. Confira o resumo mesmo quando o job falhar.

Restauração inexistente, inválida ou expirada aborta sem criar uma base substituta. Artifacts têm retenção configurada de **14 dias**, sujeitos às políticas do GitHub; não são banco permanente nem garantia de persistência. Se o job for cancelado ou falhar antes do upload do estado mais recente, **não restaure um estado anterior e continue cegamente**: preserve logs e reconcilie os itens enviados. A restauração é operacional, não automática; a seleção correta do run é responsabilidade do operador. O SQLite local de desenvolvimento não é enviado automaticamente ao GitHub. Começar lá com estado novo não deduplica as consultas feitas aqui.

A CI roda apenas testes simulados. Os workflows usam permissões de leitura e actions fixadas por SHA. Não criam recursos pagos, fazem commits, publicam páginas ou acionam reparos. Artefatos do Actions exigem login e acesso de leitura; as amostras versionadas em `docs/evidencias/` são evidências públicas, acessíveis sem baixar artifacts. Confira as cotas da conta antes de executar e não habilite cobrança adicional sem aprovação.

## Documentação e entrega

- [PDD e regras](docs/PDD.md), [requisitos e matriz](docs/requisitos.md), [contrato de saída e integração](docs/integracao.md).
- [BPMN editável](docs/processo.bpmn) e duas vistas em [assets](assets/README.md).
- [Relatório técnico PDF](output/pdf/relatorio-tecnico-rpa.pdf).
- [Vídeo demonstrativo de RPA](https://drive.google.com/file/d/1XqlXo0q4_SXJLDD0udv1aNUygJ99lG5k/view?usp=sharing). Link fornecido pelo autor.
- [Plano e decisões](docs/plano.md), [evidências](docs/evidencias/README.md), [segurança](docs/seguranca.md).

Regenerar os diagramas e o relatório, sem consultar IA:

```sh
uv sync --locked --group docs
uv run --no-sync python scripts/gerar_bpmn.py
uv run --no-sync python scripts/gerar_relatorio.py
uv run --no-sync python scripts/validar_entrega.py
```

O validador confere os artifacts preservados sem chamar a IA nem executar novamente a suíte e grava `docs/evidencias/validacao-atual.json`, separado do manifesto histórico. No checkout Windows, reconhece apenas a equivalência LF/CRLF para os hashes textuais e registra quando ela foi necessária. Os resumos originais não são reescritos.

Antes de enviar, use `uv run --no-sync python scripts/validar_entrega.py --online --final`. Esse modo retorna erro enquanto faltarem vídeo, duração válida, acesso conferido, ficha comum ou publicação da revisão. A validação documental normal não equivale à prontidão para envio. [Auditoria por critério e checklist](docs/auditoria-entrega.md).

Confira a renderização após regenerar. O PDF declara como pendentes os links ainda não existentes, sem inventar URLs de GitHub/vídeo. Prazo do enunciado: **19/11/2026 às 23h55**, na tarefa de **RPA do Teams**, por um integrante. Confirmar a ficha comum com o grupo e manter links acessíveis durante a correção. A entrega geral continua parcial enquanto esses itens faltarem.
