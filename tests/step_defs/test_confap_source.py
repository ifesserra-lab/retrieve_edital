"""
Testes do ConfapSource.

Contexto do recon (2026-08-16): o PDF de análise trata o CONFAP como hub que
agregaria as chamadas das 26 FAPs. Não é. Ele publica as chamadas **dele** —
cooperação internacional cofinanciada por um subconjunto de FAPs. Por isso este
source acrescenta cobertura internacional e não substitui a coleta por FAP.
"""

import re

import pytest

from src.components.sources.confap_source import ConfapSource

LISTAGEM = """
<html><body>
  <div class="item"><a href="/pt/editais/115/chamada-a">Ver detalhes</a></div>
  <div class="item"><a href="/pt/editais/114/chamada-b">Ver detalhes</a></div>
  <div class="item"><a href="/pt/editais/115/chamada-a">Ver detalhes</a></div>
  <a href="/pt/noticias/99/nao-e-edital">Notícia</a>
</body></html>
"""

DETALHE = """
<html><body>
  <h1 class="text-white h3">Editais</h1>
  <h2 class="text-primary text-uppercase font-weight-bold h5 mb-3">Chamada CONFAP &amp; CDTI 2026-2027</h2>
  <p class="mb-4">
    <b>Objeto:</b> <br/>
    <b>​Data de Encerramento:</b> 08/10/2026<br/>
    <b>Status:</b> Em andamento
  </p>
  <p class="mb-md-4">O CONFAP em parceria com o CDTI lançou, em 13 de julho de 2026, a chamada.
     FAPs participantes: FAPES (Espírito Santo); FAPERGS; FAPESB.</p>
  <h3>Arquivos para download</h3>
  <a href="https://fapes.es.gov.br/Media/Diretrizes.pdf">Diretrizes</a>
  <a href="/pt/pagina-qualquer">Não é anexo</a>
</body></html>
"""

SEM_TITULO = '<html><body><p class="mb-md-4">corpo sem título</p></body></html>'


class _RespostaFake:
    def __init__(self, texto, url="https://confap.org.br/pt/editais/"):
        self.text = texto
        self.url = url

    def raise_for_status(self):
        return None


class _SessaoFake:
    """Devolve a listagem para URLs de listagem e o detalhe para as demais."""

    def __init__(self, listagem=LISTAGEM, detalhe=DETALHE, paginas=1):
        self.listagem = listagem
        self.detalhe = detalhe
        self.paginas = paginas
        self.pedidos = []

    def get(self, url, timeout=None):
        self.pedidos.append(url)
        # Detalhe é /pt/editais/<id>/<slug>; qualquer outra coisa é listagem.
        # O portal responde 200 repetindo a primeira página quando o offset
        # passa do fim, e o dublê reproduz isso devolvendo sempre a listagem.
        if re.search(r"/pt/editais/\d+/", url):
            return _RespostaFake(self.detalhe, url)
        return _RespostaFake(self.listagem, url)


class TestListagem:
    def test_extrai_urls_de_detalhe_sem_repetir(self):
        urls = ConfapSource._extract_detail_urls(LISTAGEM)
        assert urls == [
            "https://confap.org.br/pt/editais/115/chamada-a",
            "https://confap.org.br/pt/editais/114/chamada-b",
        ]

    def test_ignora_links_que_nao_sao_edital(self):
        assert all("noticias" not in u for u in ConfapSource._extract_detail_urls(LISTAGEM))

    def test_paginacao_para_quando_nao_ha_item_novo(self):
        """
        O portal responde 200 com a primeira página quando o offset passa do
        fim. Sem a parada, o laço giraria até `max_pages` relendo o mesmo.
        """
        sessao = _SessaoFake()
        source = ConfapSource(session=sessao, max_pages=5)
        source.read()
        listagens = [u for u in sessao.pedidos if "pagina=" in u or u.endswith("/editais/")]
        assert len(listagens) == 2, "deve pedir a 2ª página, ver repetição e parar"

    def test_last_listing_count_reflete_a_origem(self):
        source = ConfapSource(session=_SessaoFake())
        source.read()
        assert source.last_listing_count == 2


class TestDeduplicacao:
    def test_url_ja_processada_nao_e_relida(self):
        sessao = _SessaoFake()
        source = ConfapSource(
            session=sessao,
            processed_urls={"https://confap.org.br/pt/editais/115/chamada-a"},
        )
        editais = source.read()
        assert len(editais) == 1
        assert all("/115/" not in e.url for e in editais)

    def test_dedup_nao_afeta_a_contagem_bruta(self):
        """`last_listing_count` mede a origem, não o que sobrou depois do filtro."""
        source = ConfapSource(
            session=_SessaoFake(),
            processed_urls={"https://confap.org.br/pt/editais/115/chamada-a"},
        )
        source.read()
        assert source.last_listing_count == 2


class TestExtracaoDoDetalhe:
    @pytest.fixture
    def edital(self):
        return ConfapSource(session=_SessaoFake()).read()[0]

    def test_titulo_vem_do_h2_e_nao_do_rotulo_da_secao(self, edital):
        """O `h1` da página é o rótulo fixo "Editais"; o título real é o `h2`."""
        assert edital.title == "Chamada CONFAP & CDTI 2026-2027"

    def test_prazo_vem_do_campo_rotulado(self, edital):
        prazos = [i for i in edital.raw_cronograma if i["evento"].startswith("Prazo")]
        assert prazos == [{"evento": "Prazo para envio da proposta", "data": "2026-10-08"}]

    def test_publicacao_aceita_data_por_extenso(self, edital):
        pubs = [i for i in edital.raw_cronograma if i["evento"].startswith("Publicação")]
        assert pubs == [{"evento": "Publicação da chamada", "data": "2026-07-13"}]

    def test_status_do_portal_vira_vocabulario_do_dominio(self, edital):
        assert edital.raw_status == "aberto"

    def test_faps_participantes_viram_tag(self, edital):
        """É por elas que o pesquisador sabe se a fundação do estado dele aderiu."""
        assert "FAPES" in edital.raw_tags
        assert "FAPERGS" in edital.raw_tags
        assert "cooperação internacional" in edital.raw_tags

    def test_ambito_e_internacional(self, edital):
        assert edital.raw_ambito_geografico == "internacional"

    def test_anexo_so_conta_documento(self, edital):
        assert [a["link"] for a in edital.raw_anexos] == [
            "https://fapes.es.gov.br/Media/Diretrizes.pdf"
        ]

    def test_agencia_e_categoria(self, edital):
        assert edital.raw_agency == "CONFAP"
        assert edital.source_category == "pesquisa"


class TestStatusFinalizado:
    def test_finalizado_vira_encerrado(self):
        html = DETALHE.replace("Em andamento", "Finalizado")
        edital = ConfapSource(session=_SessaoFake(detalhe=html)).read()[0]
        assert edital.raw_status == "encerrado"


class TestCoerenciaDeDatas:
    """
    A publicação é inferida da primeira data do corpo, e nem sempre é a de
    lançamento. Na amostragem real, `nexBio` saiu com publicação posterior ao
    prazo e `DAAD` com as duas iguais. Data incoerente é pior que ausente: o
    normalizador deriva `data_abertura` do cronograma e gravaria um edital que
    abre depois de fechar.
    """

    def _cronograma(self, corpo):
        html = DETALHE.replace(
            "O CONFAP em parceria com o CDTI lançou, em 13 de julho de 2026, a chamada.",
            corpo,
        )
        return ConfapSource(session=_SessaoFake(detalhe=html)).read()[0].raw_cronograma

    def test_publicacao_posterior_ao_prazo_e_descartada(self):
        # 14/11/2026 é posterior ao prazo do fixture (08/10/2026).
        crono = self._cronograma("Evento citado em 14 de novembro de 2026.")
        assert [i["evento"] for i in crono] == ["Prazo para envio da proposta"]

    def test_publicacao_igual_ao_prazo_e_descartada(self):
        crono = self._cronograma("Publicado em 08/10/2026.")
        assert [i["evento"] for i in crono] == ["Prazo para envio da proposta"]

    def test_publicacao_anterior_ao_prazo_e_mantida(self):
        crono = self._cronograma("Lançado em 1 de março de 2026.")
        assert crono[0] == {"evento": "Publicação da chamada", "data": "2026-03-01"}

    def test_o_prazo_nunca_e_descartado(self):
        """O prazo é campo rotulado do portal, não inferência — sempre fica."""
        for corpo in ("sem data alguma", "Evento em 14 de novembro de 2026."):
            crono = self._cronograma(corpo)
            assert any(i["evento"].startswith("Prazo") for i in crono)


class TestResiliencia:
    def test_chamada_sem_titulo_e_ignorada_sem_derrubar(self):
        editais = ConfapSource(session=_SessaoFake(detalhe=SEM_TITULO)).read()
        assert editais == []

    def test_erro_de_rede_na_listagem_devolve_vazio(self):
        import requests

        class _SessaoQuebrada:
            def get(self, url, timeout=None):
                raise requests.RequestException("connection refused")

        source = ConfapSource(session=_SessaoQuebrada())
        assert source.read() == []
        assert source.last_listing_count == 0


class TestPerfilDaFonte:
    """
    Sem entrada em `SOURCE_PROFILES`, o edital é gravado com `fonte_key` vazio —
    foi o que aconteceu na primeira execução real do fluxo. `fonte_key` é a chave
    técnica de rastreabilidade e de deduplicação; vazio, o edital fica órfão.
    """

    def test_confap_tem_perfil_registrado(self):
        from src.components.transforms import publication_rules

        assert publication_rules.SOURCE_PROFILES["CONFAP"] == ("internacional", "confap")

    def test_todo_flow_do_runner_tem_perfil(self):
        """Guarda contra adicionar fonte nova e esquecer o perfil."""
        from scripts import run_all_flows
        from src.components.transforms import publication_rules

        chaves = {c for _, c in publication_rules.SOURCE_PROFILES.values()}
        faltando = set(run_all_flows.REGISTRY_KEYS.values()) - chaves
        assert not faltando, f"fluxos sem perfil em SOURCE_PROFILES: {sorted(faltando)}"


class TestIndiceDeProcessados:
    """
    `processed_store.add_many` ignora silenciosamente fonte fora de `SOURCES`.
    O fluxo CONFAP rodou uma vez com a chave faltando: gravou os 5 editais e
    registrou zero, o que faria reprocessar as 30 chamadas toda noite.
    """

    def test_confap_esta_na_whitelist(self):
        from src import processed_store

        assert "confap" in processed_store.SOURCES

    def test_toda_fonte_do_runner_esta_na_whitelist(self):
        """Guarda contra adicionar fluxo novo e o índice virar no-op silencioso."""
        from scripts import run_all_flows
        from src import processed_store

        faltando = set(run_all_flows.REGISTRY_KEYS.values()) - set(processed_store.SOURCES)
        assert not faltando, f"fontes fora de processed_store.SOURCES: {sorted(faltando)}"

    def test_add_many_registra_de_fato(self, tmp_path):
        from src import processed_store

        indice = str(tmp_path / "processed.json")
        processed_store.add_many("confap", ["https://confap.org.br/pt/editais/1/x"], path=indice)
        assert processed_store.get_keys_set("confap", path=indice) == {
            "https://confap.org.br/pt/editais/1/x"
        }
