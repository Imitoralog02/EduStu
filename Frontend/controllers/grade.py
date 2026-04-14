from __future__ import annotations
from controllers.base import APIClient, ApiWorker
from models.grade import Grade
from models.transcript import Transcript
from models.student import Student


# ======================================================================
# GradeService
# ======================================================================

class GradeService(APIClient):

    def get_transcript(self, mssv: str, hoc_ky: str = "") -> dict:
        """GET /diem/{mssv}"""
        return self.get(f"/diem/{mssv}", params={"hoc_ky": hoc_ky})

    def create(self, data: dict) -> dict:
        """POST /diem"""
        return self.post("/diem", data)

    def update(self, grade_id: int, data: dict) -> dict:
        """PUT /diem/{id}"""
        return self.put(f"/diem/{grade_id}", data)

    def get_gpa(self, mssv: str) -> dict:
        """GET /diem/{mssv}/gpa"""
        return self.get(f"/diem/{mssv}/gpa")


# ======================================================================
# GradeController
# ======================================================================

class GradeController:

    def __init__(self):
        self._svc     = GradeService()
        self._workers: list[ApiWorker] = []

    def load_transcript(
        self,
        mssv:       str,
        student:    Student,
        hoc_ky:     str = "",
        on_success=None,
        on_error=None,
    ) -> None:
        """
        Lấy bảng điểm của 1 sinh viên theo học kỳ.
        on_success nhận: Transcript
        """
        def _do():
            raw = self._svc.get_transcript(mssv, hoc_ky)
            return Transcript.from_dict(raw, student)

        self._run(_do, on_success, on_error)

    def create_grade(
        self,
        mssv:    str,
        ma_hp:   str,
        hoc_ky:  str,
        diem_gk: float,
        diem_ck: float,
        on_success=None,
        on_error=None,
    ) -> None:
        """
        Validate → nhập điểm mới cho sinh viên.
        on_success nhận: Grade vừa tạo
        """
        err = self._validate_grade(mssv, ma_hp, hoc_ky, diem_gk, diem_ck)
        if err:
            if on_error:
                on_error(err)
            return

        data = {
            "mssv":    mssv,
            "ma_hp":   ma_hp,
            "hoc_ky":  hoc_ky,
            "diem_gk": diem_gk,
            "diem_ck": diem_ck,
        }

        def _do():
            raw = self._svc.create(data)
            return Grade.from_dict(raw)

        self._run(_do, on_success, on_error)

    def update_grade(
        self,
        grade_id: int,
        diem_gk:  float,
        diem_ck:  float,
        on_success=None,
        on_error=None,
    ) -> None:
        """
        Validate → cập nhật điểm đã nhập.
        on_success nhận: Grade sau khi cập nhật
        """
        if not (0 <= diem_gk <= 10 and 0 <= diem_ck <= 10):
            if on_error:
                on_error("Điểm phải nằm trong khoảng 0 đến 10.")
            return

        def _do():
            raw = self._svc.update(grade_id, {
                "diem_gk": diem_gk,
                "diem_ck": diem_ck,
            })
            return Grade.from_dict(raw)

        self._run(_do, on_success, on_error)

    # ------------------------------------------------------------------
    # Validate nội bộ
    # ------------------------------------------------------------------

    def _validate_grade(
        self,
        mssv: str, ma_hp: str, hoc_ky: str,
        diem_gk: float, diem_ck: float,
    ) -> str | None:
        if not mssv.strip():
            return "Vui lòng nhập MSSV."
        if not ma_hp.strip():
            return "Vui lòng nhập Mã học phần."
        if not hoc_ky.strip():
            return "Vui lòng nhập Học kỳ."
        if not (0 <= diem_gk <= 10):
            return "Điểm giữa kỳ phải từ 0 đến 10."
        if not (0 <= diem_ck <= 10):
            return "Điểm cuối kỳ phải từ 0 đến 10."
        return None

    def _run(self, fn, on_success, on_error) -> None:
        worker = ApiWorker(fn)
        if on_success:
            worker.success.connect(on_success)
        if on_error:
            worker.error.connect(on_error)
        worker.start()
        self._workers.append(worker)