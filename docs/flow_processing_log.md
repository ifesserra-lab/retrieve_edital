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
| 2026-06-22 06:02:34 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 5 -> 5 (delta 0); `data/output/` com 102 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-22 06:02:32 -03:00 | `CAPES` | Sucesso | Registry `capes`: 25 -> 25 (delta 0); `data/output/` com 102 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-22 06:01:30 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 7 -> 7 (delta 0); `data/output/` com 102 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-22 06:00:29 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 16 -> 16 (delta 0); `data/output/` com 102 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-22 05:59:58 -03:00 | `CONIF` | Sucesso | Registry `conif`: 7 -> 7 (delta 0); `data/output/` com 102 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-22 05:59:54 -03:00 | `FINEP` | Sucesso | Registry `finep`: 10 -> 10 (delta 0); `data/output/` com 102 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-22 05:59:33 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 30 -> 30 (delta 0); `data/output/` com 102 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-21 04:38:47 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 5 -> 5 (delta 0); `data/output/` com 102 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-21 04:38:46 -03:00 | `CAPES` | Sucesso | Registry `capes`: 25 -> 25 (delta 0); `data/output/` com 102 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-21 04:37:44 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 7 -> 7 (delta 0); `data/output/` com 102 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-21 04:36:43 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 16 -> 16 (delta 0); `data/output/` com 102 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-21 04:36:12 -03:00 | `CONIF` | Sucesso | Registry `conif`: 7 -> 7 (delta 0); `data/output/` com 102 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-21 04:36:07 -03:00 | `FINEP` | Sucesso | Registry `finep`: 10 -> 10 (delta 0); `data/output/` com 102 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-21 04:35:46 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 30 -> 30 (delta 0); `data/output/` com 102 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-20 04:06:08 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 5 -> 5 (delta 0); `data/output/` com 102 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-20 04:06:06 -03:00 | `CAPES` | Sucesso | Registry `capes`: 24 -> 25 (delta 1); `data/output/` com 102 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-20 04:05:47 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 7 -> 7 (delta 0); `data/output/` com 102 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-20 04:05:45 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 16 -> 16 (delta 0); `data/output/` com 102 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-20 04:05:28 -03:00 | `CONIF` | Sucesso | Registry `conif`: 6 -> 7 (delta 1); `data/output/` com 102 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-20 04:05:09 -03:00 | `FINEP` | Sucesso | Registry `finep`: 10 -> 10 (delta 0); `data/output/` com 101 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-20 04:04:48 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 30 -> 30 (delta 0); `data/output/` com 101 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-19 05:36:49 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 5 -> 5 (delta 0); `data/output/` com 101 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-19 05:36:47 -03:00 | `CAPES` | Sucesso | Registry `capes`: 24 -> 24 (delta 0); `data/output/` com 101 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-19 05:35:46 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 7 -> 7 (delta 0); `data/output/` com 101 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-19 05:35:45 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 16 -> 16 (delta 0); `data/output/` com 101 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-19 05:35:29 -03:00 | `CONIF` | Sucesso | Registry `conif`: 6 -> 6 (delta 0); `data/output/` com 101 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-19 05:35:25 -03:00 | `FINEP` | Sucesso | Registry `finep`: 10 -> 10 (delta 0); `data/output/` com 101 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-19 05:35:05 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 30 -> 30 (delta 0); `data/output/` com 101 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-18 04:39:08 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 5 -> 5 (delta 0); `data/output/` com 101 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-18 04:39:05 -03:00 | `CAPES` | Sucesso | Registry `capes`: 24 -> 24 (delta 0); `data/output/` com 101 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-18 04:38:04 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 7 -> 7 (delta 0); `data/output/` com 101 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-18 04:37:03 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 16 -> 16 (delta 0); `data/output/` com 101 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-18 04:36:32 -03:00 | `CONIF` | Sucesso | Registry `conif`: 6 -> 6 (delta 0); `data/output/` com 101 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-18 04:36:28 -03:00 | `FINEP` | Sucesso | Registry `finep`: 10 -> 10 (delta 0); `data/output/` com 101 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-18 04:36:06 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 29 -> 30 (delta 1); `data/output/` com 101 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-17 05:31:43 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 5 -> 5 (delta 0); `data/output/` com 100 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-17 05:31:40 -03:00 | `CAPES` | Sucesso | Registry `capes`: 24 -> 24 (delta 0); `data/output/` com 100 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-17 05:31:33 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 7 -> 7 (delta 0); `data/output/` com 100 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-17 05:31:31 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 16 -> 16 (delta 0); `data/output/` com 100 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-17 05:31:15 -03:00 | `CONIF` | Sucesso | Registry `conif`: 6 -> 6 (delta 0); `data/output/` com 100 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-17 05:31:10 -03:00 | `FINEP` | Sucesso | Registry `finep`: 10 -> 10 (delta 0); `data/output/` com 100 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-17 05:30:50 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 29 -> 29 (delta 0); `data/output/` com 100 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-16 05:49:45 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 5 -> 5 (delta 0); `data/output/` com 100 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-16 05:49:43 -03:00 | `CAPES` | Sucesso | Registry `capes`: 24 -> 24 (delta 0); `data/output/` com 100 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-16 05:49:34 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 7 -> 7 (delta 0); `data/output/` com 100 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-16 05:49:32 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 15 -> 16 (delta 1); `data/output/` com 100 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-16 05:48:58 -03:00 | `CONIF` | Sucesso | Registry `conif`: 6 -> 6 (delta 0); `data/output/` com 99 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-16 05:48:54 -03:00 | `FINEP` | Sucesso | Registry `finep`: 10 -> 10 (delta 0); `data/output/` com 99 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-16 05:48:32 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 29 -> 29 (delta 0); `data/output/` com 99 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-15 06:02:59 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 5 -> 5 (delta 0); `data/output/` com 99 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-15 06:02:57 -03:00 | `CAPES` | Sucesso | Registry `capes`: 24 -> 24 (delta 0); `data/output/` com 99 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-15 06:02:49 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 7 -> 7 (delta 0); `data/output/` com 99 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-15 06:02:47 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 15 -> 15 (delta 0); `data/output/` com 99 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-15 06:02:31 -03:00 | `CONIF` | Sucesso | Registry `conif`: 6 -> 6 (delta 0); `data/output/` com 99 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-15 06:02:26 -03:00 | `FINEP` | Sucesso | Registry `finep`: 10 -> 10 (delta 0); `data/output/` com 99 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-15 06:02:06 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 29 -> 29 (delta 0); `data/output/` com 99 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-14 04:26:40 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 5 -> 5 (delta 0); `data/output/` com 99 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-14 04:26:38 -03:00 | `CAPES` | Sucesso | Registry `capes`: 24 -> 24 (delta 0); `data/output/` com 99 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-14 04:26:29 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 7 -> 7 (delta 0); `data/output/` com 99 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-14 04:26:27 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 15 -> 15 (delta 0); `data/output/` com 99 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-14 04:26:06 -03:00 | `CONIF` | Sucesso | Registry `conif`: 6 -> 6 (delta 0); `data/output/` com 99 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-14 04:26:02 -03:00 | `FINEP` | Sucesso | Registry `finep`: 10 -> 10 (delta 0); `data/output/` com 99 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-14 04:25:41 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 29 -> 29 (delta 0); `data/output/` com 99 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-13 04:02:54 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 5 -> 5 (delta 0); `data/output/` com 99 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-13 04:02:52 -03:00 | `CAPES` | Sucesso | Registry `capes`: 24 -> 24 (delta 0); `data/output/` com 99 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-13 04:02:44 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 7 -> 7 (delta 0); `data/output/` com 99 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-13 04:01:43 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 15 -> 15 (delta 0); `data/output/` com 99 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-13 04:01:11 -03:00 | `CONIF` | Sucesso | Registry `conif`: 6 -> 6 (delta 0); `data/output/` com 99 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-13 04:01:07 -03:00 | `FINEP` | Sucesso | Registry `finep`: 10 -> 10 (delta 0); `data/output/` com 99 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-13 04:00:46 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 29 -> 29 (delta 0); `data/output/` com 99 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-12 04:25:51 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 5 -> 5 (delta 0); `data/output/` com 99 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-12 04:25:50 -03:00 | `CAPES` | Sucesso | Registry `capes`: 24 -> 24 (delta 0); `data/output/` com 99 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-12 04:25:42 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 7 -> 7 (delta 0); `data/output/` com 99 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-12 04:25:40 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 15 -> 15 (delta 0); `data/output/` com 99 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-12 04:25:21 -03:00 | `CONIF` | Sucesso | Registry `conif`: 6 -> 6 (delta 0); `data/output/` com 99 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-12 04:25:18 -03:00 | `FINEP` | Sucesso | Registry `finep`: 10 -> 10 (delta 0); `data/output/` com 99 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-12 04:24:56 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 29 -> 29 (delta 0); `data/output/` com 99 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-11 04:35:01 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 5 -> 5 (delta 0); `data/output/` com 99 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-11 04:34:59 -03:00 | `CAPES` | Sucesso | Registry `capes`: 24 -> 24 (delta 0); `data/output/` com 99 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-11 04:33:58 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 7 -> 7 (delta 0); `data/output/` com 99 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-11 04:32:58 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 15 -> 15 (delta 0); `data/output/` com 99 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-11 04:32:26 -03:00 | `CONIF` | Sucesso | Registry `conif`: 6 -> 6 (delta 0); `data/output/` com 99 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-11 04:32:22 -03:00 | `FINEP` | Sucesso | Registry `finep`: 10 -> 10 (delta 0); `data/output/` com 99 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-11 04:32:01 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 29 -> 29 (delta 0); `data/output/` com 99 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-10 04:11:00 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 5 -> 5 (delta 0); `data/output/` com 99 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-10 04:10:58 -03:00 | `CAPES` | Sucesso | Registry `capes`: 24 -> 24 (delta 0); `data/output/` com 99 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-10 04:10:51 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 7 -> 7 (delta 0); `data/output/` com 99 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-10 04:10:49 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 15 -> 15 (delta 0); `data/output/` com 99 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-10 04:10:34 -03:00 | `CONIF` | Sucesso | Registry `conif`: 6 -> 6 (delta 0); `data/output/` com 99 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-10 04:10:29 -03:00 | `FINEP` | Sucesso | Registry `finep`: 10 -> 10 (delta 0); `data/output/` com 99 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-10 04:10:08 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 28 -> 29 (delta 1); `data/output/` com 99 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-09 03:51:05 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 5 -> 5 (delta 0); `data/output/` com 98 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-09 03:51:03 -03:00 | `CAPES` | Sucesso | Registry `capes`: 24 -> 24 (delta 0); `data/output/` com 98 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-09 03:50:56 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 7 -> 7 (delta 0); `data/output/` com 98 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-09 03:50:54 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 15 -> 15 (delta 0); `data/output/` com 98 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-09 03:50:37 -03:00 | `CONIF` | Sucesso | Registry `conif`: 6 -> 6 (delta 0); `data/output/` com 98 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-09 03:50:33 -03:00 | `FINEP` | Sucesso | Registry `finep`: 10 -> 10 (delta 0); `data/output/` com 98 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-09 03:50:12 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 28 -> 28 (delta 0); `data/output/` com 98 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-08 04:34:17 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 5 -> 5 (delta 0); `data/output/` com 98 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-08 04:34:15 -03:00 | `CAPES` | Sucesso | Registry `capes`: 24 -> 24 (delta 0); `data/output/` com 98 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-08 04:34:07 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 7 -> 7 (delta 0); `data/output/` com 98 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-08 04:34:05 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 15 -> 15 (delta 0); `data/output/` com 98 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-08 04:33:34 -03:00 | `CONIF` | Sucesso | Registry `conif`: 6 -> 6 (delta 0); `data/output/` com 98 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-08 04:33:30 -03:00 | `FINEP` | Sucesso | Registry `finep`: 10 -> 10 (delta 0); `data/output/` com 98 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-08 04:33:08 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 28 -> 28 (delta 0); `data/output/` com 98 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-07 04:09:41 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 5 -> 5 (delta 0); `data/output/` com 98 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-07 04:09:40 -03:00 | `CAPES` | Sucesso | Registry `capes`: 24 -> 24 (delta 0); `data/output/` com 98 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-07 04:09:32 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 7 -> 7 (delta 0); `data/output/` com 98 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-07 04:09:30 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 15 -> 15 (delta 0); `data/output/` com 98 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-07 04:09:11 -03:00 | `CONIF` | Sucesso | Registry `conif`: 6 -> 6 (delta 0); `data/output/` com 98 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-07 04:09:06 -03:00 | `FINEP` | Sucesso | Registry `finep`: 10 -> 10 (delta 0); `data/output/` com 98 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-07 04:08:46 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 27 -> 28 (delta 1); `data/output/` com 98 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-06 03:33:08 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 5 -> 5 (delta 0); `data/output/` com 97 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-06 03:33:07 -03:00 | `CAPES` | Sucesso | Registry `capes`: 24 -> 24 (delta 0); `data/output/` com 97 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-06 03:32:06 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 7 -> 7 (delta 0); `data/output/` com 97 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-06 03:31:05 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 15 -> 15 (delta 0); `data/output/` com 97 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-06 03:30:33 -03:00 | `CONIF` | Sucesso | Registry `conif`: 6 -> 6 (delta 0); `data/output/` com 97 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-06 03:30:30 -03:00 | `FINEP` | Sucesso | Registry `finep`: 10 -> 10 (delta 0); `data/output/` com 97 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-06 03:30:09 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 27 -> 27 (delta 0); `data/output/` com 97 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-05 04:11:48 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 5 -> 5 (delta 0); `data/output/` com 97 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-05 04:11:47 -03:00 | `CAPES` | Sucesso | Registry `capes`: 24 -> 24 (delta 0); `data/output/` com 97 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-05 04:10:45 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 7 -> 7 (delta 0); `data/output/` com 97 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-05 04:09:45 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 15 -> 15 (delta 0); `data/output/` com 97 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-05 04:09:13 -03:00 | `CONIF` | Sucesso | Registry `conif`: 6 -> 6 (delta 0); `data/output/` com 97 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-05 04:09:09 -03:00 | `FINEP` | Sucesso | Registry `finep`: 10 -> 10 (delta 0); `data/output/` com 97 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-05 04:08:49 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 27 -> 27 (delta 0); `data/output/` com 97 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-04 04:30:35 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 5 -> 5 (delta 0); `data/output/` com 97 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-04 04:30:33 -03:00 | `CAPES` | Sucesso | Registry `capes`: 24 -> 24 (delta 0); `data/output/` com 97 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-04 04:29:32 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 7 -> 7 (delta 0); `data/output/` com 97 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-04 04:28:31 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 15 -> 15 (delta 0); `data/output/` com 97 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-04 04:28:00 -03:00 | `CONIF` | Sucesso | Registry `conif`: 5 -> 6 (delta 1); `data/output/` com 97 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-04 04:27:43 -03:00 | `FINEP` | Sucesso | Registry `finep`: 10 -> 10 (delta 0); `data/output/` com 96 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-04 04:27:22 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 26 -> 27 (delta 1); `data/output/` com 96 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-03 05:20:45 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 5 -> 5 (delta 0); `data/output/` com 95 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-03 05:20:43 -03:00 | `CAPES` | Sucesso | Registry `capes`: 24 -> 24 (delta 0); `data/output/` com 95 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-03 05:19:42 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 7 -> 7 (delta 0); `data/output/` com 95 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-03 05:18:41 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 15 -> 15 (delta 0); `data/output/` com 95 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-03 05:18:10 -03:00 | `CONIF` | Sucesso | Registry `conif`: 5 -> 5 (delta 0); `data/output/` com 95 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-03 05:18:06 -03:00 | `FINEP` | Sucesso | Registry `finep`: 10 -> 10 (delta 0); `data/output/` com 95 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-03 05:17:45 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 25 -> 26 (delta 1); `data/output/` com 95 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-02 04:30:33 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 5 -> 5 (delta 0); `data/output/` com 94 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-02 04:30:31 -03:00 | `CAPES` | Sucesso | Registry `capes`: 24 -> 24 (delta 0); `data/output/` com 94 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-02 04:30:24 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 7 -> 7 (delta 0); `data/output/` com 94 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-02 04:30:22 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 13 -> 15 (delta 2); `data/output/` com 94 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-02 04:29:17 -03:00 | `CONIF` | Sucesso | Registry `conif`: 5 -> 5 (delta 0); `data/output/` com 92 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-02 04:29:12 -03:00 | `FINEP` | Sucesso | Registry `finep`: 10 -> 10 (delta 0); `data/output/` com 92 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-02 04:28:51 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 22 -> 25 (delta 3); `data/output/` com 92 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-01 07:57:10 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 4 -> 5 (delta 1); `data/output/` com 89 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-01 07:57:08 -03:00 | `CAPES` | Sucesso | Registry `capes`: 8 -> 24 (delta 16); `data/output/` com 88 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-01 07:51:43 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 5 -> 7 (delta 2); `data/output/` com 73 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-01 07:50:25 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 5 -> 13 (delta 8); `data/output/` com 71 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-01 07:48:31 -03:00 | `CONIF` | Sucesso | Registry `conif`: 3 -> 5 (delta 2); `data/output/` com 63 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-01 07:48:10 -03:00 | `FINEP` | Sucesso | Registry `finep`: 10 -> 10 (delta 0); `data/output/` com 61 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-01 07:47:48 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 13 -> 22 (delta 9); `data/output/` com 61 JSONs; arquivos não-JSON: nenhum. |
| 2026-03-31 00:38:33 -03:00 | `PROEX_IFES` | Sucesso com observações | O fluxo processou 5 editais abertos da PROEX/IFES referentes a 2026, persistiu 5 JSONs em `data/output/`, atualizou a chave `proex_ifes` em `registry/processed_editais.json` com as 5 URLs dos PDFs principais e manteve `data/output/` apenas com arquivos `.json`. O portal `proex.ifes.edu.br` e arquivos hospedados na AGIFES responderam `403` para `requests`, então o source utilizou fallback com `curl` para baixar a listagem e os PDFs antes de concluir o OCR com Mistral. |
| 2026-03-30 18:52:05 -03:00 | `PRPPG_IFES` | Sucesso com observações | O fluxo processou 5 editais PRPPG/IFES com data de início em 2026, persistiu 5 JSONs em `data/output/`, atualizou a chave `prppg_ifes` em `registry/processed_editais.json` com 5 URLs estáveis `?cod=...` e manteve `data/output/` apenas com arquivos `.json`. Houve retries automáticos por `429` do Mistral OCR, mas o pipeline concluiu com sucesso. |
| 2026-03-22 18:39:33 -03:00 | `CAPES`/`CNPQ` | Limpeza validada | Após remover os 2 artefatos antigos de CAPES com `data_encerramento` inferior a 2026, a validação final da pasta `data/output/` retornou `0` casos inválidos para `CAPES` e `CNPQ`. A pasta continua contendo apenas arquivos `.json`. |
| 2026-03-22 18:36:42 -03:00 | `CAPES`/`CNPQ` | Sucesso com observações | Após ajustar os sources para aceitar apenas `data_encerramento >= ano corrente`, foi feita uma rerodagem controlada com limpeza das chaves `capes` e `cnpq` no registry. O fluxo `CAPES` processou 8 itens e o `CNPQ` processou 4. O registry ficou coerente (`capes=8`, `cnpq=4`). Persistem 2 arquivos antigos de CAPES em `data/output/` com encerramento anterior a 2026, indicando resíduo de execuções anteriores e não itens novos gerados pelo source corrigido. |
| 2026-03-22 18:15:45 -03:00 | `CNPQ` | Sem novos itens | O fluxo executou com sucesso, mas `CnpqSource` extraiu `0` chamadas novas porque as 4 URLs/permalinks atuais já estão registradas em `registry/processed_editais.json` na chave `cnpq`. Os 4 JSONs do CNPq permanecem presentes em `data/output/`. |
| 2026-03-22 17:58:37 -03:00 | `CNPQ` | Sucesso com observações | Após limpeza controlada da chave `cnpq` no registry, o fluxo processou 4 chamadas abertas, persistiu 4 JSONs, atualizou `registry/processed_editais.json` com 4 permalinks e manteve `data/output/` apenas com `.json`. O source passou a ignorar anexos `application/msword` para OCR. Na validação final, 1 JSON ficou com `orgão_fomento` vazio após a extração. |
| 2026-03-22 16:44:00 -03:00 | `CAPES` | Sucesso com observações | O fluxo processou 13 páginas da seção `Editais Abertos`, transformou 13 registros com OCR Mistral, persistiu 13 URLs no registry `capes` e manteve `data/output/` apenas com arquivos `.json`. Na validação pós-processamento, 2 JSONs ficaram com `orgão_fomento` divergente do esperado (`""` e `CAPES/SENAD`), embora os links e anexos tenham sido persistidos corretamente. |
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
