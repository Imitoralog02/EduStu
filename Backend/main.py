from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base
import models.student  # noqa: F401 — đảm bảo StudentStatusLog được đăng ký trước create_all
from routers import auth, students, courses, grades, tuition, reports, documents

# Tạo bảng mới nếu chưa tồn tại (safe, không xóa dữ liệu cũ)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="EduStu API",
    description="Backend API cho hệ thống quản lý sinh viên EduStu",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(students.router)
app.include_router(courses.router)
app.include_router(grades.router)
app.include_router(tuition.router)
app.include_router(reports.router)
app.include_router(documents.router)


@app.get("/")
def root():
    return {"message": "EduStu API đang chạy", "docs": "/docs"}
