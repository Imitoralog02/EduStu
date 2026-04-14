from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class Student:
    """
    Đại diện cho một sinh viên trong hệ thống.
    Tạo từ JSON trả về bởi GET /sinhvien hoặc GET /sinhvien/{mssv}.
    """
    mssv:           str
    ho_ten:         str
    ngay_sinh:      str = ""       # định dạng "yyyy-MM-dd"
    gioi_tinh:      str = ""
    lop:            str = ""
    khoa:           str = ""
    email:          str = ""
    so_dien_thoai:  str = ""
    dia_chi:        str = ""
    trang_thai:     str = "Đang học"   # "Đang học" | "Bảo lưu" | "Thôi học" | "Cảnh báo"
    gpa:            float | None = None

    # ------------------------------------------------------------------
    # Computed properties
    # ------------------------------------------------------------------

    @property
    def avatar_text(self) -> str:
        """
        Lấy 2 chữ cái để hiển thị avatar tròn.
        VD: 'Nguyễn Văn An' → 'NA'
        """
        parts = self.ho_ten.strip().split()
        if len(parts) >= 2:
            return (parts[0][0] + parts[-1][0]).upper()
        return self.ho_ten[:2].upper() if self.ho_ten else "?"

    @property
    def is_active(self) -> bool:
        """Sinh viên đang học hay không."""
        return self.trang_thai == "Đang học"

    @property
    def is_warned(self) -> bool:
        """Sinh viên có cảnh báo học vụ không."""
        return self.trang_thai == "Cảnh báo" or (
            self.gpa is not None and self.gpa < 1.0
        )

    @property
    def gpa_display(self) -> str:
        """GPA định dạng hiển thị. VD: 7.82 hoặc '—' nếu chưa có."""
        return f"{self.gpa:.2f}" if self.gpa is not None else "—"

    @property
    def ngay_sinh_display(self) -> str:
        """Chuyển 'yyyy-MM-dd' → 'dd/MM/yyyy' để hiển thị."""
        if not self.ngay_sinh:
            return ""
        try:
            parts = self.ngay_sinh[:10].split("-")
            return f"{parts[2]}/{parts[1]}/{parts[0]}"
        except (IndexError, ValueError):
            return self.ngay_sinh

    # ------------------------------------------------------------------
    # Chuyển đổi từ / sang dict
    # ------------------------------------------------------------------

    @classmethod
    def from_dict(cls, data: dict) -> Student:
        """Tạo Student từ dict JSON trả về bởi FastAPI."""
        return cls(
            mssv=data.get("mssv", ""),
            ho_ten=data.get("ho_ten", ""),
            ngay_sinh=data.get("ngay_sinh", ""),
            gioi_tinh=data.get("gioi_tinh", ""),
            lop=data.get("lop", ""),
            khoa=data.get("khoa", ""),
            email=data.get("email", ""),
            so_dien_thoai=data.get("so_dien_thoai", ""),
            dia_chi=data.get("dia_chi", ""),
            trang_thai=data.get("trang_thai", "Đang học"),
            gpa=data.get("gpa"),
        )

    def to_dict(self) -> dict:
        """Chuyển sang dict để gửi lên FastAPI (POST/PUT)."""
        return {
            "mssv":           self.mssv,
            "ho_ten":         self.ho_ten,
            "ngay_sinh":      self.ngay_sinh,
            "gioi_tinh":      self.gioi_tinh,
            "lop":            self.lop,
            "khoa":           self.khoa,
            "email":          self.email,
            "so_dien_thoai":  self.so_dien_thoai,
            "dia_chi":        self.dia_chi,
            "trang_thai":     self.trang_thai,
        }

    def __str__(self) -> str:
        return f"{self.mssv} - {self.ho_ten}"