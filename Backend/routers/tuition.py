from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from dependencies import admin_or_phongdt
from schemas.tuition import TuitionOut, PaymentRequest, PaymentResponse
import services.tuition_service as svc

router = APIRouter(prefix="/hocphi", tags=["Tuition"])


@router.get("", response_model=list[TuitionOut])
def list_tuition(
    search: Optional[str] = None,
    trang_thai: Optional[str] = None,
    db: Session = Depends(get_db),
    _=Depends(admin_or_phongdt),
):
    return svc.list_tuition(db, search, trang_thai)


@router.get("/conno", response_model=list[TuitionOut])
def list_debts(db: Session = Depends(get_db), _=Depends(admin_or_phongdt)):
    return svc.list_debts(db)


@router.put("/miengiam/{mssv}")
def update_mien_giam(
    mssv: str,
    mien_giam: float = 0.0,
    ly_do: Optional[str] = None,
    db: Session = Depends(get_db),
    _=Depends(admin_or_phongdt),
):
    return svc.update_mien_giam(db, mssv, mien_giam, ly_do)


@router.get("/lichsu/{mssv}")
def get_payment_history(mssv: str, db: Session = Depends(get_db), _=Depends(admin_or_phongdt)):
    return svc.get_payment_history(db, mssv)


@router.post("/thanhtoan", response_model=PaymentResponse)
def record_payment(body: PaymentRequest, db: Session = Depends(get_db), _=Depends(admin_or_phongdt)):
    result = svc.record_payment(db, body.mssv, body.so_tien, body.phuong_thuc, body.ghi_chu)
    return PaymentResponse(**result)
