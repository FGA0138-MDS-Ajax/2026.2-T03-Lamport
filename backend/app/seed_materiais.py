import os
from pathlib import Path
import yaml
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infrastructure.database import get_engine
from app.infrastructure.db.models import MaterialModel


def carregar_yaml(caminho: Path) -> list[dict]:
    if not caminho.exists():
        print(f"⚠️  Arquivo YAML não encontrado no caminho: {caminho}")
        return []
    
    with open(caminho, "r", encoding="utf-8") as f:
        dados = yaml.safe_load(f) or []
        
    # Trata caso o YAML use chave raiz (ex: materiais: [...])
    if isinstance(dados, dict):
        return dados.get("materiais", [])
    return dados


def rodar_seed(session: Session, caminho_yaml: Path):
    materiais_yaml = carregar_yaml(caminho_yaml)
    slugs_no_yaml = set()

    for item in materiais_yaml:
        slug = item["slug"]
        slugs_no_yaml.add(slug)

        material_db = session.execute(
            select(MaterialModel).where(MaterialModel.slug == slug)
        ).scalar_one_or_none()

        if material_db:
            material_db.titulo = item["titulo"]
            material_db.url = item["url"]
            material_db.fonte = item["fonte"]
            material_db.resumo = item["resumo"]
            material_db.tags = item["tags"]
            material_db.ativo = item.get("ativo", True)
            material_db.revisado_em = item["data_de_revisao"]
        else:
            novo_material = MaterialModel(
                slug=slug,
                titulo=item["titulo"],
                url=item["url"],
                fonte=item["fonte"],
                resumo=item["resumo"],
                tags=item["tags"],
                ativo=item.get("ativo", True),
                revisado_em=item["data_de_revisao"],
            )
            session.add(novo_material)

    # Marca materiais removidos do YAML como inativos
    todos_db = session.execute(select(MaterialModel)).scalars().all()
    for material in todos_db:
        if material.slug not in slugs_no_yaml:
            material.ativo = False

    session.commit()
    print(f"Seed concluído com sucesso! {len(slugs_no_yaml)} materiais processados.")


if __name__ == "__main__":
    root_dir = Path(__file__).resolve().parent.parent.parent
    caminho = root_dir / "catalog" / "materiais.yaml"

    with Session(get_engine(), expire_on_commit=False) as db:
        rodar_seed(db, caminho)