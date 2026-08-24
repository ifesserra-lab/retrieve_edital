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
| 2026-08-24 00:52:59 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 15 -> 15 (delta 0); `data/output/` com 678 JSONs; arquivos não-JSON: nenhum. Origem devolveu 9 itens brutos. |
| 2026-08-24 00:52:58 -03:00 | `CAPES` | Sucesso | Registry `capes`: 31 -> 31 (delta 0); `data/output/` com 678 JSONs; arquivos não-JSON: nenhum. Origem devolveu 29 itens brutos. |
| 2026-08-24 00:52:44 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 0 -> 0 (delta 0); `data/output/` com 678 JSONs; arquivos não-JSON: nenhum. Origem devolveu 7 itens brutos. |
| 2026-08-24 00:49:36 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 18 -> 18 (delta 0); `data/output/` com 678 JSONs; arquivos não-JSON: nenhum. Origem devolveu 110 itens brutos. |
| 2026-08-24 00:49:17 -03:00 | `CONIF` | Sucesso | Registry `conif`: 11 -> 11 (delta 0); `data/output/` com 678 JSONs; arquivos não-JSON: nenhum. Origem devolveu 6 itens brutos. |
| 2026-08-24 00:49:12 -03:00 | `FINEP` | Sucesso | Registry `finep`: 31 -> 31 (delta 0); `data/output/` com 678 JSONs; arquivos não-JSON: nenhum. Origem devolveu 37 itens brutos. |
| 2026-08-24 00:49:08 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 79 -> 79 (delta 0); `data/output/` com 678 JSONs; arquivos não-JSON: nenhum. Origem devolveu 2 itens brutos. |
| 2026-08-23 00:49:17 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 15 -> 15 (delta 0); `data/output/` com 678 JSONs; arquivos não-JSON: nenhum. Origem devolveu 9 itens brutos. |
| 2026-08-23 00:49:16 -03:00 | `CAPES` | Sucesso | Registry `capes`: 31 -> 31 (delta 0); `data/output/` com 678 JSONs; arquivos não-JSON: nenhum. Origem devolveu 29 itens brutos. |
| 2026-08-23 00:49:00 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 0 -> 0 (delta 0); `data/output/` com 678 JSONs; arquivos não-JSON: nenhum. Origem devolveu 7 itens brutos. |
| 2026-08-23 00:45:51 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 18 -> 18 (delta 0); `data/output/` com 678 JSONs; arquivos não-JSON: nenhum. Origem devolveu 110 itens brutos. |
| 2026-08-23 00:45:30 -03:00 | `CONIF` | Sucesso | Registry `conif`: 11 -> 11 (delta 0); `data/output/` com 678 JSONs; arquivos não-JSON: nenhum. Origem devolveu 6 itens brutos. |
| 2026-08-23 00:45:24 -03:00 | `FINEP` | Sucesso | Registry `finep`: 31 -> 31 (delta 0); `data/output/` com 678 JSONs; arquivos não-JSON: nenhum. Origem devolveu 37 itens brutos. |
| 2026-08-23 00:45:20 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 79 -> 79 (delta 0); `data/output/` com 678 JSONs; arquivos não-JSON: nenhum. Origem devolveu 2 itens brutos. |
| 2026-08-22 00:40:54 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 15 -> 15 (delta 0); `data/output/` com 678 JSONs; arquivos não-JSON: nenhum. Origem devolveu 9 itens brutos. |
| 2026-08-22 00:40:53 -03:00 | `CAPES` | Sucesso | Registry `capes`: 31 -> 31 (delta 0); `data/output/` com 678 JSONs; arquivos não-JSON: nenhum. Origem devolveu 29 itens brutos. |
| 2026-08-22 00:40:39 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 0 -> 0 (delta 0); `data/output/` com 678 JSONs; arquivos não-JSON: nenhum. Origem devolveu 7 itens brutos. |
| 2026-08-22 00:37:30 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 17 -> 18 (delta 1); `data/output/` com 678 JSONs; arquivos não-JSON: nenhum. Origem devolveu 110 itens brutos. |
| 2026-08-22 00:37:11 -03:00 | `CONIF` | Sucesso | Registry `conif`: 11 -> 11 (delta 0); `data/output/` com 677 JSONs; arquivos não-JSON: nenhum. Origem devolveu 6 itens brutos. |
| 2026-08-22 00:37:06 -03:00 | `FINEP` | Sucesso | Registry `finep`: 31 -> 31 (delta 0); `data/output/` com 677 JSONs; arquivos não-JSON: nenhum. Origem devolveu 37 itens brutos. |
| 2026-08-22 00:37:02 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 79 -> 79 (delta 0); `data/output/` com 677 JSONs; arquivos não-JSON: nenhum. Origem devolveu 2 itens brutos. |
| 2026-08-21 00:48:19 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 15 -> 15 (delta 0); `data/output/` com 677 JSONs; arquivos não-JSON: nenhum. Origem devolveu 9 itens brutos. |
| 2026-08-21 00:48:17 -03:00 | `CAPES` | Sucesso | Registry `capes`: 31 -> 31 (delta 0); `data/output/` com 677 JSONs; arquivos não-JSON: nenhum. Origem devolveu 29 itens brutos. |
| 2026-08-21 00:48:01 -03:00 | `PROEX_IFES` | Atenção | Registry `proex_ifes`: 0 -> 0 (delta 0); `data/output/` com 677 JSONs; arquivos não-JSON: nenhum. Origem devolveu 0 itens brutos. A origem não devolveu nenhum item — verificar se o portal mudou. |
| 2026-08-21 00:47:56 -03:00 | `PRPPG_IFES` | Atenção | Registry `prppg_ifes`: 17 -> 17 (delta 0); `data/output/` com 677 JSONs; arquivos não-JSON: nenhum. Origem devolveu 0 itens brutos. A origem não devolveu nenhum item — verificar se o portal mudou. |
| 2026-08-21 00:47:24 -03:00 | `CONIF` | Sucesso | Registry `conif`: 11 -> 11 (delta 0); `data/output/` com 677 JSONs; arquivos não-JSON: nenhum. Origem devolveu 6 itens brutos. |
| 2026-08-21 00:47:19 -03:00 | `FINEP` | Sucesso | Registry `finep`: 31 -> 31 (delta 0); `data/output/` com 677 JSONs; arquivos não-JSON: nenhum. Origem devolveu 37 itens brutos. |
| 2026-08-21 00:47:15 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 79 -> 79 (delta 0); `data/output/` com 677 JSONs; arquivos não-JSON: nenhum. Origem devolveu 6 itens brutos. |
| 2026-08-20 00:44:23 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 13 -> 15 (delta 2); `data/output/` com 677 JSONs; arquivos não-JSON: nenhum. Origem devolveu 9 itens brutos. |
| 2026-08-20 00:43:34 -03:00 | `CAPES` | Sucesso | Registry `capes`: 31 -> 31 (delta 0); `data/output/` com 675 JSONs; arquivos não-JSON: nenhum. Origem devolveu 29 itens brutos. |
| 2026-08-20 00:43:22 -03:00 | `PROEX_IFES` | Atenção | Registry `proex_ifes`: 0 -> 0 (delta 0); `data/output/` com 675 JSONs; arquivos não-JSON: nenhum. Origem devolveu 0 itens brutos. A origem não devolveu nenhum item — verificar se o portal mudou. |
| 2026-08-20 00:43:20 -03:00 | `PRPPG_IFES` | Atenção | Registry `prppg_ifes`: 17 -> 17 (delta 0); `data/output/` com 675 JSONs; arquivos não-JSON: nenhum. Origem devolveu 0 itens brutos. A origem não devolveu nenhum item — verificar se o portal mudou. |
| 2026-08-20 00:42:49 -03:00 | `CONIF` | Sucesso | Registry `conif`: 11 -> 11 (delta 0); `data/output/` com 675 JSONs; arquivos não-JSON: nenhum. Origem devolveu 6 itens brutos. |
| 2026-08-20 00:42:43 -03:00 | `FINEP` | Sucesso | Registry `finep`: 31 -> 31 (delta 0); `data/output/` com 675 JSONs; arquivos não-JSON: nenhum. Origem devolveu 37 itens brutos. |
| 2026-08-20 00:42:40 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 79 -> 79 (delta 0); `data/output/` com 675 JSONs; arquivos não-JSON: nenhum. Origem devolveu 6 itens brutos. |
| 2026-08-19 00:45:16 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 13 -> 13 (delta 0); `data/output/` com 675 JSONs; arquivos não-JSON: nenhum. Origem devolveu 7 itens brutos. |
| 2026-08-19 00:45:15 -03:00 | `CAPES` | Sucesso | Registry `capes`: 31 -> 31 (delta 0); `data/output/` com 675 JSONs; arquivos não-JSON: nenhum. Origem devolveu 29 itens brutos. |
| 2026-08-19 00:44:58 -03:00 | `PROEX_IFES` | Atenção | Registry `proex_ifes`: 0 -> 0 (delta 0); `data/output/` com 675 JSONs; arquivos não-JSON: nenhum. Origem devolveu 0 itens brutos. A origem não devolveu nenhum item — verificar se o portal mudou. |
| 2026-08-19 00:44:56 -03:00 | `PRPPG_IFES` | Atenção | Registry `prppg_ifes`: 17 -> 17 (delta 0); `data/output/` com 675 JSONs; arquivos não-JSON: nenhum. Origem devolveu 0 itens brutos. A origem não devolveu nenhum item — verificar se o portal mudou. |
| 2026-08-19 00:44:25 -03:00 | `CONIF` | Sucesso | Registry `conif`: 11 -> 11 (delta 0); `data/output/` com 675 JSONs; arquivos não-JSON: nenhum. Origem devolveu 6 itens brutos. |
| 2026-08-19 00:44:20 -03:00 | `FINEP` | Sucesso | Registry `finep`: 31 -> 31 (delta 0); `data/output/` com 675 JSONs; arquivos não-JSON: nenhum. Origem devolveu 37 itens brutos. |
| 2026-08-19 00:44:15 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 79 -> 79 (delta 0); `data/output/` com 675 JSONs; arquivos não-JSON: nenhum. Origem devolveu 6 itens brutos. |
| 2026-08-18 00:44:17 -03:00 | `CNPQ` | Atenção | Registry `cnpq`: 13 -> 13 (delta 0); `data/output/` com 675 JSONs; arquivos não-JSON: nenhum. Origem devolveu 0 itens brutos. A origem não devolveu nenhum item — verificar se o portal mudou. |
| 2026-08-18 00:43:46 -03:00 | `CAPES` | Atenção | Registry `capes`: 31 -> 31 (delta 0); `data/output/` com 675 JSONs; arquivos não-JSON: nenhum. Origem devolveu 0 itens brutos. A origem não devolveu nenhum item — verificar se o portal mudou. |
| 2026-08-18 00:42:45 -03:00 | `PROEX_IFES` | Atenção | Registry `proex_ifes`: 0 -> 0 (delta 0); `data/output/` com 675 JSONs; arquivos não-JSON: nenhum. Origem devolveu 0 itens brutos. A origem não devolveu nenhum item — verificar se o portal mudou. |
| 2026-08-18 00:41:43 -03:00 | `PRPPG_IFES` | Atenção | Registry `prppg_ifes`: 17 -> 17 (delta 0); `data/output/` com 675 JSONs; arquivos não-JSON: nenhum. Origem devolveu 0 itens brutos. A origem não devolveu nenhum item — verificar se o portal mudou. |
| 2026-08-18 00:41:12 -03:00 | `CONIF` | Sucesso | Registry `conif`: 11 -> 11 (delta 0); `data/output/` com 675 JSONs; arquivos não-JSON: nenhum. Origem devolveu 6 itens brutos. |
| 2026-08-18 00:41:06 -03:00 | `FINEP` | Sucesso | Registry `finep`: 31 -> 31 (delta 0); `data/output/` com 675 JSONs; arquivos não-JSON: nenhum. Origem devolveu 37 itens brutos. |
| 2026-08-18 00:41:02 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 79 -> 79 (delta 0); `data/output/` com 675 JSONs; arquivos não-JSON: nenhum. Origem devolveu 6 itens brutos. |
| 2026-08-17 00:46:57 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 13 -> 13 (delta 0); `data/output/` com 669 JSONs; arquivos não-JSON: nenhum. Origem devolveu 7 itens brutos. |
| 2026-08-17 00:46:55 -03:00 | `CAPES` | Sucesso | Registry `capes`: 31 -> 31 (delta 0); `data/output/` com 669 JSONs; arquivos não-JSON: nenhum. Origem devolveu 29 itens brutos. |
| 2026-08-17 00:46:42 -03:00 | `PROEX_IFES` | Atenção | Registry `proex_ifes`: 0 -> 0 (delta 0); `data/output/` com 669 JSONs; arquivos não-JSON: nenhum. Origem devolveu 0 itens brutos. A origem não devolveu nenhum item — verificar se o portal mudou. |
| 2026-08-17 00:46:40 -03:00 | `PRPPG_IFES` | Atenção | Registry `prppg_ifes`: 17 -> 17 (delta 0); `data/output/` com 669 JSONs; arquivos não-JSON: nenhum. Origem devolveu 0 itens brutos. A origem não devolveu nenhum item — verificar se o portal mudou. |
| 2026-08-17 00:46:09 -03:00 | `CONIF` | Sucesso | Registry `conif`: 11 -> 11 (delta 0); `data/output/` com 669 JSONs; arquivos não-JSON: nenhum. Origem devolveu 6 itens brutos. |
| 2026-08-17 00:46:03 -03:00 | `FINEP` | Sucesso | Registry `finep`: 31 -> 31 (delta 0); `data/output/` com 669 JSONs; arquivos não-JSON: nenhum. Origem devolveu 37 itens brutos. |
| 2026-08-17 00:46:00 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 79 -> 79 (delta 0); `data/output/` com 669 JSONs; arquivos não-JSON: nenhum. Origem devolveu 6 itens brutos. |
| 2026-08-16 00:45:35 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 13 -> 13 (delta 0); `data/output/` com 669 JSONs; arquivos não-JSON: nenhum. Origem devolveu 7 itens brutos. |
| 2026-08-16 00:45:33 -03:00 | `CAPES` | Sucesso | Registry `capes`: 31 -> 31 (delta 0); `data/output/` com 669 JSONs; arquivos não-JSON: nenhum. Origem devolveu 29 itens brutos. |
| 2026-08-16 00:45:20 -03:00 | `PROEX_IFES` | Atenção | Registry `proex_ifes`: 0 -> 0 (delta 0); `data/output/` com 669 JSONs; arquivos não-JSON: nenhum. Origem devolveu 0 itens brutos. A origem não devolveu nenhum item — verificar se o portal mudou. |
| 2026-08-16 00:45:18 -03:00 | `PRPPG_IFES` | Atenção | Registry `prppg_ifes`: 17 -> 17 (delta 0); `data/output/` com 669 JSONs; arquivos não-JSON: nenhum. Origem devolveu 0 itens brutos. A origem não devolveu nenhum item — verificar se o portal mudou. |
| 2026-08-16 00:44:47 -03:00 | `CONIF` | Sucesso | Registry `conif`: 11 -> 11 (delta 0); `data/output/` com 669 JSONs; arquivos não-JSON: nenhum. Origem devolveu 6 itens brutos. |
| 2026-08-16 00:44:41 -03:00 | `FINEP` | Sucesso | Registry `finep`: 31 -> 31 (delta 0); `data/output/` com 669 JSONs; arquivos não-JSON: nenhum. Origem devolveu 37 itens brutos. |
| 2026-08-16 00:44:38 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 79 -> 79 (delta 0); `data/output/` com 669 JSONs; arquivos não-JSON: nenhum. Origem devolveu 6 itens brutos. |
| 2026-08-15 00:37:22 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 13 -> 13 (delta 0); `data/output/` com 669 JSONs; arquivos não-JSON: nenhum. Origem devolveu 7 itens brutos. |
| 2026-08-15 00:37:21 -03:00 | `CAPES` | Sucesso | Registry `capes`: 30 -> 31 (delta 1); `data/output/` com 669 JSONs; arquivos não-JSON: nenhum. Origem devolveu 29 itens brutos. |
| 2026-08-15 00:36:18 -03:00 | `PROEX_IFES` | Atenção | Registry `proex_ifes`: 0 -> 0 (delta 0); `data/output/` com 668 JSONs; arquivos não-JSON: nenhum. Origem devolveu 0 itens brutos. A origem não devolveu nenhum item — verificar se o portal mudou. |
| 2026-08-15 00:36:16 -03:00 | `PRPPG_IFES` | Atenção | Registry `prppg_ifes`: 17 -> 17 (delta 0); `data/output/` com 668 JSONs; arquivos não-JSON: nenhum. Origem devolveu 0 itens brutos. A origem não devolveu nenhum item — verificar se o portal mudou. |
| 2026-08-15 00:35:45 -03:00 | `CONIF` | Sucesso | Registry `conif`: 11 -> 11 (delta 0); `data/output/` com 668 JSONs; arquivos não-JSON: nenhum. Origem devolveu 6 itens brutos. |
| 2026-08-15 00:35:40 -03:00 | `FINEP` | Sucesso | Registry `finep`: 31 -> 31 (delta 0); `data/output/` com 668 JSONs; arquivos não-JSON: nenhum. Origem devolveu 37 itens brutos. |
| 2026-08-15 00:35:36 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 79 -> 79 (delta 0); `data/output/` com 668 JSONs; arquivos não-JSON: nenhum. Origem devolveu 6 itens brutos. |
| 2026-08-14 01:47:27 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 13 -> 13 (delta 0); `data/output/` com 668 JSONs; arquivos não-JSON: nenhum. Origem devolveu 8 itens brutos. |
| 2026-08-14 01:47:26 -03:00 | `CAPES` | Sucesso | Registry `capes`: 30 -> 30 (delta 0); `data/output/` com 668 JSONs; arquivos não-JSON: nenhum. Origem devolveu 28 itens brutos. |
| 2026-08-14 01:47:14 -03:00 | `PROEX_IFES` | Atenção | Registry `proex_ifes`: 0 -> 0 (delta 0); `data/output/` com 668 JSONs; arquivos não-JSON: nenhum. Origem devolveu 0 itens brutos. A origem não devolveu nenhum item — verificar se o portal mudou. |
| 2026-08-14 01:47:11 -03:00 | `PRPPG_IFES` | Atenção | Registry `prppg_ifes`: 17 -> 17 (delta 0); `data/output/` com 668 JSONs; arquivos não-JSON: nenhum. Origem devolveu 0 itens brutos. A origem não devolveu nenhum item — verificar se o portal mudou. |
| 2026-08-14 01:46:40 -03:00 | `CONIF` | Sucesso | Registry `conif`: 11 -> 11 (delta 0); `data/output/` com 668 JSONs; arquivos não-JSON: nenhum. Origem devolveu 6 itens brutos. |
| 2026-08-14 01:46:34 -03:00 | `FINEP` | Sucesso | Registry `finep`: 31 -> 31 (delta 0); `data/output/` com 668 JSONs; arquivos não-JSON: nenhum. Origem devolveu 37 itens brutos. |
| 2026-08-14 01:46:31 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 79 -> 79 (delta 0); `data/output/` com 668 JSONs; arquivos não-JSON: nenhum. Origem devolveu 6 itens brutos. |
| 2026-08-13 01:54:47 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 13 -> 13 (delta 0); `data/output/` com 668 JSONs; arquivos não-JSON: nenhum. Origem devolveu 9 itens brutos. |
| 2026-08-13 01:54:46 -03:00 | `CAPES` | Sucesso | Registry `capes`: 29 -> 30 (delta 1); `data/output/` com 668 JSONs; arquivos não-JSON: nenhum. Origem devolveu 28 itens brutos. |
| 2026-08-13 01:53:24 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 0 -> 0 (delta 0); `data/output/` com 667 JSONs; arquivos não-JSON: nenhum. Origem devolveu 7 itens brutos. |
| 2026-08-13 01:50:15 -03:00 | `PRPPG_IFES` | Atenção | Registry `prppg_ifes`: 17 -> 17 (delta 0); `data/output/` com 667 JSONs; arquivos não-JSON: nenhum. Origem devolveu 0 itens brutos. A origem não devolveu nenhum item — verificar se o portal mudou. |
| 2026-08-13 01:49:44 -03:00 | `CONIF` | Sucesso | Registry `conif`: 11 -> 11 (delta 0); `data/output/` com 667 JSONs; arquivos não-JSON: nenhum. Origem devolveu 6 itens brutos. |
| 2026-08-13 01:49:39 -03:00 | `FINEP` | Sucesso | Registry `finep`: 31 -> 31 (delta 0); `data/output/` com 667 JSONs; arquivos não-JSON: nenhum. Origem devolveu 37 itens brutos. |
| 2026-08-13 01:49:35 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 79 -> 79 (delta 0); `data/output/` com 667 JSONs; arquivos não-JSON: nenhum. Origem devolveu 6 itens brutos. |
| 2026-08-12 01:46:58 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 13 -> 13 (delta 0); `data/output/` com 667 JSONs; arquivos não-JSON: nenhum. Origem devolveu 9 itens brutos. |
| 2026-08-12 01:46:56 -03:00 | `CAPES` | Sucesso | Registry `capes`: 29 -> 29 (delta 0); `data/output/` com 667 JSONs; arquivos não-JSON: nenhum. Origem devolveu 27 itens brutos. |
| 2026-08-12 01:46:41 -03:00 | `PROEX_IFES` | Atenção | Registry `proex_ifes`: 0 -> 0 (delta 0); `data/output/` com 667 JSONs; arquivos não-JSON: nenhum. Origem devolveu 0 itens brutos. A origem não devolveu nenhum item — verificar se o portal mudou. |
| 2026-08-12 01:46:39 -03:00 | `PRPPG_IFES` | Atenção | Registry `prppg_ifes`: 17 -> 17 (delta 0); `data/output/` com 667 JSONs; arquivos não-JSON: nenhum. Origem devolveu 0 itens brutos. A origem não devolveu nenhum item — verificar se o portal mudou. |
| 2026-08-12 01:46:07 -03:00 | `CONIF` | Sucesso | Registry `conif`: 11 -> 11 (delta 0); `data/output/` com 667 JSONs; arquivos não-JSON: nenhum. Origem devolveu 6 itens brutos. |
| 2026-08-12 01:46:02 -03:00 | `FINEP` | Sucesso | Registry `finep`: 31 -> 31 (delta 0); `data/output/` com 667 JSONs; arquivos não-JSON: nenhum. Origem devolveu 37 itens brutos. |
| 2026-08-12 01:45:58 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 79 -> 79 (delta 0); `data/output/` com 667 JSONs; arquivos não-JSON: nenhum. Origem devolveu 6 itens brutos. |
| 2026-08-11 01:22:37 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 12 -> 13 (delta 1); `data/output/` com 667 JSONs; arquivos não-JSON: nenhum. Origem devolveu 10 itens brutos. |
| 2026-08-11 01:21:47 -03:00 | `CAPES` | Sucesso | Registry `capes`: 23 -> 29 (delta 6); `data/output/` com 666 JSONs; arquivos não-JSON: nenhum. Origem devolveu 27 itens brutos. |
| 2026-08-11 01:18:54 -03:00 | `PROEX_IFES` | Atenção | Registry `proex_ifes`: 0 -> 0 (delta 0); `data/output/` com 661 JSONs; arquivos não-JSON: nenhum. Origem devolveu 0 itens brutos. A origem não devolveu nenhum item — verificar se o portal mudou. |
| 2026-08-11 01:17:53 -03:00 | `PRPPG_IFES` | Atenção | Registry `prppg_ifes`: 17 -> 17 (delta 0); `data/output/` com 661 JSONs; arquivos não-JSON: nenhum. Origem devolveu 0 itens brutos. A origem não devolveu nenhum item — verificar se o portal mudou. |
| 2026-08-11 01:17:22 -03:00 | `CONIF` | Sucesso | Registry `conif`: 11 -> 11 (delta 0); `data/output/` com 661 JSONs; arquivos não-JSON: nenhum. Origem devolveu 6 itens brutos. |
| 2026-08-11 01:17:15 -03:00 | `FINEP` | Sucesso | Registry `finep`: 31 -> 31 (delta 0); `data/output/` com 661 JSONs; arquivos não-JSON: nenhum. Origem devolveu 37 itens brutos. |
| 2026-08-11 01:17:11 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 79 -> 79 (delta 0); `data/output/` com 661 JSONs; arquivos não-JSON: nenhum. Origem devolveu 6 itens brutos. |
| 2026-08-10 01:33:35 -03:00 | `CNPQ` | Atenção | Registry `cnpq`: 12 -> 12 (delta 0); `data/output/` com 661 JSONs; arquivos não-JSON: nenhum. Origem devolveu 0 itens brutos. A origem não devolveu nenhum item — verificar se o portal mudou. |
| 2026-08-10 01:33:04 -03:00 | `CAPES` | Atenção | Registry `capes`: 23 -> 23 (delta 0); `data/output/` com 661 JSONs; arquivos não-JSON: nenhum. Origem devolveu 0 itens brutos. A origem não devolveu nenhum item — verificar se o portal mudou. |
| 2026-08-10 01:32:03 -03:00 | `PROEX_IFES` | Atenção | Registry `proex_ifes`: 0 -> 0 (delta 0); `data/output/` com 661 JSONs; arquivos não-JSON: nenhum. Origem devolveu 0 itens brutos. A origem não devolveu nenhum item — verificar se o portal mudou. |
| 2026-08-10 01:31:02 -03:00 | `PRPPG_IFES` | Atenção | Registry `prppg_ifes`: 17 -> 17 (delta 0); `data/output/` com 661 JSONs; arquivos não-JSON: nenhum. Origem devolveu 0 itens brutos. A origem não devolveu nenhum item — verificar se o portal mudou. |
| 2026-08-10 01:30:31 -03:00 | `CONIF` | Sucesso | Registry `conif`: 7 -> 11 (delta 4); `data/output/` com 661 JSONs; arquivos não-JSON: nenhum. Origem devolveu 6 itens brutos. |
| 2026-08-10 01:28:40 -03:00 | `FINEP` | Sucesso | Registry `finep`: 31 -> 31 (delta 0); `data/output/` com 657 JSONs; arquivos não-JSON: nenhum. Origem devolveu 37 itens brutos. |
| 2026-08-10 01:28:36 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 79 -> 79 (delta 0); `data/output/` com 657 JSONs; arquivos não-JSON: nenhum. Origem devolveu 6 itens brutos. |
| 2026-08-09 01:23:01 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 12 -> 12 (delta 0); `data/output/` com 657 JSONs; arquivos não-JSON: nenhum. Origem devolveu 10 itens brutos. |
| 2026-08-09 01:22:35 -03:00 | `CAPES` | Sucesso | Registry `capes`: 23 -> 23 (delta 0); `data/output/` com 657 JSONs; arquivos não-JSON: nenhum. Origem devolveu 27 itens brutos. |
| 2026-08-09 01:20:57 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 0 -> 0 (delta 0); `data/output/` com 657 JSONs; arquivos não-JSON: nenhum. Origem devolveu 7 itens brutos. |
| 2026-08-09 01:18:37 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 17 -> 17 (delta 0); `data/output/` com 657 JSONs; arquivos não-JSON: nenhum. Origem devolveu 110 itens brutos. |
| 2026-08-09 01:18:12 -03:00 | `CONIF` | Sucesso | Registry `conif`: 7 -> 7 (delta 0); `data/output/` com 657 JSONs; arquivos não-JSON: nenhum. Origem devolveu 6 itens brutos. |
| 2026-08-09 01:16:51 -03:00 | `FINEP` | Sucesso | Registry `finep`: 31 -> 31 (delta 0); `data/output/` com 657 JSONs; arquivos não-JSON: nenhum. Origem devolveu 37 itens brutos. |
| 2026-08-09 01:15:44 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 79 -> 79 (delta 0); `data/output/` com 657 JSONs; arquivos não-JSON: nenhum. Origem devolveu 6 itens brutos. |
| 2026-08-08 02:04:43 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 12 -> 12 (delta 0); `data/output/` com 657 JSONs; arquivos não-JSON: nenhum. Origem devolveu 10 itens brutos. |
| 2026-08-08 02:00:02 -03:00 | `CAPES` | Sucesso | Registry `capes`: 22 -> 23 (delta 1); `data/output/` com 657 JSONs; arquivos não-JSON: nenhum. Origem devolveu 27 itens brutos. |
| 2026-08-08 01:44:21 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 0 -> 0 (delta 0); `data/output/` com 656 JSONs; arquivos não-JSON: nenhum. Origem devolveu 7 itens brutos. |
| 2026-08-08 01:30:16 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 17 -> 17 (delta 0); `data/output/` com 656 JSONs; arquivos não-JSON: nenhum. Origem devolveu 110 itens brutos. |
| 2026-08-08 01:29:59 -03:00 | `CONIF` | Sucesso | Registry `conif`: 7 -> 7 (delta 0); `data/output/` com 656 JSONs; arquivos não-JSON: nenhum. Origem devolveu 6 itens brutos. |
| 2026-08-08 01:24:50 -03:00 | `FINEP` | Sucesso | Registry `finep`: 31 -> 31 (delta 0); `data/output/` com 656 JSONs; arquivos não-JSON: nenhum. Origem devolveu 37 itens brutos. |
| 2026-08-08 01:23:45 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 79 -> 79 (delta 0); `data/output/` com 656 JSONs; arquivos não-JSON: nenhum. Origem devolveu 6 itens brutos. |
| 2026-08-07 01:57:23 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 12 -> 12 (delta 0); `data/output/` com 656 JSONs; arquivos não-JSON: nenhum. Origem devolveu 10 itens brutos. |
| 2026-08-07 01:57:00 -03:00 | `CAPES` | Sucesso | Registry `capes`: 22 -> 22 (delta 0); `data/output/` com 656 JSONs; arquivos não-JSON: nenhum. Origem devolveu 26 itens brutos. |
| 2026-08-07 01:54:32 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 0 -> 0 (delta 0); `data/output/` com 656 JSONs; arquivos não-JSON: nenhum. Origem devolveu 7 itens brutos. |
| 2026-08-07 01:52:32 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 17 -> 17 (delta 0); `data/output/` com 656 JSONs; arquivos não-JSON: nenhum. Origem devolveu 110 itens brutos. |
| 2026-08-07 01:52:13 -03:00 | `CONIF` | Sucesso | Registry `conif`: 7 -> 7 (delta 0); `data/output/` com 656 JSONs; arquivos não-JSON: nenhum. Origem devolveu 6 itens brutos. |
| 2026-08-07 01:51:33 -03:00 | `FINEP` | Sucesso | Registry `finep`: 31 -> 31 (delta 0); `data/output/` com 656 JSONs; arquivos não-JSON: nenhum. Origem devolveu 37 itens brutos. |
| 2026-08-07 01:51:31 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 78 -> 79 (delta 1); `data/output/` com 656 JSONs; arquivos não-JSON: nenhum. Origem devolveu 2 itens brutos. |
| 2026-08-06 02:46:51 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 12 -> 12 (delta 0); `data/output/` com 655 JSONs; arquivos não-JSON: nenhum. Origem devolveu 11 itens brutos. |
| 2026-08-06 02:46:28 -03:00 | `CAPES` | Sucesso | Registry `capes`: 22 -> 22 (delta 0); `data/output/` com 655 JSONs; arquivos não-JSON: nenhum. Origem devolveu 26 itens brutos. |
| 2026-08-06 02:44:59 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 0 -> 0 (delta 0); `data/output/` com 655 JSONs; arquivos não-JSON: nenhum. Origem devolveu 7 itens brutos. |
| 2026-08-06 02:42:59 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 17 -> 17 (delta 0); `data/output/` com 655 JSONs; arquivos não-JSON: nenhum. Origem devolveu 110 itens brutos. |
| 2026-08-06 02:42:42 -03:00 | `CONIF` | Sucesso | Registry `conif`: 7 -> 7 (delta 0); `data/output/` com 655 JSONs; arquivos não-JSON: nenhum. Origem devolveu 6 itens brutos. |
| 2026-08-06 02:41:58 -03:00 | `FINEP` | Sucesso | Registry `finep`: 30 -> 31 (delta 1); `data/output/` com 655 JSONs; arquivos não-JSON: nenhum. Origem devolveu 37 itens brutos. |
| 2026-08-06 02:41:55 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 78 -> 78 (delta 0); `data/output/` com 654 JSONs; arquivos não-JSON: nenhum. Origem devolveu 1 itens brutos. |
| 2026-08-05 02:47:52 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 11 -> 12 (delta 1); `data/output/` com 654 JSONs; arquivos não-JSON: nenhum. Origem devolveu 11 itens brutos. |
| 2026-08-05 02:47:12 -03:00 | `CAPES` | Sucesso | Registry `capes`: 22 -> 22 (delta 0); `data/output/` com 653 JSONs; arquivos não-JSON: nenhum. Origem devolveu 26 itens brutos. |
| 2026-08-05 02:44:02 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 0 -> 0 (delta 0); `data/output/` com 653 JSONs; arquivos não-JSON: nenhum. Origem devolveu 7 itens brutos. |
| 2026-08-05 02:42:08 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 17 -> 17 (delta 0); `data/output/` com 653 JSONs; arquivos não-JSON: nenhum. Origem devolveu 110 itens brutos. |
| 2026-08-05 02:41:48 -03:00 | `CONIF` | Sucesso | Registry `conif`: 7 -> 7 (delta 0); `data/output/` com 653 JSONs; arquivos não-JSON: nenhum. Origem devolveu 6 itens brutos. |
| 2026-08-05 02:40:57 -03:00 | `FINEP` | Sucesso | Registry `finep`: 30 -> 30 (delta 0); `data/output/` com 653 JSONs; arquivos não-JSON: nenhum. Origem devolveu 36 itens brutos. |
| 2026-08-05 02:40:55 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 72 -> 78 (delta 6); `data/output/` com 653 JSONs; arquivos não-JSON: nenhum. Origem devolveu 2 itens brutos. |
| 2026-08-04 02:49:29 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 10 -> 11 (delta 1); `data/output/` com 652 JSONs; arquivos não-JSON: nenhum. Origem devolveu 9 itens brutos. |
| 2026-08-04 02:49:09 -03:00 | `CAPES` | Sucesso | Registry `capes`: 22 -> 22 (delta 0); `data/output/` com 651 JSONs; arquivos não-JSON: nenhum. Origem devolveu 26 itens brutos. |
| 2026-08-04 02:46:17 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 0 -> 0 (delta 0); `data/output/` com 651 JSONs; arquivos não-JSON: nenhum. Origem devolveu 7 itens brutos. |
| 2026-08-04 02:44:04 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 16 -> 17 (delta 1); `data/output/` com 651 JSONs; arquivos não-JSON: nenhum. Origem devolveu 110 itens brutos. |
| 2026-08-04 02:42:22 -03:00 | `CONIF` | Sucesso | Registry `conif`: 7 -> 7 (delta 0); `data/output/` com 650 JSONs; arquivos não-JSON: nenhum. Origem devolveu 6 itens brutos. |
| 2026-08-04 02:41:39 -03:00 | `FINEP` | Sucesso | Registry `finep`: 30 -> 30 (delta 0); `data/output/` com 650 JSONs; arquivos não-JSON: nenhum. Origem devolveu 36 itens brutos. |
| 2026-08-04 02:41:37 -03:00 | `FAPES` | Atenção | Registry `fapes`: 72 -> 72 (delta 0); `data/output/` com 650 JSONs; arquivos não-JSON: nenhum. Origem devolveu 0 itens brutos. A origem não devolveu nenhum item — verificar se o portal mudou. |
| 2026-08-03 03:17:51 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 10 -> 10 (delta 0); `data/output/` com 650 JSONs; arquivos não-JSON: nenhum. Origem devolveu 9 itens brutos. |
| 2026-08-03 03:17:50 -03:00 | `CAPES` | Sucesso | Registry `capes`: 22 -> 22 (delta 0); `data/output/` com 650 JSONs; arquivos não-JSON: nenhum. Origem devolveu 26 itens brutos. |
| 2026-08-03 03:15:55 -03:00 | `PROEX_IFES` | Atenção | Registry `proex_ifes`: 0 -> 0 (delta 0); `data/output/` com 650 JSONs; arquivos não-JSON: nenhum. Origem devolveu 0 itens brutos. A origem não devolveu nenhum item — verificar se o portal mudou. |
| 2026-08-03 03:14:54 -03:00 | `PRPPG_IFES` | Atenção | Registry `prppg_ifes`: 16 -> 16 (delta 0); `data/output/` com 650 JSONs; arquivos não-JSON: nenhum. Origem devolveu 0 itens brutos. A origem não devolveu nenhum item — verificar se o portal mudou. |
| 2026-08-03 03:14:22 -03:00 | `CONIF` | Sucesso | Registry `conif`: 7 -> 7 (delta 0); `data/output/` com 650 JSONs; arquivos não-JSON: nenhum. Origem devolveu 6 itens brutos. |
| 2026-08-03 03:13:37 -03:00 | `FINEP` | Sucesso | Registry `finep`: 30 -> 30 (delta 0); `data/output/` com 650 JSONs; arquivos não-JSON: nenhum. Origem devolveu 36 itens brutos. |
| 2026-08-03 03:13:35 -03:00 | `FAPES` | Atenção | Registry `fapes`: 72 -> 72 (delta 0); `data/output/` com 650 JSONs; arquivos não-JSON: nenhum. Origem devolveu 0 itens brutos. A origem não devolveu nenhum item — verificar se o portal mudou. |
| 2026-08-02 02:55:04 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 10 -> 10 (delta 0); `data/output/` com 650 JSONs; arquivos não-JSON: nenhum. Origem devolveu 9 itens brutos. |
| 2026-08-02 02:55:03 -03:00 | `CAPES` | Sucesso | Registry `capes`: 22 -> 22 (delta 0); `data/output/` com 650 JSONs; arquivos não-JSON: nenhum. Origem devolveu 26 itens brutos. |
| 2026-08-02 02:52:36 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 0 -> 0 (delta 0); `data/output/` com 650 JSONs; arquivos não-JSON: nenhum. Origem devolveu 7 itens brutos. |
| 2026-08-02 02:50:30 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 16 -> 16 (delta 0); `data/output/` com 650 JSONs; arquivos não-JSON: nenhum. Origem devolveu 110 itens brutos. |
| 2026-08-02 02:50:14 -03:00 | `CONIF` | Sucesso | Registry `conif`: 7 -> 7 (delta 0); `data/output/` com 650 JSONs; arquivos não-JSON: nenhum. Origem devolveu 6 itens brutos. |
| 2026-08-02 02:49:28 -03:00 | `FINEP` | Sucesso | Registry `finep`: 30 -> 30 (delta 0); `data/output/` com 650 JSONs; arquivos não-JSON: nenhum. Origem devolveu 36 itens brutos. |
| 2026-08-02 02:49:26 -03:00 | `FAPES` | Atenção | Registry `fapes`: 72 -> 72 (delta 0); `data/output/` com 650 JSONs; arquivos não-JSON: nenhum. Origem devolveu 0 itens brutos. A origem não devolveu nenhum item — verificar se o portal mudou. |
| 2026-08-01 02:53:42 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 10 -> 10 (delta 0); `data/output/` com 650 JSONs; arquivos não-JSON: nenhum. Origem devolveu 9 itens brutos. |
| 2026-08-01 02:53:40 -03:00 | `CAPES` | Sucesso | Registry `capes`: 22 -> 22 (delta 0); `data/output/` com 650 JSONs; arquivos não-JSON: nenhum. Origem devolveu 26 itens brutos. |
| 2026-08-01 02:52:10 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 0 -> 0 (delta 0); `data/output/` com 650 JSONs; arquivos não-JSON: nenhum. Origem devolveu 7 itens brutos. |
| 2026-08-01 02:50:11 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 16 -> 16 (delta 0); `data/output/` com 650 JSONs; arquivos não-JSON: nenhum. Origem devolveu 110 itens brutos. |
| 2026-08-01 02:49:42 -03:00 | `CONIF` | Sucesso | Registry `conif`: 7 -> 7 (delta 0); `data/output/` com 650 JSONs; arquivos não-JSON: nenhum. Origem devolveu 6 itens brutos. |
| 2026-08-01 02:49:00 -03:00 | `FINEP` | Sucesso | Registry `finep`: 30 -> 30 (delta 0); `data/output/` com 650 JSONs; arquivos não-JSON: nenhum. Origem devolveu 36 itens brutos. |
| 2026-08-01 02:48:58 -03:00 | `FAPES` | Atenção | Registry `fapes`: 72 -> 72 (delta 0); `data/output/` com 650 JSONs; arquivos não-JSON: nenhum. Origem devolveu 0 itens brutos. A origem não devolveu nenhum item — verificar se o portal mudou. |
| 2026-07-31 17:15:55 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 10 -> 10 (delta 0); `data/output/` com 650 JSONs; arquivos não-JSON: nenhum. Origem devolveu 9 itens brutos. |
| 2026-07-31 03:09:27 -03:00 | `CNPQ` | Atenção | Registry `cnpq`: 10 -> 10 (delta 0); `data/output/` com 153 JSONs; arquivos não-JSON: nenhum. Origem devolveu 9 itens brutos. |
| 2026-07-31 03:09:24 -03:00 | `CAPES` | Atenção | Registry `capes`: 31 -> 31 (delta 0); `data/output/` com 153 JSONs; arquivos não-JSON: nenhum. Sem editais novos há 20 execuções seguidas — verificar se o source ainda funciona. |
| 2026-07-31 03:09:12 -03:00 | `PROEX_IFES` | Atenção | Registry `proex_ifes`: 7 -> 7 (delta 0); `data/output/` com 153 JSONs; arquivos não-JSON: nenhum. Sem editais novos há 60 execuções seguidas — verificar se o source ainda funciona. |
| 2026-07-31 03:09:11 -03:00 | `PRPPG_IFES` | Atenção | Registry `prppg_ifes`: 16 -> 16 (delta 0); `data/output/` com 153 JSONs; arquivos não-JSON: nenhum. Sem editais novos há 45 execuções seguidas — verificar se o source ainda funciona. |
| 2026-07-31 03:08:54 -03:00 | `CONIF` | Sucesso | Registry `conif`: 16 -> 16 (delta 0); `data/output/` com 153 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-31 03:08:48 -03:00 | `FINEP` | Atenção | Registry `finep`: 36 -> 36 (delta 0); `data/output/` com 153 JSONs; arquivos não-JSON: nenhum. Origem devolveu 36 itens brutos. |
| 2026-07-31 03:08:46 -03:00 | `FAPES` | Atenção | Registry `fapes`: 62 -> 62 (delta 0); `data/output/` com 153 JSONs; arquivos não-JSON: nenhum. Sem editais novos há 11 execuções seguidas — verificar se o source ainda funciona. |
| 2026-07-30 02:43:29 -03:00 | `CNPQ` | Atenção | Registry `cnpq`: 10 -> 10 (delta 0); `data/output/` com 153 JSONs; arquivos não-JSON: nenhum. Origem devolveu 10 itens brutos. |
| 2026-07-30 02:43:28 -03:00 | `CAPES` | Atenção | Registry `capes`: 31 -> 31 (delta 0); `data/output/` com 153 JSONs; arquivos não-JSON: nenhum. Sem editais novos há 19 execuções seguidas — verificar se o source ainda funciona. |
| 2026-07-30 02:43:05 -03:00 | `PROEX_IFES` | Atenção | Registry `proex_ifes`: 7 -> 7 (delta 0); `data/output/` com 153 JSONs; arquivos não-JSON: nenhum. Sem editais novos há 59 execuções seguidas — verificar se o source ainda funciona. |
| 2026-07-30 02:43:03 -03:00 | `PRPPG_IFES` | Atenção | Registry `prppg_ifes`: 16 -> 16 (delta 0); `data/output/` com 153 JSONs; arquivos não-JSON: nenhum. Sem editais novos há 44 execuções seguidas — verificar se o source ainda funciona. |
| 2026-07-30 02:42:46 -03:00 | `CONIF` | Sucesso | Registry `conif`: 16 -> 16 (delta 0); `data/output/` com 153 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-30 02:42:41 -03:00 | `FINEP` | Atenção | Registry `finep`: 36 -> 36 (delta 0); `data/output/` com 153 JSONs; arquivos não-JSON: nenhum. Origem devolveu 36 itens brutos. |
| 2026-07-30 02:42:39 -03:00 | `FAPES` | Atenção | Registry `fapes`: 62 -> 62 (delta 0); `data/output/` com 153 JSONs; arquivos não-JSON: nenhum. Sem editais novos há 10 execuções seguidas — verificar se o source ainda funciona. |
| 2026-07-29 02:49:01 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 5 -> 5 (delta 0); `data/output/` com 175 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-29 02:48:59 -03:00 | `CAPES` | Sucesso | Registry `capes`: 31 -> 31 (delta 0); `data/output/` com 175 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-29 02:48:49 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 7 -> 7 (delta 0); `data/output/` com 175 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-29 02:48:47 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 16 -> 16 (delta 0); `data/output/` com 175 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-29 02:48:31 -03:00 | `CONIF` | Sucesso | Registry `conif`: 16 -> 16 (delta 0); `data/output/` com 175 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-29 02:48:25 -03:00 | `FINEP` | Sucesso | Registry `finep`: 10 -> 10 (delta 0); `data/output/` com 175 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-29 02:48:02 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 91 -> 91 (delta 0); `data/output/` com 175 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-28 02:44:27 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 5 -> 5 (delta 0); `data/output/` com 175 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-28 02:44:25 -03:00 | `CAPES` | Sucesso | Registry `capes`: 31 -> 31 (delta 0); `data/output/` com 175 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-28 02:44:15 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 7 -> 7 (delta 0); `data/output/` com 175 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-28 02:44:13 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 16 -> 16 (delta 0); `data/output/` com 175 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-28 02:43:57 -03:00 | `CONIF` | Sucesso | Registry `conif`: 16 -> 16 (delta 0); `data/output/` com 175 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-28 02:43:53 -03:00 | `FINEP` | Sucesso | Registry `finep`: 10 -> 10 (delta 0); `data/output/` com 175 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-28 02:43:30 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 91 -> 91 (delta 0); `data/output/` com 175 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-27 03:25:26 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 5 -> 5 (delta 0); `data/output/` com 175 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-27 03:25:25 -03:00 | `CAPES` | Sucesso | Registry `capes`: 31 -> 31 (delta 0); `data/output/` com 175 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-27 03:25:13 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 7 -> 7 (delta 0); `data/output/` com 175 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-27 03:25:11 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 16 -> 16 (delta 0); `data/output/` com 175 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-27 03:24:54 -03:00 | `CONIF` | Sucesso | Registry `conif`: 16 -> 16 (delta 0); `data/output/` com 175 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-27 03:24:50 -03:00 | `FINEP` | Sucesso | Registry `finep`: 10 -> 10 (delta 0); `data/output/` com 175 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-27 03:24:27 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 91 -> 91 (delta 0); `data/output/` com 175 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-26 02:59:47 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 5 -> 5 (delta 0); `data/output/` com 175 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-26 02:59:45 -03:00 | `CAPES` | Sucesso | Registry `capes`: 31 -> 31 (delta 0); `data/output/` com 175 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-26 02:58:44 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 7 -> 7 (delta 0); `data/output/` com 175 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-26 02:57:43 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 16 -> 16 (delta 0); `data/output/` com 175 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-26 02:57:12 -03:00 | `CONIF` | Sucesso | Registry `conif`: 15 -> 16 (delta 1); `data/output/` com 175 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-26 02:56:20 -03:00 | `FINEP` | Sucesso | Registry `finep`: 10 -> 10 (delta 0); `data/output/` com 175 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-26 02:55:57 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 91 -> 91 (delta 0); `data/output/` com 175 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-25 02:44:04 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 5 -> 5 (delta 0); `data/output/` com 175 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-25 02:44:03 -03:00 | `CAPES` | Sucesso | Registry `capes`: 31 -> 31 (delta 0); `data/output/` com 175 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-25 02:43:52 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 7 -> 7 (delta 0); `data/output/` com 175 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-25 02:43:51 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 16 -> 16 (delta 0); `data/output/` com 175 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-25 02:43:35 -03:00 | `CONIF` | Sucesso | Registry `conif`: 9 -> 15 (delta 6); `data/output/` com 175 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-25 02:40:51 -03:00 | `FINEP` | Sucesso | Registry `finep`: 10 -> 10 (delta 0); `data/output/` com 170 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-25 02:40:28 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 91 -> 91 (delta 0); `data/output/` com 170 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-24 02:47:15 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 5 -> 5 (delta 0); `data/output/` com 170 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-24 02:47:14 -03:00 | `CAPES` | Sucesso | Registry `capes`: 31 -> 31 (delta 0); `data/output/` com 170 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-24 02:47:03 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 7 -> 7 (delta 0); `data/output/` com 170 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-24 02:47:01 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 16 -> 16 (delta 0); `data/output/` com 170 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-24 02:46:45 -03:00 | `CONIF` | Sucesso | Registry `conif`: 9 -> 9 (delta 0); `data/output/` com 170 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-24 02:46:36 -03:00 | `FINEP` | Sucesso | Registry `finep`: 10 -> 10 (delta 0); `data/output/` com 170 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-24 02:46:13 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 91 -> 91 (delta 0); `data/output/` com 170 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-23 02:51:40 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 5 -> 5 (delta 0); `data/output/` com 170 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-23 02:51:39 -03:00 | `CAPES` | Sucesso | Registry `capes`: 31 -> 31 (delta 0); `data/output/` com 170 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-23 02:51:25 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 7 -> 7 (delta 0); `data/output/` com 170 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-23 02:51:23 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 16 -> 16 (delta 0); `data/output/` com 170 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-23 02:51:03 -03:00 | `CONIF` | Sucesso | Registry `conif`: 9 -> 9 (delta 0); `data/output/` com 170 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-23 02:50:58 -03:00 | `FINEP` | Sucesso | Registry `finep`: 10 -> 10 (delta 0); `data/output/` com 170 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-23 02:50:34 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 91 -> 91 (delta 0); `data/output/` com 170 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-22 02:46:29 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 5 -> 5 (delta 0); `data/output/` com 170 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-22 02:46:27 -03:00 | `CAPES` | Sucesso | Registry `capes`: 31 -> 31 (delta 0); `data/output/` com 170 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-22 02:46:13 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 7 -> 7 (delta 0); `data/output/` com 170 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-22 02:46:11 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 16 -> 16 (delta 0); `data/output/` com 170 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-22 02:45:51 -03:00 | `CONIF` | Sucesso | Registry `conif`: 9 -> 9 (delta 0); `data/output/` com 170 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-22 02:45:47 -03:00 | `FINEP` | Sucesso | Registry `finep`: 10 -> 10 (delta 0); `data/output/` com 170 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-22 02:45:24 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 91 -> 91 (delta 0); `data/output/` com 170 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-21 02:46:45 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 5 -> 5 (delta 0); `data/output/` com 170 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-21 02:46:44 -03:00 | `CAPES` | Sucesso | Registry `capes`: 31 -> 31 (delta 0); `data/output/` com 170 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-21 02:46:33 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 7 -> 7 (delta 0); `data/output/` com 170 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-21 02:46:31 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 16 -> 16 (delta 0); `data/output/` com 170 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-21 02:46:15 -03:00 | `CONIF` | Sucesso | Registry `conif`: 9 -> 9 (delta 0); `data/output/` com 170 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-21 02:46:11 -03:00 | `FINEP` | Sucesso | Registry `finep`: 10 -> 10 (delta 0); `data/output/` com 170 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-21 02:45:47 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 91 -> 91 (delta 0); `data/output/` com 170 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-20 03:13:59 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 5 -> 5 (delta 0); `data/output/` com 170 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-20 03:13:57 -03:00 | `CAPES` | Sucesso | Registry `capes`: 31 -> 31 (delta 0); `data/output/` com 170 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-20 03:13:44 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 7 -> 7 (delta 0); `data/output/` com 170 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-20 03:13:42 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 16 -> 16 (delta 0); `data/output/` com 170 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-20 03:13:24 -03:00 | `CONIF` | Sucesso | Registry `conif`: 9 -> 9 (delta 0); `data/output/` com 170 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-20 03:13:20 -03:00 | `FINEP` | Sucesso | Registry `finep`: 10 -> 10 (delta 0); `data/output/` com 170 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-20 03:12:57 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 90 -> 91 (delta 1); `data/output/` com 170 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-19 02:48:51 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 5 -> 5 (delta 0); `data/output/` com 169 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-19 02:48:49 -03:00 | `CAPES` | Sucesso | Registry `capes`: 31 -> 31 (delta 0); `data/output/` com 169 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-19 02:48:36 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 7 -> 7 (delta 0); `data/output/` com 169 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-19 02:48:34 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 16 -> 16 (delta 0); `data/output/` com 169 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-19 02:48:16 -03:00 | `CONIF` | Sucesso | Registry `conif`: 9 -> 9 (delta 0); `data/output/` com 169 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-19 02:48:12 -03:00 | `FINEP` | Sucesso | Registry `finep`: 10 -> 10 (delta 0); `data/output/` com 169 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-19 02:47:48 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 88 -> 90 (delta 2); `data/output/` com 169 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-18 02:23:10 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 5 -> 5 (delta 0); `data/output/` com 167 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-18 02:23:09 -03:00 | `CAPES` | Sucesso | Registry `capes`: 31 -> 31 (delta 0); `data/output/` com 167 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-18 02:22:56 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 7 -> 7 (delta 0); `data/output/` com 167 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-18 02:22:54 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 16 -> 16 (delta 0); `data/output/` com 167 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-18 02:22:35 -03:00 | `CONIF` | Sucesso | Registry `conif`: 9 -> 9 (delta 0); `data/output/` com 167 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-18 02:22:31 -03:00 | `FINEP` | Sucesso | Registry `finep`: 10 -> 10 (delta 0); `data/output/` com 167 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-18 02:22:08 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 86 -> 88 (delta 2); `data/output/` com 167 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-17 02:39:51 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 5 -> 5 (delta 0); `data/output/` com 165 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-17 02:39:49 -03:00 | `CAPES` | Sucesso | Registry `capes`: 31 -> 31 (delta 0); `data/output/` com 165 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-17 02:39:39 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 7 -> 7 (delta 0); `data/output/` com 165 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-17 02:39:37 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 16 -> 16 (delta 0); `data/output/` com 165 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-17 02:39:18 -03:00 | `CONIF` | Sucesso | Registry `conif`: 9 -> 9 (delta 0); `data/output/` com 165 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-17 02:39:14 -03:00 | `FINEP` | Sucesso | Registry `finep`: 10 -> 10 (delta 0); `data/output/` com 165 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-17 02:38:51 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 83 -> 86 (delta 3); `data/output/` com 165 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-16 02:38:56 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 5 -> 5 (delta 0); `data/output/` com 162 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-16 02:38:54 -03:00 | `CAPES` | Sucesso | Registry `capes`: 31 -> 31 (delta 0); `data/output/` com 162 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-16 02:38:44 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 7 -> 7 (delta 0); `data/output/` com 162 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-16 02:38:42 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 16 -> 16 (delta 0); `data/output/` com 162 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-16 02:38:26 -03:00 | `CONIF` | Sucesso | Registry `conif`: 9 -> 9 (delta 0); `data/output/` com 162 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-16 02:38:21 -03:00 | `FINEP` | Sucesso | Registry `finep`: 10 -> 10 (delta 0); `data/output/` com 162 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-16 02:37:58 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 80 -> 83 (delta 3); `data/output/` com 162 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-15 02:33:51 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 5 -> 5 (delta 0); `data/output/` com 159 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-15 02:33:50 -03:00 | `CAPES` | Sucesso | Registry `capes`: 31 -> 31 (delta 0); `data/output/` com 159 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-15 02:32:49 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 7 -> 7 (delta 0); `data/output/` com 159 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-15 02:31:48 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 16 -> 16 (delta 0); `data/output/` com 159 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-15 02:31:16 -03:00 | `CONIF` | Sucesso | Registry `conif`: 9 -> 9 (delta 0); `data/output/` com 159 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-15 02:31:12 -03:00 | `FINEP` | Sucesso | Registry `finep`: 10 -> 10 (delta 0); `data/output/` com 159 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-15 02:30:48 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 73 -> 80 (delta 7); `data/output/` com 159 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-14 02:33:29 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 5 -> 5 (delta 0); `data/output/` com 152 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-14 02:33:28 -03:00 | `CAPES` | Sucesso | Registry `capes`: 31 -> 31 (delta 0); `data/output/` com 152 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-14 02:33:14 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 7 -> 7 (delta 0); `data/output/` com 152 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-14 02:33:12 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 16 -> 16 (delta 0); `data/output/` com 152 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-14 02:32:52 -03:00 | `CONIF` | Sucesso | Registry `conif`: 8 -> 9 (delta 1); `data/output/` com 152 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-14 02:32:32 -03:00 | `FINEP` | Sucesso | Registry `finep`: 10 -> 10 (delta 0); `data/output/` com 152 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-14 02:32:10 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 70 -> 73 (delta 3); `data/output/` com 152 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-13 03:19:10 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 5 -> 5 (delta 0); `data/output/` com 149 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-13 03:19:08 -03:00 | `CAPES` | Sucesso | Registry `capes`: 31 -> 31 (delta 0); `data/output/` com 149 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-13 03:18:07 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 7 -> 7 (delta 0); `data/output/` com 149 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-13 03:17:06 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 16 -> 16 (delta 0); `data/output/` com 149 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-13 03:16:35 -03:00 | `CONIF` | Sucesso | Registry `conif`: 8 -> 8 (delta 0); `data/output/` com 149 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-13 03:16:30 -03:00 | `FINEP` | Sucesso | Registry `finep`: 10 -> 10 (delta 0); `data/output/` com 149 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-13 03:16:07 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 70 -> 70 (delta 0); `data/output/` com 149 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-12 03:02:19 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 5 -> 5 (delta 0); `data/output/` com 149 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-12 03:02:18 -03:00 | `CAPES` | Sucesso | Registry `capes`: 31 -> 31 (delta 0); `data/output/` com 149 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-12 03:02:07 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 7 -> 7 (delta 0); `data/output/` com 149 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-12 03:02:05 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 16 -> 16 (delta 0); `data/output/` com 149 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-12 03:01:39 -03:00 | `CONIF` | Sucesso | Registry `conif`: 8 -> 8 (delta 0); `data/output/` com 149 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-12 03:01:34 -03:00 | `FINEP` | Sucesso | Registry `finep`: 10 -> 10 (delta 0); `data/output/` com 149 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-12 03:01:11 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 68 -> 70 (delta 2); `data/output/` com 149 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-11 02:42:50 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 5 -> 5 (delta 0); `data/output/` com 147 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-11 02:42:47 -03:00 | `CAPES` | Sucesso | Registry `capes`: 30 -> 31 (delta 1); `data/output/` com 147 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-11 02:42:31 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 7 -> 7 (delta 0); `data/output/` com 146 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-11 02:42:29 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 16 -> 16 (delta 0); `data/output/` com 146 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-11 02:42:04 -03:00 | `CONIF` | Sucesso | Registry `conif`: 8 -> 8 (delta 0); `data/output/` com 146 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-11 02:42:01 -03:00 | `FINEP` | Sucesso | Registry `finep`: 10 -> 10 (delta 0); `data/output/` com 146 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-11 02:41:37 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 68 -> 68 (delta 0); `data/output/` com 146 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-10 03:47:25 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 5 -> 5 (delta 0); `data/output/` com 146 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-10 03:47:23 -03:00 | `CAPES` | Sucesso | Registry `capes`: 30 -> 30 (delta 0); `data/output/` com 146 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-10 03:46:22 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 7 -> 7 (delta 0); `data/output/` com 146 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-10 03:45:21 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 16 -> 16 (delta 0); `data/output/` com 146 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-10 03:44:50 -03:00 | `CONIF` | Sucesso | Registry `conif`: 8 -> 8 (delta 0); `data/output/` com 146 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-10 03:44:46 -03:00 | `FINEP` | Sucesso | Registry `finep`: 10 -> 10 (delta 0); `data/output/` com 146 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-10 03:44:26 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 68 -> 68 (delta 0); `data/output/` com 146 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-09 03:57:03 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 5 -> 5 (delta 0); `data/output/` com 146 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-09 03:57:02 -03:00 | `CAPES` | Sucesso | Registry `capes`: 30 -> 30 (delta 0); `data/output/` com 146 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-09 03:56:00 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 7 -> 7 (delta 0); `data/output/` com 146 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-09 03:54:59 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 16 -> 16 (delta 0); `data/output/` com 146 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-09 03:54:28 -03:00 | `CONIF` | Sucesso | Registry `conif`: 7 -> 8 (delta 1); `data/output/` com 146 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-09 03:54:07 -03:00 | `FINEP` | Sucesso | Registry `finep`: 10 -> 10 (delta 0); `data/output/` com 145 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-09 03:53:46 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 66 -> 68 (delta 2); `data/output/` com 145 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-08 02:53:12 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 5 -> 5 (delta 0); `data/output/` com 143 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-08 02:53:09 -03:00 | `CAPES` | Sucesso | Registry `capes`: 30 -> 30 (delta 0); `data/output/` com 143 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-08 02:52:55 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 7 -> 7 (delta 0); `data/output/` com 143 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-08 02:52:53 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 16 -> 16 (delta 0); `data/output/` com 143 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-08 02:52:31 -03:00 | `CONIF` | Sucesso | Registry `conif`: 7 -> 7 (delta 0); `data/output/` com 143 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-08 02:52:27 -03:00 | `FINEP` | Sucesso | Registry `finep`: 10 -> 10 (delta 0); `data/output/` com 143 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-08 02:52:05 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 63 -> 66 (delta 3); `data/output/` com 143 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-07 03:45:44 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 5 -> 5 (delta 0); `data/output/` com 140 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-07 03:45:42 -03:00 | `CAPES` | Sucesso | Registry `capes`: 30 -> 30 (delta 0); `data/output/` com 140 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-07 03:45:30 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 7 -> 7 (delta 0); `data/output/` com 140 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-07 03:45:28 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 16 -> 16 (delta 0); `data/output/` com 140 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-07 03:45:10 -03:00 | `CONIF` | Sucesso | Registry `conif`: 7 -> 7 (delta 0); `data/output/` com 140 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-07 03:45:06 -03:00 | `FINEP` | Sucesso | Registry `finep`: 10 -> 10 (delta 0); `data/output/` com 140 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-07 03:44:45 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 58 -> 63 (delta 5); `data/output/` com 140 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-06 04:09:41 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 5 -> 5 (delta 0); `data/output/` com 135 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-06 04:09:39 -03:00 | `CAPES` | Sucesso | Registry `capes`: 30 -> 30 (delta 0); `data/output/` com 135 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-06 04:09:26 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 7 -> 7 (delta 0); `data/output/` com 135 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-06 04:09:24 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 16 -> 16 (delta 0); `data/output/` com 135 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-06 04:09:05 -03:00 | `CONIF` | Sucesso | Registry `conif`: 7 -> 7 (delta 0); `data/output/` com 135 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-06 04:09:02 -03:00 | `FINEP` | Sucesso | Registry `finep`: 10 -> 10 (delta 0); `data/output/` com 135 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-06 04:08:40 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 58 -> 58 (delta 0); `data/output/` com 135 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-05 03:38:21 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 5 -> 5 (delta 0); `data/output/` com 135 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-05 03:38:19 -03:00 | `CAPES` | Sucesso | Registry `capes`: 29 -> 30 (delta 1); `data/output/` com 135 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-05 03:38:04 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 7 -> 7 (delta 0); `data/output/` com 134 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-05 03:38:01 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 16 -> 16 (delta 0); `data/output/` com 134 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-05 03:37:41 -03:00 | `CONIF` | Sucesso | Registry `conif`: 7 -> 7 (delta 0); `data/output/` com 134 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-05 03:37:36 -03:00 | `FINEP` | Sucesso | Registry `finep`: 10 -> 10 (delta 0); `data/output/` com 134 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-05 03:37:15 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 58 -> 58 (delta 0); `data/output/` com 134 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-04 03:19:48 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 5 -> 5 (delta 0); `data/output/` com 134 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-04 03:19:46 -03:00 | `CAPES` | Sucesso | Registry `capes`: 29 -> 29 (delta 0); `data/output/` com 134 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-04 03:18:45 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 7 -> 7 (delta 0); `data/output/` com 134 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-04 03:17:44 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 16 -> 16 (delta 0); `data/output/` com 134 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-04 03:17:13 -03:00 | `CONIF` | Sucesso | Registry `conif`: 7 -> 7 (delta 0); `data/output/` com 134 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-04 03:17:10 -03:00 | `FINEP` | Sucesso | Registry `finep`: 10 -> 10 (delta 0); `data/output/` com 134 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-04 03:16:49 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 56 -> 58 (delta 2); `data/output/` com 134 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-03 03:30:02 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 5 -> 5 (delta 0); `data/output/` com 132 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-03 03:30:01 -03:00 | `CAPES` | Sucesso | Registry `capes`: 29 -> 29 (delta 0); `data/output/` com 132 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-03 03:29:49 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 7 -> 7 (delta 0); `data/output/` com 132 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-03 03:29:47 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 16 -> 16 (delta 0); `data/output/` com 132 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-03 03:29:31 -03:00 | `CONIF` | Sucesso | Registry `conif`: 7 -> 7 (delta 0); `data/output/` com 132 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-03 03:29:27 -03:00 | `FINEP` | Sucesso | Registry `finep`: 10 -> 10 (delta 0); `data/output/` com 132 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-03 03:29:05 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 51 -> 56 (delta 5); `data/output/` com 132 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-02 03:39:42 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 5 -> 5 (delta 0); `data/output/` com 127 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-02 03:39:40 -03:00 | `CAPES` | Sucesso | Registry `capes`: 28 -> 29 (delta 1); `data/output/` com 127 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-02 03:39:26 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 7 -> 7 (delta 0); `data/output/` com 126 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-02 03:39:24 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 16 -> 16 (delta 0); `data/output/` com 126 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-02 03:39:05 -03:00 | `CONIF` | Sucesso | Registry `conif`: 7 -> 7 (delta 0); `data/output/` com 126 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-02 03:39:01 -03:00 | `FINEP` | Sucesso | Registry `finep`: 10 -> 10 (delta 0); `data/output/` com 126 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-02 03:38:40 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 46 -> 51 (delta 5); `data/output/` com 126 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-01 04:12:10 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 5 -> 5 (delta 0); `data/output/` com 121 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-01 04:12:08 -03:00 | `CAPES` | Sucesso | Registry `capes`: 27 -> 28 (delta 1); `data/output/` com 121 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-01 04:11:57 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 7 -> 7 (delta 0); `data/output/` com 120 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-01 04:11:55 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 16 -> 16 (delta 0); `data/output/` com 120 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-01 04:11:40 -03:00 | `CONIF` | Sucesso | Registry `conif`: 7 -> 7 (delta 0); `data/output/` com 120 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-01 04:11:36 -03:00 | `FINEP` | Sucesso | Registry `finep`: 10 -> 10 (delta 0); `data/output/` com 120 JSONs; arquivos não-JSON: nenhum. |
| 2026-07-01 04:11:15 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 38 -> 46 (delta 8); `data/output/` com 120 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-30 04:01:49 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 5 -> 5 (delta 0); `data/output/` com 112 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-30 04:01:47 -03:00 | `CAPES` | Sucesso | Registry `capes`: 27 -> 27 (delta 0); `data/output/` com 112 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-30 04:00:46 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 7 -> 7 (delta 0); `data/output/` com 112 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-30 03:59:45 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 16 -> 16 (delta 0); `data/output/` com 112 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-30 03:59:13 -03:00 | `CONIF` | Sucesso | Registry `conif`: 7 -> 7 (delta 0); `data/output/` com 112 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-30 03:59:09 -03:00 | `FINEP` | Sucesso | Registry `finep`: 10 -> 10 (delta 0); `data/output/` com 112 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-30 03:58:47 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 37 -> 38 (delta 1); `data/output/` com 112 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-29 04:31:33 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 5 -> 5 (delta 0); `data/output/` com 111 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-29 04:31:31 -03:00 | `CAPES` | Sucesso | Registry `capes`: 27 -> 27 (delta 0); `data/output/` com 111 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-29 04:31:18 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 7 -> 7 (delta 0); `data/output/` com 111 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-29 04:31:17 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 16 -> 16 (delta 0); `data/output/` com 111 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-29 04:31:01 -03:00 | `CONIF` | Sucesso | Registry `conif`: 7 -> 7 (delta 0); `data/output/` com 111 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-29 04:30:57 -03:00 | `FINEP` | Sucesso | Registry `finep`: 10 -> 10 (delta 0); `data/output/` com 111 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-29 04:30:37 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 36 -> 37 (delta 1); `data/output/` com 111 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-28 04:05:01 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 5 -> 5 (delta 0); `data/output/` com 110 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-28 04:04:59 -03:00 | `CAPES` | Sucesso | Registry `capes`: 27 -> 27 (delta 0); `data/output/` com 110 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-28 04:04:49 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 7 -> 7 (delta 0); `data/output/` com 110 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-28 04:04:48 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 16 -> 16 (delta 0); `data/output/` com 110 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-28 04:04:32 -03:00 | `CONIF` | Sucesso | Registry `conif`: 7 -> 7 (delta 0); `data/output/` com 110 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-28 04:04:28 -03:00 | `FINEP` | Sucesso | Registry `finep`: 10 -> 10 (delta 0); `data/output/` com 110 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-28 04:04:06 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 34 -> 36 (delta 2); `data/output/` com 110 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-27 03:33:49 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 5 -> 5 (delta 0); `data/output/` com 108 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-27 03:33:47 -03:00 | `CAPES` | Sucesso | Registry `capes`: 27 -> 27 (delta 0); `data/output/` com 108 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-27 03:33:34 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 7 -> 7 (delta 0); `data/output/` com 108 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-27 03:33:32 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 16 -> 16 (delta 0); `data/output/` com 108 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-27 03:33:14 -03:00 | `CONIF` | Sucesso | Registry `conif`: 7 -> 7 (delta 0); `data/output/` com 108 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-27 03:33:10 -03:00 | `FINEP` | Sucesso | Registry `finep`: 10 -> 10 (delta 0); `data/output/` com 108 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-27 03:32:48 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 33 -> 34 (delta 1); `data/output/` com 108 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-26 03:55:04 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 5 -> 5 (delta 0); `data/output/` com 107 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-26 03:55:02 -03:00 | `CAPES` | Sucesso | Registry `capes`: 27 -> 27 (delta 0); `data/output/` com 107 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-26 03:54:53 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 7 -> 7 (delta 0); `data/output/` com 107 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-26 03:54:51 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 16 -> 16 (delta 0); `data/output/` com 107 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-26 03:54:35 -03:00 | `CONIF` | Sucesso | Registry `conif`: 7 -> 7 (delta 0); `data/output/` com 107 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-26 03:54:32 -03:00 | `FINEP` | Sucesso | Registry `finep`: 10 -> 10 (delta 0); `data/output/` com 107 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-26 03:54:11 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 32 -> 33 (delta 1); `data/output/` com 107 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-25 03:49:06 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 5 -> 5 (delta 0); `data/output/` com 106 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-25 03:49:04 -03:00 | `CAPES` | Sucesso | Registry `capes`: 27 -> 27 (delta 0); `data/output/` com 106 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-25 03:48:51 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 7 -> 7 (delta 0); `data/output/` com 106 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-25 03:48:49 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 16 -> 16 (delta 0); `data/output/` com 106 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-25 03:48:34 -03:00 | `CONIF` | Sucesso | Registry `conif`: 7 -> 7 (delta 0); `data/output/` com 106 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-25 03:48:30 -03:00 | `FINEP` | Sucesso | Registry `finep`: 10 -> 10 (delta 0); `data/output/` com 106 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-25 03:48:09 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 32 -> 32 (delta 0); `data/output/` com 106 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-24 03:47:01 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 5 -> 5 (delta 0); `data/output/` com 106 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-24 03:47:00 -03:00 | `CAPES` | Sucesso | Registry `capes`: 27 -> 27 (delta 0); `data/output/` com 106 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-24 03:46:45 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 7 -> 7 (delta 0); `data/output/` com 106 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-24 03:46:43 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 16 -> 16 (delta 0); `data/output/` com 106 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-24 03:46:23 -03:00 | `CONIF` | Sucesso | Registry `conif`: 7 -> 7 (delta 0); `data/output/` com 106 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-24 03:46:19 -03:00 | `FINEP` | Sucesso | Registry `finep`: 10 -> 10 (delta 0); `data/output/` com 106 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-24 03:45:58 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 32 -> 32 (delta 0); `data/output/` com 106 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-23 03:50:20 -03:00 | `CNPQ` | Sucesso | Registry `cnpq`: 5 -> 5 (delta 0); `data/output/` com 106 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-23 03:50:18 -03:00 | `CAPES` | Sucesso | Registry `capes`: 25 -> 27 (delta 2); `data/output/` com 106 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-23 03:50:00 -03:00 | `PROEX_IFES` | Sucesso | Registry `proex_ifes`: 7 -> 7 (delta 0); `data/output/` com 104 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-23 03:49:58 -03:00 | `PRPPG_IFES` | Sucesso | Registry `prppg_ifes`: 16 -> 16 (delta 0); `data/output/` com 104 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-23 03:49:38 -03:00 | `CONIF` | Sucesso | Registry `conif`: 7 -> 7 (delta 0); `data/output/` com 104 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-23 03:49:34 -03:00 | `FINEP` | Sucesso | Registry `finep`: 10 -> 10 (delta 0); `data/output/` com 104 JSONs; arquivos não-JSON: nenhum. |
| 2026-06-23 03:49:13 -03:00 | `FAPES` | Sucesso | Registry `fapes`: 30 -> 32 (delta 2); `data/output/` com 104 JSONs; arquivos não-JSON: nenhum. |
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
