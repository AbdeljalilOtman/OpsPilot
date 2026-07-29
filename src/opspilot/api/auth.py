from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from sqlalchemy.orm import Session

from opspilot.config import get_settings
from opspilot.db.models import User
from opspilot.db.session import get_db

bearer_scheme = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class Principal:
    id: str
    role: str
    team_id: str | None


def _serializer() -> URLSafeTimedSerializer:
    settings = get_settings()
    return URLSafeTimedSerializer(
        settings.dev_token_secret.get_secret_value(), salt="opspilot-dev-token-v1"
    )


def create_dev_token(user_id: str) -> str:
    """Mint a local demo token; do not expose this helper in a deployed service."""
    if get_settings().env != "development":
        raise RuntimeError("Development tokens can only be minted in development mode")
    return _serializer().dumps({"sub": user_id, "iat": int(datetime.now(UTC).timestamp())})


def get_current_principal(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> Principal:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bearer token required")
    try:
        claims = _serializer().loads(
            credentials.credentials, max_age=get_settings().dev_token_ttl_seconds
        )
    except (BadSignature, SignatureExpired):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token") from None

    user_id = claims.get("sub") if isinstance(claims, dict) else None
    user = db.get(User, user_id) if isinstance(user_id, str) else None
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unknown user")
    return Principal(id=user.id, role=user.role, team_id=user.team_id)
