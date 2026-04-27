from pydantic import BaseModel
from typing import Optional
from datetime import date


# ── DocumentType ──────────────────────────────────────────────────────────────

class DocumentTypeCreate(BaseModel):
    ten_loai: str
    bat_buoc: bool = True
    mo_ta:    Optional[str] = None
    thu_tu:   int = 0


class DocumentTypeUpdate(BaseModel):
    ten_loai: Optional[str] = None
    bat_buoc: Optional[bool] = None
    mo_ta:    Optional[str] = None
    thu_tu:   Optional[int] = None


class DocumentTypeOut(BaseModel):
    id:       int
    ten_loai: str
    bat_buoc: bool
    mo_ta:    Optional[str]
    thu_tu:   int

    model_config = {"from_attributes": True}


# ── StudentDocument ───────────────────────────────────────────────────────────

class DocumentUpdate(BaseModel):
    da_nop:   bool
    ngay_nop: Optional[date] = None
    ghi_chu:  Optional[str]  = None


class DocumentOut(BaseModel):
    id:        int
    mssv:      str
    loai_giay: str
    da_nop:    bool
    ngay_nop:  Optional[date]
    ghi_chu:   Optional[str]
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None

    model_config = {"from_attributes": True}


class StudentDocSummary(BaseModel):
    mssv:       str
    ho_ten:     str
    khoa:       Optional[str]
    lop:        Optional[str]
    tong:       int
    da_nop:     int
    con_thieu:  int
    hoan_chinh: bool
