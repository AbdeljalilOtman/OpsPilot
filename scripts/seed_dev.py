from opspilot.db.base import Base
from opspilot.db.seed import seed_users
from opspilot.db.session import get_engine, get_session_factory


def main() -> None:
    Base.metadata.create_all(bind=get_engine())
    with get_session_factory()() as session:
        seed_users(session)
    print("Seeded fictional development identities.")


if __name__ == "__main__":
    main()
