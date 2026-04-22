from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from dependencies import all_roles
from schemas.grade import GradeCreate, GradeUpdate, GradeOut, TranscriptOut
import services.grade_service as svc

router = APIRouter(tags=["Grades"])


@router.get("/diem/{mssv}", response_model=TranscriptOut)
def get_transcript(
    mssv: str, hoc_ky: Optional[str] = Query(None),
    db: Session = Depends(get_db), _=Depends(all_roles),
):
    result = svc.get_transcript(db, mssv, hoc_ky)
    return TranscriptOut(diem_list=result["diem_list"], hoc_ky=result["hoc_ky"],
                         **{k: v for k, v in result.items() if k not in ("diem_list", "hoc_ky")})


@router.get("/diem/{mssv}/gpa")
def get_gpa(mssv: str, db: Session = Depends(get_db), _=Depends(all_roles)):
    return svc.get_gpa(db, mssv)


@router.post("/diem", response_model=GradeOut, status_code=201)
def create_grade(body: GradeCreate, db: Session = Depends(get_db), _=Depends(all_roles)):
    return svc.create_grade(db, body.model_dump())


@router.put("/diem/{grade_id}", response_model=GradeOut)
def update_grade(grade_id: int, body: GradeUpdate, db: Session = Depends(get_db), _=Depends(all_roles)):
    return svc.update_grade(db, grade_id, body.model_dump(exclude_unset=True))
