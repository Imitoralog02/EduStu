# EduStu

EduStu la ung dung desktop quan ly sinh vien viet bang `PyQt6`, to chuc theo huong `MVC` cho phan frontend. Repo hien tai chua gom backend; frontend giao tiep voi API qua HTTP va mac dinh goi den `http://localhost:8000`.

## Chuc nang hien co

- Dang nhap
- Dashboard tong quan
- Quan ly sinh vien
- Quan ly hoc phan
- Tra cuu va nhap diem
- Theo doi hoc phi va ghi nhan thanh toan
- Xuat bao cao Excel

## Cong nghe

- Python 3
- PyQt6
- requests

## Cau truc repo

```text
EduStu/
|-- Frontend/
|   |-- main.py
|   |-- controllers/
|   |   |-- auth.py
|   |   |-- base.py
|   |   |-- course.py
|   |   |-- grade.py
|   |   |-- report.py
|   |   |-- student.py
|   |   `-- tuition.py
|   |-- models/
|   |   |-- course.py
|   |   |-- grade.py
|   |   |-- student.py
|   |   |-- transcript.py
|   |   |-- tuition.py
|   |   `-- user.py
|   |-- utils/
|   |   |-- config.py
|   |   |-- helpers.py
|   |   `-- session.py
|   `-- views/
|       |-- base_view.py
|       |-- course_view.py
|       |-- dashboard_view.py
|       |-- grade_view.py
|       |-- login_view.py
|       |-- main_window.py
|       |-- report_view.py
|       |-- student_view.py
|       `-- tuition_view.py
|-- requirements.txt
`-- README.md
```

## Kien truc

Frontend duoc tach thanh 4 lop chinh:

- `views/`: giao dien PyQt6
- `controllers/`: validate du lieu, goi API, dieu phoi logic giao dien
- `models/`: dataclass va logic hien thi/nghiep vu nhe
- `utils/`: config, helper format, session dang nhap

`Frontend/main.py` la diem vao cua ung dung. Sau khi dang nhap thanh cong, app mo `MainWindow` va dieu huong sang cac man hinh chuc nang.

## API frontend dang su dung

Frontend hien tai ky vong backend co cac endpoint sau:

- `POST /auth/login`
- `PUT /auth/password`
- `GET /sinhvien`
- `GET /sinhvien/{mssv}`
- `POST /sinhvien`
- `PUT /sinhvien/{mssv}`
- `DELETE /sinhvien/{mssv}`
- `POST /sinhvien/import`
- `GET /hocphan`
- `POST /hocphan`
- `PUT /hocphan/{ma_hp}`
- `DELETE /hocphan/{ma_hp}`
- `GET /dangky/{mssv}`
- `POST /dangky`
- `DELETE /dangky/{id}`
- `GET /diem/{mssv}`
- `POST /diem`
- `PUT /diem/{id}`
- `GET /diem/{mssv}/gpa`
- `GET /hocphi`
- `GET /hocphi/conno`
- `POST /hocphi/thanhtoan`
- `GET /baocao/dashboard`
- `GET /baocao/thongke`
- `GET /baocao/export/excel`

## Cai dat

Tao moi truong ao va cai dependency:

```powershell
cd C:\Users\admin\EduStu
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Neu PowerShell chan script, chay tam:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

## Cach chay

Chay frontend:

```powershell
cd C:\Users\admin\EduStu\Frontend
python main.py
```

Hoac neu dang dung virtual environment o root repo:

```powershell
cd C:\Users\admin\EduStu
.\.venv\Scripts\python.exe .\Frontend\main.py
```

## Cau hinh

File cau hinh chinh nam o `Frontend/utils/config.py`.

Gia tri quan trong:

- `API_BASE_URL`
- `BASE_URL`
- mau giao dien
- danh sach hoc ky, khoa, gioi tinh, trang thai

Mac dinh:

```python
API_BASE_URL = "http://localhost:8000"
```

Neu backend cua ban chay o cong hoac host khac, sua gia tri nay truoc khi mo app.

## Ghi chu thuc te

- Repo hien tai la frontend, khong co ma nguon backend.
- Neu backend khong chay hoac khong dung contract API, cac man hinh se bao loi ket noi/du lieu.
- File `requirements.txt` hien tai chi gom dependency toi thieu cho frontend:

```text
PyQt6>=6.6.0
requests>=2.31.0
```

## Huong phat trien tiep

- Bo sung backend FastAPI hoac dong bo lai contract API
- Them xu ly fallback/offline neu can
- Bo sung test cho controller/model
- Chuan hoa encoding tieng Viet trong source
- Them dong goi/phat hanh cho desktop app
