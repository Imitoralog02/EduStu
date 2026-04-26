from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from database import Base


class Course(Base):
    __tablename__ = "courses"

    ma_hp = Column(String(20), primary_key=True)
    ten_hp = Column(String(200), nullable=False)
    so_tin_chi = Column(Integer, default=3, nullable=False)
    giao_vien = Column(String(100), nullable=True)
    hoc_ky = Column(String(20), nullable=True)

    grades = relationship("Grade", back_populates="course", cascade="all, delete-orphan")
