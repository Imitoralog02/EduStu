from __future__ import annotations
from controllers.base import APIClient, ApiWorker
from models.tuition import Tuition


# ======================================================================
# TuitionService
# ======================================================================

class TuitionService(APIClient):

    def get_list(self, search: str = "", trang_thai: str = "") -> list:
        """GET /hocphi"""
        return self.get("/hocphi", params={
            "search":     search,
            "trang_thai": trang_thai,
        })

    def record_payment(
        self,
        mssv:        str,
        so_tien:     float,
        phuong_thuc: str,
        ghi_chu:     str = "",
    ) -> dict:
        """POST /hocphi/thanhtoan"""
        return self.post("/hocphi/thanhtoan", {
            "mssv":        mssv,
            "so_tien":     so_tien,
            "phuong_thuc": phuong_thuc,
            "ghi_chu":     ghi_chu,
        })

    def get_debt_list(self) -> list:
        """GET /hocphi/conno"""
        return self.get("/hocphi/conno")


# ======================================================================
# TuitionController
# ======================================================================

class TuitionController:

    def __init__(self):
        self._svc     = TuitionService()
        self._workers: list[ApiWorker] = []

    def load_list(
        self,
        search:     str = "",
        trang_thai: str = "",
        on_success=None,
        on_error=None,
    ) -> None:
        """
        Lấy danh sách học phí.
        on_success nhận: list[Tuition]
        """
        def _do():
            raw = self._svc.get_list(search, trang_thai)
            return [Tuition.from_dict(t) for t in raw]

        self._run(_do, on_success, on_error)

    def load_debt_list(self, on_success=None, on_error=None) -> None:
        """
        Lấy danh sách sinh viên còn nợ học phí.
        on_success nhận: list[Tuition]
        """
        def _do():
            raw = self._svc.get_debt_list()
            return [Tuition.from_dict(t) for t in raw]

        self._run(_do, on_success, on_error)

    def record_payment(
        self,
        mssv:        str,
        so_tien:     float,
        phuong_thuc: str,
        ghi_chu:     str = "",
        on_success=None,
        on_error=None,
    ) -> None:
        """
        Validate → ghi nhận thanh toán học phí.
        on_success nhận: dict {"message": str, "trang_thai_moi": str}
        """
        err = self._validate_payment(mssv, so_tien, phuong_thuc)
        if err:
            if on_error:
                on_error(err)
            return

        self._run(
            lambda: self._svc.record_payment(mssv, so_tien, phuong_thuc, ghi_chu),
            on_success,
            on_error,
        )

    # ------------------------------------------------------------------
    # Validate nội bộ
    # ------------------------------------------------------------------

    def _validate_payment(
        self, mssv: str, so_tien: float, phuong_thuc: str
    ) -> str | None:
        if not mssv.strip():
            return "Vui lòng nhập MSSV."
        if so_tien <= 0:
            return "Số tiền phải lớn hơn 0."
        if so_tien > 100_000_000:
            return "Số tiền không hợp lệ (quá lớn)."
        if not phuong_thuc.strip():
            return "Vui lòng chọn phương thức thanh toán."
        return None

    def _run(self, fn, on_success, on_error) -> None:
        worker = ApiWorker(fn)
        if on_success:
            worker.success.connect(on_success)
        if on_error:
            worker.error.connect(on_error)
        worker.start()
        self._workers.append(worker)