import hashlib
import json
import os
import logging
from typing import Dict, List
from dataclasses import asdict
from src.core.interfaces import ISink
from src.components.transforms import cross_source_dedup
from src.domain.models import EditalDomain

logger = logging.getLogger(__name__)


def key_from_nome(nome: str, fallback: str = "edital_anonimo") -> str:
    """
    Same key used for the output filename base (no extension).
    Use this to build the processed index key for FAPES so source and sink stay in sync.
    """
    keepcharacters = (" ", ".", "_", "-")
    base = "".join(c for c in nome if c.isalnum() or c in keepcharacters).rstrip()
    if not base:
        return fallback
    if len(base) > 150:
        base = f"{base[:140]}_{hashlib.md5(nome.encode()).hexdigest()[:6]}"
    return base.replace(" ", "_").lower()


class LocalJSONSink(ISink[EditalDomain]):
    """
    Persists valid editais into JSON files in the local filesystem.
    """

    def __init__(self, output_dir: str = "data/output"):
        self.output_dir = output_dir

    def _sanitize_filename(self, filename: str) -> str:
        """Removes invalid characters from a string to build a safe filename."""
        keepcharacters = (" ", ".", "_", "-")
        return "".join(c for c in filename if c.isalnum() or c in keepcharacters).rstrip()

    def basename_for(self, item: EditalDomain, index: int = 1) -> str:
        """Base filename (no .json) for this item; same logic as write() for the processed index."""
        base_name = self._sanitize_filename(item.nome)
        if not base_name:
            base_name = f"edital_anonimo_{index}"
        if len(base_name) > 150:
            base_name = f"{base_name[:140]}_{hashlib.md5(item.nome.encode()).hexdigest()[:6]}"
        return base_name.replace(" ", "_").lower()

    def _holds_same_edital(self, filepath: str, item: EditalDomain) -> bool:
        """
        True quando o arquivo existente é o mesmo edital — ou seja, gravar em cima
        é atualização legítima, não perda de dado.
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                existing = json.load(f)
        except (OSError, ValueError) as e:
            logger.warning(
                "Não foi possível ler %s para comparar (%s); tratando como colisão.",
                filepath,
                e,
            )
            return False

        existing_link = (existing.get("link") or "").strip()
        if not existing_link:
            # Arquivo legado sem link: não há como distinguir os dois editais.
            # Mantém o comportamento histórico de sobrescrever, em vez de
            # multiplicar arquivos a cada execução.
            return True
        return existing_link == (item.link or "").strip()

    def _resolve_basename(self, item: EditalDomain, index: int) -> str:
        """
        Resolve o nome-base do arquivo, desviando de colisão entre editais distintos.

        Dois editais com o mesmo título produzem o mesmo slug e um sobrescrevia o
        outro em silêncio — com a chave de ambos gravada no registry, o perdido
        nunca voltava. O sufixo vem do `link`, não de um contador, para que
        reexecuções produzam sempre o mesmo nome e não gerem arquivo novo a cada
        rodada.
        """
        base_name = self.basename_for(item, index=index)
        filepath = os.path.join(self.output_dir, f"{base_name}.json")
        if not os.path.exists(filepath) or self._holds_same_edital(filepath, item):
            return base_name

        discriminator = hashlib.md5(
            (item.link or item.nome).encode()
        ).hexdigest()[:6]
        resolved = f"{base_name}_{discriminator}"
        logger.info(
            "Colisão de nome para '%s': gravando como %s.json para não sobrescrever outro edital.",
            item.nome[:60],
            resolved,
        )
        return resolved

    def _replace_aggregator_records(
        self, items: List[EditalDomain]
    ) -> List[EditalDomain]:
        """
        Remove o arquivo do agregador quando a fonte original grava o mesmo edital.

        Devolve a lista de itens inalterada: quem decide o que gravar é o
        chamador. Falha ao apagar não interrompe a gravação — ficar com dois
        arquivos é ruim, não gravar o edital é pior.
        """
        _, obsoletos = cross_source_dedup.filter_superseded(items, self.output_dir)
        for caminho in obsoletos:
            try:
                os.remove(caminho)
                logger.info(
                    "Registro do agregador removido em favor da fonte original: %s",
                    os.path.basename(caminho),
                )
            except OSError as exc:
                logger.warning("Falha ao remover %s: %s", caminho, exc)
        return items

    def write(self, items: List[EditalDomain]) -> Dict[str, EditalDomain]:
        """
        Persiste os editais e devolve o que de fato foi para o disco, indexado pelo
        nome-base do arquivo.

        O retorno existe para que o flow registre no índice apenas o que foi
        gravado, e com a chave correta:

        - fluxos que deduplicam por link usam `.values()`;
        - o fluxo FAPES, que deduplica pelo nome do arquivo, usa `.keys()` — assim
          a chave acompanha o sufixo quando houve colisão, em vez de ficar
          dessincronizada do arquivo real.

        Registrar um edital cuja gravação falhou o marcaria como processado sem
        arquivo correspondente, e ele nunca seria recoletado.
        """
        if not items:
            logger.warning("No items to persist.")
            return {}

        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)

        # Precedência entre fontes no sentido "original chega depois": se um
        # agregador já gravou este edital, o arquivo dele sai para dar lugar ao
        # da fonte original. O sentido oposto — agregador chegando quando a
        # original já publicou — é resolvido antes, no normalizador, para que a
        # recusa entre no índice com validade e não se repita toda noite.
        items = self._replace_aggregator_records(items)

        persisted: Dict[str, EditalDomain] = {}
        for idx, item in enumerate(items, start=1):
            base_name = self._resolve_basename(item, index=idx)
            filepath = os.path.join(self.output_dir, f"{base_name}.json")

            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(asdict(item), f, ensure_ascii=False, indent=4)
                logger.debug(f"Saved {filepath}")
                persisted[base_name] = item
            except OSError as e:
                logger.error(f"Failed to write {filepath}: {e}")
                # Continuing the loop per pipeline fault-tolerance
                continue

        logger.info(
            f"Successfully persisted {len(persisted)} of {len(items)} editais to {self.output_dir}"
        )
        return persisted
