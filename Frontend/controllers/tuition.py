from __future__ import annotations
from controllers.base import APIClient, ApiWorker
from models.tuition import Tuition


class TuitionService(APIClient):

    def get_list(self, search: str = "", trang_thai: str = "") -> list:
        return self.get("/hocphi", params={"search": search, "trang_thai": trang_thai})

    def record_payment(self, mssv: str, so_tien: float, phuong_thuc: str, ghi_chu: str = "") -> dict:
        return self.post("/hocphi/thanhtoan", {
            "mssv": mssv, "so_tien": so_tien,
            "phuong_thuc": phuong_thuc, "ghi_chu": ghi_chu,
        })

    def get_debt_list(self) -> list:
        return self.get("/hocphi/conno")

    def get_stats(self) -> dict:
        return self.get("/hocphi/thongke")

    def get_payment_history(self, mssv: str) -> list:
        return self.get(f"/hocphi/lichsu/{mssv}")

    def create_semester(self, so_tien: float, ghi_chu: str = "") -> dict:
        return self.post("/hocphi/hocky-moi", {"so_tien": so_tien, "ghi_chu": ghi_chu})


class TuitionController:

    def __init__(self):
        self._svc     = TuitionService()
        self._workers: list[ApiWorker] = []

    def load_list(self, search: str = "", trang_thai: str = "", on_success=None, on_error=None) -> None:
        def _do():
            raw = self._svc.get_list(search, trang_thai)
            return [Tuition.from_dict(t) for t in raw]
        self._run(_do, on_success, on_error)

    def load_payment_history(self, mssv: str, on_success=None, on_error=None) -> None:
        self._run(lambda: self._svc.get_payment_history(mssv), on_success, on_error)

    def load_debt_list(self, on_success=None, on_error=None) -> None:
        def _do():
            raw = self._svc.get_debt_list()
            return [Tuition.from_dict(t) for t in raw]
        self._run(_do, on_success, on_error)

    def load_stats(self, on_success=None, on_error=None) -> None:
        self._run(lambda: self._svc.get_stats(), on_success, on_error)

    def record_payment(self, mssv: str, so_tien: float, phuong_thuc: str, ghi_chu: str = "",
                       on_success=None, on_error=None) -> None:
        err = self._validate_payment(mssv, so_tien, phuong_thuc)
        if err:
            if on_error: on_error(err)
            return
        self._run(
            lambda: self._svc.record_payment(mssv, so_tien, phuong_thuc, ghi_chu),
            on_success, on_error,
        )

    def create_semester(self, so_tien: float, ghi_chu: str = "", on_success=None, on_error=None) -> None:
        if so_tien <= 0:
            if on_error: on_error("Số tiền học phí phải lớn hơn 0.")
            return
        self._run(lambda: self._svc.create_semester(so_tien, ghi_chu), on_success, on_error)

    def _validate_payment(self, mssv: str, so_tien: float, phuong_thuc: str) -> str | None:
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
        if on_success: worker.success.connect(on_success)
        if on_error:   worker.error.connect(on_error)
        worker.start()
        self._workers.append(worker)
