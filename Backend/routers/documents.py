from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from database import get_db
from dependencies import admin_or_phongdt, all_roles
from schemas.document import DocumentOut, DocumentUpdate, StudentDocSummary
from models.document import LOAI_GIAY_YEU_CAU
import services.document_service as svc

router = APIRouter(prefix="/giayto", tags=["Documents"])


@router.get("/loai")
def get_loai_giay():
    return LOAI_GIAY_YEU_CAU


@router.get("/summary", response_model=list[StudentDocSummary])
def get_summary(db: Session = Depends(get_db), _=Depends(admin_or_phongdt)):
    return svc.get_summary(db)


@router.get("/thongbao")
def get_missing(db: Session = Depends(get_db), _=Depends(all_roles)):
    return svc.get_missing_summary(db)


@router.get("/{mssv}", response_model=list[DocumentOut])
def get_docs(mssv: str, db: Session = Depends(get_db), _=Depends(all_roles)):
    return svc.get_docs(db, mssv)


@router.put("/{doc_id}", response_model=DocumentOut)
def update_doc(doc_id: int, body: DocumentUpdate, db: Session = Depends(get_db), _=Depends(admin_or_phongdt)):
    return svc.update_doc(db, doc_id, body.da_nop, body.ngay_nop, body.ghi_chu)
