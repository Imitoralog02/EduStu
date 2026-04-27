from controllers.base import APIClient, ApiWorker
from models.document import StudentDocument, DocSummary, DocumentType


class DocumentService(APIClient):

    # ── DocumentType ──────────────────────────────────────────────────────────

    def get_doc_types(self) -> list[DocumentType]:
        raw = self.get("/giayto/loai")
        return [DocumentType.from_dict(d) for d in raw]

    def create_doc_type(self, ten_loai: str, bat_buoc: bool, mo_ta: str, thu_tu: int) -> DocumentType:
        raw = self.post("/giayto/loai", {
            "ten_loai": ten_loai, "bat_buoc": bat_buoc,
            "mo_ta": mo_ta or None, "thu_tu": thu_tu,
        })
        return DocumentType.from_dict(raw)

    def update_doc_type(self, type_id: int, data: dict) -> DocumentType:
        raw = self.put(f"/giayto/loai/{type_id}", data)
        return DocumentType.from_dict(raw)

    def delete_doc_type(self, type_id: int) -> dict:
        return self.delete(f"/giayto/loai/{type_id}")

    # ── StudentDocument ───────────────────────────────────────────────────────

    def get_summary(self) -> list[DocSummary]:
        raw = self.get("/giayto/summary")
        return [DocSummary.from_dict(d) for d in raw]

    def get_docs(self, mssv: str) -> list[StudentDocument]:
        raw = self.get(f"/giayto/{mssv}")
        return [StudentDocument.from_dict(d) for d in raw]

    def update_doc(self, doc_id: int, da_nop: bool, ngay_nop=None, ghi_chu=None) -> StudentDocument:
        raw = self.put(f"/giayto/{doc_id}", {
            "da_nop": da_nop,
            "ngay_nop": str(ngay_nop) if ngay_nop else None,
            "ghi_chu": ghi_chu,
        })
        return StudentDocument.from_dict(raw)

    def upload_file(self, doc_id: int, file_path: str) -> StudentDocument:
        raw = self.post_file(f"/giayto/{doc_id}/upload", file_path)
        return StudentDocument.from_dict(raw)

    def delete_file(self, doc_id: int) -> StudentDocument:
        raw = self.delete(f"/giayto/{doc_id}/file")
        return StudentDocument.from_dict(raw)

    def get_file_url(self, doc_id: int) -> str:
        from utils.config import BASE_URL
        from utils.session import Session
        return f"{BASE_URL}/giayto/{doc_id}/file"

    def get_missing(self):
        return self.get("/giayto/thongbao")


class DocumentController:
    def __init__(self):
        self._svc     = DocumentService()
        self._workers: list[ApiWorker] = []

    def _run(self, fn, on_success=None, on_error=None):
        w = ApiWorker(fn)
        if on_success: w.success.connect(on_success)
        if on_error:   w.error.connect(on_error)
        w.start()
        self._workers.append(w)
        return w

    # ── DocumentType ──────────────────────────────────────────────────────────

    def load_doc_types(self, on_success, on_error=None):
        return self._run(self._svc.get_doc_types, on_success, on_error)

    def create_doc_type(self, ten_loai, bat_buoc, mo_ta, thu_tu, on_success, on_error=None):
        if not ten_loai.strip():
            if on_error: on_error("Tên loại giấy tờ không được trống")
            return
        return self._run(
            lambda: self._svc.create_doc_type(ten_loai.strip(), bat_buoc, mo_ta, thu_tu),
            on_success, on_error,
        )

    def update_doc_type(self, type_id, data, on_success, on_error=None):
        return self._run(lambda: self._svc.update_doc_type(type_id, data), on_success, on_error)

    def delete_doc_type(self, type_id, on_success, on_error=None):
        return self._run(lambda: self._svc.delete_doc_type(type_id), on_success, on_error)

    # ── StudentDocument ───────────────────────────────────────────────────────

    def load_summary(self, on_success, on_error=None):
        return self._run(self._svc.get_summary, on_success, on_error)

    def load_docs(self, mssv: str, on_success, on_error=None):
        return self._run(lambda: self._svc.get_docs(mssv), on_success, on_error)

    def update_doc(self, doc_id, da_nop, ngay_nop, ghi_chu, on_success, on_error=None):
        return self._run(
            lambda: self._svc.update_doc(doc_id, da_nop, ngay_nop, ghi_chu),
            on_success, on_error,
        )

    def upload_file(self, doc_id, file_path, on_success, on_error=None):
        return self._run(lambda: self._svc.upload_file(doc_id, file_path), on_success, on_error)

    def delete_file(self, doc_id, on_success, on_error=None):
        return self._run(lambda: self._svc.delete_file(doc_id), on_success, on_error)

    def download_file(self, doc_id, on_success, on_error=None):
        return self._run(lambda: self._svc.get_bytes(f"/giayto/{doc_id}/file_bytes"),
                         on_success, on_error)

    def open_file(self, doc_id: int):
        """Tải file về thư mục tạm rồi mở bằng phần mềm mặc định của OS."""
        import tempfile, os, sys

        def _open_bytes(raw: bytes):
            ext = ".bin"
            if raw[:4] == b"%PDF":
                ext = ".pdf"
            elif raw[:2] in (b"\xff\xd8", b"\xff\xe0", b"\xff\xe1"):
                ext = ".jpg"
            elif raw[:8] == b"\x89PNG\r\n\x1a\n":
                ext = ".png"
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
            tmp.write(raw)
            tmp.close()
            if sys.platform == "win32":
                os.startfile(tmp.name)
            elif sys.platform == "darwin":
                os.system(f'open "{tmp.name}"')
            else:
                os.system(f'xdg-open "{tmp.name}"')

        self._run(lambda: self._svc.get_bytes(f"/giayto/{doc_id}/file_bytes"),
                  on_success=_open_bytes,
                  on_error=lambda msg: None)
