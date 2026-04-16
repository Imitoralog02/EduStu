# EDUSТU - Hệ Thống Quản Lý Sinh Viên


## Cấu Trúc Cơ Bản

```
Frontend/
├── main.py                 # Điểm khởi động ứng dụng
├── controllers/            # Xử lý logic chính
│   ├── auth.py            # Xác thực người dùng
│   ├── student.py         # Quản lý sinh viên
│   ├── course.py          # Quản lý khóa học
│   ├── grade.py           # Quản lý điểm số
│   ├── tuition.py         # Quản lý học phí
│   └── report.py          # Báo cáo & thống kê
├── Models/                # Định nghĩa cấu trúc dữ liệu
│   ├── user.py            # Dữ liệu người dùng
│   ├── student.py         # Dữ liệu sinh viên
│   ├── course.py          # Dữ liệu khóa học
│   ├── grade.py           # Dữ liệu điểm số
│   └── tuition.py         # Dữ liệu học phí
├── views/                 # Giao diện người dùng
│   ├── main_window.py     # Cửa sổ chính
│   ├── login_view.py      # Màn hình đăng nhập
│   ├── dashboard_view.py  # Trang chủ
│   ├── student_view.py    # Quản lý sinh viên
│   ├── course_view.py     # Quản lý khóa học
│   ├── grade_view.py      # Quản lý điểm số
│   ├── tuition_view.py    # Quản lý học phí
│   └── report_view.py     # Báo cáo
└── utils/                 # Các hàm tiện ích
    ├── config.py          # Cấu hình chung
    ├── session.py         # Quản lý phiên đăng nhập
    └── helpers.py         # Hàm hỗ trợ
```

---

## 6 Tính Năng Chính

### 1. Xác Thực & Đăng Nhập

- Đăng nhập bằng tên đăng nhập và mật khẩu
- Lưu trữ và quản lý token xác thực
- Đăng xuất an toàn
- Thay đổi mật khẩu
- Quản lý phiên làm việc người dùng

---

### 2. Quản Lý Sinh Viên

- Xem danh sách sinh viên
- Thêm sinh viên mới
- Cập nhật thông tin sinh viên
- Xóa sinh viên
- Tìm kiếm theo mã số hoặc tên
- Nhập danh sách từ file Excel
- Quản lý: MSSV, tên, ngày sinh, giới tính, email, điện thoại, địa chỉ

---

### 3. Quản Lý Khóa Học

- Xem danh sách khóa học
- Thêm khóa học mới
- Cập nhật thông tin khóa học
- Xóa khóa học
- Quản lý đăng ký sinh viên vào khóa học
- Theo dõi danh sách sinh viên trong mỗi khóa

---

### 4. Quản Lý Điểm Số

- Nhập và cập nhật điểm số sinh viên
- Xem bảng điểm của sinh viên
- Tính GPA (Điểm trung bình tích lũy)
- Tính điểm trung bình theo học kỳ
- Xem lịch sử học tập
- Quản lý: điểm chính thức, xếp loại (A, B, C, D, F), trạng thái (Đạt/Không đạt)

---

### 5. Quản Lý Học Phí

- Theo dõi học phí của sinh viên
- Ghi nhận thanh toán
- Tính toán số tiền nợ
- Theo dõi trạng thái thanh toán
- Xuất danh sách sinh viên nợ
- Quản lý: tổng phí, đã thanh toán, còn nợ, ngày tạo, ngày thanh toán

---

### 6. Báo Cáo & Thống Kê

- Xem bảng điều khiển với các chỉ số chính
- Thống kê số lượng sinh viên, khóa học
- Thống kê kết quả học tập
- Thống kê tình hình học phí
- Xuất báo cáo ra file Excel
- Xem các biểu đồ thống kê cơ bản

---

## Tóm Tắt

| Tính Năng | Mô Tả |
|--------------|--------|
| **Xác Thực** | Đăng nhập, đăng xuất, quản lý phiên |
| **Sinh Viên**| CRUD, tìm kiếm, import Excel |
| **Khóa Học** | CRUD, quản lý đăng ký |
| **Điểm Số**  | Nhập/cập nhật, tính GPA, xem bảng điểm |
| **Học Phí**  | Theo dõi thanh toán, tính nợ, xuất báo cáo |
| **Báo Cáo**  | Thống kê, dashboard, xuất Excel |






