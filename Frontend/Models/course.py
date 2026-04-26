from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Course:
    """
    Đại diện cho một học phần trong hệ thống.
    Tạo từ JSON trả về bởi GET /hocphan.
    """
    ma_hp:       str
    ten_hp:      str
    so_tin_chi:  int  = 3
    giao_vien:   str  = ""
    hoc_ky:      str  = ""

    # ------------------------------------------------------------------
    # Computed properties
    # ------------------------------------------------------------------

    @property
    def display_name(self) -> str:
        """Tên hiển thị đầy đủ. VD: 'INT101 - Lập trình cơ bản (3 TC)'"""
        return f"{self.ma_hp} - {self.ten_hp} ({self.so_tin_chi} TC)"

    # ------------------------------------------------------------------
    # Chuyển đổi từ / sang dict
    # ------------------------------------------------------------------

    @classmethod
    def from_dict(cls, data: dict) -> Course:
        """Tạo Course từ dict JSON trả về bởi FastAPI."""
        return cls(
            ma_hp=data.get("ma_hp", ""),
            ten_hp=data.get("ten_hp", ""),
            so_tin_chi=data.get("so_tin_chi", 3),
            giao_vien=data.get("giao_vien", ""),
            hoc_ky=data.get("hoc_ky", ""),
        )

    def to_dict(self) -> dict:
        """Chuyển sang dict để gửi lên FastAPI (POST/PUT)."""
        return {
            "ma_hp":      self.ma_hp,
            "ten_hp":     self.ten_hp,
            "so_tin_chi": self.so_tin_chi,
            "giao_vien":  self.giao_vien,
            "hoc_ky":     self.hoc_ky,
        }

    def __str__(self) -> str:
        return self.display_name
