from pydantic import BaseModel
from typing import Optional
from datetime import date


class DocumentUpdate(BaseModel):
    da_nop:    bool
    ngay_nop:  Optional[date] = None
    ghi_chu:   Optional[str]  = None


class DocumentOut(BaseModel):
    id:        int
    mssv:      str
    loai_giay: str
    da_nop:    bool
    ngay_nop:  Optional[date]
    ghi_chu:   Optional[str]

    model_config = {"from_attributes": True}


class StudentDocSummary(BaseModel):
    mssv:         str
    ho_ten:       str
    khoa:         Optional[str]
    lop:          Optional[str]
    tong:         int
    da_nop:       int
    con_thieu:    int
    hoan_chinh:   bool
