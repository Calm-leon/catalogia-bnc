import os
from typing import Dict

from fastapi import Depends, Header, HTTPException, status

from app.security import Role


def _token_env_var(role: Role) -> str:
    return f"{role.value.upper()}_TOKEN"


def _load_tokens() -> Dict[str, Role]:
    tokens: Dict[str, Role] = {}
    for role in Role:
        token = os.getenv(_token_env_var(role), "").strip()
        if token:
            tokens[token] = role
    return tokens


def require_role(*allowed: Role):
    def _auth(authorization: str = Header(default="")) -> Role:
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
        token = authorization.removeprefix("Bearer ").strip()
        tokens = _load_tokens()
        role = tokens.get(token)
        if role is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        if allowed and role not in allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
        return role

    return Depends(_auth)