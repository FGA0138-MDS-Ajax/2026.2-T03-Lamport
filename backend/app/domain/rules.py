from enum import Enum
from typing import List, Optional, Dict, Any, NamedTuple

class Nivel(Enum):
    AUTOCUIDADO = "N0"  
    ALERTA = "N1"       
    CRISE = "N2"        

class Tag(Enum):
    ANSIEDADE = "ansiedade"
    ESTRESSE = "estresse"
    SONO = "sono"
    HUMOR = "humor"
    FOCO = "foco"
    BEM_ESTAR = "bem_estar"

LIMITE_PADRAO_SUGESTOES = 3
DIAS_BLOQUEIO_ULTIMAS_EXIBICOES = 7

class ResultadoCheckin(NamedTuple):
    nivel: Nivel
    tags: tuple
    regras: tuple

def avaliar_checkin(
    p1: Optional[int] = None, 
    p2: Optional[int] = None, 
    p3: Optional[int] = None, 
    p4: Optional[int] = None, 
    p5: Optional[bool] = None
) -> ResultadoCheckin:
    """
    Avalia o check-in do usuário retornando o nível de risco, as tags identificadas 
    e as regras acionadas (R-D1 a R-D6).
    """
    regras_acionadas: List[str] = []
    tags_detectadas: List[Tag] = []

    if p5 is True:
        return ResultadoCheckin(Nivel.CRISE, (), ("R-D1",))

    if p2 is not None and p2 >= 2:
        regras_acionadas.append("R-D3")
        tags_detectadas.append(Tag.ANSIEDADE)

    if p1 is not None and p1 <= 2:
        regras_acionadas.append("R-D2")
        tags_detectadas.append(Tag.HUMOR)

    if p4 is not None and p4 >= 2:
        regras_acionadas.append("R-D5")
        tags_detectadas.append(Tag.ESTRESSE)

    if p3 is not None and p3 <= 2:
        regras_acionadas.append("R-D4")
        tags_detectadas.append(Tag.SONO)

    if regras_acionadas:
        return ResultadoCheckin(
            Nivel.AUTOCUIDADO, 
            tuple(tags_detectadas), 
            tuple(regras_acionadas)
        )

    return ResultadoCheckin(Nivel.AUTOCUIDADO, (Tag.BEM_ESTAR,), ("R-D6",))

def selecionar_materiais(
    tags: tuple, 
    catalogo: List[Dict[str, Any]], 
    ultimas_exibicoes: List[str], 
    limite: int = LIMITE_PADRAO_SUGESTOES
) -> List[Dict[str, str]]:
    """
    Seleciona sugestões de materiais com base nas tags, filtrando itens recentes.
    """
    sugestoes: List[Dict[str, str]] = []
    
    for item in catalogo:
        material_id = item.get("material_id")
        item_tags = item.get("tags", [])
        
        if material_id in ultimas_exibicoes:
            continue

        match_encontrado = any(tag in item_tags for tag in tags)
        
        if match_encontrado:
            sugestoes.append({
                "material_id": material_id,
                "regra": "R-S3",
                "motivo": item.get("motivo", "")
            })
            
        if len(sugestoes) >= limite:
            break

    if not sugestoes and catalogo:
        for item in catalogo:
            if item.get("material_id") not in ultimas_exibicoes:
                sugestoes.append({
                    "material_id": item.get("material_id"),
                    "regra": "R-S6",
                    "motivo": "Conteúdo geral de apoio"
                })
                if len(sugestoes) >= limite:
                    break

    return sugestoes