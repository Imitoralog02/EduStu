from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException

from models.student import Student
from models.grade import Grade
from models.course import Course
from utils.grade_calc import calc_tong_ket


def _batch_gpa(db: Session, mssv_list: list[str]) -> dict[str, Optional[float]]:
    if not mssv_list:
        return {}
    rows = (
        db.query(Grade, Course.so_tin_chi)
        .join(Course, Grade.ma_hp == Course.ma_hp)
        .filter(Grade.mssv.in_(mssv_list))
        .all()
    )
    data: dict[str, tuple[float, int]] = {}
    for grade, tc in rows:
        tong = calc_tong_ket(grade.diem_gk, grade.diem_ck)
        if tong is not None:
            prev = data.get(grade.mssv, (0.0, 0))
            data[grade.mssv] = (prev[0] + tong * tc, prev[1] + tc)

    return {
        mssv: (round(data[mssv][0] / data[mssv][1], 2) if data.get(mssv, (0, 0))[1] > 0 else None)
        for mssv in mssv_list
    }


def _compute_gpa(db: Session, mssv: str) -> Optional[float]:
    return _batch_gpa(db, [mssv]).get(mssv)


def _to_out(student: Student, gpa: Optional[float] = None) -> dict:
    data = {c.name: getattr(student, c.name) for c in student.__table__.columns}
    data["ngay_sinh"] = str(data["ngay_sinh"]) if data.get("ngay_sinh") else None
    data["gpa"] = gpa
    return data


def list_students(
    db: Session,
    search: Optional[str],
    khoa: Optional[str],
    trang_thai: Optional[str],
    lop: Optional[str],
    page: int,
    page_size: int,
) -> dict:
    q = db.query(Student)
    if search:
        q = q.filter(
            or_(Student.mssv.ilike(f"%{search}%"), Student.ho_ten.ilike(f"%{search}%"))
        )
    if khoa:
        q = q.filter(Student.khoa == khoa)
    if trang_thai:
        q = q.filter(Student.trang_thai == trang_thai)
    if lop:
        q = q.filter(Student.lop.ilike(f"%{lop}%"))

    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    gpa_map = _batch_gpa(db, [sv.mssv for sv in items])
    return {"items": [_to_out(sv, gpa_map.get(sv.mssv)) for sv in items], "total": total}


def get_student(db: Session, mssv: str) -> dict:
    sv = db.query(Student).filter(Student.mssv == mssv).first()
    if not sv:
        raise HTTPException(status_code=404, detail="Không tìm thấy sinh viên")
    return _to_out(sv, _compute_gpa(db, mssv))


def create_student(db: Session, data: dict) -> dict:
    if db.query(Student).filter(Student.mssv == data["mssv"]).first():
        raise HTTPException(status_code=400, detail="MSSV đã tồn tại")
    sv = Student(**data)
    db.add(sv)
    db.commit()
    db.refresh(sv)
    return _to_out(sv, None)


def update_student(db: Session, mssv: str, data: dict) -> dict:
    sv = db.query(Student).filter(Student.mssv == mssv).first()
    if not sv:
        raise HTTPException(status_code=404, detail="Không tìm thấy sinh viên")
    for field, value in data.items():
        setattr(sv, field, value)
    db.commit()
    db.refresh(sv)
    return _to_out(sv, _compute_gpa(db, mssv))


def delete_student(db: Session, mssv: str) -> dict:
    sv = db.query(Student).filter(Student.mssv == mssv).first()
    if not sv:
        raise HTTPException(status_code=404, detail="Không tìm thấy sinh viên")
    sv.trang_thai = "Thôi học"
    db.commit()
    return {"message": f"Đã cập nhật trạng thái sinh viên {mssv} thành 'Thôi học'"}
