from pydantic import BaseModel, field_validator
from typing import Optional
from enum import Enum
import re


class TrangThaiEnum(str, Enum):
    dang_hoc = "Đang học"
    bao_luu = "Bảo lưu"
    thoi_hoc = "Thôi học"
    canh_bao = "Cảnh báo"


class StudentBase(BaseModel):
    ho_ten: str
    ngay_sinh: Optional[str] = None
    gioi_tinh: Optional[str] = None
    lop: Optional[str] = None
    khoa: Optional[str] = None
    email: Optional[str] = None
    so_dien_thoai: Optional[str] = None
    dia_chi: Optional[str] = None
    trang_thai: TrangThaiEnum = TrangThaiEnum.dang_hoc
    nam_nhap_hoc: Optional[int] = None
    doi_tuong: Optional[str] = None
    ho_ten_cha: Optional[str] = None
    ho_ten_me: Optional[str] = None
    sdt_phu_huynh: Optional[str] = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        if v and not re.match(r"^[\w.+-]+@[\w-]+\.[\w.]+$", v):
            raise ValueError("Email không hợp lệ")
        return v

    @field_validator("so_dien_thoai")
    @classmethod
    def validate_phone(cls, v):
        if v and not re.match(r"^(0|\+84)\d{9,10}$", v):
            raise ValueError("Số điện thoại không hợp lệ")
        return v


class StudentCreate(StudentBase):
    mssv: str

    @field_validator("mssv")
    @classmethod
    def validate_mssv(cls, v):
        if not re.match(r"^[A-Za-z0-9]+$", v):
            raise ValueError("MSSV chỉ được chứa chữ và số")
        return v


class StudentUpdate(StudentBase):
    pass


class StudentOut(StudentBase):
    mssv: str
    gpa: Optional[float] = None

    model_config = {"from_attributes": True}


class StudentListResponse(BaseModel):
    items: list[StudentOut]
    total: int
