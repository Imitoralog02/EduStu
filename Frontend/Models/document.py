from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class DocumentType:
    id:       int
    ten_loai: str
    bat_buoc: bool  = True
    mo_ta:    Optional[str] = None
    thu_tu:   int   = 0

    @classmethod
    def from_dict(cls, d: dict) -> DocumentType:
        return cls(
            id       = d.get("id", 0),
            ten_loai = d.get("ten_loai", ""),
            bat_buoc = bool(d.get("bat_buoc", True)),
            mo_ta    = d.get("mo_ta") or None,
            thu_tu   = d.get("thu_tu", 0),
        )


@dataclass
class StudentDocument:
    id:        int
    mssv:      str
    loai_giay: str
    da_nop:    bool
    ngay_nop:  Optional[str] = None
    ghi_chu:   Optional[str] = None
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None

    @property
    def has_file(self) -> bool:
        return bool(self.file_name)

    @property
    def file_size_display(self) -> str:
        if not self.file_size:
            return ""
        if self.file_size < 1024:
            return f"{self.file_size} B"
        if self.file_size < 1024 * 1024:
            return f"{self.file_size / 1024:.1f} KB"
        return f"{self.file_size / (1024 * 1024):.1f} MB"

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
            file_name = d.get("file_name") or None,
            file_size = d.get("file_size") or None,
            mime_type = d.get("mime_type") or None,
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
            tong       = d.get("tong", 0),
            da_nop     = d.get("da_nop", 0),
            con_thieu  = d.get("con_thieu", 0),
            hoan_chinh = bool(d.get("hoan_chinh", False)),
        )
