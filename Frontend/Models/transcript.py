from __future__ import annotations
from dataclasses import dataclass, field
from models.grade import Grade
from models.student import Student


@dataclass
class Transcript:
    """
    Bảng điểm tổng hợp của một sinh viên.
    Chứa danh sách Grade và tính toán GPA, xếp loại, cảnh báo học vụ.

    Tạo từ JSON trả về bởi GET /diem/{mssv}.
    """
    student:    Student
    grades:     list[Grade]    = field(default_factory=list)
    hoc_ky:     str            = ""     # rỗng = tất cả học kỳ

    # ------------------------------------------------------------------
    # Computed properties — GPA
    # ------------------------------------------------------------------

    @property
    def grades_passed(self) -> list[Grade]:
        """Danh sách môn đã đạt."""
        return [g for g in self.grades if g.dat]

    @property
    def grades_failed(self) -> list[Grade]:
        """Danh sách môn rớt."""
        return [g for g in self.grades if not g.dat]

    @property
    def tin_chi_dang_ky(self) -> int:
        """Tổng tín chỉ đã đăng ký."""
        return sum(g.so_tin_chi for g in self.grades)

    @property
    def tin_chi_dat(self) -> int:
        """Tổng tín chỉ đã đạt."""
        return sum(g.so_tin_chi for g in self.grades if g.dat)

    @property
    def gpa_ky(self) -> float | None:
        """
        GPA học kỳ = Σ(điểm_tổng_kết × tín_chỉ) / Σtín_chỉ
        Chỉ tính các môn trong học kỳ hiện tại.
        """
        grades = self.grades
        if not grades:
            return None
        total_tc = sum(g.so_tin_chi for g in grades)
        if total_tc == 0:
            return None
        total_diem = sum(g.tong_ket * g.so_tin_chi for g in grades)
        return round(total_diem / total_tc, 2)

    @property
    def gpa_tich_luy(self) -> float | None:
        """
        GPA tích lũy = Σ(điểm_tổng_kết × tín_chỉ) / Σtín_chỉ
        Tính trên toàn bộ các môn đã học.
        Nếu đang xem theo kỳ cụ thể thì bằng gpa_ky.
        """
        return self.gpa_ky

    @property
    def xep_loai(self) -> str:
        """
        Xếp loại học lực theo GPA tích lũy:
            >= 8.5  → Xuất sắc
            >= 7.0  → Giỏi
            >= 5.5  → Khá
            >= 4.0  → Trung bình
            <  4.0  → Yếu
        """
        gpa = self.gpa_tich_luy
        if gpa is None:
            return "—"
        if gpa >= 8.5:
            return "Xuất sắc"
        if gpa >= 7.0:
            return "Giỏi"
        if gpa >= 5.5:
            return "Khá"
        if gpa >= 4.0:
            return "Trung bình"
        return "Yếu"

    @property
    def canh_bao(self) -> str:
        """
        Cảnh báo học vụ theo QĐ 43/2007/QĐ-BGDĐT:
            GPA < 1.0  → Cảnh báo lần 1
            GPA < 0.8  → Cảnh báo lần 2 (nguy cơ buộc thôi học)
            GPA >= 1.0 → Không có cảnh báo (trả về chuỗi rỗng)
        """
        gpa = self.gpa_tich_luy
        if gpa is None:
            return ""
        if gpa < 0.8:
            return "Cảnh báo lần 2"
        if gpa < 1.0:
            return "Cảnh báo lần 1"
        return ""

    @property
    def gpa_display(self) -> str:
        gpa = self.gpa_tich_luy
        return f"{gpa:.2f}" if gpa is not None else "—"

    @property
    def gpa_ky_display(self) -> str:
        gpa = self.gpa_ky
        return f"{gpa:.2f}" if gpa is not None else "—"

    # ------------------------------------------------------------------
    # Chuyển đổi từ dict (JSON từ API)
    # ------------------------------------------------------------------

    @classmethod
    def from_dict(cls, data: dict, student: Student) -> Transcript:
        """
        Tạo Transcript từ dict JSON trả về bởi GET /diem/{mssv}.

        Ví dụ data:
        {
            "diem_list": [...],
            "hoc_ky": "HK1-2024"
        }
        """
        grades = [
            Grade.from_dict(g)
            for g in data.get("diem_list", [])
        ]
        return cls(
            student=student,
            grades=grades,
            hoc_ky=data.get("hoc_ky", ""),
        )

    def __str__(self) -> str:
        return (
            f"Bảng điểm {self.student.mssv} | "
            f"GPA: {self.gpa_display} | "
            f"Xếp loại: {self.xep_loai} | "
            f"TC đạt: {self.tin_chi_dat}/{self.tin_chi_dang_ky}"
        )