"""
Deduplicação entre fontes, com precedência da fonte original.

O mesmo edital pode chegar por dois caminhos. O caso concreto que motivou este
módulo: a **Chamada CONFAP & CDTI 2026-2027** foi coletada pela FAPES — que
hospeda o PDF de diretrizes e é quem de fato financia a proposta capixaba — e
também pelo CONFAP, que a publica como chamada de cooperação internacional.
Os dois arquivos foram parar em `data/output/`, um deles com sufixo de colisão.

Regra: **a fonte original vence o agregador.** A FAPES é quem recebe a
submissão, define critérios complementares de elegibilidade e responde pelo
edital para o pesquisador do IFES; o CONFAP é a vitrine nacional da mesma
chamada. Manter o registro do agregador no lugar do da fonte primária mandaria
o pesquisador para a página errada.

A precedência vale nos dois sentidos:

- agregador chega e a fonte original já está gravada  → o agregador é descartado;
- fonte original chega e o agregador já está gravado  → o registro do agregador
  é substituído pelo da fonte original.

Não é dedução por semelhança: a chave canônica exige título normalizado **e**
mesma data de encerramento. Dois editais distintos de nomes parecidos têm prazos
diferentes e não colidem; a mesma chamada publicada por dois portais tem o mesmo
prazo, porque o prazo é o do edital, não o do portal.
"""

import json
import logging
import os
import re
import unicodedata
from typing import Dict, Iterable, List, Optional, Tuple

from src.domain.models import EditalDomain

logger = logging.getLogger(__name__)

# Fontes que republicam chamadas de terceiros. Só elas perdem a disputa; entre
# duas fontes primárias não há precedência definida, e nesse caso nada é
# descartado — inventar um vencedor arbitrário seria pior que manter as duas e
# deixar o caso visível.
AGGREGATOR_SOURCES = frozenset({"confap"})

_NON_ALNUM = re.compile(r"[^0-9a-z]+")


def _normalize(texto: str) -> str:
    """Minúsculas, sem acento e sem pontuação — só o esqueleto do título."""
    sem_acento = unicodedata.normalize("NFKD", texto or "")
    sem_acento = "".join(c for c in sem_acento if not unicodedata.combining(c))
    return _NON_ALNUM.sub(" ", sem_acento.lower()).strip()


def canonical_key(nome: str, data_encerramento: str) -> str:
    """
    Identidade do edital entre portais: título normalizado + prazo.

    Devolve string vazia quando não há título ou não há prazo. Sem prazo não há
    como afirmar que dois editais de título parecido são o mesmo — e uma
    deduplicação errada apaga oportunidade real, então o silêncio é o certo.
    """
    titulo = _normalize(nome)
    prazo = (data_encerramento or "").strip()
    if not titulo or not prazo:
        return ""
    return f"{titulo}|{prazo}"


def is_aggregator(fonte_key: str) -> bool:
    return (fonte_key or "").strip().lower() in AGGREGATOR_SOURCES


def index_published(output_dir: str = "data/output") -> Dict[str, Tuple[str, str]]:
    """
    Mapa `chave canônica -> (fonte_key, caminho do arquivo)` do que já está gravado.

    Ler os JSONs é barato (medido: 650 arquivos em 0,09s) e evita um segundo
    índice para manter em sincronia com o diretório de saída.
    """
    indice: Dict[str, Tuple[str, str]] = {}
    if not os.path.isdir(output_dir):
        return indice
    for nome_arquivo in os.listdir(output_dir):
        if not nome_arquivo.endswith(".json"):
            continue
        caminho = os.path.join(output_dir, nome_arquivo)
        try:
            with open(caminho, "r", encoding="utf-8") as handle:
                dados = json.load(handle)
        except (OSError, ValueError):
            continue
        chave = canonical_key(dados.get("nome", ""), dados.get("data_encerramento", ""))
        if not chave:
            continue
        # Empate entre arquivos já gravados: a fonte primária fica no índice,
        # para que um agregador que chegue depois seja corretamente descartado.
        atual = indice.get(chave)
        if atual is None or (is_aggregator(atual[0]) and not is_aggregator(dados.get("fonte_key", ""))):
            indice[chave] = (dados.get("fonte_key", ""), caminho)
    return indice


def filter_superseded(
    items: Iterable[EditalDomain],
    output_dir: str = "data/output",
    indice: Optional[Dict[str, Tuple[str, str]]] = None,
) -> Tuple[List[EditalDomain], List[str]]:
    """
    Separa o que deve ser gravado do que perde para um registro já existente.

    Devolve `(a_gravar, arquivos_a_remover)`:

    - `a_gravar` exclui os itens de agregador cuja chave já pertence a uma fonte
      primária;
    - `arquivos_a_remover` são registros de agregador que a fonte primária vem
      substituir agora.

    O chamador decide o que fazer com a lista de remoção — este módulo não apaga
    arquivo, para que a decisão fique num lugar só.
    """
    if indice is None:
        indice = index_published(output_dir)

    a_gravar: List[EditalDomain] = []
    a_remover: List[str] = []

    for item in items:
        chave = canonical_key(item.nome, item.data_encerramento)
        existente = indice.get(chave) if chave else None
        if existente is None:
            a_gravar.append(item)
            continue

        fonte_existente, caminho_existente = existente
        nova_e_agregador = is_aggregator(item.fonte_key)
        existente_e_agregador = is_aggregator(fonte_existente)

        if nova_e_agregador and not existente_e_agregador:
            logger.info(
                "Edital já publicado pela fonte original '%s'; descartando a "
                "versão do agregador '%s': %s",
                fonte_existente,
                item.fonte_key,
                item.nome[:70],
            )
            continue

        if existente_e_agregador and not nova_e_agregador:
            logger.info(
                "Fonte original '%s' substitui o registro do agregador '%s': %s",
                item.fonte_key,
                fonte_existente,
                item.nome[:70],
            )
            a_remover.append(caminho_existente)

        a_gravar.append(item)

    return a_gravar, a_remover
