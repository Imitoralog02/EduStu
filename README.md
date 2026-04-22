# EduStu — Hệ thống Quản lý Sinh viên

Ứng dụng desktop quản lý sinh viên toàn diện, kết hợp **FastAPI** (backend) và **PyQt6** (frontend), hỗ trợ quản lý hồ sơ, điểm số, học phí và báo cáo thống kê.

---

## Tính năng

| Tính năng | Mô tả |
|-----------|-------|
| Xác thực | Đăng nhập JWT với 3 vai trò: Admin, Phòng đào tạo, Giáo viên |
| Sinh viên | CRUD hồ sơ, tìm kiếm, lọc theo khoa/lớp/trạng thái, nhập Excel |
| Học phần | Quản lý môn học theo khoa, đăng ký học phần |
| Điểm số | Nhập/sửa điểm GK-CK, tính GPA, xếp loại tự động |
| Học phí | Theo dõi thanh toán, miễn giảm, lịch sử giao dịch |
| Báo cáo | Dashboard tổng quan, thống kê theo khoa, xuất Excel |

---

## Tech Stack

```
Frontend  PyQt6 · requests
Backend   FastAPI · SQLAlchemy · Pydantic · PyMySQL
Database  MySQL 5.7+
Auth      JWT (python-jose) · bcrypt (passlib)
Export    pandas · openpyxl
```

---

## Cấu trúc dự án

```
EduStu/
├── Backend/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── dependencies.py
│   ├── .env
│   ├── models/          # SQLAlchemy ORM models
│   ├── schemas/         # Pydantic request/response
│   ├── services/        # Business logic
│   ├── routers/         # API endpoints
│   └── utils/
│       ├── grade_calc.py
│       ├── security.py
│       └── excel.py
├── Frontend/
│   ├── main.py
│   ├── controllers/     # Gọi API, xử lý response
│   ├── views/           # Màn hình PyQt6
│   ├── models/          # Data classes
│   └── utils/
│       ├── config.py
│       ├── session.py
│       └── helpers.py
├── edustu.sql
└── requirements.txt
```

---

## Cài đặt

### Yêu cầu
- Python 3.10+
- MySQL 5.7+

### 1. Clone & tạo môi trường ảo

```bash
git clone https://github.com/Imitoralog02/EduStu.git
cd EduStu

python -m venv venv

# Windows
venv\Scripts\activate
# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Tạo database

```bash
mysql -u root -p < edustu.sql
```

> File `edustu.sql` tự động tạo database `edustu` và nạp dữ liệu mẫu.

### 3. Cấu hình Backend

Tạo file `Backend/.env`:

```env
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=edustu
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=480
```

### 4. Chạy Backend

```bash
cd Backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

API docs: http://localhost:8000/docs

### 5. Chạy Frontend

Mở terminal mới (vẫn trong virtualenv):

```bash
cd Frontend
python main.py
```

---

## Tài khoản mặc định

| Username | Password | Vai trò |
|----------|----------|---------|
| `admin` | `admin123` | Quản trị viên (toàn quyền) |
| `phongdt` | `phong123` | Phòng đào tạo |
| `giaovien` | `giao123` | Giáo viên |

**Phân quyền:**
- **admin** — truy cập toàn bộ chức năng
- **phongdt** — quản lý sinh viên, học phí, xem báo cáo
- **giaovien** — xem dashboard, nhập/xem điểm số

---

## API Endpoints

### Auth
| Method | Endpoint | Mô tả |
|--------|----------|-------|
| POST | `/auth/login` | Đăng nhập |
| PUT | `/auth/password` | Đổi mật khẩu |

### Sinh viên
| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/sinhvien` | Danh sách (phân trang, tìm kiếm) |
| GET | `/sinhvien/{mssv}` | Chi tiết sinh viên |
| POST | `/sinhvien` | Tạo mới |
| PUT | `/sinhvien/{mssv}` | Cập nhật |
| DELETE | `/sinhvien/{mssv}` | Xóa |
| POST | `/sinhvien/import` | Nhập từ Excel |

### Học phần & Đăng ký
| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/hocphan` | Danh sách học phần |
| POST | `/hocphan` | Tạo học phần |
| PUT | `/hocphan/{ma_hp}` | Cập nhật |
| DELETE | `/hocphan/{ma_hp}` | Xóa |
| GET | `/dangky/{mssv}` | Danh sách đăng ký của SV |
| POST | `/dangky` | Đăng ký học phần |
| DELETE | `/dangky/{id}` | Hủy đăng ký |

### Điểm số
| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/diem/{mssv}` | Bảng điểm |
| GET | `/diem/{mssv}/gpa` | GPA tích lũy |
| POST | `/diem` | Nhập điểm |
| PUT | `/diem/{grade_id}` | Sửa điểm |

### Học phí
| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/hocphi` | Danh sách học phí |
| GET | `/hocphi/conno` | Danh sách còn nợ |
| PUT | `/hocphi/miengiam/{mssv}` | Cập nhật miễn giảm |
| GET | `/hocphi/lichsu/{mssv}` | Lịch sử thanh toán |
| POST | `/hocphi/thanhtoan` | Ghi nhận thanh toán |

### Báo cáo
| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/baocao/dashboard` | Tổng quan hệ thống |
| GET | `/baocao/thongke` | Thống kê theo khoa |
| GET | `/baocao/export/excel?loai=` | Xuất Excel (`sinhvien`, `bangdiem`, `conno`) |

---

## Công thức tính điểm

```
Điểm tổng kết  = Điểm GK × 0.3 + Điểm CK × 0.7

Xếp loại:
  >= 8.5  →  Xuất sắc
  >= 7.0  →  Giỏi
  >= 5.5  →  Khá
  >= 4.0  →  Trung bình
  <  4.0  →  Yếu

GPA tích lũy   = Σ(Điểm × Tín chỉ) / Σ(Tín chỉ)
Cảnh báo học vụ: GPA < 1.0
```

---

## Dữ liệu mẫu

File `edustu.sql` đi kèm:
- 20 sinh viên (SV001–SV020) thuộc 3 khoa: Công nghệ thông tin, Kinh tế, Xây dựng
- 10 học phần với điểm số đầy đủ
- Dữ liệu học phí và lịch sử thanh toán
