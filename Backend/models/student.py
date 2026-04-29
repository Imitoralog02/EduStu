from sqlalchemy import Column, String, Date, Enum, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class StudentStatusLog(Base):
    """Lịch sử thay đổi trạng thái sinh viên."""
    __tablename__ = "student_status_logs"

    id             = Column(Integer, primary_key=True, autoincrement=True)
    mssv           = Column(String(20), ForeignKey("students.mssv", ondelete="CASCADE"), nullable=False)
    trang_thai_cu  = Column(String(50), nullable=True)
    trang_thai_moi = Column(String(50), nullable=False)
    ly_do          = Column(Text, nullable=True)
    nguoi_thay_doi = Column(String(100), nullable=True)
    thoi_gian      = Column(DateTime, server_default=func.now(), nullable=False)

    student = relationship("Student", back_populates="status_logs")


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
    status_logs = relationship("StudentStatusLog", back_populates="student", cascade="all, delete-orphan",
                               order_by="StudentStatusLog.thoi_gian.desc()")
