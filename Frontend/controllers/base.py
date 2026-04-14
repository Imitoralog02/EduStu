from __future__ import annotations
import requests
from PyQt6.QtCore import QThread, pyqtSignal


# ======================================================================
# APIError — exception tùy chỉnh cho lỗi HTTP
# ======================================================================

class APIError(Exception):
    """
    Exception cho mọi lỗi từ FastAPI.
    Controller bắt lỗi này và chuyển message về View qua callback.
    """
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail      = detail
        super().__init__(detail)

    def __str__(self) -> str:
        return f"[{self.status_code}] {self.detail}"


# ======================================================================
# APIClient — base HTTP client, tất cả Service kế thừa
# ======================================================================

class APIClient:
    """
    Cung cấp get / post / put / delete / post_file / get_bytes.
    Tự động gắn JWT header và xử lý lỗi HTTP thống nhất.
    """

    def _get_base_url(self) -> str:
        from utils.config import BASE_URL
        return BASE_URL

    def _get_token(self) -> str | None:
        from utils.session import Session
        return Session.token()

    def _headers(self) -> dict:
        headers = {"Content-Type": "application/json"}
        token = self._get_token()
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def _handle(self, response: requests.Response) -> dict | list:
        if response.status_code in (200, 201):
            return response.json()
        try:
            detail = response.json().get("detail", "Lỗi không xác định")
        except Exception:
            detail = response.text or "Lỗi không xác định"
        raise APIError(response.status_code, str(detail))

    def _on_connection_error(self, exc: Exception) -> None:
        if isinstance(exc, requests.exceptions.ConnectionError):
            raise APIError(0, "Không thể kết nối server. Kiểm tra backend đang chạy.")
        if isinstance(exc, requests.exceptions.Timeout):
            raise APIError(0, "Server phản hồi quá chậm. Vui lòng thử lại.")
        raise exc

    # ------------------------------------------------------------------
    # HTTP methods
    # ------------------------------------------------------------------

    def get(self, path: str, params: dict | None = None) -> dict | list:
        try:
            r = requests.get(
                f"{self._get_base_url()}{path}",
                headers=self._headers(),
                params=params,
                timeout=10,
            )
            return self._handle(r)
        except APIError:
            raise
        except Exception as e:
            self._on_connection_error(e)

    def post(self, path: str, data: dict) -> dict | list:
        try:
            r = requests.post(
                f"{self._get_base_url()}{path}",
                headers=self._headers(),
                json=data,
                timeout=10,
            )
            return self._handle(r)
        except APIError:
            raise
        except Exception as e:
            self._on_connection_error(e)

    def put(self, path: str, data: dict) -> dict | list:
        try:
            r = requests.put(
                f"{self._get_base_url()}{path}",
                headers=self._headers(),
                json=data,
                timeout=10,
            )
            return self._handle(r)
        except APIError:
            raise
        except Exception as e:
            self._on_connection_error(e)

    def delete(self, path: str) -> dict | list:
        try:
            r = requests.delete(
                f"{self._get_base_url()}{path}",
                headers=self._headers(),
                timeout=10,
            )
            return self._handle(r)
        except APIError:
            raise
        except Exception as e:
            self._on_connection_error(e)

    def post_file(self, path: str, file_path: str) -> dict | list:
        """POST multipart/form-data — dùng cho import Excel."""
        try:
            with open(file_path, "rb") as f:
                r = requests.post(
                    f"{self._get_base_url()}{path}",
                    headers={"Authorization": f"Bearer {self._get_token()}"},
                    files={"file": f},
                    timeout=30,
                )
            return self._handle(r)
        except APIError:
            raise
        except FileNotFoundError:
            raise APIError(0, f"Không tìm thấy file: {file_path}")
        except Exception as e:
            self._on_connection_error(e)

    def get_bytes(self, path: str, params: dict | None = None) -> bytes:
        """GET trả về bytes — dùng cho xuất Excel / PDF."""
        try:
            r = requests.get(
                f"{self._get_base_url()}{path}",
                headers={"Authorization": f"Bearer {self._get_token()}"},
                params=params,
                timeout=30,
            )
            if r.status_code == 200:
                return r.content
            try:
                detail = r.json().get("detail", "Lỗi xuất file")
            except Exception:
                detail = "Lỗi xuất file"
            raise APIError(r.status_code, detail)
        except APIError:
            raise
        except Exception as e:
            self._on_connection_error(e)


# ======================================================================
# ApiWorker — chạy HTTP call ở background thread, tránh đơ UI
# ======================================================================

class ApiWorker(QThread):
    """
    Nhận 1 hàm lambda, chạy ở background QThread.
    Emit signal success / error về Controller.

    Ví dụ dùng trong Controller:
        worker = ApiWorker(lambda: self._svc.get_list())
        worker.success.connect(on_success)
        worker.error.connect(on_error)
        worker.start()
        self._workers.append(worker)   # giữ tham chiếu, tránh bị GC
    """
    success = pyqtSignal(object)
    error   = pyqtSignal(str)

    def __init__(self, fn, parent=None):
        super().__init__(parent)
        self._fn = fn

    def run(self):
        try:
            result = self._fn()
            self.success.emit(result)
        except APIError as e:
            self.error.emit(e.detail)
        except Exception as e:
            self.error.emit(str(e))