"""Filtros combinados, visibilidade e rollback real sem commit no repository."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.categories.models import Category
from app.modules.skills.models import Skill
from app.modules.challenges.models import Challenge
from app.modules.challenges.repository import ChallengeRepository
from app.modules.challenges.schemas import ChallengeCreate, ChallengeUpdate, ChallengeRead, ChallengeSkillRead


def test_challenge_repository(migrated_database):
    engine, _ = migrated_database
    with Session(engine) as session:
        category = Category(name="Test", slug="test")
        session.add(category)
        session.flush()
        skills = [Skill(category_id=category.id, name=str(i), slug=f"skill-{i}", is_active=i != 2) for i in range(3)]
        session.add_all(skills)
        session.commit()
        ids = [item.id for item in skills]
        repo = ChallengeRepository(session)

        def create(title, links, active=True, kind="CODE"):
            return repo.create(ChallengeCreate(title=title, description="Fixture", challenge_type=kind,
                difficulty="EASY", difficulty_score=100, estimated_minutes=10, is_active=active,
                skills=[dict(skill_id=sid, weight=weight) for sid, weight in links]))

        first = create("First", [(ids[1], 50), (ids[0], 50)])
        second = create("Second", [(ids[0], 100)], kind="SQL")
        hidden = create("Hidden", [(ids[0], 50), (ids[2], 50)])
        inactive = create("Inactive", [(ids[0], 100)], active=False)
        session.commit()
        first_id, second_id, hidden_id, inactive_id = first.id, second.id, hidden.id, inactive.id
        page, total = repo.list_page(limit=1, offset=1, visible_only=True, skill=ids[0], difficulty="EASY")
        assert total == 2 and [item.id for item in page] == [second_id]
        assert repo.get_by_id(hidden_id, visible_only=True) is None
        assert repo.get_by_id(inactive_id, visible_only=True) is None
        assert repo.get_by_id(hidden_id) is not None
        assert repo.list_page(limit=20, offset=0)[1] == 4
        assert repo.list_page(limit=20, offset=0, is_active=False)[1] == 1
        assert repo.list_page(limit=20, offset=0, visible_only=True, challenge_type="SQL")[1] == 1
        assert repo.list_page(limit=20, offset=0, skill=2147483647) == ([], 0)
        assert repo.list_page(limit=20, offset=20, visible_only=True) == ([], 2)
        links = repo.get_links([first_id, second_id])
        assert [link.skill_id for link in links[first_id]] == ids[:2]
        assert repo.get_links([]) == {}
        assert [item.id for item in repo.get_skills_locked(ids[::-1])] == ids
        public = ChallengeRead.model_validate(dict(
            **{name: getattr(first, name) for name in ChallengeRead.model_fields if name != "skills"},
            skills=[ChallengeSkillRead.model_validate(link) for link in links[first_id]]))
        assert set(public.skills[0].model_dump()) == {"skill_id", "weight"}
        repo.update(repo.get_locked(first_id), ChallengeUpdate(title="Changed", skills=[dict(skill_id=ids[1], weight=100)]))
        assert len(repo.get_links([first_id])[first_id]) == 1
        session.rollback()
        assert repo.get_by_id(first_id).title == "First"
        assert len(repo.get_links([first_id])[first_id]) == 2
        fresh = create("Rolled back", [(ids[0], 100)])
        fresh_id = fresh.id
        session.rollback()
        assert session.get(Challenge, fresh_id) is None
        skills[2].is_active = True
        session.commit()
        assert repo.get_by_id(hidden_id, visible_only=True) is not None
        assert session.scalar(select(Challenge.id).where(Challenge.id == first_id)) == first_id
