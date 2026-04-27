import os
import shutil
from pathlib import Path
from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile

from models.document import StudentDocument, DocumentType
from models.student import Student

UPLOAD_DIR = Path(__file__).parent.parent / "uploads" / "documents"


def _get_active_types(db: Session) -> list[DocumentType]:
    return db.query(DocumentType).order_by(DocumentType.thu_tu, DocumentType.ten_loai).all()


def _ensure_docs_exist(db: Session, mssv: str) -> None:
    """Tự động tạo bản ghi cho mỗi loại giấy tờ trong DocumentType nếu chưa có."""
    types = _get_active_types(db)
    existing = {d.loai_giay for d in db.query(StudentDocument).filter(StudentDocument.mssv == mssv).all()}
    for dt in types:
        if dt.ten_loai not in existing:
            db.add(StudentDocument(mssv=mssv, loai_giay=dt.ten_loai, da_nop=False))
    db.commit()


# ── DocumentType CRUD ─────────────────────────────────────────────────────────

def list_doc_types(db: Session) -> list:
    return _get_active_types(db)


def create_doc_type(db: Session, ten_loai: str, bat_buoc: bool, mo_ta: str | None, thu_tu: int) -> DocumentType:
    if db.query(DocumentType).filter(DocumentType.ten_loai == ten_loai).first():
        raise HTTPException(status_code=409, detail=f"Loại giấy '{ten_loai}' đã tồn tại")
    dt = DocumentType(ten_loai=ten_loai, bat_buoc=bat_buoc, mo_ta=mo_ta, thu_tu=thu_tu)
    db.add(dt)
    db.commit()
    db.refresh(dt)
    return dt


def update_doc_type(db: Session, type_id: int, data: dict) -> DocumentType:
    dt = db.query(DocumentType).filter(DocumentType.id == type_id).first()
    if not dt:
        raise HTTPException(status_code=404, detail="Không tìm thấy loại giấy tờ")
    # Kiểm tra trùng tên nếu đổi tên
    new_name = data.get("ten_loai")
    if new_name and new_name != dt.ten_loai:
        if db.query(DocumentType).filter(DocumentType.ten_loai == new_name).first():
            raise HTTPException(status_code=409, detail=f"Loại giấy '{new_name}' đã tồn tại")
    for k, v in data.items():
        setattr(dt, k, v)
    db.commit()
    db.refresh(dt)
    return dt


def delete_doc_type(db: Session, type_id: int) -> dict:
    dt = db.query(DocumentType).filter(DocumentType.id == type_id).first()
    if not dt:
        raise HTTPException(status_code=404, detail="Không tìm thấy loại giấy tờ")
    # Xóa document records liên quan
    db.query(StudentDocument).filter(StudentDocument.loai_giay == dt.ten_loai).delete()
    db.delete(dt)
    db.commit()
    return {"message": f"Đã xóa loại giấy '{dt.ten_loai}'"}


# ── StudentDocument ───────────────────────────────────────────────────────────

def get_docs(db: Session, mssv: str) -> list:
    if not db.query(Student).filter(Student.mssv == mssv).first():
        raise HTTPException(status_code=404, detail="Không tìm thấy sinh viên")
    _ensure_docs_exist(db, mssv)
    return (
        db.query(StudentDocument)
        .filter(StudentDocument.mssv == mssv)
        .order_by(StudentDocument.loai_giay)
        .all()
    )


def update_doc(db: Session, doc_id: int, da_nop: bool, ngay_nop, ghi_chu) -> StudentDocument:
    doc = db.query(StudentDocument).filter(StudentDocument.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Không tìm thấy giấy tờ")
    doc.da_nop   = da_nop
    doc.ngay_nop = ngay_nop
    doc.ghi_chu  = ghi_chu
    db.commit()
    db.refresh(doc)
    return doc


async def upload_doc_file(db: Session, doc_id: int, file: UploadFile) -> StudentDocument:
    doc = db.query(StudentDocument).filter(StudentDocument.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Không tìm thấy giấy tờ")

    # Kiểm tra định dạng
    allowed = {"application/pdf", "image/jpeg", "image/png", "image/jpg"}
    if file.content_type not in allowed:
        raise HTTPException(status_code=400, detail="Chỉ hỗ trợ PDF, JPG, PNG")

    # Tạo thư mục lưu file
    save_dir = UPLOAD_DIR / doc.mssv
    save_dir.mkdir(parents=True, exist_ok=True)

    # Xóa file cũ nếu có
    if doc.file_path and os.path.exists(doc.file_path):
        os.remove(doc.file_path)

    # Tên file an toàn
    ext = Path(file.filename).suffix.lower()
    safe_name = f"{doc_id}_{doc.loai_giay.replace('/', '_').replace(' ', '_')}{ext}"
    save_path = save_dir / safe_name

    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    file_size = os.path.getsize(save_path)
    doc.file_path = str(save_path)
    doc.file_name = file.filename
    doc.file_size = file_size
    doc.mime_type = file.content_type
    db.commit()
    db.refresh(doc)
    return doc


def delete_doc_file(db: Session, doc_id: int) -> StudentDocument:
    doc = db.query(StudentDocument).filter(StudentDocument.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Không tìm thấy giấy tờ")
    if doc.file_path and os.path.exists(doc.file_path):
        os.remove(doc.file_path)
    doc.file_path = None
    doc.file_name = None
    doc.file_size = None
    doc.mime_type = None
    db.commit()
    db.refresh(doc)
    return doc


def get_summary(db: Session) -> list:
    students  = db.query(Student).order_by(Student.khoa, Student.ho_ten).all()
    types     = _get_active_types(db)
    type_names = {dt.ten_loai for dt in types}
    tong      = len(types)

    # Một lần query toàn bộ documents, nhóm theo mssv
    all_docs = db.query(StudentDocument).all()
    docs_by_mssv: dict[str, list[StudentDocument]] = {}
    for d in all_docs:
        docs_by_mssv.setdefault(d.mssv, []).append(d)

    # Tạo bản ghi còn thiếu cho tất cả sinh viên trong một batch
    new_records = []
    for sv in students:
        existing = {d.loai_giay for d in docs_by_mssv.get(sv.mssv, [])}
        for name in type_names:
            if name not in existing:
                rec = StudentDocument(mssv=sv.mssv, loai_giay=name, da_nop=False)
                new_records.append(rec)
                docs_by_mssv.setdefault(sv.mssv, []).append(rec)
    if new_records:
        db.add_all(new_records)
        db.commit()

    result = []
    for sv in students:
        docs   = docs_by_mssv.get(sv.mssv, [])
        da_nop = sum(1 for d in docs if d.da_nop)
        result.append({
            "mssv":       sv.mssv,
            "ho_ten":     sv.ho_ten,
            "khoa":       sv.khoa,
            "lop":        sv.lop,
            "tong":       tong,
            "da_nop":     da_nop,
            "con_thieu":  max(0, tong - da_nop),
            "hoan_chinh": da_nop >= tong,
        })
    return result


def get_missing_summary(db: Session) -> dict:
    summary = get_summary(db)
    thieu   = [s for s in summary if not s["hoan_chinh"]]
    return {"tong_sv": len(summary), "thieu_giay": len(thieu), "ds_thieu": thieu[:10]}
