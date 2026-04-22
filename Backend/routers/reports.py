from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Literal
import io

from database import get_db
from dependencies import admin_or_phongdt, all_roles
import services.report_service as svc

router = APIRouter(prefix="/baocao", tags=["Reports"])


@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db), _=Depends(all_roles)):
    return svc.get_dashboard(db)


@router.get("/thongke")
def statistics(db: Session = Depends(get_db), _=Depends(admin_or_phongdt)):
    return svc.get_statistics(db)


@router.get("/export/excel")
def export_excel(
    loai: Literal["sinhvien", "bangdiem", "conno"] = Query(...),
    db: Session = Depends(get_db),
    _=Depends(admin_or_phongdt),
):
    file_bytes, filename = svc.export_data(db, loai)
    return StreamingResponse(
        io.BytesIO(file_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
