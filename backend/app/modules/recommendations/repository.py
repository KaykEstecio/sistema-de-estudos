"""Contexto do dono em uma instrução SQL, sem commits ou consultas por item."""

from dataclasses import dataclass
from datetime import datetime
from itertools import groupby

from sqlalchemy import and_, func, or_, select, true
from sqlalchemy.orm import Session
from app.modules.assessments.models import Assessment, AssessmentResult
from app.modules.attempts.models import ChallengeAttempt
from app.modules.challenges.models import Challenge, ChallengeSkill
from app.modules.evaluation.models import AttemptEvaluation
from app.modules.onboarding.models import UserInterest
from app.modules.skills.models import Skill
from app.modules.skills.progress_models import UserSkill
from app.modules.recommendations.policy import Candidate, SkillContext


@dataclass(frozen=True)
class CandidateDetail:
    candidate: Candidate
    title: str
    estimated_minutes: int
    skill_names: dict[int, str]


class RecommendationRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def load(self, user_id: int, skill_id: int, now: datetime) -> list[CandidateDetail] | None:
        """None: focal indisponível; []: focal válida sem candidatos."""
        focal = select(Skill.id).join(UserInterest, UserInterest.category_id == Skill.category_id).where(
            Skill.id == skill_id, Skill.is_active.is_(True), UserInterest.user_id == user_id).cte("focal")
        has_focal = select(ChallengeSkill.challenge_id).where(
            ChallengeSkill.challenge_id == Challenge.id, ChallengeSkill.skill_id == skill_id).exists()
        inactive = select(ChallengeSkill.challenge_id).join(Skill).where(
            ChallengeSkill.challenge_id == Challenge.id, Skill.is_active.is_(False)).exists()
        candidates = select(Challenge.id, Challenge.title, Challenge.difficulty_score,
                            Challenge.estimated_minutes).where(
            Challenge.is_active.is_(True), has_focal, ~inactive).cte("candidates")
        ranked_results = select(AssessmentResult.skill_id, AssessmentResult.score,
            func.row_number().over(partition_by=AssessmentResult.skill_id,
                order_by=(Assessment.completed_at.desc(), Assessment.id.desc())).label("position")
        ).join(Assessment, Assessment.id == AssessmentResult.assessment_id).where(
            Assessment.user_id == user_id, Assessment.completed_at <= now).cte("ranked_results")
        reviewed = select(AttemptEvaluation.id).where(
            AttemptEvaluation.attempt_id == ChallengeAttempt.id).exists()
        history = select(ChallengeAttempt.challenge_id,
            func.bool_or(ChallengeAttempt.status == "IN_PROGRESS").label("has_open"),
            func.bool_or(and_(ChallengeAttempt.status == "SUBMITTED", ~reviewed)).label("has_pending"),
            func.bool_or(or_(ChallengeAttempt.started_at > now,
                             ChallengeAttempt.submitted_at > now)).label("has_future"),
            func.max(ChallengeAttempt.submitted_at).label("last_submitted_at")
        ).where(ChallengeAttempt.user_id == user_id,
                ChallengeAttempt.challenge_id.in_(select(candidates.c.id)))
        history = history.group_by(ChallengeAttempt.challenge_id).cte("history")

        statement = select(candidates.c.id.label("challenge_id"), candidates.c.title,
            candidates.c.difficulty_score, candidates.c.estimated_minutes,
            Skill.id.label("skill_id"), Skill.name.label("skill_name"), ChallengeSkill.weight,
            UserSkill.score, UserSkill.confidence, UserSkill.attempts,
            ranked_results.c.score.label("assessment_score"), history.c.has_open,
            history.c.has_pending, history.c.has_future, history.c.last_submitted_at
        ).select_from(focal).outerjoin(candidates, true()).outerjoin(
            ChallengeSkill, ChallengeSkill.challenge_id == candidates.c.id).outerjoin(
            Skill, Skill.id == ChallengeSkill.skill_id).outerjoin(
            UserSkill, and_(UserSkill.skill_id == Skill.id, UserSkill.user_id == user_id)).outerjoin(
            ranked_results, and_(ranked_results.c.skill_id == Skill.id, ranked_results.c.position == 1)).outerjoin(
            history, history.c.challenge_id == candidates.c.id).order_by(candidates.c.id, Skill.id)
        rows = self.session.execute(statement).mappings().all()
        if not rows:
            return None
        details: list[CandidateDetail] = []
        for challenge_id, group in groupby(rows, key=lambda row: row["challenge_id"]):
            if challenge_id is None:
                continue
            links = list(group)
            first = links[0]
            skills = tuple(SkillContext(skill_id=row["skill_id"], weight=row["weight"],
                score=row["score"], confidence=row["confidence"], attempts=row["attempts"],
                assessment_score=row["assessment_score"]) for row in links)
            candidate = Candidate(challenge_id=challenge_id, difficulty_score=first["difficulty_score"],
                skills=skills, has_open_attempt=bool(first["has_open"]),
                has_pending_evaluation=bool(first["has_pending"]),
                has_future_practice=bool(first["has_future"]), last_submitted_at=first["last_submitted_at"])
            details.append(CandidateDetail(candidate, first["title"], first["estimated_minutes"],
                                           {row["skill_id"]: row["skill_name"] for row in links}))
        return details
