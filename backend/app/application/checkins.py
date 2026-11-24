from __future__ import annotations

import logging
import uuid
from collections.abc import Callable
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from app.domain.checkin import Checkin, CheckinRepository, Nivel
from app.domain.errors import CheckinAlreadyExistsError, CheckinNotFoundError
from app.domain.recomendacao import Recomendacao, RecomendacaoRepository
from app.rules.checkin import avaliar_checkin, tags_selecao_checkin
from app.rules.selecao import MaterialCatalogo, selecionar_materiais

CHECKIN_TIMEZONE = ZoneInfo("America/Sao_Paulo")
LIMITE_RECOMENDACOES_CHECKIN = 3

logger = logging.getLogger(__name__)


def today_in_checkin_timezone() -> date:
    return datetime.now(CHECKIN_TIMEZONE).date()


class CheckinService:
    def __init__(
        self,
        checkins: CheckinRepository,
        recomendacoes: RecomendacaoRepository,
        commit: Callable[[], None] = lambda: None,
    ) -> None:
        self.checkins = checkins
        self.recomendacoes = recomendacoes
        self.commit = commit

    def create(
        self,
        user_id: uuid.UUID,
        p1: int | None,
        p2: int | None,
        p3: int | None,
        p4: int | None,
        p5: bool,
    ) -> Checkin:
        today = today_in_checkin_timezone()
        if self.checkins.get_by_user_and_date(user_id, today) is not None:
            raise CheckinAlreadyExistsError

        resultado = avaliar_checkin(p1, p2, p3, p4, p5)
        # p1 a p5 são os nomes da API; o domínio usa os nomes da Figura 6.
        checkin = Checkin(
            user_id=user_id,
            data=today,
            humor=p1,
            ansiedade=p2,
            sono=p3,
            sobrecarga=p4,
            pensamento_risco=p5,
            nivel=resultado.nivel,
            tags=list(resultado.tags),
        )
        self.checkins.add(checkin)

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
                tags=tags_selecao_checkin(resultado),
                catalogo=catalogo,
                ultimas_exibicoes=ultimas_exibicoes,
                limite=LIMITE_RECOMENDACOES_CHECKIN,
            )
            recomendacoes = [
                Recomendacao(
                    user_id=user_id,
                    checkin_id=checkin.id,
                    material_id=sugestao.material_id,
                    regra=sugestao.regra,
                    motivo=sugestao.motivo,
                    titulo=materiais_por_id[sugestao.material_id].titulo,
                    fonte=materiais_por_id[sugestao.material_id].fonte,
                    resumo=materiais_por_id[sugestao.material_id].resumo,
                    url=materiais_por_id[sugestao.material_id].url,
                    criado_em=checkin.criado_em + timedelta(microseconds=idx),
                )
                for idx, sugestao in enumerate(sugestoes)
            ]
            self.recomendacoes.add_all(recomendacoes)
            checkin.recomendacoes = recomendacoes

        self.commit()
        logger.info("Check-in created id=%s user_id=%s", checkin.id, user_id)
        return checkin

    def get_today(self, user_id: uuid.UUID) -> Checkin:
        checkin = self.checkins.get_by_user_and_date(user_id, today_in_checkin_timezone())
        if checkin is None:
            raise CheckinNotFoundError
        checkin.recomendacoes = self.recomendacoes.list_by_checkin(checkin.id)
        return checkin

    def get_by_id(self, checkin_id: uuid.UUID, user_id: uuid.UUID) -> Checkin:
        checkin = self.checkins.get_by_id_for_user(checkin_id, user_id)
        if checkin is None:
            raise CheckinNotFoundError
        return checkin

    def list(self, user_id: uuid.UUID, limit: int = 30) -> list[Checkin]:
        clamped_limit = min(max(1, limit), 30)
        return self.checkins.list_by_user(user_id, limit=clamped_limit)

    # Aliases de compatibilidade
    def get_checkin_detail(self, checkin_id: uuid.UUID, user_id: uuid.UUID) -> Checkin:
        return self.get_by_id(checkin_id, user_id)

    def get_today_checkin(self, user_id: uuid.UUID, today: date | None = None) -> Checkin:
        target_date = today or today_in_checkin_timezone()
        checkin = self.checkins.get_by_user_and_date(user_id, target_date)
        if checkin is None:
            raise CheckinNotFoundError
        checkin.recomendacoes = self.recomendacoes.list_by_checkin(checkin.id)
        return checkin

    def list_checkins(
        self,
        user_id: uuid.UUID,
        limit: int = 30,
        offset: int = 0,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> list[Checkin]:
        return self.list(user_id, limit=limit)
