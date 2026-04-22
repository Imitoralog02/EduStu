from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException

from models.grade import Grade
from models.course import Course
from models.student import Student
from utils.grade_calc import calc_tong_ket, is_passed, compute_transcript_stats


def _grade_to_out(grade: Grade, course: Course) -> dict:
    tong = calc_tong_ket(grade.diem_gk, grade.diem_ck)
    dat = is_passed(tong)
    return {
        "id": grade.id,
        "mssv": grade.mssv,
        "ma_hp": grade.ma_hp,
        "ten_hp": course.ten_hp,
        "so_tin_chi": course.so_tin_chi,
        "hoc_ky": grade.hoc_ky,
        "diem_gk": grade.diem_gk,
        "diem_ck": grade.diem_ck,
        "tong_ket": tong,
        "dat": dat,
        "ket_qua": ("Đạt" if dat else "Rớt") if dat is not None else None,
    }


def _update_canh_bao(db: Session, mssv: str) -> None:
    rows = db.query(Grade, Course).join(Course, Grade.ma_hp == Course.ma_hp).filter(Grade.mssv == mssv).all()
    raw = [{"so_tin_chi": c.so_tin_chi, "diem_gk": g.diem_gk, "diem_ck": g.diem_ck} for g, c in rows]
    stats = compute_transcript_stats(raw)
    gpa = stats.get("gpa")
    student = db.query(Student).filter(Student.mssv == mssv).first()
    if not student:
        return
    if gpa is not None and gpa < 1.0 and student.trang_thai == "Đang học":
        student.trang_thai = "Cảnh báo"
        db.commit()
    elif gpa is not None and gpa >= 1.0 and student.trang_thai == "Cảnh báo":
        student.trang_thai = "Đang học"
        db.commit()


def get_transcript(db: Session, mssv: str, hoc_ky: Optional[str]) -> dict:
    if not db.query(Student).filter(Student.mssv == mssv).first():
        raise HTTPException(status_code=404, detail="Không tìm thấy sinh viên")

    q = db.query(Grade, Course).join(Course, Grade.ma_hp == Course.ma_hp).filter(Grade.mssv == mssv)
    if hoc_ky:
        q = q.filter(Grade.hoc_ky == hoc_ky)

    rows = q.all()
    diem_list = [_grade_to_out(g, c) for g, c in rows]
    raw = [{"so_tin_chi": c.so_tin_chi, "diem_gk": g.diem_gk, "diem_ck": g.diem_ck} for g, c in rows]
    stats = compute_transcript_stats(raw)
    return {"diem_list": diem_list, "hoc_ky": hoc_ky or "", **stats}


def get_gpa(db: Session, mssv: str) -> dict:
    rows = db.query(Grade, Course).join(Course, Grade.ma_hp == Course.ma_hp).filter(Grade.mssv == mssv).all()
    raw = [{"so_tin_chi": c.so_tin_chi, "diem_gk": g.diem_gk, "diem_ck": g.diem_ck} for g, c in rows]
    return compute_transcript_stats(raw)


def create_grade(db: Session, data: dict) -> dict:
    if db.query(Grade).filter(
        Grade.mssv == data["mssv"],
        Grade.ma_hp == data["ma_hp"],
        Grade.hoc_ky == data["hoc_ky"],
    ).first():
        raise HTTPException(status_code=400, detail="Điểm học phần này đã tồn tại")

    course = db.query(Course).filter(Course.ma_hp == data["ma_hp"]).first()
    if not course:
        raise HTTPException(status_code=404, detail="Không tìm thấy học phần")

    grade = Grade(**data)
    db.add(grade)
    db.commit()
    db.refresh(grade)
    _update_canh_bao(db, data["mssv"])
    return _grade_to_out(grade, course)


def update_grade(db: Session, grade_id: int, data: dict) -> dict:
    grade = db.query(Grade).filter(Grade.id == grade_id).first()
    if not grade:
        raise HTTPException(status_code=404, detail="Không tìm thấy điểm")
    course = db.query(Course).filter(Course.ma_hp == grade.ma_hp).first()
    for field, value in data.items():
        setattr(grade, field, value)
    db.commit()
    db.refresh(grade)
    _update_canh_bao(db, grade.mssv)
    return _grade_to_out(grade, course)
