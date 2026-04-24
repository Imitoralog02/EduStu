from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass
class StudentDocument:
    id:        int
    mssv:      str
    loai_giay: str
    da_nop:    bool
    ngay_nop:  Optional[str] = None   # "yyyy-MM-dd" hoặc None
    ghi_chu:   Optional[str] = None

    @classmethod
    def from_dict(cls, d: dict) -> StudentDocument:
        da_nop = d.get("da_nop")
        return cls(
            id        = d.get("id", 0),
            mssv      = d.get("mssv", ""),
            loai_giay = d.get("loai_giay", ""),
            da_nop    = bool(da_nop is True or da_nop == 1),
            ngay_nop  = str(d["ngay_nop"]) if d.get("ngay_nop") else None,
            ghi_chu   = d.get("ghi_chu") or None,
        )


@dataclass
class DocSummary:
    mssv:       str
    ho_ten:     str
    khoa:       Optional[str]
    lop:        Optional[str]
    tong:       int
    da_nop:     int
    con_thieu:  int
    hoan_chinh: bool

    @classmethod
    def from_dict(cls, d: dict) -> DocSummary:
        return cls(
            mssv       = d.get("mssv", ""),
            ho_ten     = d.get("ho_ten", ""),
            khoa       = d.get("khoa") or None,
            lop        = d.get("lop") or None,
            tong       = d.get("tong", 6),
            da_nop     = d.get("da_nop", 0),
            con_thieu  = d.get("con_thieu", 0),
            hoan_chinh = bool(d.get("hoan_chinh", False)),
        )
