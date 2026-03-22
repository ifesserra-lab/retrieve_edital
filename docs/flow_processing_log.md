# Flow Processing Log

Documento operacional para registrar a data de processamento dos fluxos do projeto.

## Regras Operacionais
- Este arquivo deve ser atualizado sempre após a execução de qualquer fluxo ETL do repositório.
- Registrar a data/hora do processamento, o fluxo executado e um resumo objetivo do resultado.
- A pasta `data/output/` deve conter apenas arquivos `.json` de editais.
- Qualquer artefato temporário, log intermediário ou arquivo auxiliar gerado durante execução deve ficar fora de `data/output/`.

## Últimas Execuções

| Data/Hora | Fluxo | Resultado | Observações |
| :-- | :-- | :-- | :-- |
| 2026-03-22 17:58:37 -03:00 | `CNPQ` | Sucesso com observações | Após limpeza controlada da chave `cnpq` no registry, o fluxo processou 4 chamadas abertas, persistiu 4 JSONs, atualizou `registry/processed_editais.json` com 4 permalinks e manteve `data/output/` apenas com `.json`. O source passou a ignorar anexos `application/msword` para OCR. Na validação final, 1 JSON ficou com `orgão_fomento` vazio após a extração. |
| 2026-03-22 16:00:20 -03:00 | `CONIF` | Sucesso | Após limpeza completa do registry, o fluxo processou 3 editais, persistiu 3 JSONs e atualizou a chave `conif` com 3 URLs. |
| 2026-03-22 15:57:50 -03:00 | `FINEP` | Sucesso | Após limpeza completa do registry, o fluxo processou 10 chamadas da primeira página, persistiu 10 JSONs e atualizou a chave `finep` com 10 URLs. |
| 2026-03-22 15:39:03 -03:00 | `FAPES` | Sucesso com retries | Após limpeza completa do registry, o fluxo processou 13 editais e atualizou a chave `fapes` com 13 chaves. Houve múltiplos retries por `429` do Mistral, mas o pipeline concluiu com sucesso. |
| 2026-03-22 15:35:11 -03:00 | `CONIF` | Sucesso | Registry `conif` reinicializado para rerodagem controlada. O fluxo processou 3 editais, persistiu 3 JSONs válidos em `data/output/`, atualizou `registry/processed_editais.json` e manteve `data/output/` apenas com arquivos `.json`. Verificação dos JSONs: descrição preenchida, link da página de detalhe preservado, cronograma presente e anexos persistidos (7, 10 e 7 itens). |
| 2026-03-22 15:33:35 -03:00 | `CONIF` | Sem novos itens | O fluxo executou com sucesso, mas `ConifSource` extraiu `0` editais porque as 3 URLs do CONIF já estão registradas em `registry/processed_editais.json`. A validação dos JSONs gerados ficou bloqueada porque não há arquivos CONIF atualmente em `data/output/`, indicando inconsistência entre registry e saída persistida. `data/output/` segue contendo apenas JSONs. |
| 2026-03-22 15:24 -03:00 | `CONIF` | Sucesso | OCR do edital principal executado via Mistral; URLs registradas em `registry/processed_editais.json`; `data/output/` mantido apenas com JSONs de editais. |

## Como Atualizar
1. Rodar o fluxo desejado.
2. Verificar se `data/output/` contém apenas arquivos `.json`.
3. Atualizar esta tabela com a execução mais recente.
4. Registrar falhas, timeouts ou observações relevantes de forma objetiva.
