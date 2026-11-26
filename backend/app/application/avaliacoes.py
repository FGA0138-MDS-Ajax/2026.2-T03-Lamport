from __future__ import annotations

import logging
import uuid
from collections.abc import Callable, Sequence
from datetime import timedelta

from app.domain.avaliacao import Avaliacao, AvaliacaoRepository
from app.domain.checkin import Nivel
from app.domain.errors import AvaliacaoNotFoundError
from app.domain.recomendacao import Recomendacao, RecomendacaoRepository
from app.rules.avaliacao import (
    decidir_avaliacao,
    limite_recomendacoes_avaliacao,
    tags_selecao_avaliacao,
)
from app.rules.selecao import MaterialCatalogo, selecionar_materiais

logger = logging.getLogger(__name__)


class AvaliacaoService:
    def __init__(
        self,
        avaliacoes: AvaliacaoRepository,
        recomendacoes: RecomendacaoRepository,
        commit: Callable[[], None] = lambda: None,
    ) -> None:
        self.avaliacoes = avaliacoes
        self.recomendacoes = recomendacoes
        self.commit = commit

    def create(
        self,
        user_id: uuid.UUID,
        phq9: Sequence[int],
        gad7: Sequence[int],
    ) -> Avaliacao:
        resultado = decidir_avaliacao(phq9, gad7)
        avaliacao = Avaliacao(
            user_id=user_id,
            respostas_phq9=list(phq9),
            respostas_gad7=list(gad7),
            escore_phq9=resultado.escore_phq9,
            escore_gad7=resultado.escore_gad7,
            faixa_phq9=resultado.faixa_phq9,
            faixa_gad7=resultado.faixa_gad7,
            nivel=resultado.nivel,
        )
        self.avaliacoes.add(avaliacao)

        if resultado.nivel != Nivel.CRISE:
            materiais_ativos = self.recomendacoes.list_active_materials()
            materiais_por_id = {m.id: m for m in materiais_ativos if m.id is not None}
            catalogo = [
                MaterialCatalogo(material_id=m.id, tags=set(m.tags), ativo=m.ativo)
                for m in materiais_ativos
                if m.id is not None
            ]
            ultimas_exibicoes = self.recomendacoes.get_last_displayed_by_user(user_id)
            sugestoes = selecionar_materiais(
                tags=tags_selecao_avaliacao(resultado),
                catalogo=catalogo,
                ultimas_exibicoes=ultimas_exibicoes,
                limite=limite_recomendacoes_avaliacao(resultado.nivel),
            )
            recomendacoes = [
                Recomendacao(
                    user_id=user_id,
                    avaliacao_id=avaliacao.id,
                    material_id=sugestao.material_id,
                    regra=sugestao.regra,
                    motivo=sugestao.motivo,
                    titulo=materiais_por_id[sugestao.material_id].titulo,
                    fonte=materiais_por_id[sugestao.material_id].fonte,
                    resumo=materiais_por_id[sugestao.material_id].resumo,
                    url=materiais_por_id[sugestao.material_id].url,
                    criado_em=avaliacao.criado_em + timedelta(microseconds=idx),
                )
                for idx, sugestao in enumerate(sugestoes)
            ]
            self.recomendacoes.add_all(recomendacoes)
            avaliacao.recomendacoes = recomendacoes

        self.commit()
        logger.info("Avaliacao created id=%s user_id=%s", avaliacao.id, user_id)
        return avaliacao

    def list(self, user_id: uuid.UUID) -> list[Avaliacao]:
        """Todas as avaliações do usuário, da mais recente para a mais antiga (R12)."""
        return self.avaliacoes.list_by_user(user_id)

    def get_by_id(self, avaliacao_id: uuid.UUID, user_id: uuid.UUID) -> Avaliacao:
        """Avaliação do próprio usuário com as recomendações gravadas (DP-3).

        Inexistente e de outro usuário levantam o mesmo erro, para não revelar ids alheios.
        """
        avaliacao = self.avaliacoes.get_by_id_for_user(avaliacao_id, user_id)
        if avaliacao is None:
            raise AvaliacaoNotFoundError
        avaliacao.recomendacoes = self.recomendacoes.list_by_avaliacao(avaliacao.id)
        return avaliacao
