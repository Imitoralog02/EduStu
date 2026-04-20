from sqlalchemy import Column, Integer, String, Float, Date, Enum, Text, ForeignKey, TIMESTAMP, func
from sqlalchemy.orm import relationship
from database import Base


class Tuition(Base):
    __tablename__ = "tuition"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    mssv            = Column(String(20), ForeignKey("students.mssv", ondelete="CASCADE"), unique=True, nullable=False)
    phai_nop        = Column(Float, default=0.0)
    mien_giam       = Column(Float, default=0.0)
    ly_do_mien_giam = Column(Text, nullable=True)
    da_nop          = Column(Float, default=0.0)
    han_nop         = Column(Date, nullable=True)
    ghi_chu         = Column(Text, nullable=True)

    student = relationship("Student", back_populates="tuition")
    payment_logs = relationship("PaymentLog", back_populates="tuition_record", cascade="all, delete-orphan")


class PaymentLog(Base):
    __tablename__ = "payment_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tuition_id = Column(Integer, ForeignKey("tuition.id", ondelete="CASCADE"), nullable=False)
    mssv = Column(String(20), nullable=False)
    so_tien = Column(Float, nullable=False)
    phuong_thuc = Column(Enum("Tiền mặt", "Chuyển khoản", "Thẻ", "MoMo"), nullable=False)
    ghi_chu = Column(Text, nullable=True)
    ngay_nop = Column(TIMESTAMP, server_default=func.now())

    tuition_record = relationship("Tuition", back_populates="payment_logs")
