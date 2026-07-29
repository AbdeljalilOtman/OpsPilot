from sqlalchemy.orm import Session

from opspilot.db.models import User

SEEDED_USERS = (
    User(id="employee-alex", display_name="Alex Employee", role="employee", team_id=None),
    User(id="employee-sam", display_name="Sam Employee", role="employee", team_id=None),
    User(id="analyst-jordan", display_name="Jordan Analyst", role="analyst", team_id="service_desk"),
)


def seed_users(session: Session) -> None:
    for seeded_user in SEEDED_USERS:
        if session.get(User, seeded_user.id) is None:
            session.add(
                User(
                    id=seeded_user.id,
                    display_name=seeded_user.display_name,
                    role=seeded_user.role,
                    team_id=seeded_user.team_id,
                )
            )
    session.commit()
