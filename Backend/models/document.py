from sqlalchemy import Column, Integer, String, Boolean, Date, Text, ForeignKey, TIMESTAMP, func
from sqlalchemy.orm import relationship
from database import Base


LOAI_GIAY_YEU_CAU = [
    "CCCD/CMND",
    "Giấy khai sinh",
    "Học bạ THPT",
    "Bằng tốt nghiệp THPT",
    "Ảnh thẻ 3x4",
    "Sổ hộ khẩu",
]


class StudentDocument(Base):
    __tablename__ = "student_documents"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    mssv       = Column(String(20), ForeignKey("students.mssv", ondelete="CASCADE"), nullable=False)
    loai_giay  = Column(String(100), nullable=False)
    da_nop     = Column(Boolean, default=False, nullable=False)
    ngay_nop   = Column(Date, nullable=True)
    ghi_chu    = Column(Text, nullable=True)
    cap_nhat   = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    student = relationship("Student", back_populates="documents")
