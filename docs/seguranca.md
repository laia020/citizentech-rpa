# Segurança, privacidade e operação

POC acadêmica de dados fictícios. `simulada: true` é uma declaração obrigatória, **não um detector de dados pessoais**. Não incluir nomes de moradores, CPF, telefone, e-mail, localização residencial real ou segredos em relatos. A equipe deve revisar os lotes antes de enviá-los. Os nomes/RMs acadêmicos da equipe são os fornecidos para identificação da entrega.

Whitelist impede encaminhar colunas extras. O RPA valida esquema, limites de tamanho, IDs, datas com fuso e referência de calibração declarada. Não converte unidades, autentica laudos ou determina causa elétrica. Uma IA pode errar; o encaminhamento final exige pessoa responsável.

Auditoria registra códigos internos, referência hash e índice do item; não registra relatos, stack traces, corpos arbitrários de erro, tokens ou cabeçalhos. Resultados e SQLite preservam o conteúdo válido, somente fictício; não publique lotes reais. A hash de ID não constitui anonimização formal.

No Mac/Linux, arquivos de resultado e SQLite são criados com permissões 0600 e diretórios de execução 0700. O SQLite não é criptografado e as permissões não substituem controle de acesso ao computador ou à conta GitHub. Não há autenticação de usuário no CLI. Não expor este estado como serviço público.

A API é HTTPS com certificado validado pelo runtime; redirecionamentos não são seguidos para evitar envio do corpo a outro destino. O serviço tem cotas; lote pequeno e sequencial, tentativas limitadas e sem replay automático em resultado incerto. Não realizar teste destrutivo ou de carga no serviço publicado.

`.env`, `.venv`, estado e execuções locais ficam fora do Git. O workflow usa `GITHUB_TOKEN` efêmero pelo ambiente, com leitura de contents/actions; não há token estático no projeto. Dependências fixadas em `uv.lock`; actions fixadas por SHA. Não atualizar ferramentas globais como parte da reprodução.

Retenção proposta para POC: preservar evidências fictícias públicas durante a correção; artifacts configurados por 14 dias e sujeitos à política da conta. Logs/estado local são mantidos até revisão do responsável; nenhum expurgo automático foi implementado. Antes de uso real, alinhar finalidade, base legal, acesso, minimização, retenção e direitos com o responsável da operação. Esta POC não equivale a certificação de conformidade LGPD.

Sem alertas a terceiros, ordens de serviço, reparos, contratação paga ou cobrança adicional autorizada. Para incidente: interromper os próximos envios, preservar evidências, revisar com a equipe e somente então retomar. Não apagar sucessos nem reiniciar estado para esconder falha.
