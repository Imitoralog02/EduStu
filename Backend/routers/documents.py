from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional
import os

from database import get_db
from dependencies import admin_or_phongdt, all_roles
from schemas.document import (
    DocumentOut, DocumentUpdate, StudentDocSummary,
    DocumentTypeOut, DocumentTypeCreate, DocumentTypeUpdate,
)
import services.document_service as svc

router = APIRouter(prefix="/giayto", tags=["Documents"])


# ── DocumentType endpoints ────────────────────────────────────────────────────

@router.get("/loai", response_model=list[DocumentTypeOut])
def get_loai_giay(db: Session = Depends(get_db), _=Depends(all_roles)):
    return svc.list_doc_types(db)


@router.post("/loai", response_model=DocumentTypeOut, status_code=201)
def create_loai(body: DocumentTypeCreate, db: Session = Depends(get_db), _=Depends(admin_or_phongdt)):
    return svc.create_doc_type(db, body.ten_loai, body.bat_buoc, body.mo_ta, body.thu_tu)


@router.put("/loai/{type_id}", response_model=DocumentTypeOut)
def update_loai(type_id: int, body: DocumentTypeUpdate, db: Session = Depends(get_db), _=Depends(admin_or_phongdt)):
    return svc.update_doc_type(db, type_id, body.model_dump(exclude_none=True))


@router.delete("/loai/{type_id}")
def delete_loai(type_id: int, db: Session = Depends(get_db), _=Depends(admin_or_phongdt)):
    return svc.delete_doc_type(db, type_id)


# ── StudentDocument endpoints ─────────────────────────────────────────────────

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


@router.post("/{doc_id}/upload", response_model=DocumentOut)
async def upload_file(
    doc_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _=Depends(admin_or_phongdt),
):
    return await svc.upload_doc_file(db, doc_id, file)


@router.delete("/{doc_id}/file", response_model=DocumentOut)
def delete_file(doc_id: int, db: Session = Depends(get_db), _=Depends(admin_or_phongdt)):
    return svc.delete_doc_file(db, doc_id)


@router.get("/{doc_id}/file")
def get_file(doc_id: int, db: Session = Depends(get_db), _=Depends(all_roles)):
    from models.document import StudentDocument
    doc = db.query(StudentDocument).filter(StudentDocument.id == doc_id).first()
    if not doc or not doc.file_path:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Không có file đính kèm")
    if not os.path.exists(doc.file_path):
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="File không tồn tại trên server")
    return FileResponse(
        path=doc.file_path,
        media_type=doc.mime_type or "application/octet-stream",
        filename=doc.file_name or "file",
    )


@router.get("/{doc_id}/file_bytes")
def get_file_bytes(doc_id: int, db: Session = Depends(get_db), _=Depends(all_roles)):
    """Trả về raw bytes với Bearer token — dùng cho desktop client."""
    from fastapi import HTTPException
    from fastapi.responses import Response
    from models.document import StudentDocument
    doc = db.query(StudentDocument).filter(StudentDocument.id == doc_id).first()
    if not doc or not doc.file_path:
        raise HTTPException(status_code=404, detail="Không có file đính kèm")
    if not os.path.exists(doc.file_path):
        raise HTTPException(status_code=404, detail="File không tồn tại trên server")
    with open(doc.file_path, "rb") as f:
        data = f.read()
    return Response(
        content=data,
        media_type=doc.mime_type or "application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{doc.file_name or "file"}"'},
    )
