import pytest

from app.domain.checkin import Nivel, Tag
from app.rules.checkin import avaliar_checkin
from app.rules.selecao import MaterialCatalogo, selecionar_materiais


def test_tu05_crise_p5_tem_precedencia():
    # p5=True deve ignorar os outros parâmetros (R-D1)
    res = avaliar_checkin(p1=1, p2=3, p3=1, p4=3, p5=True)
    assert res.nivel == Nivel.CRISE
    assert res.tags == ()
    assert res.regras == ("R-D1",)


def test_tu05_limites_exatos_e_ordem_rs1():
    # Testa os limites das constantes e a saída ordenada por ORDEM_TAGS
    res = avaliar_checkin(p1=2, p2=2, p3=2, p4=2, p5=False)
    assert res.nivel == Nivel.PRIORITARIO  # 4 regras acionadas
    # ORDEM_TAGS = ANSIEDADE, HUMOR, ESTRESSE, SONO
    assert res.tags == (Tag.ANSIEDADE, Tag.HUMOR, Tag.ESTRESSE, Tag.SONO)
    assert res.regras == ("R-D3", "R-D2", "R-D5", "R-D4")


def test_tu05_nenhum_risco_retorna_autocuidado_rd6():
    res = avaliar_checkin(p1=3, p2=1, p3=3, p4=1, p5=False)
    assert res.nivel == Nivel.AUTOCUIDADO
    assert res.tags == (Tag.BEM_ESTAR,)
    assert res.regras == ("R-D6",)


@pytest.fixture
def catalogo():
    return [
        MaterialCatalogo("m1", {"ansiedade"}, "Apoio 1"),
        MaterialCatalogo("m2", {"sono"}, "Apoio 2"),
        MaterialCatalogo("m3", {"bem_estar"}, "Apoio 3"),
    ]


def test_tu06_selecao_limite_zero_ou_catalogo_vazio(catalogo):
    assert selecionar_materiais((Tag.ANSIEDADE,), catalogo, set(), limite=0) == []
    assert selecionar_materiais((Tag.ANSIEDADE,), [], set(), limite=3) == []


def test_tu06_rs2_ignora_ultimas_exibicoes(catalogo):
    # m1 tem a tag ansiedade, mas está no bloqueio R-S2
    res = selecionar_materiais((Tag.ANSIEDADE,), catalogo, {"m1"}, limite=3)
    assert "m1" not in [r.material_id for r in res]
    # Deve cair no fallback R-S6 e pegar m3
    assert res[0].regra == "R-S6"


def test_tu06_rs3_match_exato_de_tags(catalogo):
    res = selecionar_materiais((Tag.SONO,), catalogo, set(), limite=1)
    assert len(res) == 1
    assert res[0].material_id == "m2"
    assert res[0].regra == "R-S3"
