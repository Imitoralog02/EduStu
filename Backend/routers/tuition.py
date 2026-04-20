from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import date
from typing import Optional

from database import get_db
from dependencies import admin_or_phongdt
from models.tuition import Tuition, PaymentLog
from models.student import Student
from schemas.tuition import TuitionOut, PaymentRequest, PaymentResponse

router = APIRouter(prefix="/hocphi", tags=["Tuition"])


def _compute_status(tuition: Tuition) -> str:
    thuc_phai_nop = max(0.0, tuition.phai_nop - (tuition.mien_giam or 0.0))
    if tuition.da_nop >= thuc_phai_nop:
        return "Đã nộp"
    if tuition.han_nop and tuition.han_nop < date.today():
        return "Quá hạn"
    if tuition.da_nop > 0:
        return "Nộp thiếu"
    return "Chưa nộp"


def _to_out(tuition: Tuition, student: Student) -> dict:
    mien_giam = tuition.mien_giam or 0.0
    return {
        "mssv": tuition.mssv,
        "ho_ten": student.ho_ten,
        "phai_nop": tuition.phai_nop,
        "mien_giam": mien_giam,
        "ly_do_mien_giam": tuition.ly_do_mien_giam,
        "thuc_phai_nop": max(0.0, tuition.phai_nop - mien_giam),
        "da_nop": tuition.da_nop,
        "han_nop": str(tuition.han_nop) if tuition.han_nop else None,
        "trang_thai": _compute_status(tuition),
        "ghi_chu": tuition.ghi_chu,
    }


@router.get("", response_model=list[TuitionOut])
def list_tuition(
    search: Optional[str] = None,
    trang_thai: Optional[str] = None,
    db: Session = Depends(get_db),
    _=Depends(admin_or_phongdt),
):
    q = db.query(Tuition, Student).join(Student, Tuition.mssv == Student.mssv)
    if search:
        q = q.filter(
            or_(Tuition.mssv.ilike(f"%{search}%"), Student.ho_ten.ilike(f"%{search}%"))
        )
    rows = q.all()
    result = [_to_out(t, sv) for t, sv in rows]
    if trang_thai:
        result = [r for r in result if r["trang_thai"] == trang_thai]
    return result


@router.get("/conno", response_model=list[TuitionOut])
def list_debts(db: Session = Depends(get_db), _=Depends(admin_or_phongdt)):
    rows = db.query(Tuition, Student).join(Student, Tuition.mssv == Student.mssv).all()
    result = [_to_out(t, sv) for t, sv in rows]
    return [r for r in result if r["trang_thai"] != "Đã nộp"]


@router.put("/miengiam/{mssv}")
def update_mien_giam(
    mssv: str,
    mien_giam: float = 0.0,
    ly_do: Optional[str] = None,
    db: Session = Depends(get_db),
    _=Depends(admin_or_phongdt),
):
    tuition = db.query(Tuition).filter(Tuition.mssv == mssv).first()
    if not tuition:
        raise HTTPException(status_code=404, detail="Không tìm thấy thông tin học phí")
    tuition.mien_giam = mien_giam
    tuition.ly_do_mien_giam = ly_do
    db.commit()
    return {"message": "Cập nhật miễn giảm thành công"}


@router.get("/lichsu/{mssv}")
def get_payment_history(
    mssv: str,
    db: Session = Depends(get_db),
    _=Depends(admin_or_phongdt),
):
    tuition = db.query(Tuition).filter(Tuition.mssv == mssv).first()
    if not tuition:
        raise HTTPException(status_code=404, detail="Không tìm thấy thông tin học phí")
    logs = db.query(PaymentLog).filter(PaymentLog.mssv == mssv).order_by(PaymentLog.ngay_nop.desc()).all()
    return [
        {
            "id": log.id,
            "so_tien": log.so_tien,
            "phuong_thuc": log.phuong_thuc,
            "ghi_chu": log.ghi_chu,
            "ngay_nop": str(log.ngay_nop) if log.ngay_nop else None,
        }
        for log in logs
    ]


@router.post("/thanhtoan", response_model=PaymentResponse)
def record_payment(
    body: PaymentRequest,
    db: Session = Depends(get_db),
    _=Depends(admin_or_phongdt),
):
    tuition = db.query(Tuition).filter(Tuition.mssv == body.mssv).first()
    if not tuition:
        raise HTTPException(status_code=404, detail="Không tìm thấy thông tin học phí")

    tuition.da_nop += body.so_tien
    new_status = _compute_status(tuition)

    log = PaymentLog(
        tuition_id=tuition.id,
        mssv=body.mssv,
        so_tien=body.so_tien,
        phuong_thuc=body.phuong_thuc,
        ghi_chu=body.ghi_chu,
    )
    db.add(log)
    db.commit()

    return PaymentResponse(message="Ghi nhận thanh toán thành công", trang_thai_moi=new_status)
