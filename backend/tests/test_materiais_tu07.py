import re
from datetime import date
from urllib.parse import urlparse

import pytest
import yaml

from app.domain.checkin import Tag
from app.seed_materiais import CAMINHO_CATALOGO

DOMINIOS_PERMITIDOS = ["gov.br", "paho.org", "who.int", "cvv.org.br"]
LIMITES_DE_TEXTO = {"slug": 100, "titulo": 255, "url": 500, "fonte": 100, "resumo": 500}
CAMPOS = {*LIMITES_DE_TEXTO, "tags", "ativo", "data_de_revisao"}


@pytest.fixture
def materiais():
    with open(CAMINHO_CATALOGO, encoding="utf-8") as f:
        dados = yaml.safe_load(f)
    assert isinstance(dados, list) and dados, "O catálogo precisa ser uma lista de materiais."
    return dados


def test_esquema_valido(materiais):
    tags_validas = {tag.value for tag in Tag}
    for m in materiais:
        assert set(m) == CAMPOS, f"Campos incorretos em {m.get('slug')}."
        for campo, limite in LIMITES_DE_TEXTO.items():
            assert isinstance(m[campo], str), f"{campo} de {m['slug']} precisa ser texto."
            assert 0 < len(m[campo]) <= limite, f"{campo} de {m['slug']} fora do limite."
        assert isinstance(m["tags"], list), f"tags de {m['slug']} precisa ser uma lista."
        assert m["tags"], f"{m['slug']} precisa ter ao menos uma tag."
        assert set(m["tags"]) <= tags_validas, f"Tag inválida em {m['slug']}."
        assert isinstance(m["ativo"], bool), f"ativo de {m['slug']} precisa ser booleano."
        assert isinstance(m["data_de_revisao"], date), f"Data inválida em {m['slug']}."
        frases = re.findall(r"[.!?](?:\s|$)", m["resumo"])
        assert len(frases) <= 2, f"Resumo de {m['slug']} tem mais de duas frases."


def test_slugs_unicos(materiais):
    slugs = [m["slug"] for m in materiais]
    assert len(slugs) == len(set(slugs)), "Existem slugs duplicados."


def test_urls_https_e_dominios_permitidos(materiais):
    for m in materiais:
        url = m["url"]
        assert url.startswith("https://"), f"URL {m['slug']} precisa ser HTTPS."
        dominio = urlparse(url).netloc
        assert any(dominio == d or dominio.endswith(f".{d}") for d in DOMINIOS_PERMITIDOS), (
            f"Domínio {dominio} não permitido."
        )


def test_pelo_menos_um_material_ativo_por_tag(materiais):
    tags_ativas = {t for m in materiais if m.get("ativo", True) for t in m["tags"]}
    faltando = {tag.value for tag in Tag} - tags_ativas
    assert not faltando, f"Faltam materiais ativos para as tags: {faltando}"
