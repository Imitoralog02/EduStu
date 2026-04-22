from typing import Optional
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException

from models.tuition import Tuition, PaymentLog
from models.student import Student


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


def list_tuition(db: Session, search: Optional[str], trang_thai: Optional[str]) -> list:
    q = db.query(Tuition, Student).join(Student, Tuition.mssv == Student.mssv)
    if search:
        q = q.filter(
            or_(Tuition.mssv.ilike(f"%{search}%"), Student.ho_ten.ilike(f"%{search}%"))
        )
    result = [_to_out(t, sv) for t, sv in q.all()]
    if trang_thai:
        result = [r for r in result if r["trang_thai"] == trang_thai]
    return result


def list_debts(db: Session) -> list:
    rows = db.query(Tuition, Student).join(Student, Tuition.mssv == Student.mssv).all()
    return [_to_out(t, sv) for t, sv in rows if _compute_status(t) != "Đã nộp"]


def update_mien_giam(db: Session, mssv: str, mien_giam: float, ly_do: Optional[str]) -> dict:
    tuition = db.query(Tuition).filter(Tuition.mssv == mssv).first()
    if not tuition:
        raise HTTPException(status_code=404, detail="Không tìm thấy thông tin học phí")
    tuition.mien_giam = mien_giam
    tuition.ly_do_mien_giam = ly_do
    db.commit()
    return {"message": "Cập nhật miễn giảm thành công"}


def get_payment_history(db: Session, mssv: str) -> list:
    if not db.query(Tuition).filter(Tuition.mssv == mssv).first():
        raise HTTPException(status_code=404, detail="Không tìm thấy thông tin học phí")
    logs = (
        db.query(PaymentLog)
        .filter(PaymentLog.mssv == mssv)
        .order_by(PaymentLog.ngay_nop.desc())
        .all()
    )
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


def record_payment(db: Session, mssv: str, so_tien: float, phuong_thuc: str, ghi_chu: Optional[str]) -> dict:
    tuition = db.query(Tuition).filter(Tuition.mssv == mssv).first()
    if not tuition:
        raise HTTPException(status_code=404, detail="Không tìm thấy thông tin học phí")
    tuition.da_nop += so_tien
    new_status = _compute_status(tuition)
    log = PaymentLog(
        tuition_id=tuition.id,
        mssv=mssv,
        so_tien=so_tien,
        phuong_thuc=phuong_thuc,
        ghi_chu=ghi_chu,
    )
    db.add(log)
    db.commit()
    return {"message": "Ghi nhận thanh toán thành công", "trang_thai_moi": new_status}
