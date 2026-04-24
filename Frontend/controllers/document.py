from controllers.base import APIClient, ApiWorker
from models.document import StudentDocument, DocSummary


class DocumentService(APIClient):
    def get_summary(self) -> list[DocSummary]:
        raw = self.get("/giayto/summary")
        return [DocSummary.from_dict(d) for d in raw]

    def get_docs(self, mssv: str) -> list[StudentDocument]:
        raw = self.get(f"/giayto/{mssv}")
        return [StudentDocument.from_dict(d) for d in raw]

    def update_doc(self, doc_id: int, da_nop: bool, ngay_nop=None, ghi_chu=None) -> StudentDocument:
        raw = self.put(f"/giayto/{doc_id}", {
            "da_nop":   da_nop,
            "ngay_nop": str(ngay_nop) if ngay_nop else None,
            "ghi_chu":  ghi_chu,
        })
        return StudentDocument.from_dict(raw)

    def get_missing(self):
        return self.get("/giayto/thongbao")


class DocumentController:
    def __init__(self):
        self._svc = DocumentService()

    def _run(self, fn, on_success=None, on_error=None):
        w = ApiWorker(fn)
        if on_success:
            w.success.connect(on_success)
        if on_error:
            w.error.connect(on_error)
        w.start()
        return w

    def load_summary(self, on_success, on_error=None):
        return self._run(self._svc.get_summary, on_success, on_error)

    def load_docs(self, mssv: str, on_success, on_error=None):
        return self._run(lambda: self._svc.get_docs(mssv), on_success, on_error)

    def update_doc(self, doc_id, da_nop, ngay_nop, ghi_chu, on_success, on_error=None):
        return self._run(
            lambda: self._svc.update_doc(doc_id, da_nop, ngay_nop, ghi_chu),
            on_success, on_error,
        )