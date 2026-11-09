import yaml
import pytest
from pathlib import Path
from urllib.parse import urlparse
from app.domain.checkin import Tag

DOMINIOS_PERMITIDOS = ["gov.br", "paho.org", "who.int", "cvv.org.br"]

@pytest.fixture
def materiais():
    root_dir = Path(__file__).resolve().parent.parent.parent
    caminho = root_dir / "catalog" / "materiais.yaml"
    
    if not caminho.exists():
        pytest.skip("Arquivo catalog/materiais.yaml não encontrado.")
    with open(caminho, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or []

def test_slugs_unicos(materiais):
    slugs = [m['slug'] for m in materiais]
    assert len(slugs) == len(set(slugs)), "Existem slugs duplicados."

def test_urls_https_e_dominios_permitidos(materiais):
    for m in materiais:
        url = m['url']
        assert url.startswith("https://"), f"URL {m['slug']} precisa ser HTTPS."
        dominio = urlparse(url).netloc
        assert any(dominio == d or dominio.endswith(f".{d}") for d in DOMINIOS_PERMITIDOS), f"Domínio {dominio} não permitido."

def test_pelo_menos_um_material_ativo_por_tag(materiais):
    tags_ativas = {t for m in materiais if m.get('ativo', True) for t in m['tags']}
    todas_as_tags = {tag.value for tag in Tag}
    assert not (todas_as_tags - tags_ativas), f"Faltam materiais ativos para as tags: {todas_as_tags - tags_ativas}"