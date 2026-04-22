-- ============================================================
-- EduStu Database Script
-- Chạy: mysql -u root -p < database.sql
-- Hoặc copy paste vào MySQL Workbench
-- ============================================================

CREATE DATABASE IF NOT EXISTS edustu
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE edustu;

-- ── Users ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    username      VARCHAR(50)  NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    ho_ten        VARCHAR(100) NOT NULL,
    role          ENUM('admin', 'phongdt', 'giaovien') NOT NULL,
    email         VARCHAR(100),
    INDEX idx_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── Students ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS students (
    mssv          VARCHAR(20)  PRIMARY KEY,
    ho_ten        VARCHAR(100) NOT NULL,
    ngay_sinh     DATE,
    gioi_tinh     VARCHAR(10),
    lop           VARCHAR(50),
    khoa          VARCHAR(100),
    email         VARCHAR(100),
    so_dien_thoai VARCHAR(20),
    dia_chi       VARCHAR(500),
    trang_thai    ENUM('Đang học', 'Bảo lưu', 'Thôi học', 'Cảnh báo') NOT NULL DEFAULT 'Đang học'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── Courses ──────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS courses (
    ma_hp      VARCHAR(20)  PRIMARY KEY,
    ten_hp     VARCHAR(200) NOT NULL,
    so_tin_chi INT          NOT NULL DEFAULT 3,
    giao_vien  VARCHAR(100),
    hoc_ky     VARCHAR(20)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── Enrollments ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS enrollments (
    id     INT AUTO_INCREMENT PRIMARY KEY,
    mssv   VARCHAR(20) NOT NULL,
    ma_hp  VARCHAR(20) NOT NULL,
    hoc_ky VARCHAR(20) NOT NULL,
    CONSTRAINT fk_enroll_student FOREIGN KEY (mssv)  REFERENCES students(mssv) ON DELETE CASCADE,
    CONSTRAINT fk_enroll_course  FOREIGN KEY (ma_hp) REFERENCES courses(ma_hp) ON DELETE CASCADE,
    CONSTRAINT uq_enrollment     UNIQUE (mssv, ma_hp, hoc_ky)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── Grades ───────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS grades (
    id      INT AUTO_INCREMENT PRIMARY KEY,
    mssv    VARCHAR(20) NOT NULL,
    ma_hp   VARCHAR(20) NOT NULL,
    hoc_ky  VARCHAR(20) NOT NULL,
    diem_gk FLOAT,
    diem_ck FLOAT,
    CONSTRAINT fk_grade_student FOREIGN KEY (mssv)  REFERENCES students(mssv) ON DELETE CASCADE,
    CONSTRAINT fk_grade_course  FOREIGN KEY (ma_hp) REFERENCES courses(ma_hp) ON DELETE CASCADE,
    CONSTRAINT uq_grade         UNIQUE (mssv, ma_hp, hoc_ky)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── Tuition ──────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS tuition (
    id       INT AUTO_INCREMENT PRIMARY KEY,
    mssv     VARCHAR(20) NOT NULL UNIQUE,
    phai_nop FLOAT       DEFAULT 0.0,
    da_nop   FLOAT       DEFAULT 0.0,
    han_nop  DATE,
    ghi_chu  TEXT,
    CONSTRAINT fk_tuition_student FOREIGN KEY (mssv) REFERENCES students(mssv) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── Payment Logs ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS payment_logs (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    tuition_id  INT         NOT NULL,
    mssv        VARCHAR(20) NOT NULL,
    so_tien     FLOAT       NOT NULL,
    phuong_thuc ENUM('Tiền mặt', 'Chuyển khoản', 'Thẻ', 'MoMo') NOT NULL,
    ghi_chu     TEXT,
    ngay_nop    TIMESTAMP   DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_paylog_tuition FOREIGN KEY (tuition_id) REFERENCES tuition(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── Tài khoản ────────────────────────────────────────────────
-- admin/admin123 | phongdt/phong123 | giaovien/giao123
INSERT INTO users (username, password_hash, ho_ten, role, email) VALUES
('admin',    '$2b$12$G.Vc5s8YYQIqS6RgQfs3f.1lL4SltgQF4uHTkvUpGXrZe0DNK7rhS', 'Quản trị viên',    'admin',    'admin@edustu.vn'),
('phongdt',  '$2b$12$6vRhAvGnMti1U61IVk.GNuLzSZGmCp3ercw2Ohm4EKCg1mT8HVgVi', 'Phòng Đào Tạo',   'phongdt',  'phongdt@edustu.vn'),
('giaovien', '$2b$12$Q6hqIsPKwM/XgjoUgcbUIunZKlHX1bThNFqkaiamh6pgUZwUczv/C', 'Giáo Viên Mẫu',   'giaovien', 'giaovien@edustu.vn');

-- ── Sinh viên (20 bản ghi) ────────────────────────────────────
INSERT INTO students (mssv, ho_ten, ngay_sinh, gioi_tinh, lop, khoa, email, so_dien_thoai, dia_chi, trang_thai) VALUES
('SV001', 'Nguyễn Văn An',       '2002-05-12', 'Nam', 'CNTT01', 'Công nghệ thông tin', 'an.nguyen@sv.edu.vn',       '0901234567', 'Hà Nội',       'Đang học'),
('SV002', 'Trần Thị Bình',       '2003-03-20', 'Nữ',  'CNTT01', 'Công nghệ thông tin', 'binh.tran@sv.edu.vn',       '0912345678', 'Hà Nội',       'Đang học'),
('SV003', 'Lê Minh Cường',       '2002-08-10', 'Nam', 'KT02',   'Kinh tế',             'cuong.le@sv.edu.vn',        '0923456789', 'Hải Phòng',    'Cảnh báo'),
('SV004', 'Phạm Thị Dung',       '2003-01-25', 'Nữ',  'KT02',   'Kinh tế',             'dung.pham@sv.edu.vn',       '0934567890', 'Nam Định',     'Đang học'),
('SV005', 'Hoàng Văn Em',        '2001-12-05', 'Nam', 'XD03',   'Xây dựng',            'em.hoang@sv.edu.vn',        '0945678901', 'Thanh Hóa',    'Bảo lưu'),
('SV006', 'Vũ Thị Phương',       '2002-07-18', 'Nữ',  'CNTT01', 'Công nghệ thông tin', 'phuong.vu@sv.edu.vn',       '0956789012', 'Hà Nội',       'Đang học'),
('SV007', 'Đặng Minh Quân',      '2003-04-22', 'Nam', 'KT02',   'Kinh tế',             'quan.dang@sv.edu.vn',       '0967890123', 'Hà Nam',       'Đang học'),
('SV008', 'Bùi Thị Hoa',         '2002-09-14', 'Nữ',  'XD03',   'Xây dựng',            'hoa.bui@sv.edu.vn',         '0978901234', 'Ninh Bình',    'Đang học'),
('SV009', 'Ngô Văn Sơn',         '2002-11-30', 'Nam', 'CNTT02', 'Công nghệ thông tin', 'son.ngo@sv.edu.vn',         '0989012345', 'Hà Nội',       'Đang học'),
('SV010', 'Đinh Thị Lan',        '2003-06-08', 'Nữ',  'KT03',   'Kinh tế',             'lan.dinh@sv.edu.vn',        '0990123456', 'Thái Bình',    'Đang học'),
('SV011', 'Trương Văn Tú',       '2001-03-17', 'Nam', 'XD03',   'Xây dựng',            'tu.truong@sv.edu.vn',       '0901122334', 'Nghệ An',      'Thôi học'),
('SV012', 'Lý Thị Mai',          '2002-10-02', 'Nữ',  'CNTT02', 'Công nghệ thông tin', 'mai.ly@sv.edu.vn',          '0912233445', 'Hà Nội',       'Đang học'),
('SV013', 'Phan Văn Đức',        '2003-02-28', 'Nam', 'KT03',   'Kinh tế',             'duc.phan@sv.edu.vn',        '0923344556', 'Bắc Giang',    'Đang học'),
('SV014', 'Đỗ Thị Thu',          '2002-08-16', 'Nữ',  'XD04',   'Xây dựng',            'thu.do@sv.edu.vn',          '0934455667', 'Vĩnh Phúc',    'Cảnh báo'),
('SV015', 'Hà Văn Long',         '2002-05-03', 'Nam', 'CNTT02', 'Công nghệ thông tin', 'long.ha@sv.edu.vn',         '0945566778', 'Hưng Yên',     'Đang học'),
('SV016', 'Cao Thị Nga',         '2003-09-11', 'Nữ',  'KT03',   'Kinh tế',             'nga.cao@sv.edu.vn',         '0956677889', 'Hà Nội',       'Đang học'),
('SV017', 'Tô Minh Khoa',        '2002-01-20', 'Nam', 'XD04',   'Xây dựng',            'khoa.to@sv.edu.vn',         '0967788990', 'Phú Thọ',      'Đang học'),
('SV018', 'Dương Thị Yến',       '2003-07-05', 'Nữ',  'CNTT02', 'Công nghệ thông tin', 'yen.duong@sv.edu.vn',       '0978899001', 'Hà Nội',       'Đang học'),
('SV019', 'Mai Văn Hải',         '2001-11-14', 'Nam', 'KT03',   'Kinh tế',             'hai.mai@sv.edu.vn',         '0989900112', 'Quảng Ninh',   'Bảo lưu'),
('SV020', 'Lưu Thị Hằng',        '2002-04-27', 'Nữ',  'XD04',   'Xây dựng',            'hang.luu@sv.edu.vn',        '0990011223', 'Hải Dương',    'Đang học');

-- ── Học phần (10 bản ghi) ─────────────────────────────────────
INSERT INTO courses (ma_hp, ten_hp, so_tin_chi, giao_vien, hoc_ky) VALUES
('CNTT101', 'Lập trình Python cơ bản',       3, 'GV. Nguyễn Hữu Tài',   'HK1-2024-2025'),
('CNTT102', 'Cơ sở dữ liệu',                3, 'GV. Trần Văn Minh',    'HK1-2024-2025'),
('CNTT103', 'Mạng máy tính',                2, 'GV. Lê Thị Hoa',       'HK1-2024-2025'),
('CNTT104', 'Lập trình Web',                3, 'GV. Phạm Văn Đức',     'HK2-2024-2025'),
('CNTT105', 'Trí tuệ nhân tạo',             3, 'GV. Hoàng Thị Lan',    'HK2-2024-2025'),
('KT201',   'Kinh tế vi mô',               3, 'GV. Vũ Minh Tuấn',     'HK1-2024-2025'),
('KT202',   'Kế toán đại cương',            2, 'GV. Đặng Thị Ngọc',    'HK1-2024-2025'),
('KT203',   'Tài chính doanh nghiệp',       3, 'GV. Bùi Văn Hùng',     'HK2-2024-2025'),
('XD301',   'Cơ học kết cấu',               3, 'GV. Ngô Thị Thu',      'HK1-2024-2025'),
('XD302',   'Vật liệu xây dựng',            2, 'GV. Đinh Văn Mạnh',    'HK1-2024-2025');

-- ── Đăng ký học phần ─────────────────────────────────────────
INSERT INTO enrollments (mssv, ma_hp, hoc_ky) VALUES
('SV001','CNTT101','HK1-2024-2025'), ('SV001','CNTT102','HK1-2024-2025'), ('SV001','CNTT103','HK1-2024-2025'),
('SV002','CNTT101','HK1-2024-2025'), ('SV002','CNTT102','HK1-2024-2025'), ('SV002','CNTT103','HK1-2024-2025'),
('SV003','KT201',  'HK1-2024-2025'), ('SV003','KT202',  'HK1-2024-2025'),
('SV004','KT201',  'HK1-2024-2025'), ('SV004','KT202',  'HK1-2024-2025'),
('SV006','CNTT101','HK1-2024-2025'), ('SV006','CNTT102','HK1-2024-2025'),
('SV007','KT201',  'HK1-2024-2025'), ('SV007','KT202',  'HK1-2024-2025'),
('SV008','XD301',  'HK1-2024-2025'), ('SV008','XD302',  'HK1-2024-2025'),
('SV009','CNTT101','HK1-2024-2025'), ('SV009','CNTT103','HK1-2024-2025'),
('SV010','KT201',  'HK1-2024-2025'), ('SV010','KT202',  'HK1-2024-2025'),
('SV012','CNTT101','HK1-2024-2025'), ('SV012','CNTT102','HK1-2024-2025'),
('SV013','KT201',  'HK1-2024-2025'), ('SV013','KT202',  'HK1-2024-2025'),
('SV015','CNTT101','HK1-2024-2025'), ('SV015','CNTT102','HK1-2024-2025'),
('SV016','KT201',  'HK1-2024-2025'), ('SV017','XD301',  'HK1-2024-2025'),
('SV018','CNTT101','HK1-2024-2025'), ('SV020','XD301',  'HK1-2024-2025');

-- ── Điểm số ───────────────────────────────────────────────────
INSERT INTO grades (mssv, ma_hp, hoc_ky, diem_gk, diem_ck) VALUES
('SV001','CNTT101','HK1-2024-2025', 8.0, 8.5),
('SV001','CNTT102','HK1-2024-2025', 7.0, 7.5),
('SV001','CNTT103','HK1-2024-2025', 6.5, 7.0),
('SV002','CNTT101','HK1-2024-2025', 9.0, 9.5),
('SV002','CNTT102','HK1-2024-2025', 8.5, 8.0),
('SV002','CNTT103','HK1-2024-2025', 7.5, 8.0),
('SV003','KT201',  'HK1-2024-2025', 3.0, 3.5),
('SV003','KT202',  'HK1-2024-2025', 4.0, 3.0),
('SV004','KT201',  'HK1-2024-2025', 7.0, 8.0),
('SV004','KT202',  'HK1-2024-2025', 6.5, 7.5),
('SV006','CNTT101','HK1-2024-2025', 8.5, 9.0),
('SV006','CNTT102','HK1-2024-2025', 7.0, 8.0),
('SV007','KT201',  'HK1-2024-2025', 6.0, 6.5),
('SV007','KT202',  'HK1-2024-2025', 5.5, 6.0),
('SV008','XD301',  'HK1-2024-2025', 7.5, 8.0),
('SV008','XD302',  'HK1-2024-2025', 8.0, 7.5),
('SV009','CNTT101','HK1-2024-2025', 5.0, 5.5),
('SV009','CNTT103','HK1-2024-2025', 4.5, 5.0),
('SV010','KT201',  'HK1-2024-2025', 7.5, 7.0),
('SV010','KT202',  'HK1-2024-2025', 8.0, 8.5),
('SV012','CNTT101','HK1-2024-2025', 9.5,10.0),
('SV012','CNTT102','HK1-2024-2025', 8.5, 9.0),
('SV013','KT201',  'HK1-2024-2025', 6.0, 6.5),
('SV013','KT202',  'HK1-2024-2025', 5.0, 5.5),
('SV015','CNTT101','HK1-2024-2025', 7.0, 7.5),
('SV015','CNTT102','HK1-2024-2025', 6.5, 7.0),
('SV016','KT201',  'HK1-2024-2025', 8.0, 8.5),
('SV017','XD301',  'HK1-2024-2025', 7.0, 7.5),
('SV018','CNTT101','HK1-2024-2025', 6.0, 6.5),
('SV020','XD301',  'HK1-2024-2025', 8.5, 9.0);

-- ── Học phí ───────────────────────────────────────────────────
INSERT INTO tuition (mssv, phai_nop, da_nop, han_nop, ghi_chu) VALUES
('SV001', 8400000, 8400000, '2024-09-30', NULL),
('SV002', 8400000, 8400000, '2024-09-30', NULL),
('SV003', 7200000,       0, '2024-09-30', 'Sinh viên cảnh báo, chưa đóng'),
('SV004', 8400000, 4200000, '2024-09-30', 'Nộp thiếu kỳ 1'),
('SV005', 6000000, 6000000, '2024-09-30', 'Đang bảo lưu'),
('SV006', 8400000, 8400000, '2024-09-30', NULL),
('SV007', 7200000, 7200000, '2024-09-30', NULL),
('SV008', 7200000, 3600000, '2024-09-30', 'Nộp thiếu'),
('SV009', 6000000,       0, '2024-09-30', 'Chưa đóng'),
('SV010', 8400000, 8400000, '2024-09-30', NULL),
('SV011',       0,       0, NULL,          'Đã thôi học'),
('SV012', 8400000, 8400000, '2024-09-30', NULL),
('SV013', 7200000, 7200000, '2024-09-30', NULL),
('SV014', 7200000,       0, '2024-09-30', 'Sinh viên cảnh báo'),
('SV015', 8400000, 8400000, '2024-09-30', NULL),
('SV016', 8400000, 8400000, '2024-09-30', NULL),
('SV017', 7200000, 7200000, '2024-09-30', NULL),
('SV018', 8400000, 4200000, '2024-09-30', 'Nộp thiếu'),
('SV019', 6000000,       0, NULL,          'Đang bảo lưu'),
('SV020', 7200000, 7200000, '2024-09-30', NULL);

-- ── Cập nhật cấu trúc bảng (chạy nếu đã có DB cũ) ───────────
-- Thêm cột mở rộng hồ sơ sinh viên
-- Thêm cột thiếu vào bảng tuition
ALTER TABLE tuition
  ADD COLUMN mien_giam FLOAT DEFAULT 0.0,
  ADD COLUMN ly_do_mien_giam TEXT NULL;

-- Thêm cột thiếu vào bảng students
ALTER TABLE students
  ADD COLUMN nam_nhap_hoc INT NULL,
  ADD COLUMN doi_tuong VARCHAR(100) NULL,
  ADD COLUMN ho_ten_cha VARCHAR(100) NULL,
  ADD COLUMN ho_ten_me VARCHAR(100) NULL,
  ADD COLUMN sdt_phu_huynh VARCHAR(20) NULL;

-- ── Lịch sử thanh toán ────────────────────────────────────────
INSERT INTO payment_logs (tuition_id, mssv, so_tien, phuong_thuc, ghi_chu) VALUES
(1,  'SV001', 8400000, 'Chuyển khoản', 'Đóng đủ học phí HK1'),
(2,  'SV002', 8400000, 'Tiền mặt',     'Đóng đủ học phí HK1'),
(4,  'SV004', 4200000, 'MoMo',         'Đóng 50% học phí'),
(6,  'SV006', 8400000, 'Chuyển khoản', 'Đóng đủ học phí HK1'),
(7,  'SV007', 7200000, 'Thẻ',          'Đóng đủ học phí HK1'),
(8,  'SV008', 3600000, 'Tiền mặt',     'Đóng 50% học phí'),
(10, 'SV010', 8400000, 'Chuyển khoản', 'Đóng đủ học phí HK1'),
(12, 'SV012', 8400000, 'Chuyển khoản', 'Đóng đủ học phí HK1'),
(13, 'SV013', 7200000, 'MoMo',         'Đóng đủ học phí HK1'),
(15, 'SV015', 8400000, 'Thẻ',          'Đóng đủ học phí HK1'),
(16, 'SV016', 8400000, 'Chuyển khoản', 'Đóng đủ học phí HK1'),
(17, 'SV017', 7200000, 'Tiền mặt',     'Đóng đủ học phí HK1'),
(18, 'SV018', 4200000, 'MoMo',         'Đóng 50% học phí'),
(20, 'SV020', 7200000, 'Chuyển khoản', 'Đóng đủ học phí HK1');
