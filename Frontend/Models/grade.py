from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Grade:
    """
    Đại diện cho điểm số của một sinh viên trong một học phần.
    Tạo từ JSON trả về bởi GET /diem/{mssv}.
    """
    id:          int
    mssv:        str
    ma_hp:       str
    ten_hp:      str   = ""
    so_tin_chi:  int   = 0
    hoc_ky:      str   = ""
    diem_gk:     float = 0.0    # điểm giữa kỳ  (trọng số 30%)
    diem_ck:     float = 0.0    # điểm cuối kỳ  (trọng số 70%)

    # ------------------------------------------------------------------
    # Computed properties — tính toán từ dữ liệu gốc
    # ------------------------------------------------------------------

    @property
    def tong_ket(self) -> float:
        """Điểm tổng kết = GK * 30% + CK * 70%."""
        return round(self.diem_gk * 0.3 + self.diem_ck * 0.7, 2)

    @property
    def dat(self) -> bool:
        """Sinh viên đạt môn học không (tổng kết >= 5.0)."""
        return self.tong_ket >= 5.0

    @property
    def ket_qua(self) -> str:
        """Nhãn kết quả: 'Đạt' hoặc 'Rớt'."""
        return "Đạt" if self.dat else "Rớt"

    @property
    def diem_gk_display(self) -> str:
        return f"{self.diem_gk:.1f}"

    @property
    def diem_ck_display(self) -> str:
        return f"{self.diem_ck:.1f}"

    @property
    def tong_ket_display(self) -> str:
        return f"{self.tong_ket:.2f}"

    # ------------------------------------------------------------------
    # Chuyển đổi từ / sang dict
    # ------------------------------------------------------------------

    @classmethod
    def from_dict(cls, data: dict) -> Grade:
        """Tạo Grade từ dict JSON trả về bởi FastAPI."""
        return cls(
            id=data.get("id", 0),
            mssv=data.get("mssv", ""),
            ma_hp=data.get("ma_hp", ""),
            ten_hp=data.get("ten_hp", ""),
            so_tin_chi=data.get("so_tin_chi", 0),
            hoc_ky=data.get("hoc_ky", ""),
            diem_gk=float(data.get("diem_gk") or 0),
            diem_ck=float(data.get("diem_ck") or 0),
        )

    def to_dict(self) -> dict:
        """Chuyển sang dict để gửi lên FastAPI (POST /diem)."""
        return {
            "mssv":    self.mssv,
            "ma_hp":   self.ma_hp,
            "hoc_ky":  self.hoc_ky,
            "diem_gk": self.diem_gk,
            "diem_ck": self.diem_ck,
        }

    def __str__(self) -> str:
        return f"{self.ma_hp} | GK:{self.diem_gk_display} CK:{self.diem_ck_display} → {self.tong_ket_display} ({self.ket_qua})"