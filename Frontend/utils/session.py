from __future__ import annotations
from models.user import User


class Session:
    _token: str | None  = None
    _user:  User | None = None

    @classmethod
    def set(cls, token: str, user: User) -> None:
        cls._token = token
        cls._user  = user

    @classmethod
    def clear(cls) -> None:
        cls._token = None
        cls._user  = None

    @classmethod
    def token(cls) -> str | None:
        return cls._token

    @classmethod
    def user(cls) -> User | None:
        return cls._user

    @classmethod
    def role(cls) -> str | None:
        return cls._user.role if cls._user else None

    @classmethod
    def is_logged_in(cls) -> bool:
        return cls._token is not None

    @classmethod
    def can(cls, *roles: str) -> bool:
        return cls.role() in roles

    @classmethod
    def can_do(cls, module: str, action: str) -> bool:
        """Kiểm tra role hiện tại có được phép thực hiện action trong module không.

        Ví dụ:
            Session.can_do("sinhvien", "delete")  → False nếu là phongdt
            Session.can_do("giayto", "manage_types") → True nếu là admin
        """
        from utils.config import PERMISSIONS
        role = cls.role() or ""
        return action in PERMISSIONS.get(role, {}).get(module, [])