from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date

from models.student import Student
from models.grade import Grade
from models.course import Course
from models.tuition import Tuition
from utils.grade_calc import calc_tong_ket, compute_transcript_stats


def get_dashboard(db: Session) -> dict:
    counts = dict(
        db.query(Student.trang_thai, func.count(Student.mssv))
        .group_by(Student.trang_thai)
        .all()
    )
    tong_sv     = sum(counts.values())
    dang_hoc    = counts.get("Đang học", 0)
    canh_bao_hv = counts.get("Cảnh báo", 0)
    bao_luu     = counts.get("Bảo lưu", 0)
    thoi_hoc    = counts.get("Thôi học", 0)

    no_hoc_phi = db.query(
        func.sum(Tuition.phai_nop - Tuition.da_nop)
    ).filter(Tuition.phai_nop > Tuition.da_nop).scalar() or 0

    tuition_stats = db.query(
        func.sum(Tuition.phai_nop),
        func.sum(Tuition.da_nop),
    ).first()
    tong_phai_nop = tuition_stats[0] or 0
    tong_da_thu   = tuition_stats[1] or 0

    warned = db.query(Student.ho_ten).filter(Student.trang_thai == "Cảnh báo").limit(6).all()

    return {
        "tong_sv": tong_sv,
        "dang_hoc": dang_hoc,
        "canh_bao_hv": canh_bao_hv,
        "bao_luu": bao_luu,
        "thoi_hoc": thoi_hoc,
        "no_hoc_phi": round(no_hoc_phi),
        "tong_phai_nop": round(tong_phai_nop),
        "tong_da_thu": round(tong_da_thu),
        "alerts": [{"ho_ten": row.ho_ten, "mo_ta": "Cảnh báo học vụ"} for row in warned],
    }


def get_statistics(db: Session) -> list:
    sv_rows = (
        db.query(Student.khoa, Student.trang_thai, func.count(Student.mssv))
        .filter(Student.khoa.isnot(None))
        .group_by(Student.khoa, Student.trang_thai)
        .all()
    )
    khoa_stats: dict[str, dict] = {}
    for khoa, tt, cnt in sv_rows:
        if khoa not in khoa_stats:
            khoa_stats[khoa] = {"tong_sv": 0, "dang_hoc": 0, "canh_bao_hv": 0}
        khoa_stats[khoa]["tong_sv"] += cnt
        if tt == "Đang học":
            khoa_stats[khoa]["dang_hoc"] = cnt
        elif tt == "Cảnh báo":
            khoa_stats[khoa]["canh_bao_hv"] = cnt

    grade_rows = (
        db.query(Student.khoa, Grade.diem_gk, Grade.diem_ck, Course.so_tin_chi)
        .join(Grade, Grade.mssv == Student.mssv)
        .join(Course, Course.ma_hp == Grade.ma_hp)
        .filter(Student.khoa.isnot(None))
        .all()
    )
    khoa_grade: dict[str, dict] = {}
    for khoa, diem_gk, diem_ck, tc in grade_rows:
        if khoa not in khoa_grade:
            khoa_grade[khoa] = {"weighted": 0.0, "total_tc": 0, "passed": 0, "total": 0}
        tong = calc_tong_ket(diem_gk, diem_ck)
        if tong is not None:
            khoa_grade[khoa]["weighted"] += tong * tc
            khoa_grade[khoa]["total_tc"] += tc
            khoa_grade[khoa]["total"] += 1
            if tong >= 5.0:
                khoa_grade[khoa]["passed"] += 1

    result = []
    for khoa, stats in khoa_stats.items():
        g = khoa_grade.get(khoa, {})
        total_tc = g.get("total_tc", 0)
        total    = g.get("total", 0)
        result.append({
            "khoa": khoa,
            "tong_sv": stats["tong_sv"],
            "dang_hoc": stats["dang_hoc"],
            "canh_bao_hv": stats["canh_bao_hv"],
            "gpa_tb": round(g["weighted"] / total_tc, 2) if total_tc > 0 else 0.0,
            "ti_le_dat": round(g["passed"] / total * 100, 1) if total > 0 else 0.0,
        })
    return result


def export_data(db: Session, loai: str) -> tuple[bytes, str]:
    from utils.excel import export_students, export_grades, export_debts

    if loai == "sinhvien":
        students = db.query(Student).all()
        data = [{c.name: getattr(sv, c.name) for c in sv.__table__.columns} for sv in students]
        for d in data:
            d["ngay_sinh"] = str(d["ngay_sinh"]) if d.get("ngay_sinh") else None
            d["gpa"] = None
        return export_students(data), "danh_sach_sinh_vien.xlsx"

    if loai == "bangdiem":
        rows = db.query(Grade, Course, Student).join(
            Course, Grade.ma_hp == Course.ma_hp
        ).join(Student, Grade.mssv == Student.mssv).all()
        data = []
        for g, c, sv in rows:
            tong = calc_tong_ket(g.diem_gk, g.diem_ck)
            data.append({
                "mssv": g.mssv, "ho_ten": sv.ho_ten,
                "ma_hp": g.ma_hp, "ten_hp": c.ten_hp,
                "so_tin_chi": c.so_tin_chi, "hoc_ky": g.hoc_ky,
                "diem_gk": g.diem_gk, "diem_ck": g.diem_ck,
                "tong_ket": tong,
                "ket_qua": ("Đạt" if tong >= 5.0 else "Rớt") if tong is not None else None,
            })
        return export_grades(data), "bang_diem.xlsx"

    # conno
    rows = db.query(Tuition, Student).join(Student, Tuition.mssv == Student.mssv).filter(
        Tuition.da_nop < Tuition.phai_nop
    ).all()
    data = [{
        "mssv": t.mssv, "ho_ten": sv.ho_ten,
        "phai_nop": t.phai_nop, "da_nop": t.da_nop,
        "han_nop": str(t.han_nop) if t.han_nop else None,
        "trang_thai": "Quá hạn" if t.han_nop and t.han_nop < date.today() else "Chưa nộp",
    } for t, sv in rows]
    return export_debts(data), "con_no_hoc_phi.xlsx"
