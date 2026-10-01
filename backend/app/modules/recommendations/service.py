"""Seleciona atividades sem alterar evidência ou iniciar tentativas."""

from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.modules.recommendations.policy import CONFIDENCE_THRESHOLD, MIN_ATTEMPTS, POLICY_VERSION, Selection, select_candidates
from app.modules.recommendations.repository import CandidateDetail, RecommendationRepository
from app.modules.recommendations.schemas import (
    RecommendationQuery, RecommendationRead, RecommendationResponse, SkillReferenceRead,
)


class RecommendationSkillUnavailable(Exception):
    pass


class RecommendationService:
    def __init__(self, session: Session) -> None:
        self.repository = RecommendationRepository(session)

    def recommend(self, user_id: int, query: RecommendationQuery, *, now: datetime | None = None) -> RecommendationResponse:
        if now is not None and now.utcoffset() is None:
            raise ValueError("Data deve conter fuso horário.")
        now = datetime.now(timezone.utc) if now is None else now.astimezone(timezone.utc)
        details = self.repository.load(user_id, query.skill_id, now)
        if details is None:
            raise RecommendationSkillUnavailable()
        selected = select_candidates([item.candidate for item in details], skill_id=query.skill_id,
                                     limit=query.limit, now=now)
        by_id = {item.candidate.challenge_id: item for item in details}
        items = [self._read(item, by_id[item.challenge_id]) for item in selected]
        return RecommendationResponse(policy_version=POLICY_VERSION, generated_at=now,
            skill_id=query.skill_id, limit=query.limit, items=items,
            empty_reason=None if items else "NO_ELIGIBLE_CHALLENGES")

    @staticmethod
    def _read(selection: Selection, detail: CandidateDetail) -> RecommendationRead:
        labels = {"EXPLORATION": "Exploração para coletar evidências.",
                  "PRACTICE": "Prática dentro dos limites das referências disponíveis.",
                  "PROGRESSION": "Progressão moderada dentro dos limites de cada habilidade.",
                  "REVIEW": "Revisão abaixo das referências disponíveis em todas as habilidades."}
        reasons = [labels[selection.kind]]
        contexts = {skill.skill_id: skill for skill in detail.candidate.skills}
        for reference in selection.references:
            name = detail.skill_names[reference.skill_id]
            if reference.source == "NONE":
                reasons.append(f"{name}: sem evidência disponível; selecionado conteúdo introdutório.")
            elif reference.source == "ASSESSMENT":
                reasons.append(f"{name}: referência provisória do diagnóstico ({reference.score}).")
            else:
                reasons.append(f"{name}: score de prática {reference.score}.")
                context = contexts[reference.skill_id]
                assert context.confidence is not None and context.attempts is not None
                if context.confidence < CONFIDENCE_THRESHOLD or context.attempts < MIN_ATTEMPTS:
                    reasons.append(f"{name}: margem conservadora de dificuldade; evidência limitada.")
        if selection.practiced_recently:
            reasons.append("Praticado nos últimos sete dias; recebeu menor prioridade.")
        return RecommendationRead(challenge_id=selection.challenge_id, title=detail.title,
            difficulty_score=detail.candidate.difficulty_score, estimated_minutes=detail.estimated_minutes,
            kind=selection.kind, practiced_recently=selection.practiced_recently, reason=" ".join(reasons),
            skills=[SkillReferenceRead(skill_id=r.skill_id, weight=r.weight, source=r.source,
                                      reference_score=r.score, confidence=r.confidence) for r in selection.references])
