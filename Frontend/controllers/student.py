from __future__ import annotations
import re
from controllers.base import APIClient, ApiWorker
from models.student import Student


# ======================================================================
# StudentService — chỉ gọi HTTP
# ======================================================================

class StudentService(APIClient):

    def get_list(
        self,
        search:     str = "",
        khoa:       str = "",
        trang_thai: str = "",
        page:       int = 1,
        page_size:  int = 20,
    ) -> dict:
        """GET /sinhvien → {"items": [...], "total": int}"""
        return self.get("/sinhvien", params={
            "search":     search,
            "khoa":       khoa,
            "trang_thai": trang_thai,
            "page":       page,
            "page_size":  page_size,
        })

    def get_by_mssv(self, mssv: str) -> dict:
        """GET /sinhvien/{mssv}"""
        return self.get(f"/sinhvien/{mssv}")

    def create(self, data: dict) -> dict:
        """POST /sinhvien"""
        return self.post("/sinhvien", data)

    def update(self, mssv: str, data: dict) -> dict:
        """PUT /sinhvien/{mssv}"""
        return self.put(f"/sinhvien/{mssv}", data)

    def soft_delete(self, mssv: str) -> dict:
        """DELETE /sinhvien/{mssv} → chuyển trạng thái 'Thôi học'"""
        return self.delete(f"/sinhvien/{mssv}")

    def import_excel(self, file_path: str) -> dict:
        """POST /sinhvien/import (multipart)"""
        return self.post_file("/sinhvien/import", file_path)


# ======================================================================
# StudentController — validate + điều phối
# ======================================================================

class StudentController:
    """
    View gọi các method của class này.
    Controller validate dữ liệu, gọi Service, tạo Student model,
    rồi trả kết quả về View qua callback.
    """

    def __init__(self):
        self._svc     = StudentService()
        self._workers: list[ApiWorker] = []

    # ------------------------------------------------------------------
    # Lấy danh sách
    # ------------------------------------------------------------------

    def load_list(
        self,
        search:     str = "",
        khoa:       str = "",
        trang_thai: str = "",
        page:       int = 1,
        on_success=None,
        on_error=None,
    ) -> None:
        """
        Lấy danh sách sinh viên có phân trang + lọc.
        on_success nhận: {"items": list[Student], "total": int}
        """
        def _do():
            raw = self._svc.get_list(search, khoa, trang_thai, page)
            return {
                "items": [Student.from_dict(s) for s in raw.get("items", [])],
                "total": raw.get("total", 0),
            }

        self._run(_do, on_success, on_error)

    # ------------------------------------------------------------------
    # Lấy 1 sinh viên
    # ------------------------------------------------------------------

    def load_one(self, mssv: str, on_success=None, on_error=None) -> None:
        """
        Lấy thông tin đầy đủ 1 sinh viên.
        on_success nhận: Student
        """
        def _do():
            raw = self._svc.get_by_mssv(mssv)
            return Student.from_dict(raw)

        self._run(_do, on_success, on_error)

    # ------------------------------------------------------------------
    # Thêm mới
    # ------------------------------------------------------------------

    def create(self, data: dict, on_success=None, on_error=None) -> None:
        """
        Validate → tạo mới sinh viên.
        on_success nhận: Student vừa tạo
        """
        err = self._validate(data)
        if err:
            if on_error:
                on_error(err)
            return

        def _do():
            raw = self._svc.create(data)
            return Student.from_dict(raw)

        self._run(_do, on_success, on_error)

    # ------------------------------------------------------------------
    # Cập nhật
    # ------------------------------------------------------------------

    def update(
        self, mssv: str, data: dict, on_success=None, on_error=None
    ) -> None:
        """
        Validate → cập nhật hồ sơ sinh viên.
        on_success nhận: Student sau khi cập nhật
        """
        err = self._validate(data, is_edit=True)
        if err:
            if on_error:
                on_error(err)
            return

        def _do():
            raw = self._svc.update(mssv, data)
            return Student.from_dict(raw)

        self._run(_do, on_success, on_error)

    # ------------------------------------------------------------------
    # Xóa mềm
    # ------------------------------------------------------------------

    def soft_delete(self, mssv: str, on_success=None, on_error=None) -> None:
        """
        Chuyển trạng thái sinh viên → 'Thôi học'.
        on_success nhận: dict {"message": str}
        """
        if not mssv:
            if on_error:
                on_error("MSSV không hợp lệ.")
            return

        self._run(lambda: self._svc.soft_delete(mssv), on_success, on_error)

    # ------------------------------------------------------------------
    # Import Excel
    # ------------------------------------------------------------------

    def import_excel(
        self, file_path: str, on_success=None, on_error=None
    ) -> None:
        """
        Import hàng loạt từ file Excel/CSV.
        on_success nhận: {"count": int, "errors": list}
        """
        if not file_path:
            if on_error:
                on_error("Chưa chọn file.")
            return

        self._run(
            lambda: self._svc.import_excel(file_path),
            on_success,
            on_error,
        )

    # ------------------------------------------------------------------
    # Validate — dùng nội bộ
    # ------------------------------------------------------------------

    def _validate(self, data: dict, is_edit: bool = False) -> str | None:
        """
        Kiểm tra dữ liệu trước khi gửi lên API.
        Trả về None nếu hợp lệ, trả về chuỗi lỗi nếu không hợp lệ.
        """
        mssv    = data.get("mssv", "").strip()
        ho_ten  = data.get("ho_ten", "").strip()
        lop     = data.get("lop", "").strip()
        email   = data.get("email", "").strip()
        sdt     = data.get("so_dien_thoai", "").strip()

        if not is_edit and not mssv:
            return "Vui lòng nhập Mã số sinh viên."
        if not ho_ten:
            return "Vui lòng nhập Họ và tên."
        if any(c.isdigit() for c in ho_ten):
            return "Họ và tên không được chứa số."
        if not lop:
            return "Vui lòng nhập Lớp."
        if email and not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
            return "Email không đúng định dạng."
        if sdt and not re.match(r"^0\d{9}$", sdt):
            return "Số điện thoại phải có 10 chữ số và bắt đầu bằng 0."
        return None

    # ------------------------------------------------------------------
    # Helper chạy worker
    # ------------------------------------------------------------------

    def _run(self, fn, on_success, on_error) -> None:
        worker = ApiWorker(fn)
        if on_success:
            worker.success.connect(on_success)
        if on_error:
            worker.error.connect(on_error)
        worker.start()
        self._workers.append(worker)