from pydantic import BaseModel, field_validator
from typing import Optional


class CourseBase(BaseModel):
    ten_hp: str
    so_tin_chi: int = 3
    giao_vien: Optional[str] = None
    hoc_ky: Optional[str] = None

    @field_validator("so_tin_chi")
    @classmethod
    def validate_credits(cls, v):
        if not (1 <= v <= 10):
            raise ValueError("Số tín chỉ phải từ 1 đến 10")
        return v


class CourseCreate(CourseBase):
    ma_hp: str


class CourseUpdate(CourseBase):
    pass


class CourseOut(CourseBase):
    ma_hp: str

    model_config = {"from_attributes": True}
