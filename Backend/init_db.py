"""
Script khởi tạo database và dữ liệu mẫu.
Chạy: python init_db.py
"""

from database import engine, Base
import models  # import all models to register them

from sqlalchemy.orm import Session
from models.user import User
from models.student import Student
from models.course import Course
from models.tuition import Tuition
from models.document import DocumentType, LOAI_GIAY_DEFAULT
from utils.security import hash_password
from datetime import date


def create_tables():
    print("Tạo các bảng trong database...")
    Base.metadata.create_all(bind=engine)
    print("Done.")


def seed_users(db: Session):
    if db.query(User).count() > 0:
        print("Bảng users đã có dữ liệu, bỏ qua seed.")
        return

    users = [
        User(username="admin", password_hash=hash_password("admin123"), ho_ten="Quản trị viên", role="admin", email="admin@edustu.vn"),
        User(username="phongdt", password_hash=hash_password("phong123"), ho_ten="Phòng Đào Tạo", role="phongdt", email="phongdt@edustu.vn"),
        User(username="giaovien", password_hash=hash_password("giao123"), ho_ten="Giáo Viên Mẫu", role="giaovien", email="giaovien@edustu.vn"),
    ]
    db.add_all(users)
    db.commit()
    print(f"Đã tạo {len(users)} tài khoản mẫu.")


def seed_students(db: Session):
    if db.query(Student).count() > 0:
        print("Bảng students đã có dữ liệu, bỏ qua seed.")
        return

    students = [
        Student(mssv="SV001", ho_ten="Nguyễn Văn An", ngay_sinh=date(2002, 5, 15), gioi_tinh="Nam",
                lop="CNTT01", khoa="Công nghệ thông tin", email="an.nguyen@sv.edu.vn",
                so_dien_thoai="0912345678", trang_thai="Đang học"),
        Student(mssv="SV002", ho_ten="Trần Thị Bình", ngay_sinh=date(2003, 3, 20), gioi_tinh="Nữ",
                lop="CNTT01", khoa="Công nghệ thông tin", email="binh.tran@sv.edu.vn",
                so_dien_thoai="0987654321", trang_thai="Đang học"),
        Student(mssv="SV003", ho_ten="Lê Minh Cường", ngay_sinh=date(2002, 8, 10), gioi_tinh="Nam",
                lop="KT02", khoa="Kinh tế", email="cuong.le@sv.edu.vn",
                so_dien_thoai="0901234567", trang_thai="Cảnh báo"),
        Student(mssv="SV004", ho_ten="Phạm Thị Dung", ngay_sinh=date(2003, 1, 25), gioi_tinh="Nữ",
                lop="KT02", khoa="Kinh tế", email="dung.pham@sv.edu.vn",
                so_dien_thoai="0978901234", trang_thai="Đang học"),
        Student(mssv="SV005", ho_ten="Hoàng Văn Em", ngay_sinh=date(2001, 12, 5), gioi_tinh="Nam",
                lop="XD03", khoa="Xây dựng", email="em.hoang@sv.edu.vn",
                so_dien_thoai="0956789012", trang_thai="Bảo lưu"),
    ]
    db.add_all(students)
    db.commit()
    print(f"Đã tạo {len(students)} sinh viên mẫu.")


def seed_courses(db: Session):
    if db.query(Course).count() > 0:
        print("Bảng courses đã có dữ liệu, bỏ qua seed.")
        return

    courses = [
        Course(ma_hp="CNTT101", ten_hp="Lập trình Python cơ bản", so_tin_chi=3, giao_vien="Nguyễn Hữu Tài", hoc_ky="2024-1"),
        Course(ma_hp="CNTT102", ten_hp="Cơ sở dữ liệu", so_tin_chi=3, giao_vien="Trần Văn Minh", hoc_ky="2024-1"),
        Course(ma_hp="CNTT103", ten_hp="Mạng máy tính", so_tin_chi=2, giao_vien="Lê Thị Hoa", hoc_ky="2024-2"),
        Course(ma_hp="KT201", ten_hp="Kinh tế vi mô", so_tin_chi=3, giao_vien="Phạm Văn Đức", hoc_ky="2024-1"),
        Course(ma_hp="KT202", ten_hp="Kế toán đại cương", so_tin_chi=2, giao_vien="Hoàng Thị Lan", hoc_ky="2024-1"),
    ]
    db.add_all(courses)
    db.commit()
    print(f"Đã tạo {len(courses)} học phần mẫu.")


def seed_tuition(db: Session):
    if db.query(Tuition).count() > 0:
        print("Bảng tuition đã có dữ liệu, bỏ qua seed.")
        return

    tuitions = [
        Tuition(mssv="SV001", phai_nop=8_400_000, da_nop=8_400_000, han_nop=date(2024, 9, 30)),
        Tuition(mssv="SV002", phai_nop=8_400_000, da_nop=4_200_000, han_nop=date(2024, 9, 30)),
        Tuition(mssv="SV003", phai_nop=7_200_000, da_nop=0, han_nop=date(2024, 9, 30)),
        Tuition(mssv="SV004", phai_nop=8_400_000, da_nop=8_400_000, han_nop=date(2024, 9, 30)),
        Tuition(mssv="SV005", phai_nop=6_000_000, da_nop=2_000_000, han_nop=date(2024, 9, 30)),
    ]
    db.add_all(tuitions)
    db.commit()
    print(f"Đã tạo {len(tuitions)} bản ghi học phí mẫu.")


def seed_doc_types(db: Session):
    if db.query(DocumentType).count() > 0:
        print("Bảng document_types đã có dữ liệu, bỏ qua seed.")
        return
    for ten, bat_buoc, mo_ta, thu_tu in LOAI_GIAY_DEFAULT:
        db.add(DocumentType(ten_loai=ten, bat_buoc=bat_buoc, mo_ta=mo_ta, thu_tu=thu_tu))
    db.commit()
    print(f"Đã tạo {len(LOAI_GIAY_DEFAULT)} loại giấy tờ mặc định.")


if __name__ == "__main__":
    create_tables()
    with Session(engine) as db:
        seed_users(db)
        seed_students(db)
        seed_courses(db)
        seed_tuition(db)
        seed_doc_types(db)
    print("\nKhởi tạo database hoàn tất!")
    print("\nTài khoản mẫu:")
    print("  admin    / admin123  (Quản trị viên)")
    print("  phongdt  / phong123  (Phòng đào tạo)")
    print("  giaovien / giao123   (Giáo viên)")
