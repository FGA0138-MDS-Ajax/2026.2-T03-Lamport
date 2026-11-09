import sys
import os

# Adiciona a pasta backend ao path para encontrar o app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "backend")))

from app.rules.checkin import avaliar_checkin, selecionar_materiais, Nivel, Tag

def testar_tudo():
    print("Rodando testes de regras...")
    
    # Teste 1: R-D1 (Crise)
    res1 = avaliar_checkin(1, 3, 1, 3, True)
    assert res1.nivel == Nivel.CRISE
    assert res1.regras == ("R-D1",)
    print("✅ R-D1 (Crise) passou!")

    # Teste 2: Autocuidado / Padrão
    res2 = avaliar_checkin(None, None, None, None, False)
    assert res2.nivel == Nivel.AUTOCUIDADO
    assert Tag.BEM_ESTAR in res2.tags
    print("✅ R-D6 (Autocuidado) passou!")

    # Teste 3: Seleção de materiais (Catálogo e Limite)
    catalogo = [
        {"material_id": "m1", "tags": (Tag.ANSIEDADE,), "motivo": "Ansiedade"},
        {"material_id": "m2", "tags": (Tag.SONO,), "motivo": "Sono"}
    ]
    sugestoes = selecionar_materiais(tags=(Tag.ANSIEDADE,), catalogo=catalogo, ultimas_exibicoes=[], limite=1)
    assert len(sugestoes) == 1
    assert sugestoes[0]["material_id"] == "m1"
    print("✅ Seleção de Materiais passou!")

    print("\n TUDO VERDE! Suas funções puras estão perfeitas e sem tocar no banco de dados!")

if __name__ == "__main__":
    testar_tudo()