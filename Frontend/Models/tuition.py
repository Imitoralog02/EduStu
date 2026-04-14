from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Tuition:
    """
    Đại diện cho thông tin học phí của một sinh viên.
    Tạo từ JSON trả về bởi GET /hocphi.
    """
    mssv:       str
    ho_ten:     str   = ""
    phai_nop:   float = 0.0    # tổng số tiền phải đóng
    da_nop:     float = 0.0    # số tiền đã đóng
    han_nop:    str   = ""     # hạn nộp "yyyy-MM-dd"
    trang_thai: str   = ""     # "Đã nộp" | "Chưa nộp" | "Nộp thiếu" | "Quá hạn"
    ghi_chu:    str   = ""

    # ------------------------------------------------------------------
    # Computed properties
    # ------------------------------------------------------------------

    @property
    def con_thieu(self) -> float:
        """Số tiền còn thiếu chưa nộp."""
        return max(0.0, self.phai_nop - self.da_nop)

    @property
    def is_paid(self) -> bool:
        """Đã đóng đủ học phí chưa."""
        return self.con_thieu == 0

    @property
    def is_overdue(self) -> bool:
        """Có bị quá hạn không."""
        return self.trang_thai == "Quá hạn"

    @property
    def phai_nop_display(self) -> str:
        return _fmt_money(self.phai_nop)

    @property
    def da_nop_display(self) -> str:
        return _fmt_money(self.da_nop)

    @property
    def con_thieu_display(self) -> str:
        return _fmt_money(self.con_thieu) if self.con_thieu > 0 else "—"

    @property
    def han_nop_display(self) -> str:
        """Chuyển 'yyyy-MM-dd' → 'dd/MM/yyyy'."""
        if not self.han_nop:
            return ""
        try:
            p = self.han_nop[:10].split("-")
            return f"{p[2]}/{p[1]}/{p[0]}"
        except (IndexError, ValueError):
            return self.han_nop

    # ------------------------------------------------------------------
    # Chuyển đổi từ / sang dict
    # ------------------------------------------------------------------

    @classmethod
    def from_dict(cls, data: dict) -> Tuition:
        """Tạo Tuition từ dict JSON trả về bởi FastAPI."""
        return cls(
            mssv=data.get("mssv", ""),
            ho_ten=data.get("ho_ten", ""),
            phai_nop=float(data.get("so_tien_phai_nop") or 0),
            da_nop=float(data.get("so_tien_da_nop") or 0),
            han_nop=data.get("han_nop", ""),
            trang_thai=data.get("trang_thai", ""),
            ghi_chu=data.get("ghi_chu", ""),
        )

    def to_dict(self) -> dict:
        return {
            "mssv":       self.mssv,
            "phai_nop":   self.phai_nop,
            "da_nop":     self.da_nop,
            "han_nop":    self.han_nop,
            "trang_thai": self.trang_thai,
        }

    def __str__(self) -> str:
        return f"{self.mssv} | {self.phai_nop_display} | {self.trang_thai}"


# ------------------------------------------------------------------
# Helper nội bộ
# ------------------------------------------------------------------

def _fmt_money(value: float) -> str:
    """4200000 → '4.200.000 đ'"""
    return f"{int(value):,}".replace(",", ".") + " đ"