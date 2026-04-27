from sqlalchemy import Column, Integer, String, Boolean, Date, Text, ForeignKey, TIMESTAMP, BigInteger, func
from sqlalchemy.orm import relationship
from database import Base


class DocumentType(Base):
    """Bảng quản lý loại giấy tờ — có thể thêm/sửa/xóa qua UI."""
    __tablename__ = "document_types"

    id        = Column(Integer, primary_key=True, autoincrement=True)
    ten_loai  = Column(String(100), nullable=False, unique=True)
    bat_buoc  = Column(Boolean, default=True, nullable=False)
    mo_ta     = Column(Text, nullable=True)
    thu_tu    = Column(Integer, default=0, nullable=False)


class StudentDocument(Base):
    __tablename__ = "student_documents"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    mssv       = Column(String(20), ForeignKey("students.mssv", ondelete="CASCADE"), nullable=False)
    loai_giay  = Column(String(100), nullable=False)
    da_nop     = Column(Boolean, default=False, nullable=False)
    ngay_nop   = Column(Date, nullable=True)
    ghi_chu    = Column(Text, nullable=True)
    # File đính kèm
    file_path  = Column(String(500), nullable=True)   # đường dẫn tuyệt đối trên server
    file_name  = Column(String(255), nullable=True)   # tên file gốc
    file_size  = Column(BigInteger, nullable=True)    # byte
    mime_type  = Column(String(100), nullable=True)
    cap_nhat   = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    student = relationship("Student", back_populates="documents")


# Danh sách mặc định để seed — không còn dùng để lọc trong service
LOAI_GIAY_DEFAULT = [
    ("CCCD/CMND",              True,  "Bản photo công chứng",             1),
    ("Giấy khai sinh",         True,  "Bản photo công chứng",             2),
    ("Học bạ THPT",            True,  "Bản photo có xác nhận",            3),
    ("Bằng tốt nghiệp THPT",   True,  "Bản photo công chứng hoặc bản gốc",4),
    ("Ảnh thẻ 3x4",            True,  "4 ảnh màu nền trắng",              5),
    ("Sổ hộ khẩu",             True,  "Bản photo công chứng",             6),
]
