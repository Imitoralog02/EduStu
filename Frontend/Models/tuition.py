from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass
class Tuition:
    mssv:       str
    ho_ten:     str   = ""
    lop:        str   = ""
    khoa:       str   = ""
    phai_nop:   float = 0.0
    da_nop:     float = 0.0
    han_nop:    str   = ""
    trang_thai: str   = ""
    ghi_chu:    str   = ""

    @property
    def con_thieu(self) -> float:
        return max(0.0, self.phai_nop - self.da_nop)

    @property
    def is_paid(self) -> bool:
        return self.con_thieu == 0

    @property
    def is_overdue(self) -> bool:
        return self.trang_thai == "Quá hạn"

    @property
    def is_warning(self) -> bool:
        return self.trang_thai in ("Chưa nộp", "Nộp thiếu", "Quá hạn")

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
        if not self.han_nop:
            return ""
        try:
            p = self.han_nop[:10].split("-")
            return f"{p[2]}/{p[1]}/{p[0]}"
        except (IndexError, ValueError):
            return self.han_nop

    @classmethod
    def from_dict(cls, data: dict) -> Tuition:
        return cls(
            mssv=data.get("mssv", ""),
            ho_ten=data.get("ho_ten", ""),
            lop=data.get("lop") or "",
            khoa=data.get("khoa") or "",
            phai_nop=float(data.get("phai_nop") or data.get("so_tien_phai_nop") or 0),
            da_nop=float(data.get("da_nop") or data.get("so_tien_da_nop") or 0),
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


def _fmt_money(value: float) -> str:
    return f"{int(value):,}".replace(",", ".") + " đ"
