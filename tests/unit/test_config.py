from secrets import token_urlsafe

import pytest
from pydantic import SecretStr, ValidationError

from opspilot.config import Settings


def test_missing_signing_key_is_rejected(monkeypatch):
    monkeypatch.delenv("OPSPILOT_DEV_TOKEN_SECRET", raising=False)

    with pytest.raises(ValidationError):
        Settings(_env_file=None)


@pytest.mark.parametrize("signing_key", ["", "short", " " * 32])
def test_empty_or_short_signing_key_is_rejected(signing_key):
    with pytest.raises(ValidationError):
        Settings(dev_token_secret=SecretStr(signing_key), _env_file=None)


def test_signing_key_is_redacted_from_settings_representation():
    signing_key = token_urlsafe(32)
    settings = Settings(dev_token_secret=SecretStr(signing_key), _env_file=None)

    assert signing_key not in repr(settings)
