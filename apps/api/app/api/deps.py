from typing import Annotated
from fastapi import Header, status
from jose import JWTError, jwt

from app.core.config import settings
from app.core.exceptions import PragyaException
from app.core.security import UserRole
from app.db.session import get_db


async def require_admin_role(
    x_user_role: Annotated[str | None, Header(alias="X-User-Role")] = None,
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
) -> str:
    """
    Ensures that only authorized administrators (ADMIN or SUPER_ADMIN)
    can access workforce-level intelligence and cadre analytics.
    Rejects EMPLOYEE, TRAINER, or missing credentials with 403 Forbidden.
    """
    role = x_user_role

    if not role and authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET,
                algorithms=[settings.JWT_ALGORITHM],
            )
            role = payload.get("role")
        except JWTError:
            pass

    if role:
        role_normalized = role.strip().upper()
        if role_normalized in [UserRole.ADMIN.value, UserRole.SUPER_ADMIN.value]:
            return role_normalized
        raise PragyaException(
            message="Administrator authorization required to access workforce intelligence.",
            code="UNAUTHORIZED_ACCESS",
            status_code=status.HTTP_403_FORBIDDEN,
        )

    raise PragyaException(
        message="Administrator authorization required to access workforce intelligence.",
        code="UNAUTHORIZED_ACCESS",
        status_code=status.HTTP_403_FORBIDDEN,
    )


__all__ = ["get_db", "require_admin_role"]
