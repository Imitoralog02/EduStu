from sqlalchemy import Column, String, Date, Enum, Integer
from sqlalchemy.orm import relationship
from database import Base


class Student(Base):
    __tablename__ = "students"

    mssv = Column(String(20), primary_key=True)
    ho_ten = Column(String(100), nullable=False)
    ngay_sinh = Column(Date, nullable=True)
    gioi_tinh = Column(String(10), nullable=True)
    lop = Column(String(50), nullable=True)
    khoa = Column(String(100), nullable=True)
    email = Column(String(100), nullable=True)
    so_dien_thoai = Column(String(20), nullable=True)
    dia_chi = Column(String(500), nullable=True)
    trang_thai = Column(
        Enum("Đang học", "Bảo lưu", "Thôi học", "Cảnh báo"),
        default="Đang học",
        nullable=False,
    )
    # Thông tin hồ sơ mở rộng
    nam_nhap_hoc = Column(Integer, nullable=True)
    doi_tuong = Column(String(100), nullable=True)   # Đối tượng ưu tiên
    ho_ten_cha = Column(String(100), nullable=True)
    ho_ten_me = Column(String(100), nullable=True)
    sdt_phu_huynh = Column(String(20), nullable=True)

    grades      = relationship("Grade", back_populates="student", cascade="all, delete-orphan")
    tuition     = relationship("Tuition", back_populates="student", uselist=False, cascade="all, delete-orphan")
    documents   = relationship("StudentDocument", back_populates="student", cascade="all, delete-orphan")
