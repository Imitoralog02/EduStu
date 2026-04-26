from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from dependencies import admin_or_phongdt, all_roles
from schemas.course import CourseCreate, CourseUpdate, CourseOut
import services.course_service as svc

router = APIRouter(tags=["Courses"])


@router.get("/hocphan", response_model=list[CourseOut])
def list_courses(search: Optional[str] = None, db: Session = Depends(get_db), _=Depends(all_roles)):
    return svc.list_courses(db, search)


@router.post("/hocphan", response_model=CourseOut, status_code=201)
def create_course(body: CourseCreate, db: Session = Depends(get_db), _=Depends(admin_or_phongdt)):
    return svc.create_course(db, body.model_dump())


@router.put("/hocphan/{ma_hp}", response_model=CourseOut)
def update_course(ma_hp: str, body: CourseUpdate, db: Session = Depends(get_db), _=Depends(admin_or_phongdt)):
    return svc.update_course(db, ma_hp, body.model_dump(exclude_unset=True))


@router.delete("/hocphan/{ma_hp}")
def delete_course(ma_hp: str, db: Session = Depends(get_db), _=Depends(admin_or_phongdt)):
    return svc.delete_course(db, ma_hp)
