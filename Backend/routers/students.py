from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import Optional
import pandas as pd
import io

from database import get_db
from dependencies import admin_or_phongdt, get_current_user
from models.student import Student
from models.grade import Grade
from models.course import Course
from schemas.student import StudentCreate, StudentUpdate, StudentOut, StudentListResponse
from utils.grade_calc import calc_tong_ket

router = APIRouter(prefix="/sinhvien", tags=["Students"])


def _compute_gpa(db: Session, mssv: str) -> Optional[float]:
    grades = db.query(Grade, Course.so_tin_chi).join(
        Course, Grade.ma_hp == Course.ma_hp
    ).filter(Grade.mssv == mssv).all()

    total_credits = 0
    weighted = 0.0
    for grade, tc in grades:
        tong = calc_tong_ket(grade.diem_gk, grade.diem_ck)
        if tong is not None:
            weighted += tong * tc
            total_credits += tc
    if total_credits == 0:
        return None
    return round(weighted / total_credits, 2)


def _to_out(student: Student, db: Session) -> dict:
    data = {c.name: getattr(student, c.name) for c in student.__table__.columns}
    data["ngay_sinh"] = str(data["ngay_sinh"]) if data.get("ngay_sinh") else None
    data["gpa"] = _compute_gpa(db, student.mssv)
    return data


@router.get("", response_model=StudentListResponse)
def list_students(
    search: Optional[str] = None,
    khoa: Optional[str] = None,
    trang_thai: Optional[str] = None,
    lop: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _=Depends(admin_or_phongdt),
):
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
    return {"items": [_to_out(sv, db) for sv in items], "total": total}


@router.get("/{mssv}", response_model=StudentOut)
def get_student(mssv: str, db: Session = Depends(get_db), _=Depends(admin_or_phongdt)):
    sv = db.query(Student).filter(Student.mssv == mssv).first()
    if not sv:
        raise HTTPException(status_code=404, detail="Không tìm thấy sinh viên")
    return _to_out(sv, db)


@router.post("", response_model=StudentOut, status_code=201)
def create_student(body: StudentCreate, db: Session = Depends(get_db), _=Depends(admin_or_phongdt)):
    if db.query(Student).filter(Student.mssv == body.mssv).first():
        raise HTTPException(status_code=400, detail="MSSV đã tồn tại")
    sv = Student(**body.model_dump())
    db.add(sv)
    db.commit()
    db.refresh(sv)
    return _to_out(sv, db)


@router.put("/{mssv}", response_model=StudentOut)
def update_student(
    mssv: str, body: StudentUpdate, db: Session = Depends(get_db), _=Depends(admin_or_phongdt)
):
    sv = db.query(Student).filter(Student.mssv == mssv).first()
    if not sv:
        raise HTTPException(status_code=404, detail="Không tìm thấy sinh viên")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(sv, field, value)
    db.commit()
    db.refresh(sv)
    return _to_out(sv, db)


@router.delete("/{mssv}")
def soft_delete_student(mssv: str, db: Session = Depends(get_db), _=Depends(admin_or_phongdt)):
    sv = db.query(Student).filter(Student.mssv == mssv).first()
    if not sv:
        raise HTTPException(status_code=404, detail="Không tìm thấy sinh viên")
    sv.trang_thai = "Thôi học"
    db.commit()
    return {"message": f"Đã cập nhật trạng thái sinh viên {mssv} thành 'Thôi học'"}


@router.post("/import")
async def import_students(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _=Depends(admin_or_phongdt),
):
    content = await file.read()
    try:
        df = pd.read_excel(io.BytesIO(content))
    except Exception:
        raise HTTPException(status_code=400, detail="File không hợp lệ")

    count = 0
    errors = []
    for i, row in df.iterrows():
        try:
            mssv = str(row.get("mssv", "")).strip()
            if not mssv:
                errors.append(f"Dòng {i+2}: thiếu MSSV")
                continue
            if db.query(Student).filter(Student.mssv == mssv).first():
                errors.append(f"Dòng {i+2}: MSSV {mssv} đã tồn tại")
                continue
            sv = Student(
                mssv=mssv,
                ho_ten=str(row.get("ho_ten", "")).strip(),
                khoa=str(row.get("khoa", "")).strip() or None,
                lop=str(row.get("lop", "")).strip() or None,
                trang_thai="Đang học",
            )
            db.add(sv)
            count += 1
        except Exception as e:
            errors.append(f"Dòng {i+2}: {str(e)}")
    db.commit()
    return {"count": count, "errors": errors}
