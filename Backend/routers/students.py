from fastapi import APIRouter, Depends, Query, UploadFile, File
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import Optional
import pandas as pd
import io

from database import get_db
from dependencies import admin_or_phongdt, get_current_user
from models.student import Student
from schemas.student import StudentCreate, StudentUpdate, StudentOut, StudentListResponse
import services.student_service as svc

router = APIRouter(prefix="/sinhvien", tags=["Students"])


@router.get("", response_model=StudentListResponse)
def list_students(
    search: Optional[str] = None,
    khoa: Optional[str] = None,
    trang_thai: Optional[str] = None,
    lop: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    nam_nhap_hoc: Optional[int] = None,
    thieu_giay_to: bool = False,
    no_hoc_phi: bool = False,
    db: Session = Depends(get_db),
    _=Depends(admin_or_phongdt),
):
    return svc.list_students(
        db, search, khoa, trang_thai, lop, page, page_size,
        nam_nhap_hoc, thieu_giay_to, no_hoc_phi,
    )


@router.get("/khoa-list")
def get_khoa_list(db: Session = Depends(get_db), _=Depends(admin_or_phongdt)):
    """Trả về danh sách các khoa đang có trong DB (distinct, bỏ null/rỗng, sort A-Z)."""
    rows = db.query(Student.khoa).distinct().all()
    result = sorted({r[0] for r in rows if r[0] and r[0].strip()})
    return result


@router.get("/{mssv}", response_model=StudentOut)
def get_student(mssv: str, db: Session = Depends(get_db), _=Depends(admin_or_phongdt)):
    return svc.get_student(db, mssv)


@router.post("", response_model=StudentOut, status_code=201)
def create_student(body: StudentCreate, db: Session = Depends(get_db), _=Depends(admin_or_phongdt)):
    return svc.create_student(db, body.model_dump())


@router.put("/{mssv}", response_model=StudentOut)
def update_student(mssv: str, body: StudentUpdate, db: Session = Depends(get_db), _=Depends(admin_or_phongdt)):
    return svc.update_student(db, mssv, body.model_dump(exclude_unset=True))


@router.delete("/{mssv}")
def delete_student(mssv: str, db: Session = Depends(get_db), _=Depends(admin_or_phongdt)):
    return svc.delete_student(db, mssv)


@router.get("/{mssv}/export")
def export_student_profile(mssv: str, db: Session = Depends(get_db), _=Depends(admin_or_phongdt)):
    """Xuất hồ sơ cá nhân sinh viên ra Excel (4 sheets)."""
    data = svc.export_student_profile(db, mssv)
    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=hoso_{mssv}.xlsx"},
    )


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
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="File không hợp lệ")

    count, errors = 0, []
    for i, row in df.iterrows():
        try:
            mssv = str(row.get("mssv", "")).strip()
            if not mssv:
                errors.append(f"Dòng {i+2}: thiếu MSSV")
                continue
            if db.query(Student).filter(Student.mssv == mssv).first():
                errors.append(f"Dòng {i+2}: MSSV {mssv} đã tồn tại")
                continue
            db.add(Student(
                mssv=mssv,
                ho_ten=str(row.get("ho_ten", "")).strip(),
                khoa=str(row.get("khoa", "")).strip() or None,
                lop=str(row.get("lop", "")).strip() or None,
                trang_thai="Đang học",
            ))
            count += 1
        except Exception as e:
            errors.append(f"Dòng {i+2}: {str(e)}")
    db.commit()
    return {"count": count, "errors": errors}
