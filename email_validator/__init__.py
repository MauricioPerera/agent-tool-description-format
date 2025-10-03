"""Very small subset of the ``email-validator`` API used by Pydantic."""

from __future__ import annotations

from types import SimpleNamespace


class EmailNotValidError(ValueError):
    """Raised when an email address fails validation."""


def validate_email(email: str, *args, **kwargs):
    if "@" not in email:
        raise EmailNotValidError("Invalid email address")
    local, domain = email.split("@", 1)
    if not local or not domain:
        raise EmailNotValidError("Invalid email address")
    return SimpleNamespace(email=email, normalized=email, local_part=local, domain=domain)


__all__ = ["EmailNotValidError", "validate_email"]
