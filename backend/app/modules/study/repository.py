from sqlalchemy import select, func, and_, true, Select
from sqlalchemy.engine import RowMapping
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session
from app.modules.skills.models import Skill
from app.modules.study.models import StudyContent, StudyCompletion
from app.modules.study.schemas import StudyCreate, StudyQuery


class StudyRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def active_skill(self, skill_id: int) -> Skill | None:
        return self.session.scalar(select(Skill).where(Skill.id == skill_id, Skill.is_active.is_(True)).with_for_update(read=True))

    def query(self, user_id: int) -> Select:
        return select(StudyContent.id, StudyContent.skill_id, Skill.name.label("skill_name"),
                      StudyContent.title, StudyCompletion.completed_at).join(Skill, Skill.id == StudyContent.skill_id).outerjoin(
                          StudyCompletion, and_(StudyCompletion.content_id == StudyContent.id, StudyCompletion.user_id == user_id)
                      ).where(Skill.is_active.is_(True))

    def list_page(self, user_id: int, query: StudyQuery) -> tuple[list[RowMapping], int]:
        statement = self.query(user_id)
        if query.skill_id is not None:
            statement = statement.where(StudyContent.skill_id == query.skill_id)
        contents = statement.cte("available_contents")
        count = select(func.count().label("total")).select_from(contents).cte("content_count")
        page = select(contents).order_by(contents.c.id.desc()).limit(query.limit).offset(query.offset).cte("content_page")
        rows = self.session.execute(select(count.c.total, page).select_from(count.outerjoin(page, true())).order_by(page.c.id.desc())).mappings().all()
        return [row for row in rows if row['id'] is not None], rows[0]['total']

    def get(self, user_id: int, content_id: int) -> RowMapping | None:
        return self.session.execute(self.query(user_id).add_columns(StudyContent.explanation,
            StudyContent.code_example, StudyContent.common_mistakes).where(StudyContent.id == content_id)).mappings().one_or_none()

    def create(self, data: StudyCreate) -> StudyContent:
        content = StudyContent(**data.model_dump())
        self.session.add(content); self.session.flush()
        return content

    def complete(self, user_id: int, content_id: int) -> None:
        self.session.execute(insert(StudyCompletion).values(user_id=user_id, content_id=content_id)
            .on_conflict_do_nothing(index_elements=['user_id', 'content_id']))
