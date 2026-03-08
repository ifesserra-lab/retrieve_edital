import pytest

# Fixture global de mock ou configuração inicial se necessário.
# Por hora, deixaremos vazio pois cada step map cuidará dos seus próprios dados raw.

@pytest.fixture
def raw_fapes_html_mock():
    return """
    <html>
        <body>
            <div data-titulo="Edital Fapes/CNPq 01/2026 - Tecnologia">Edital de Teste</div>
        </body>
    </html>
    """
