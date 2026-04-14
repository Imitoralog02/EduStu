from __future__ import annotations
from controllers.base import APIClient, ApiWorker


# ======================================================================
# ReportService
# ======================================================================

class ReportService(APIClient):

    def get_dashboard(self) -> dict:
        """GET /baocao/dashboard"""
        return self.get("/baocao/dashboard")

    def get_statistics(self) -> list:
        """GET /baocao/thongke"""
        return self.get("/baocao/thongke")

    def export_excel(self, loai: str, params: dict | None = None) -> bytes:
        """GET /baocao/export/excel?loai=..."""
        query = {"loai": loai}
        if params:
            query.update(params)
        return self.get_bytes("/baocao/export/excel", params=query)


# ======================================================================
# ReportController
# ======================================================================

class ReportController:

    def __init__(self):
        self._svc     = ReportService()
        self._workers: list[ApiWorker] = []

    def load_dashboard(self, on_success=None, on_error=None) -> None:
        """
        Lấy số liệu tổng quan cho Dashboard.
        on_success nhận: dict {tong_sv, dang_hoc, canh_bao_hv, no_hoc_phi, alerts, ...}
        """
        self._run(self._svc.get_dashboard, on_success, on_error)

    def load_statistics(self, on_success=None, on_error=None) -> None:
        """
        Lấy thống kê theo khoa.
        on_success nhận: list[dict] mỗi dict là 1 khoa
        """
        self._run(self._svc.get_statistics, on_success, on_error)

    def export_excel(
        self,
        loai:       str,
        save_path:  str,
        on_success=None,
        on_error=None,
    ) -> None:
        """
        Xuất Excel và lưu ra file.
        loai: "sinhvien" | "bangdiem" | "conno"
        on_success nhận: save_path (str) để View hiển thị thông báo thành công.
        """
        if not loai:
            if on_error:
                on_error("Loại báo cáo không hợp lệ.")
            return
        if not save_path:
            if on_error:
                on_error("Chưa chọn đường dẫn lưu file.")
            return

        def _do():
            data = self._svc.export_excel(loai)
            with open(save_path, "wb") as f:
                f.write(data)
            return save_path

        self._run(_do, on_success, on_error)

    def _run(self, fn, on_success, on_error) -> None:
        worker = ApiWorker(fn)
        if on_success:
            worker.success.connect(on_success)
        if on_error:
            worker.error.connect(on_error)
        worker.start()
        self._workers.append(worker)