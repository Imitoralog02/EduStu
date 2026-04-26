from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException

from models.course import Course


# ── Courses ───────────────────────────────────────────────────────────────────

def list_courses(db: Session, search: Optional[str]) -> list:
    q = db.query(Course)
    if search:
        q = q.filter(
            Course.ma_hp.ilike(f"%{search}%") | Course.ten_hp.ilike(f"%{search}%")
        )
    return q.all()


def create_course(db: Session, data: dict) -> Course:
    if db.query(Course).filter(Course.ma_hp == data["ma_hp"]).first():
        raise HTTPException(status_code=400, detail="Mã học phần đã tồn tại")
    course = Course(**data)
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


def update_course(db: Session, ma_hp: str, data: dict) -> Course:
    course = db.query(Course).filter(Course.ma_hp == ma_hp).first()
    if not course:
        raise HTTPException(status_code=404, detail="Không tìm thấy học phần")
    for field, value in data.items():
        setattr(course, field, value)
    db.commit()
    db.refresh(course)
    return course


def delete_course(db: Session, ma_hp: str) -> dict:
    course = db.query(Course).filter(Course.ma_hp == ma_hp).first()
    if not course:
        raise HTTPException(status_code=404, detail="Không tìm thấy học phần")
    db.delete(course)
    db.commit()
    return {"message": f"Đã xóa học phần {ma_hp}"}

