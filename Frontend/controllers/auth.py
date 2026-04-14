from __future__ import annotations
from controllers.base import APIClient, ApiWorker
from models.user import User


# ======================================================================
# AuthService — chỉ gọi HTTP, không biết UI hay business logic
# ======================================================================

class AuthService(APIClient):

    def login(self, username: str, password: str) -> dict:
        """POST /auth/login → {"access_token": str, "user": dict}"""
        return self.post("/auth/login", {
            "username": username,
            "password": password,
        })

    def change_password(self, old_password: str, new_password: str) -> dict:
        """PUT /auth/password → {"message": str}"""
        return self.put("/auth/password", {
            "mat_khau_cu":  old_password,
            "mat_khau_moi": new_password,
        })


# ======================================================================
# AuthController — validate + điều phối + quản lý Session
# ======================================================================

class AuthController:
    """
    Xử lý đăng nhập, đăng xuất, đổi mật khẩu.
    View gọi các method của class này, không gọi Service trực tiếp.
    """

    def __init__(self):
        self._svc     = AuthService()
        self._workers: list[ApiWorker] = []

    # ------------------------------------------------------------------
    # Đăng nhập
    # ------------------------------------------------------------------

    def login(
        self,
        username:   str,
        password:   str,
        on_success,          # callback(user: User)
        on_error,            # callback(message: str)
    ) -> None:
        """
        Validate → gọi AuthService.login() ở background thread.
        Nếu thành công: tạo User model, lưu Session, gọi on_success(user).
        Nếu thất bại:   gọi on_error(message).
        """
        # Validate phía client trước khi gọi API
        username = username.strip()
        password = password.strip()

        if not username:
            on_error("Vui lòng nhập tên đăng nhập.")
            return
        if not password:
            on_error("Vui lòng nhập mật khẩu.")
            return

        def _do():
            return self._svc.login(username, password)

        def _on_success(data: dict):
            # Tạo User model từ JSON
            user = User.from_dict(data.get("user", {}))
            token = data.get("access_token", "")
            # Lưu vào Session
            from utils.session import Session
            Session.set(token, user)
            on_success(user)

        worker = ApiWorker(_do)
        worker.success.connect(_on_success)
        worker.error.connect(on_error)
        worker.start()
        self._workers.append(worker)

    # ------------------------------------------------------------------
    # Đăng xuất
    # ------------------------------------------------------------------

    def logout(self) -> None:
        """Xóa Session — đồng bộ, không cần gọi API."""
        from utils.session import Session
        Session.clear()

    # ------------------------------------------------------------------
    # Đổi mật khẩu
    # ------------------------------------------------------------------

    def change_password(
        self,
        old_password: str,
        new_password: str,
        confirm:      str,
        on_success,
        on_error,
    ) -> None:
        """
        Validate độ dài + xác nhận mật khẩu mới.
        Gọi AuthService.change_password() ở background thread.
        """
        old_password = old_password.strip()
        new_password = new_password.strip()
        confirm      = confirm.strip()

        if not old_password:
            on_error("Vui lòng nhập mật khẩu hiện tại.")
            return
        if len(new_password) < 6:
            on_error("Mật khẩu mới phải có ít nhất 6 ký tự.")
            return
        if new_password != confirm:
            on_error("Mật khẩu xác nhận không khớp.")
            return
        if new_password == old_password:
            on_error("Mật khẩu mới phải khác mật khẩu hiện tại.")
            return

        def _do():
            return self._svc.change_password(old_password, new_password)

        worker = ApiWorker(_do)
        worker.success.connect(lambda _: on_success("Đổi mật khẩu thành công."))
        worker.error.connect(on_error)
        worker.start()
        self._workers.append(worker)