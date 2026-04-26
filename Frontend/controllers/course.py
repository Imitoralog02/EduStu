from __future__ import annotations
from controllers.base import APIClient, ApiWorker
from models.course import Course


# ======================================================================
# CourseService
# ======================================================================

class CourseService(APIClient):

    def get_list(self, search: str = "") -> list:
        """GET /hocphan"""
        return self.get("/hocphan", params={"search": search})

    def create(self, data: dict) -> dict:
        """POST /hocphan"""
        return self.post("/hocphan", data)

    def update(self, ma_hp: str, data: dict) -> dict:
        """PUT /hocphan/{ma_hp}"""
        return self.put(f"/hocphan/{ma_hp}", data)

    def delete(self, ma_hp: str) -> dict:
        """DELETE /hocphan/{ma_hp}"""
        return self.delete(f"/hocphan/{ma_hp}")


# ======================================================================
# CourseController
# ======================================================================

class CourseController:

    def __init__(self):
        self._svc     = CourseService()
        self._workers: list[ApiWorker] = []

    def load_list(self, search: str = "", on_success=None, on_error=None) -> None:
        """
        Lấy danh sách học phần.
        on_success nhận: list[Course]
        """
        def _do():
            raw = self._svc.get_list(search)
            return [Course.from_dict(c) for c in raw]

        self._run(_do, on_success, on_error)

    def create(self, data: dict, on_success=None, on_error=None) -> None:
        """
        Validate → tạo mới học phần.
        on_success nhận: Course vừa tạo
        """
        err = self._validate(data)
        if err:
            if on_error:
                on_error(err)
            return

        def _do():
            raw = self._svc.create(data)
            return Course.from_dict(raw)

        self._run(_do, on_success, on_error)

    def update(self, ma_hp: str, data: dict, on_success=None, on_error=None) -> None:
        """
        Validate → cập nhật học phần.
        on_success nhận: Course sau khi cập nhật
        """
        err = self._validate(data, is_edit=True)
        if err:
            if on_error:
                on_error(err)
            return

        def _do():
            raw = self._svc.update(ma_hp, data)
            return Course.from_dict(raw)

        self._run(_do, on_success, on_error)

    def delete(self, ma_hp: str, on_success=None, on_error=None) -> None:
        """on_success nhận: dict {"message": str}"""
        if not ma_hp:
            if on_error:
                on_error("Mã học phần không hợp lệ.")
            return
        self._run(lambda: self._svc.delete(ma_hp), on_success, on_error)

    def _validate(self, data: dict, is_edit: bool = False) -> str | None:
        if not is_edit and not data.get("ma_hp", "").strip():
            return "Vui lòng nhập Mã học phần."
        if not data.get("ten_hp", "").strip():
            return "Vui lòng nhập Tên học phần."
        tc = data.get("so_tin_chi", 0)
        if not (1 <= int(tc) <= 10):
            return "Số tín chỉ phải từ 1 đến 10."
        return None

    def _run(self, fn, on_success, on_error) -> None:
        worker = ApiWorker(fn)
        if on_success:
            worker.success.connect(on_success)
        if on_error:
            worker.error.connect(on_error)
        worker.start()
        self._workers.append(worker)
