from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException

from models.course import Course
from models.enrollment import Enrollment


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


# ── Enrollments ───────────────────────────────────────────────────────────────

def get_enrollments(db: Session, mssv: str, hoc_ky: Optional[str]) -> list:
    q = (
        db.query(Enrollment, Course.ten_hp)
        .join(Course, Enrollment.ma_hp == Course.ma_hp)
        .filter(Enrollment.mssv == mssv)
    )
    if hoc_ky:
        q = q.filter(Enrollment.hoc_ky == hoc_ky)
    return [
        {"id": e.id, "mssv": e.mssv, "ma_hp": e.ma_hp, "ten_hp": ten_hp, "hoc_ky": e.hoc_ky}
        for e, ten_hp in q.all()
    ]


def create_enrollment(db: Session, data: dict) -> dict:
    if db.query(Enrollment).filter(
        Enrollment.mssv == data["mssv"],
        Enrollment.ma_hp == data["ma_hp"],
        Enrollment.hoc_ky == data["hoc_ky"],
    ).first():
        raise HTTPException(status_code=400, detail="Sinh viên đã đăng ký học phần này")

    course = db.query(Course).filter(Course.ma_hp == data["ma_hp"]).first()
    if not course:
        raise HTTPException(status_code=404, detail="Không tìm thấy học phần")

    enrollment = Enrollment(**data)
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    return {
        "id": enrollment.id, "mssv": enrollment.mssv,
        "ma_hp": enrollment.ma_hp, "ten_hp": course.ten_hp, "hoc_ky": enrollment.hoc_ky,
    }


def cancel_enrollment(db: Session, enrollment_id: int) -> dict:
    e = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
    if not e:
        raise HTTPException(status_code=404, detail="Không tìm thấy đăng ký")
    db.delete(e)
    db.commit()
    return {"message": "Đã hủy đăng ký"}
