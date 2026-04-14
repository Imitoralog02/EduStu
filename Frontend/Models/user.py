from __future__ import annotations
from dataclasses import dataclass


@dataclass
class User:
    """
    Đại diện cho tài khoản đăng nhập.
    Được tạo sau khi đăng nhập thành công từ JWT payload.
    """
    id:       int
    username: str
    ho_ten:   str
    role:     str        # "admin" | "phongdt" | "giaovien"
    email:    str = ""

    # ------------------------------------------------------------------
    # Computed properties
    # ------------------------------------------------------------------

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"

    @property
    def is_phongdt(self) -> bool:
        return self.role == "phongdt"

    @property
    def is_giaovien(self) -> bool:
        return self.role == "giaovien"

    @property
    def avatar_text(self) -> str:
        """
        Lấy 2 chữ cái đầu + cuối để hiển thị avatar.
        VD: 'Nguyễn Văn An' → 'NA'
        """
        parts = self.ho_ten.strip().split()
        if len(parts) >= 2:
            return (parts[0][0] + parts[-1][0]).upper()
        return self.ho_ten[:2].upper() if self.ho_ten else "?"

    @property
    def role_label(self) -> str:
        """Nhãn hiển thị tiếng Việt của role."""
        mapping = {
            "admin":    "Quản trị viên",
            "phongdt":  "Phòng đào tạo",
            "giaovien": "Giảng viên",
        }
        return mapping.get(self.role, self.role)

    # ------------------------------------------------------------------
    # Kiểm tra quyền
    # ------------------------------------------------------------------

    def can(self, *roles: str) -> bool:
        """
        Kiểm tra user có thuộc role được phép không.

        Ví dụ:
            user.can("admin", "phongdt")  → True nếu là admin hoặc phongdt
        """
        return self.role in roles

    # ------------------------------------------------------------------
    # Chuyển đổi từ / sang dict
    # ------------------------------------------------------------------

    @classmethod
    def from_dict(cls, data: dict) -> User:
        """Tạo User từ dict JSON trả về bởi FastAPI."""
        return cls(
            id=data.get("id", 0),
            username=data.get("username", ""),
            ho_ten=data.get("ho_ten", ""),
            role=data.get("role", ""),
            email=data.get("email", ""),
        )

    def to_dict(self) -> dict:
        return {
            "id":       self.id,
            "username": self.username,
            "ho_ten":   self.ho_ten,
            "role":     self.role,
            "email":    self.email,
        }

    def __str__(self) -> str:
        return f"{self.ho_ten} ({self.role_label})"