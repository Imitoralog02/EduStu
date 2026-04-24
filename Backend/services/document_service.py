from sqlalchemy.orm import Session
from fastapi import HTTPException

from models.document import StudentDocument, LOAI_GIAY_YEU_CAU
from models.student import Student


def _ensure_docs_exist(db: Session, mssv: str) -> None:
    """Tự động tạo đủ bản ghi cho mỗi loại giấy tờ nếu chưa có."""
    existing = {d.loai_giay for d in db.query(StudentDocument).filter(StudentDocument.mssv == mssv).all()}
    for loai in LOAI_GIAY_YEU_CAU:
        if loai not in existing:
            db.add(StudentDocument(mssv=mssv, loai_giay=loai, da_nop=False))
    db.commit()


def get_docs(db: Session, mssv: str) -> list:
    if not db.query(Student).filter(Student.mssv == mssv).first():
        raise HTTPException(status_code=404, detail="Không tìm thấy sinh viên")
    _ensure_docs_exist(db, mssv)
    return db.query(StudentDocument).filter(StudentDocument.mssv == mssv).order_by(StudentDocument.loai_giay).all()


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


def get_summary(db: Session) -> list:
    """Danh sách tất cả sinh viên kèm trạng thái giấy tờ."""
    students = db.query(Student).order_by(Student.khoa, Student.ho_ten).all()
    result = []
    for sv in students:
        _ensure_docs_exist(db, sv.mssv)
        docs = db.query(StudentDocument).filter(StudentDocument.mssv == sv.mssv).all()
        da_nop  = sum(1 for d in docs if d.da_nop)
        tong    = len(LOAI_GIAY_YEU_CAU)
        result.append({
            "mssv":       sv.mssv,
            "ho_ten":     sv.ho_ten,
            "khoa":       sv.khoa,
            "lop":        sv.lop,
            "tong":       tong,
            "da_nop":     da_nop,
            "con_thieu":  tong - da_nop,
            "hoan_chinh": da_nop >= tong,
        })
    return result


def get_missing_summary(db: Session) -> dict:
    """Tổng hợp cho dashboard: số SV còn thiếu giấy tờ."""
    summary = get_summary(db)
    thieu   = [s for s in summary if not s["hoan_chinh"]]
    return {
        "tong_sv":    len(summary),
        "thieu_giay": len(thieu),
        "ds_thieu":   thieu[:10],
    }
