from datetime import date

import pytest
import yaml
from sqlalchemy import func, select

from app.infrastructure.models import MaterialModel
from app.seed_materiais import CAMINHO_CATALOGO, carregar_yaml, rodar_seed


def _material(slug):
    return {
        "slug": slug,
        "titulo": "Título",
        "url": "https://www.gov.br/saude",
        "fonte": "Ministério da Saúde",
        "resumo": "Resumo do material.",
        "tags": ["sono"],
        "ativo": True,
        "data_de_revisao": date(2026, 11, 9),
    }


def _catalogo(pasta, materiais):
    arquivo = pasta / "materiais.yaml"
    arquivo.write_text(yaml.safe_dump(materiais, allow_unicode=True), encoding="utf-8")
    return arquivo


def test_seed_carrega_o_catalogo_real_sem_duplicar(db_session):
    rodar_seed(db_session, CAMINHO_CATALOGO)
    rodar_seed(db_session, CAMINHO_CATALOGO)

    total = db_session.scalar(select(func.count()).select_from(MaterialModel))
    assert total == len(carregar_yaml(CAMINHO_CATALOGO))


def test_material_retirado_fica_inativo_e_continua_no_banco(db_session, tmp_path):
    rodar_seed(db_session, _catalogo(tmp_path, [_material("a"), _material("b")]))

    rodar_seed(db_session, _catalogo(tmp_path, [_material("a")]))

    linhas = db_session.execute(select(MaterialModel.slug, MaterialModel.ativo)).all()
    assert dict(linhas) == {"a": True, "b": False}


def test_seed_sem_arquivo_falha_e_mantem_materiais_ativos(db_session, tmp_path):
    rodar_seed(db_session, _catalogo(tmp_path, [_material("a")]))

    with pytest.raises(FileNotFoundError):
        rodar_seed(db_session, tmp_path / "inexistente.yaml")

    assert db_session.scalar(select(MaterialModel.ativo)) is True


def test_seed_com_catalogo_vazio_falha_e_mantem_materiais_ativos(db_session, tmp_path):
    rodar_seed(db_session, _catalogo(tmp_path, [_material("a")]))

    with pytest.raises(ValueError):
        rodar_seed(db_session, _catalogo(tmp_path, []))

    assert db_session.scalar(select(MaterialModel.ativo)) is True
