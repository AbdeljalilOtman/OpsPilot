from fastapi import FastAPI

from opspilot.api.routes import router
from opspilot.db.base import Base
from opspilot.db.models import Ticket, User  # noqa: F401 - register model metadata
from opspilot.db.seed import seed_users
from opspilot.db.session import get_engine, get_session_factory


def create_app(*, initialize_database: bool = True) -> FastAPI:
    app = FastAPI(title="OpsPilot", version="0.1.0", description="Synthetic service operations prototype")
    app.include_router(router)

    @app.get("/health/live", tags=["health"])
    def liveness() -> dict[str, str]:
        return {"status": "alive"}

    if initialize_database:
        @app.on_event("startup")
        def initialize() -> None:
            Base.metadata.create_all(bind=get_engine())
            with get_session_factory()() as session:
                seed_users(session)

    return app


app = create_app()
