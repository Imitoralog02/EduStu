-- ============================================================
-- EduStu Database Script  (đầy đủ, phiên bản mới nhất)
-- Chạy lần đầu:  mysql -u root -p < edustu.sql
-- Reset DB:      DROP DATABASE edustu; rồi chạy lại script
-- ============================================================

CREATE DATABASE IF NOT EXISTS edustu
CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE edustu;

-- ── Users ────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    username      VARCHAR(50)  NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    ho_ten        VARCHAR(100) NOT NULL,
    role          ENUM('admin', 'phongdt', 'giaovien') NOT NULL,
    email         VARCHAR(100),
    INDEX idx_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── Students ─────────────────────────────────────────────────────────────────
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
    trang_thai    ENUM('Đang học', 'Bảo lưu', 'Thôi học', 'Cảnh báo') NOT NULL DEFAULT 'Đang học',
    -- Hồ sơ mở rộng
    nam_nhap_hoc  INT          NULL,
    doi_tuong     VARCHAR(100) NULL,
    ho_ten_cha    VARCHAR(100) NULL,
    ho_ten_me     VARCHAR(100) NULL,
    sdt_phu_huynh VARCHAR(20)  NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── Courses ──────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS courses (
    ma_hp      VARCHAR(20)  PRIMARY KEY,
    ten_hp     VARCHAR(200) NOT NULL,
    so_tin_chi INT          NOT NULL DEFAULT 3,
    giao_vien  VARCHAR(100),
    hoc_ky     VARCHAR(20)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── Enrollments ──────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS enrollments (
    id     INT AUTO_INCREMENT PRIMARY KEY,
    mssv   VARCHAR(20) NOT NULL,
    ma_hp  VARCHAR(20) NOT NULL,
    hoc_ky VARCHAR(20) NOT NULL,
    CONSTRAINT fk_enroll_student FOREIGN KEY (mssv)  REFERENCES students(mssv) ON DELETE CASCADE,
    CONSTRAINT fk_enroll_course  FOREIGN KEY (ma_hp) REFERENCES courses(ma_hp) ON DELETE CASCADE,
    UNIQUE KEY uq_enrollment (mssv, ma_hp, hoc_ky)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── Grades ───────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS grades (
    id      INT AUTO_INCREMENT PRIMARY KEY,
    mssv    VARCHAR(20) NOT NULL,
    ma_hp   VARCHAR(20) NOT NULL,
    hoc_ky  VARCHAR(20) NOT NULL,
diem_gk FLOAT,
    diem_ck FLOAT,
    CONSTRAINT fk_grade_student FOREIGN KEY (mssv)  REFERENCES students(mssv) ON DELETE CASCADE,
    CONSTRAINT fk_grade_course  FOREIGN KEY (ma_hp) REFERENCES courses(ma_hp) ON DELETE CASCADE,
    UNIQUE KEY uq_grade (mssv, ma_hp, hoc_ky)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── Tuition ──────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS tuition (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    mssv            VARCHAR(20) NOT NULL UNIQUE,
    phai_nop        FLOAT       DEFAULT 0.0,
    da_nop          FLOAT       DEFAULT 0.0,
    mien_giam       FLOAT       DEFAULT 0.0,
    ly_do_mien_giam TEXT        NULL,
    han_nop         DATE,
    ghi_chu         TEXT,
    CONSTRAINT fk_tuition_student FOREIGN KEY (mssv) REFERENCES students(mssv) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── Payment Logs ─────────────────────────────────────────────────────────────
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

-- ── Student Documents ────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS student_documents (
    id        INT AUTO_INCREMENT PRIMARY KEY,
    mssv      VARCHAR(20)  NOT NULL,
    loai_giay VARCHAR(100) NOT NULL,
    da_nop    TINYINT(1)   NOT NULL DEFAULT 0,
    ngay_nop  DATE,
    ghi_chu   TEXT,
    cap_nhat  TIMESTAMP    DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_doc_student FOREIGN KEY (mssv) REFERENCES students(mssv) ON DELETE CASCADE,
    UNIQUE KEY uq_doc (mssv, loai_giay)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
-- ═════════════════════════════════════════════════════════════════════════════
-- DỮ LIỆU MẪU
-- ═════════════════════════════════════════════════════════════════════════════

-- ── Tài khoản hệ thống ───────────────────────────────────────────────────────
-- Mật khẩu:  admin/admin123  |  phongdt/phong123  |  giaovien/giao123
INSERT INTO users (username, password_hash, ho_ten, role, email) VALUES
('admin',    '$2b$12$G.Vc5s8YYQIqS6RgQfs3f.1lL4SltgQF4uHTkvUpGXrZe0DNK7rhS', 'Quản trị viên',  'admin',    'admin@edustu.vn'),
('phongdt',  '$2b$12$6vRhAvGnMti1U61IVk.GNuLzSZGmCp3ercw2Ohm4EKCg1mT8HVgVi', 'Phòng Đào Tạo', 'phongdt',  'phongdt@edustu.vn'),
('giaovien', '$2b$12$Q6hqIsPKwM/XgjoUgcbUIunZKlHX1bThNFqkaiamh6pgUZwUczv/C', 'Giáo Viên Mẫu', 'giaovien', 'giaovien@edustu.vn');

-- ── Sinh viên (20 bản ghi) ───────────────────────────────────────────────────
INSERT INTO students
    (mssv, ho_ten, ngay_sinh, gioi_tinh, lop, khoa, email, so_dien_thoai, dia_chi, trang_thai,
     nam_nhap_hoc, doi_tuong, ho_ten_cha, ho_ten_me, sdt_phu_huynh)
VALUES
('SV001','Nguyễn Văn An',   '2002-05-12','Nam','CNTT01','Công nghệ thông tin','an.nguyen@sv.edu.vn',  '0901234567','Hà Nội',     'Đang học',2022,NULL,         'Nguyễn Văn Bình','Trần Thị Cúc',  '0912000001'),
('SV002','Trần Thị Bình',   '2003-03-20','Nữ', 'CNTT01','Công nghệ thông tin','binh.tran@sv.edu.vn',  '0912345678','Hà Nội',     'Đang học',2023,'Hộ nghèo',  'Trần Văn Định', 'Lê Thị Em',     '0912000002'),
('SV003','Lê Minh Cường',   '2002-08-10','Nam','KT02',  'Kinh tế',            'cuong.le@sv.edu.vn',   '0923456789','Hải Phòng',  'Cảnh báo', 2022,NULL,         'Lê Văn Giang',  'Phạm Thị Hoa',  '0912000003'),
('SV004','Phạm Thị Dung',   '2003-01-25','Nữ', 'KT02',  'Kinh tế',            'dung.pham@sv.edu.vn',  '0934567890','Nam Định',   'Đang học',2023,NULL,         'Phạm Văn Inh',  'Ngô Thị Kim',   '0912000004'),
('SV005','Hoàng Văn Em',    '2001-12-05','Nam','XD03',  'Xây dựng',           'em.hoang@sv.edu.vn',   '0945678901','Thanh Hóa',  'Bảo lưu',  2021,NULL,         'Hoàng Văn Long','Đặng Thị Mai',  '0912000005'),
('SV006','Vũ Thị Phương',   '2002-07-18','Nữ', 'CNTT01','Công nghệ thông tin','phuong.vu@sv.edu.vn',  '0956789012','Hà Nội',     'Đang học',2022,'Dân tộc thiểu số','Vũ Văn Nam','Bùi Thị Oanh','0912000006'),
('SV007','Đặng Minh Quân',  '2003-04-22','Nam','KT02',  'Kinh tế',            'quan.dang@sv.edu.vn',  '0967890123','Hà Nam',     'Đang học',2023,NULL,         'Đặng Văn Phú',  'Lý Thị Quyên',  '0912000007'),
('SV008','Bùi Thị Hoa',     '2002-09-14','Nữ', 'XD03',  'Xây dựng',           'hoa.bui@sv.edu.vn',   '0978901234','Ninh Bình',  'Đang học',2022,NULL,         'Bùi Văn Sơn',   'Tô Thị Thu',    '0912000008'),
('SV009','Ngô Văn Sơn',     '2002-11-30','Nam','CNTT02','Công nghệ thông tin','son.ngo@sv.edu.vn',    '0989012345','Hà Nội',     'Đang học',2022,NULL,         'Ngô Văn Uy',    'Cao Thị Vân',   '0912000009'),
('SV010','Đinh Thị Lan',    '2003-06-08','Nữ', 'KT03',  'Kinh tế',            'lan.dinh@sv.edu.vn',   '0990123456','Thái Bình',  'Đang học',2023,NULL,         'Đinh Văn Xuân', 'Hà Thị Yến',   '0912000010'),
('SV011','Trương Văn Tú',   '2001-03-17','Nam','XD03',  'Xây dựng',           'tu.truong@sv.edu.vn',  '0901122334','Nghệ An',    'Thôi học', 2021,NULL,         'Trương Văn An', 'Dương Thị Bé',  '0912000011'),
('SV012','Lý Thị Mai',      '2002-10-02','Nữ', 'CNTT02','Công nghệ thông tin','mai.ly@sv.edu.vn',     '0912233445','Hà Nội',     'Đang học',2022,NULL,         'Lý Văn Cần',    'Phan Thị Dịu',  '0912000012'),
('SV013','Phan Văn Đức',    '2003-02-28','Nam','KT03',  'Kinh tế',            'duc.phan@sv.edu.vn',   '0923344556','Bắc Giang',  'Đang học',2023,NULL,         'Phan Văn Êm',   'Đỗ Thị Phúc',   '0912000013'),
('SV014','Đỗ Thị Thu',      '2002-08-16','Nữ', 'XD04',  'Xây dựng',           'thu.do@sv.edu.vn',     '0934455667','Vĩnh Phúc',  'Cảnh báo', 2022,NULL,         'Đỗ Văn Ghi',    'Hồ Thị Hải',   '0912000014'),
('SV015','Hà Văn Long',     '2002-05-03','Nam','CNTT02','Công nghệ thông tin','long.ha@sv.edu.vn',    '0945566778','Hưng Yên',   'Đang học',2022,NULL,         'Hà Văn Ích',    'Kiều Thị Kim',  '0912000015'),
('SV016','Cao Thị Nga',     '2003-09-11','Nữ', 'KT03',  'Kinh tế',            'nga.cao@sv.edu.vn',    '0956677889','Hà Nội',     'Đang học',2023,'Hộ cận nghèo','Cao Văn Lộc','Mai Thị Mơ',  '0912000016'),
('SV017','Tô Minh Khoa',    '2002-01-20','Nam','XD04',  'Xây dựng',           'khoa.to@sv.edu.vn',    '0967788990','Phú Thọ',    'Đang học',2022,NULL,         'Tô Văn Nhanh',  'Lưu Thị Oanh',  '0912000017'),
('SV018','Dương Thị Yến',   '2003-07-05','Nữ', 'CNTT02','Công nghệ thông tin','yen.duong@sv.edu.vn',  '0978899001','Hà Nội',     'Đang học',2023,NULL,         'Dương Văn Phong','Nguyễn Thị Quỳnh','0912000018'),
('SV019','Mai Văn Hải',     '2001-11-14','Nam','KT03',  'Kinh tế',            'hai.mai@sv.edu.vn',    '0989900112','Quảng Ninh', 'Bảo lưu',  2021,NULL,         'Mai Văn Rộng',  'Trần Thị Sen',  '0912000019'),
('SV020','Lưu Thị Hằng',    '2002-04-27','Nữ', 'XD04',  'Xây dựng',           'hang.luu@sv.edu.vn',   '0990011223','Hải Dương',  'Đang học',2022,NULL,         'Lưu Văn Tân',   'Vũ Thị Uyên',   '0912000020');

-- ── Học phần ─────────────────────────────────────────────────────────────────
INSERT INTO courses (ma_hp, ten_hp, so_tin_chi, giao_vien, hoc_ky) VALUES
('CNTT101','Lập trình Python cơ bản',   3,'GV. Nguyễn Hữu Tài', 'HK1-2024-2025'),
('CNTT102','Cơ sở dữ liệu',            3,'GV. Trần Văn Minh',  'HK1-2024-2025'),
('CNTT103','Mạng máy tính',            2,'GV. Lê Thị Hoa',     'HK1-2024-2025'),
('CNTT104','Lập trình Web',            3,'GV. Phạm Văn Đức',   'HK2-2024-2025'),
('CNTT105','Trí tuệ nhân tạo',         3,'GV. Hoàng Thị Lan',  'HK2-2024-2025'),
('KT201',  'Kinh tế vi mô',            3,'GV. Vũ Minh Tuấn',   'HK1-2024-2025'),
('KT202',  'Kế toán đại cương',        2,'GV. Đặng Thị Ngọc',  'HK1-2024-2025'),
('KT203',  'Tài chính doanh nghiệp',   3,'GV. Bùi Văn Hùng',   'HK2-2024-2025'),
('XD301',  'Cơ học kết cấu',           3,'GV. Ngô Thị Thu',    'HK1-2024-2025'),
('XD302',  'Vật liệu xây dựng',        2,'GV. Đinh Văn Mạnh',  'HK1-2024-2025');

-- ── Đăng ký học phần ─────────────────────────────────────────────────────────
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

-- ── Điểm số ──────────────────────────────────────────────────────────────────
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

-- ── Học phí ──────────────────────────────────────────────────────────────────
INSERT INTO tuition (mssv, phai_nop, da_nop, mien_giam, ly_do_mien_giam, han_nop, ghi_chu) VALUES
('SV001', 8400000, 8400000, 0,       NULL,                    '2024-09-30', NULL),
('SV002', 8400000, 7560000, 840000,  'Hộ nghèo (10%)',        '2024-09-30', NULL),
('SV003', 7200000,       0, 0,       NULL,                    '2024-09-30', 'Sinh viên cảnh báo, chưa đóng'),
('SV004', 8400000, 4200000, 0,       NULL,                    '2024-09-30', 'Nộp thiếu kỳ 1'),
('SV005', 6000000, 6000000, 0,       NULL,                    '2024-09-30', 'Đang bảo lưu'),
('SV006', 8400000, 7560000, 840000,  'Dân tộc thiểu số (10%)','2024-09-30', NULL),
('SV007', 7200000, 7200000, 0,       NULL,                    '2024-09-30', NULL),
('SV008', 7200000, 3600000, 0,       NULL,                    '2024-09-30', 'Nộp thiếu'),
('SV009', 6000000,       0, 0,       NULL,                    '2024-09-30', 'Chưa đóng'),
('SV010', 8400000, 8400000, 0,       NULL,                    '2024-09-30', NULL),
('SV011',       0,       0, 0,       NULL,                    NULL,         'Đã thôi học'),
('SV012', 8400000, 8400000, 0,       NULL,                    '2024-09-30', NULL),
('SV013', 7200000, 7200000, 0,       NULL,                    '2024-09-30', NULL),
('SV014', 7200000,       0, 0,       NULL,                    '2024-09-30', 'Sinh viên cảnh báo'),
('SV015', 8400000, 8400000, 0,       NULL,                    '2024-09-30', NULL),
('SV016', 8400000, 7560000, 840000,  'Hộ cận nghèo (10%)',    '2024-09-30', NULL),
('SV017', 7200000, 7200000, 0,       NULL,                    '2024-09-30', NULL),
('SV018', 8400000, 4200000, 0,       NULL,                    '2024-09-30', 'Nộp thiếu'),
('SV019', 6000000,       0, 0,       NULL,                    NULL,         'Đang bảo lưu'),
('SV020', 7200000, 7200000, 0,       NULL,                    '2024-09-30', NULL);

-- ── Lịch sử thanh toán ───────────────────────────────────────────────────────
INSERT INTO payment_logs (tuition_id, mssv, so_tien, phuong_thuc, ghi_chu) VALUES
(1,  'SV001', 8400000, 'Chuyển khoản', 'Đóng đủ học phí HK1'),
(2,  'SV002', 7560000, 'Tiền mặt',     'Đóng đủ sau miễn giảm'),
(4,  'SV004', 4200000, 'MoMo',         'Đóng 50% học phí'),
(5,  'SV005', 6000000, 'Chuyển khoản', 'Đóng học phí bảo lưu'),
(6,  'SV006', 7560000, 'Chuyển khoản', 'Đóng đủ sau miễn giảm'),
(7,  'SV007', 7200000, 'Thẻ',          'Đóng đủ học phí HK1'),
(8,  'SV008', 3600000, 'Tiền mặt',     'Đóng 50% học phí'),
(10, 'SV010', 8400000, 'Chuyển khoản', 'Đóng đủ học phí HK1'),
(12, 'SV012', 8400000, 'Chuyển khoản', 'Đóng đủ học phí HK1'),
(13, 'SV013', 7200000, 'MoMo',         'Đóng đủ học phí HK1'),
(15, 'SV015', 8400000, 'Thẻ',          'Đóng đủ học phí HK1'),
(16, 'SV016', 7560000, 'Chuyển khoản', 'Đóng đủ sau miễn giảm'),
(17, 'SV017', 7200000, 'Tiền mặt',     'Đóng đủ học phí HK1'),
(18, 'SV018', 4200000, 'MoMo',         'Đóng 50% học phí'),
(20, 'SV020', 7200000, 'Chuyển khoản', 'Đóng đủ học phí HK1');

-- ── Giấy tờ hồ sơ sinh viên ──────────────────────────────────────────────────
-- SV001: đã nộp đủ
INSERT INTO student_documents (mssv, loai_giay, da_nop, ngay_nop) VALUES
('SV001','CCCD/CMND',           1,'2022-09-05'),
('SV001','Giấy khai sinh',      1,'2022-09-05'),
('SV001','Học bạ THPT',         1,'2022-09-05'),
('SV001','Bằng tốt nghiệp THPT',1,'2022-09-05'),
('SV001','Ảnh thẻ 3x4',         1,'2022-09-05'),
('SV001','Sổ hộ khẩu',          1,'2022-09-05');

-- SV002: thiếu bằng tốt nghiệp
INSERT INTO student_documents (mssv, loai_giay, da_nop, ngay_nop, ghi_chu) VALUES
('SV002','CCCD/CMND',           1,'2023-09-04', NULL),
('SV002','Giấy khai sinh',      1,'2023-09-04', NULL),
('SV002','Học bạ THPT',         1,'2023-09-04', NULL),
('SV002','Bằng tốt nghiệp THPT',0, NULL,        'Chờ công nhận kết quả'),
('SV002','Ảnh thẻ 3x4',         1,'2023-09-04', NULL),
('SV002','Sổ hộ khẩu',          1,'2023-09-04', NULL);

-- SV003: thiếu nhiều giấy tờ (cảnh báo học vụ)
INSERT INTO student_documents (mssv, loai_giay, da_nop, ngay_nop) VALUES
('SV003','CCCD/CMND',           1,'2022-09-06'),
('SV003','Giấy khai sinh',      0, NULL),
('SV003','Học bạ THPT',         1,'2022-09-06'),
('SV003','Bằng tốt nghiệp THPT',0, NULL),
('SV003','Ảnh thẻ 3x4',         0, NULL),
('SV003','Sổ hộ khẩu',          1,'2022-09-06');

-- SV004: đã nộp đủ
INSERT INTO student_documents (mssv, loai_giay, da_nop, ngay_nop) VALUES
('SV004','CCCD/CMND',           1,'2023-09-03'),
('SV004','Giấy khai sinh',      1,'2023-09-03'),
('SV004','Học bạ THPT',         1,'2023-09-03'),
('SV004','Bằng tốt nghiệp THPT',1,'2023-09-03'),
('SV004','Ảnh thẻ 3x4',         1,'2023-09-03'),
('SV004','Sổ hộ khẩu',          1,'2023-09-03');

-- SV005: bảo lưu, thiếu sổ hộ khẩu
INSERT INTO student_documents (mssv, loai_giay, da_nop, ngay_nop) VALUES
('SV005','CCCD/CMND',           1,'2021-09-05'),
('SV005','Giấy khai sinh',      1,'2021-09-05'),
('SV005','Học bạ THPT',         1,'2021-09-05'),
('SV005','Bằng tốt nghiệp THPT',1,'2021-09-05'),
('SV005','Ảnh thẻ 3x4',         1,'2021-09-05'),
('SV005','Sổ hộ khẩu',          0, NULL);

-- SV006–SV020: tạo bản ghi cho tất cả (mix đủ / thiếu)
INSERT INTO student_documents (mssv, loai_giay, da_nop, ngay_nop) VALUES
('SV006','CCCD/CMND',           1,'2022-09-05'), ('SV006','Giấy khai sinh',      1,'2022-09-05'),
('SV006','Học bạ THPT',         1,'2022-09-05'), ('SV006','Bằng tốt nghiệp THPT',1,'2022-09-05'),
('SV006','Ảnh thẻ 3x4',         1,'2022-09-05'), ('SV006','Sổ hộ khẩu',          1,'2022-09-05'),

('SV007','CCCD/CMND',           1,'2023-09-04'), ('SV007','Giấy khai sinh',      1,'2023-09-04'),
('SV007','Học bạ THPT',         1,'2023-09-04'), ('SV007','Bằng tốt nghiệp THPT',0, NULL),
('SV007','Ảnh thẻ 3x4',         1,'2023-09-04'), ('SV007','Sổ hộ khẩu',          0, NULL),

('SV008','CCCD/CMND',           1,'2022-09-06'), ('SV008','Giấy khai sinh',      1,'2022-09-06'),
('SV008','Học bạ THPT',         1,'2022-09-06'), ('SV008','Bằng tốt nghiệp THPT',1,'2022-09-06'),
('SV008','Ảnh thẻ 3x4',         1,'2022-09-06'), ('SV008','Sổ hộ khẩu',          1,'2022-09-06'),

('SV009','CCCD/CMND',           1,'2022-09-05'), ('SV009','Giấy khai sinh',      0, NULL),
('SV009','Học bạ THPT',         0, NULL),        ('SV009','Bằng tốt nghiệp THPT',0, NULL),
('SV009','Ảnh thẻ 3x4',         1,'2022-09-05'), ('SV009','Sổ hộ khẩu',          0, NULL),

('SV010','CCCD/CMND',           1,'2023-09-03'), ('SV010','Giấy khai sinh',      1,'2023-09-03'),
('SV010','Học bạ THPT',         1,'2023-09-03'), ('SV010','Bằng tốt nghiệp THPT',1,'2023-09-03'),
('SV010','Ảnh thẻ 3x4',         1,'2023-09-03'), ('SV010','Sổ hộ khẩu',          1,'2023-09-03'),

('SV011','CCCD/CMND',           1,'2021-09-05'), ('SV011','Giấy khai sinh',      1,'2021-09-05'),
('SV011','Học bạ THPT',         1,'2021-09-05'), ('SV011','Bằng tốt nghiệp THPT',1,'2021-09-05'),
('SV011','Ảnh thẻ 3x4',         1,'2021-09-05'), ('SV011','Sổ hộ khẩu',          1,'2021-09-05'),

('SV012','CCCD/CMND',           1,'2022-09-05'), ('SV012','Giấy khai sinh',      1,'2022-09-05'),
('SV012','Học bạ THPT',         1,'2022-09-05'), ('SV012','Bằng tốt nghiệp THPT',1,'2022-09-05'),
('SV012','Ảnh thẻ 3x4',         1,'2022-09-05'), ('SV012','Sổ hộ khẩu',          1,'2022-09-05'),

('SV013','CCCD/CMND',           1,'2023-09-04'), ('SV013','Giấy khai sinh',      1,'2023-09-04'),
('SV013','Học bạ THPT',         1,'2023-09-04'), ('SV013','Bằng tốt nghiệp THPT',0, NULL),
('SV013','Ảnh thẻ 3x4',         1,'2023-09-04'), ('SV013','Sổ hộ khẩu',          1,'2023-09-04'),

('SV014','CCCD/CMND',           1,'2022-09-06'), ('SV014','Giấy khai sinh',      0, NULL),
('SV014','Học bạ THPT',         1,'2022-09-06'), ('SV014','Bằng tốt nghiệp THPT',0, NULL),
('SV014','Ảnh thẻ 3x4',         0, NULL),        ('SV014','Sổ hộ khẩu',          0, NULL),

('SV015','CCCD/CMND',           1,'2022-09-05'), ('SV015','Giấy khai sinh',      1,'2022-09-05'),
('SV015','Học bạ THPT',         1,'2022-09-05'), ('SV015','Bằng tốt nghiệp THPT',1,'2022-09-05'),
('SV015','Ảnh thẻ 3x4',         1,'2022-09-05'), ('SV015','Sổ hộ khẩu',          1,'2022-09-05'),

('SV016','CCCD/CMND',           1,'2023-09-03'), ('SV016','Giấy khai sinh',      1,'2023-09-03'),
('SV016','Học bạ THPT',         1,'2023-09-03'), ('SV016','Bằng tốt nghiệp THPT',1,'2023-09-03'),
('SV016','Ảnh thẻ 3x4',         1,'2023-09-03'), ('SV016','Sổ hộ khẩu',          0, NULL),

('SV017','CCCD/CMND',           1,'2022-09-05'), ('SV017','Giấy khai sinh',      1,'2022-09-05'),
('SV017','Học bạ THPT',         1,'2022-09-05'), ('SV017','Bằng tốt nghiệp THPT',1,'2022-09-05'),
('SV017','Ảnh thẻ 3x4',         1,'2022-09-05'), ('SV017','Sổ hộ khẩu',          1,'2022-09-05'),

('SV018','CCCD/CMND',           1,'2023-09-04'), ('SV018','Giấy khai sinh',      1,'2023-09-04'),
('SV018','Học bạ THPT',         1,'2023-09-04'), ('SV018','Bằng tốt nghiệp THPT',0, NULL),
('SV018','Ảnh thẻ 3x4',         1,'2023-09-04'), ('SV018','Sổ hộ khẩu',          1,'2023-09-04'),

('SV019','CCCD/CMND',           1,'2021-09-05'), ('SV019','Giấy khai sinh',      1,'2021-09-05'),
('SV019','Học bạ THPT',         1,'2021-09-05'), ('SV019','Bằng tốt nghiệp THPT',1,'2021-09-05'),
('SV019','Ảnh thẻ 3x4',         0, NULL),        ('SV019','Sổ hộ khẩu',          1,'2021-09-05'),
('SV020','CCCD/CMND',           1,'2022-09-06'), ('SV020','Giấy khai sinh',      1,'2022-09-06'),
('SV020','Học bạ THPT',         1,'2022-09-06'), ('SV020','Bằng tốt nghiệp THPT',1,'2022-09-06'),
('SV020','Ảnh thẻ 3x4',         1,'2022-09-06'), ('SV020','Sổ hộ khẩu',          1,'2022-09-06');

-- ═════════════════════════════════════════════════════════════════════════════
-- MỞ RỘNG: Các ngành mới — Du lịch, Cơ khí, Điện tử, Dược, Điều dưỡng,
--           Luật, Kế toán, Ngôn ngữ
-- ═════════════════════════════════════════════════════════════════════════════

-- ── Học phần theo ngành mới ──────────────────────────────────────────────────
INSERT INTO courses (ma_hp, ten_hp, so_tin_chi, giao_vien, hoc_ky) VALUES
-- Du lịch
('DL101',    'Nghiệp vụ hướng dẫn du lịch',    3, 'GV. Nguyễn Thị Hương',   'HK1-2024-2025'),
('DL102',    'Marketing du lịch',               3, 'GV. Trần Minh Khải',     'HK1-2024-2025'),
('DL103',    'Địa lý du lịch Việt Nam',         2, 'GV. Lê Thị Phương',      'HK2-2024-2025'),
-- Cơ khí
('CK101',    'Nguyên lý máy',                   3, 'GV. Phạm Văn Cường',     'HK1-2024-2025'),
('CK102',    'Sức bền vật liệu',                3, 'GV. Hoàng Minh Tuấn',    'HK1-2024-2025'),
('CK103',    'Công nghệ chế tạo máy',           3, 'GV. Vũ Đức Anh',         'HK2-2024-2025'),
-- Điện tử
('DTE101',   'Kỹ thuật điện tử cơ bản',         3, 'GV. Đặng Văn Hải',       'HK1-2024-2025'),
('DTE102',   'Vi xử lý và vi điều khiển',       3, 'GV. Bùi Thị Nga',        'HK1-2024-2025'),
('DTE103',   'Thông tin di động',               2, 'GV. Ngô Văn Tuấn',       'HK2-2024-2025'),
-- Dược
('DUOC101',  'Dược lý học',                     3, 'GV. Đinh Thị Thu Hà',    'HK1-2024-2025'),
('DUOC102',  'Hóa dược',                        3, 'GV. Trương Văn Lâm',     'HK1-2024-2025'),
('DUOC103',  'Bào chế học',                     3, 'GV. Lý Minh Phúc',       'HK2-2024-2025'),
-- Điều dưỡng
('DDU101',   'Giải phẫu sinh lý',               3, 'GV. Phan Thị Hồng',      'HK1-2024-2025'),
('DDU102',   'Điều dưỡng cơ bản',               3, 'GV. Đỗ Văn Nam',         'HK1-2024-2025'),
('DDU103',   'Chăm sóc sức khỏe cộng đồng',    2, 'GV. Hà Thị Liên',        'HK2-2024-2025'),
-- Luật
('LUAT101',  'Luật dân sự',                     3, 'GV. Cao Minh Đức',       'HK1-2024-2025'),
('LUAT102',  'Luật hình sự',                    3, 'GV. Tô Văn Bình',        'HK1-2024-2025'),
('LUAT103',  'Luật thương mại',                 3, 'GV. Dương Thị Nga',      'HK2-2024-2025'),
-- Kế toán
('KTOAN101', 'Kế toán tài chính',               3, 'GV. Mai Thị Hà',         'HK1-2024-2025'),
('KTOAN102', 'Kiểm toán căn bản',               3, 'GV. Lưu Văn Thành',      'HK1-2024-2025'),
('KTOAN103', 'Phân tích tài chính doanh nghiệp',3, 'GV. Nguyễn Hữu Phước',  'HK2-2024-2025'),
-- Ngôn ngữ
('NNGU101',  'Tiếng Anh thương mại',            3, 'GV. Trần Thị Mỹ Linh',   'HK1-2024-2025'),
('NNGU102',  'Dịch thuật căn bản',              3, 'GV. Phạm Quang Minh',    'HK1-2024-2025'),
('NNGU103',  'Tiếng Nhật sơ cấp',              2, 'GV. Lê Thị Sakura',       'HK2-2024-2025');

-- ── Sinh viên ngành mới (SV021 – SV044) ─────────────────────────────────────
INSERT INTO students
    (mssv, ho_ten, ngay_sinh, gioi_tinh, lop, khoa, email, so_dien_thoai, dia_chi, trang_thai,
     nam_nhap_hoc, doi_tuong, ho_ten_cha, ho_ten_me, sdt_phu_huynh)
VALUES
-- Du lịch (3 SV)
('SV021','Nguyễn Thị Ánh',    '2003-02-14','Nữ', 'DL01','Du lịch',       'anh.nguyen21@sv.edu.vn',  '0901230021','Hà Nội',      'Đang học',2023,NULL,        'Nguyễn Văn Bảo',  'Trần Thị Cẩm',   '0912100021'),
('SV022','Trần Văn Bình',     '2002-06-25','Nam','DL01','Du lịch',       'binh.tran22@sv.edu.vn',   '0901230022','Đà Nẵng',     'Đang học',2022,NULL,        'Trần Văn Châu',   'Lê Thị Diệu',    '0912100022'),
('SV023','Lê Thị Cẩm',       '2003-11-08','Nữ', 'DL02','Du lịch',       'cam.le23@sv.edu.vn',      '0901230023','Hội An',      'Đang học',2023,'Hộ nghèo',  'Lê Văn Đại',     'Phạm Thị Ê',     '0912100023'),
-- Cơ khí (3 SV)
('SV024','Phạm Văn Dũng',     '2002-03-17','Nam','CK01','Cơ khí',        'dung.pham24@sv.edu.vn',   '0901230024','Hà Nội',      'Đang học',2022,NULL,        'Phạm Văn Gia',    'Hoàng Thị Hân',  '0912100024'),
('SV025','Hoàng Thị Lan',     '2003-07-30','Nữ', 'CK01','Cơ khí',        'lan.hoang25@sv.edu.vn',   '0901230025','Thái Nguyên', 'Đang học',2023,NULL,        'Hoàng Văn Kiên',  'Vũ Thị Liên',    '0912100025'),
('SV026','Vũ Minh Khôi',      '2002-09-05','Nam','CK02','Cơ khí',        'khoi.vu26@sv.edu.vn',     '0901230026','Bắc Ninh',    'Cảnh báo', 2022,NULL,        'Vũ Văn Mạnh',    'Đặng Thị Nhi',   '0912100026'),
-- Điện tử (3 SV)
('SV027','Đặng Thị Oanh',     '2003-01-22','Nữ', 'DTE01','Điện tử',      'oanh.dang27@sv.edu.vn',   '0901230027','Hà Nội',      'Đang học',2023,NULL,        'Đặng Văn Phúc',   'Bùi Thị Quỳnh',  '0912100027'),
('SV028','Bùi Văn Phong',     '2002-05-16','Nam','DTE01','Điện tử',      'phong.bui28@sv.edu.vn',   '0901230028','Hải Phòng',   'Đang học',2022,NULL,        'Bùi Văn Rồng',   'Ngô Thị Sen',    '0912100028'),
('SV029','Ngô Thị Quỳnh',     '2002-12-03','Nữ', 'DTE02','Điện tử',      'quynh.ngo29@sv.edu.vn',   '0901230029','Hà Nội',      'Bảo lưu',  2022,NULL,        'Ngô Văn Thắng',  'Đinh Thị Uyên',  '0912100029'),
-- Dược (3 SV)
('SV030','Đinh Văn Sang',     '2003-04-11','Nam','DUOC01','Dược',         'sang.dinh30@sv.edu.vn',   '0901230030','Nam Định',    'Đang học',2023,'Hộ nghèo',  'Đinh Văn Tám',   'Trương Thị Vân', '0912100030'),
('SV031','Trương Thị Tâm',    '2003-08-27','Nữ', 'DUOC01','Dược',         'tam.truong31@sv.edu.vn',  '0901230031','Hà Nội',      'Đang học',2023,NULL,        'Trương Văn Xuyên','Lý Thị Yến',     '0912100031'),
('SV032','Lý Minh Toàn',      '2002-10-14','Nam','DUOC02','Dược',         'toan.ly32@sv.edu.vn',     '0901230032','Hà Nam',      'Đang học',2022,NULL,        'Lý Văn Ân',      'Phan Thị Bảo',   '0912100032'),
-- Điều dưỡng (3 SV)
('SV033','Phan Thị Uyên',     '2003-03-06','Nữ', 'DDU01','Điều dưỡng',   'uyen.phan33@sv.edu.vn',   '0901230033','Hà Nội',      'Đang học',2023,NULL,        'Phan Văn Cần',   'Đỗ Thị Dịu',     '0912100033'),
('SV034','Đỗ Văn Vinh',       '2002-07-19','Nam','DDU01','Điều dưỡng',   'vinh.do34@sv.edu.vn',     '0901230034','Ninh Bình',   'Đang học',2022,NULL,        'Đỗ Văn Em',      'Hà Thị Giang',   '0912100034'),
('SV035','Hà Thị Xuân',       '2003-11-25','Nữ', 'DDU02','Điều dưỡng',   'xuan.ha35@sv.edu.vn',     '0901230035','Vĩnh Phúc',   'Đang học',2023,'Dân tộc thiểu số','Hà Văn Hùng','Cao Thị Ích',    '0912100035'),
-- Luật (3 SV)
('SV036','Cao Minh Yên',      '2002-02-08','Nam','LUAT01','Luật',         'yen.cao36@sv.edu.vn',     '0901230036','Hà Nội',      'Đang học',2022,NULL,        'Cao Văn Kim',    'Tô Thị Linh',    '0912100036'),
('SV037','Tô Thị Hằng',       '2003-06-14','Nữ', 'LUAT01','Luật',         'hang.to37@sv.edu.vn',     '0901230037','Hà Nội',      'Đang học',2023,NULL,        'Tô Văn Mười',   'Dương Thị Ngát',  '0912100037'),
('SV038','Dương Văn Hào',     '2002-09-29','Nam','LUAT02','Luật',         'hao.duong38@sv.edu.vn',   '0901230038','Hà Tĩnh',     'Cảnh báo', 2022,NULL,        'Dương Văn Ổn',   'Mai Thị Phượng', '0912100038'),
-- Kế toán (3 SV)
('SV039','Mai Thị Bích',      '2003-01-17','Nữ', 'KTOAN01','Kế toán',    'bich.mai39@sv.edu.vn',    '0901230039','Hà Nội',      'Đang học',2023,NULL,        'Mai Văn Quang',  'Lưu Thị Rang',   '0912100039'),
('SV040','Lưu Văn Chiến',     '2002-05-03','Nam','KTOAN01','Kế toán',    'chien.luu40@sv.edu.vn',   '0901230040','Hưng Yên',    'Đang học',2022,NULL,        'Lưu Văn Sáng',  'Nguyễn Thị Tâm', '0912100040'),
('SV041','Nguyễn Thị Diễm',  '2003-08-21','Nữ', 'KTOAN02','Kế toán',    'diem.nguyen41@sv.edu.vn', '0901230041','Thái Bình',   'Đang học',2023,'Hộ cận nghèo','Nguyễn Văn Uy','Trần Thị Vẻ',    '0912100041'),
-- Ngôn ngữ (3 SV)
('SV042','Trần Minh Hiếu',    '2003-03-12','Nam','NNGU01','Ngôn ngữ',    'hieu.tran42@sv.edu.vn',   '0901230042','Hà Nội',      'Đang học',2023,NULL,        'Trần Văn Xuân',  'Lê Thị Yến',     '0912100042'),
('SV043','Lê Thị Khánh',      '2002-07-08','Nữ', 'NNGU01','Ngôn ngữ',    'khanh.le43@sv.edu.vn',    '0901230043','Hà Nội',      'Đang học',2022,NULL,        'Lê Văn Bách',    'Phạm Thị Cúc',   '0912100043'),
('SV044','Phạm Văn Long',     '2003-10-30','Nam','NNGU02','Ngôn ngữ',    'long.pham44@sv.edu.vn',   '0901230044','Hải Dương',   'Bảo lưu',  2023,NULL,        'Phạm Văn Điền',  'Hoàng Thị Én',   '0912100044');

-- ── Đăng ký học phần — ngành mới ────────────────────────────────────────────
INSERT INTO enrollments (mssv, ma_hp, hoc_ky) VALUES
-- Du lịch
('SV021','DL101','HK1-2024-2025'), ('SV021','DL102','HK1-2024-2025'),
('SV022','DL101','HK1-2024-2025'), ('SV022','DL102','HK1-2024-2025'), ('SV022','DL103','HK1-2024-2025'),
('SV023','DL101','HK1-2024-2025'), ('SV023','DL102','HK1-2024-2025'),
-- Cơ khí
('SV024','CK101','HK1-2024-2025'), ('SV024','CK102','HK1-2024-2025'),
('SV025','CK101','HK1-2024-2025'), ('SV025','CK102','HK1-2024-2025'), ('SV025','CK103','HK1-2024-2025'),
('SV026','CK101','HK1-2024-2025'), ('SV026','CK102','HK1-2024-2025'),
-- Điện tử
('SV027','DTE101','HK1-2024-2025'), ('SV027','DTE102','HK1-2024-2025'),
('SV028','DTE101','HK1-2024-2025'), ('SV028','DTE102','HK1-2024-2025'), ('SV028','DTE103','HK1-2024-2025'),
('SV029','DTE101','HK1-2024-2025'),
-- Dược
('SV030','DUOC101','HK1-2024-2025'), ('SV030','DUOC102','HK1-2024-2025'),
('SV031','DUOC101','HK1-2024-2025'), ('SV031','DUOC102','HK1-2024-2025'), ('SV031','DUOC103','HK1-2024-2025'),
('SV032','DUOC101','HK1-2024-2025'), ('SV032','DUOC102','HK1-2024-2025'),
-- Điều dưỡng
('SV033','DDU101','HK1-2024-2025'), ('SV033','DDU102','HK1-2024-2025'),
('SV034','DDU101','HK1-2024-2025'), ('SV034','DDU102','HK1-2024-2025'), ('SV034','DDU103','HK1-2024-2025'),
('SV035','DDU101','HK1-2024-2025'), ('SV035','DDU102','HK1-2024-2025'),
-- Luật
('SV036','LUAT101','HK1-2024-2025'), ('SV036','LUAT102','HK1-2024-2025'),
('SV037','LUAT101','HK1-2024-2025'), ('SV037','LUAT102','HK1-2024-2025'), ('SV037','LUAT103','HK1-2024-2025'),
('SV038','LUAT101','HK1-2024-2025'), ('SV038','LUAT102','HK1-2024-2025'),
-- Kế toán
('SV039','KTOAN101','HK1-2024-2025'), ('SV039','KTOAN102','HK1-2024-2025'),
('SV040','KTOAN101','HK1-2024-2025'), ('SV040','KTOAN102','HK1-2024-2025'), ('SV040','KTOAN103','HK1-2024-2025'),
('SV041','KTOAN101','HK1-2024-2025'), ('SV041','KTOAN102','HK1-2024-2025'),
-- Ngôn ngữ
('SV042','NNGU101','HK1-2024-2025'), ('SV042','NNGU102','HK1-2024-2025'),
('SV043','NNGU101','HK1-2024-2025'), ('SV043','NNGU102','HK1-2024-2025'), ('SV043','NNGU103','HK1-2024-2025'),
('SV044','NNGU101','HK1-2024-2025');

-- ── Điểm số — ngành mới ──────────────────────────────────────────────────────
INSERT INTO grades (mssv, ma_hp, hoc_ky, diem_gk, diem_ck) VALUES
-- Du lịch
('SV021','DL101','HK1-2024-2025', 8.0, 8.5), ('SV021','DL102','HK1-2024-2025', 7.5, 8.0),
('SV022','DL101','HK1-2024-2025', 9.0, 9.0), ('SV022','DL102','HK1-2024-2025', 8.5, 8.5), ('SV022','DL103','HK1-2024-2025', 8.0, 8.5),
('SV023','DL101','HK1-2024-2025', 6.5, 7.0), ('SV023','DL102','HK1-2024-2025', 7.0, 6.5),
-- Cơ khí
('SV024','CK101','HK1-2024-2025', 7.5, 8.0), ('SV024','CK102','HK1-2024-2025', 8.0, 7.5),
('SV025','CK101','HK1-2024-2025', 8.5, 9.0), ('SV025','CK102','HK1-2024-2025', 7.0, 8.0), ('SV025','CK103','HK1-2024-2025', 8.5, 8.0),
('SV026','CK101','HK1-2024-2025', 3.5, 4.0), ('SV026','CK102','HK1-2024-2025', 4.0, 3.5),
-- Điện tử
('SV027','DTE101','HK1-2024-2025', 9.0, 9.5), ('SV027','DTE102','HK1-2024-2025', 8.5, 9.0),
('SV028','DTE101','HK1-2024-2025', 7.0, 7.5), ('SV028','DTE102','HK1-2024-2025', 6.5, 7.0), ('SV028','DTE103','HK1-2024-2025', 7.5, 7.0),
('SV029','DTE101','HK1-2024-2025', 6.0, 6.5),
-- Dược
('SV030','DUOC101','HK1-2024-2025', 8.0, 8.5), ('SV030','DUOC102','HK1-2024-2025', 7.5, 8.0),
('SV031','DUOC101','HK1-2024-2025', 9.5,10.0), ('SV031','DUOC102','HK1-2024-2025', 9.0, 9.5), ('SV031','DUOC103','HK1-2024-2025', 9.0, 9.0),
('SV032','DUOC101','HK1-2024-2025', 7.0, 7.5), ('SV032','DUOC102','HK1-2024-2025', 6.5, 7.0),
-- Điều dưỡng
('SV033','DDU101','HK1-2024-2025', 8.5, 8.0), ('SV033','DDU102','HK1-2024-2025', 9.0, 8.5),
('SV034','DDU101','HK1-2024-2025', 7.5, 7.0), ('SV034','DDU102','HK1-2024-2025', 7.0, 7.5), ('SV034','DDU103','HK1-2024-2025', 8.0, 7.5),
('SV035','DDU101','HK1-2024-2025', 8.0, 8.5), ('SV035','DDU102','HK1-2024-2025', 7.5, 8.0),
-- Luật
('SV036','LUAT101','HK1-2024-2025', 8.0, 8.5), ('SV036','LUAT102','HK1-2024-2025', 7.5, 8.0),
('SV037','LUAT101','HK1-2024-2025', 9.0, 9.5), ('SV037','LUAT102','HK1-2024-2025', 8.5, 9.0), ('SV037','LUAT103','HK1-2024-2025', 8.0, 8.5),
('SV038','LUAT101','HK1-2024-2025', 4.0, 3.5), ('SV038','LUAT102','HK1-2024-2025', 3.0, 4.0),
-- Kế toán
('SV039','KTOAN101','HK1-2024-2025', 8.5, 9.0), ('SV039','KTOAN102','HK1-2024-2025', 8.0, 8.5),
('SV040','KTOAN101','HK1-2024-2025', 7.0, 7.5), ('SV040','KTOAN102','HK1-2024-2025', 7.5, 7.0), ('SV040','KTOAN103','HK1-2024-2025', 8.0, 7.5),
('SV041','KTOAN101','HK1-2024-2025', 9.0, 9.5), ('SV041','KTOAN102','HK1-2024-2025', 8.5, 9.0),
-- Ngôn ngữ
('SV042','NNGU101','HK1-2024-2025', 9.5,10.0), ('SV042','NNGU102','HK1-2024-2025', 9.0, 9.5),
('SV043','NNGU101','HK1-2024-2025', 8.0, 8.5), ('SV043','NNGU102','HK1-2024-2025', 7.5, 8.0), ('SV043','NNGU103','HK1-2024-2025', 8.5, 8.0),
('SV044','NNGU101','HK1-2024-2025', 6.5, 7.0);

-- ── Học phí — ngành mới ──────────────────────────────────────────────────────
INSERT INTO tuition (mssv, phai_nop, da_nop, mien_giam, ly_do_mien_giam, han_nop, ghi_chu) VALUES
('SV021', 9600000, 9600000, 0,       NULL,                    '2024-09-30', NULL),
('SV022', 9600000, 9600000, 0,       NULL,                    '2024-09-30', NULL),
('SV023', 9600000, 8640000, 960000,  'Hộ nghèo (10%)',        '2024-09-30', NULL),
('SV024', 8400000, 8400000, 0,       NULL,                    '2024-09-30', NULL),
('SV025', 8400000, 8400000, 0,       NULL,                    '2024-09-30', NULL),
('SV026', 8400000,       0, 0,       NULL,                    '2024-09-30', 'Sinh viên cảnh báo, chưa đóng'),
('SV027',10200000,10200000, 0,       NULL,                    '2024-09-30', NULL),
('SV028',10200000, 5100000, 0,       NULL,                    '2024-09-30', 'Nộp thiếu kỳ 1'),
('SV029',10200000,10200000, 0,       NULL,                    '2024-09-30', 'Đang bảo lưu'),
('SV030',12000000,10800000,1200000,  'Hộ nghèo (10%)',        '2024-09-30', NULL),
('SV031',12000000,12000000, 0,       NULL,                    '2024-09-30', NULL),
('SV032',12000000,12000000, 0,       NULL,                    '2024-09-30', NULL),
('SV033',11400000,11400000, 0,       NULL,                    '2024-09-30', NULL),
('SV034',11400000,11400000, 0,       NULL,                    '2024-09-30', NULL),
('SV035',11400000,10260000,1140000,  'Dân tộc thiểu số (10%)','2024-09-30', NULL),
('SV036', 9000000, 9000000, 0,       NULL,                    '2024-09-30', NULL),
('SV037', 9000000, 9000000, 0,       NULL,                    '2024-09-30', NULL),
('SV038', 9000000,       0, 0,       NULL,                    '2024-09-30', 'Sinh viên cảnh báo, chưa đóng'),
('SV039', 8400000, 8400000, 0,       NULL,                    '2024-09-30', NULL),
('SV040', 8400000, 8400000, 0,       NULL,                    '2024-09-30', NULL),
('SV041', 8400000, 7560000, 840000,  'Hộ cận nghèo (10%)',    '2024-09-30', NULL),
('SV042', 7800000, 7800000, 0,       NULL,                    '2024-09-30', NULL),
('SV043', 7800000, 7800000, 0,       NULL,                    '2024-09-30', NULL),
('SV044', 7800000, 7800000, 0,       NULL,                    '2024-09-30', 'Đang bảo lưu');

-- ── Lịch sử thanh toán — ngành mới ──────────────────────────────────────────
INSERT INTO payment_logs (tuition_id, mssv, so_tien, phuong_thuc, ghi_chu) VALUES
(21,'SV021', 9600000,'Chuyển khoản','Đóng đủ học phí HK1'),
(22,'SV022', 9600000,'MoMo',        'Đóng đủ học phí HK1'),
(23,'SV023', 8640000,'Tiền mặt',    'Đóng đủ sau miễn giảm'),
(24,'SV024', 8400000,'Chuyển khoản','Đóng đủ học phí HK1'),
(25,'SV025', 8400000,'Thẻ',         'Đóng đủ học phí HK1'),
(27,'SV027',10200000,'Chuyển khoản','Đóng đủ học phí HK1'),
(28,'SV028', 5100000,'MoMo',        'Đóng 50% học phí'),
(29,'SV029',10200000,'Tiền mặt',    'Đóng học phí bảo lưu'),
(30,'SV030',10800000,'Chuyển khoản','Đóng đủ sau miễn giảm'),
(31,'SV031',12000000,'Chuyển khoản','Đóng đủ học phí HK1'),
(32,'SV032',12000000,'Thẻ',         'Đóng đủ học phí HK1'),
(33,'SV033',11400000,'Chuyển khoản','Đóng đủ học phí HK1'),
(34,'SV034',11400000,'MoMo',        'Đóng đủ học phí HK1'),
(35,'SV035',10260000,'Tiền mặt',    'Đóng đủ sau miễn giảm'),
(36,'SV036', 9000000,'Chuyển khoản','Đóng đủ học phí HK1'),
(37,'SV037', 9000000,'Thẻ',         'Đóng đủ học phí HK1'),
(39,'SV039', 8400000,'Chuyển khoản','Đóng đủ học phí HK1'),
(40,'SV040', 8400000,'MoMo',        'Đóng đủ học phí HK1'),
(41,'SV041', 7560000,'Tiền mặt',    'Đóng đủ sau miễn giảm'),
(42,'SV042', 7800000,'Chuyển khoản','Đóng đủ học phí HK1'),
(43,'SV043', 7800000,'Thẻ',         'Đóng đủ học phí HK1'),
(44,'SV044', 7800000,'MoMo',        'Đóng học phí bảo lưu');

-- ── Giấy tờ hồ sơ — ngành mới (SV021–SV044) ─────────────────────────────────
INSERT INTO student_documents (mssv, loai_giay, da_nop, ngay_nop, ghi_chu) VALUES
-- SV021: đủ hồ sơ
('SV021','CCCD/CMND',1,'2023-09-04',NULL),('SV021','Giấy khai sinh',1,'2023-09-04',NULL),
('SV021','Học bạ THPT',1,'2023-09-04',NULL),('SV021','Bằng tốt nghiệp THPT',1,'2023-09-04',NULL),
('SV021','Ảnh thẻ 3x4',1,'2023-09-04',NULL),('SV021','Sổ hộ khẩu',1,'2023-09-04',NULL),
-- SV022: đủ hồ sơ
('SV022','CCCD/CMND',1,'2022-09-05',NULL),('SV022','Giấy khai sinh',1,'2022-09-05',NULL),
('SV022','Học bạ THPT',1,'2022-09-05',NULL),('SV022','Bằng tốt nghiệp THPT',1,'2022-09-05',NULL),
('SV022','Ảnh thẻ 3x4',1,'2022-09-05',NULL),('SV022','Sổ hộ khẩu',1,'2022-09-05',NULL),
-- SV023: thiếu bằng TN và sổ hộ khẩu
('SV023','CCCD/CMND',1,'2023-09-04',NULL),('SV023','Giấy khai sinh',1,'2023-09-04',NULL),
('SV023','Học bạ THPT',1,'2023-09-04',NULL),('SV023','Bằng tốt nghiệp THPT',0,NULL,'Chờ công nhận'),
('SV023','Ảnh thẻ 3x4',1,'2023-09-04',NULL),('SV023','Sổ hộ khẩu',0,NULL,NULL),
-- SV024: đủ hồ sơ
('SV024','CCCD/CMND',1,'2022-09-05',NULL),('SV024','Giấy khai sinh',1,'2022-09-05',NULL),
('SV024','Học bạ THPT',1,'2022-09-05',NULL),('SV024','Bằng tốt nghiệp THPT',1,'2022-09-05',NULL),
('SV024','Ảnh thẻ 3x4',1,'2022-09-05',NULL),('SV024','Sổ hộ khẩu',1,'2022-09-05',NULL),
-- SV025: đủ hồ sơ
('SV025','CCCD/CMND',1,'2023-09-04',NULL),('SV025','Giấy khai sinh',1,'2023-09-04',NULL),
('SV025','Học bạ THPT',1,'2023-09-04',NULL),('SV025','Bằng tốt nghiệp THPT',1,'2023-09-04',NULL),
('SV025','Ảnh thẻ 3x4',1,'2023-09-04',NULL),('SV025','Sổ hộ khẩu',1,'2023-09-04',NULL),
-- SV026: thiếu nhiều (cảnh báo)
('SV026','CCCD/CMND',1,'2022-09-06',NULL),('SV026','Giấy khai sinh',0,NULL,NULL),
('SV026','Học bạ THPT',0,NULL,NULL),('SV026','Bằng tốt nghiệp THPT',0,NULL,NULL),
('SV026','Ảnh thẻ 3x4',1,'2022-09-06',NULL),('SV026','Sổ hộ khẩu',0,NULL,NULL),
-- SV027: đủ hồ sơ
('SV027','CCCD/CMND',1,'2023-09-04',NULL),('SV027','Giấy khai sinh',1,'2023-09-04',NULL),
('SV027','Học bạ THPT',1,'2023-09-04',NULL),('SV027','Bằng tốt nghiệp THPT',1,'2023-09-04',NULL),
('SV027','Ảnh thẻ 3x4',1,'2023-09-04',NULL),('SV027','Sổ hộ khẩu',1,'2023-09-04',NULL),
-- SV028: thiếu sổ hộ khẩu
('SV028','CCCD/CMND',1,'2022-09-05',NULL),('SV028','Giấy khai sinh',1,'2022-09-05',NULL),
('SV028','Học bạ THPT',1,'2022-09-05',NULL),('SV028','Bằng tốt nghiệp THPT',1,'2022-09-05',NULL),
('SV028','Ảnh thẻ 3x4',1,'2022-09-05',NULL),('SV028','Sổ hộ khẩu',0,NULL,'Chưa nộp'),
-- SV029: đủ hồ sơ (bảo lưu)
('SV029','CCCD/CMND',1,'2022-09-05',NULL),('SV029','Giấy khai sinh',1,'2022-09-05',NULL),
('SV029','Học bạ THPT',1,'2022-09-05',NULL),('SV029','Bằng tốt nghiệp THPT',1,'2022-09-05',NULL),
('SV029','Ảnh thẻ 3x4',1,'2022-09-05',NULL),('SV029','Sổ hộ khẩu',1,'2022-09-05',NULL),
-- SV030: đủ hồ sơ
('SV030','CCCD/CMND',1,'2023-09-04',NULL),('SV030','Giấy khai sinh',1,'2023-09-04',NULL),
('SV030','Học bạ THPT',1,'2023-09-04',NULL),('SV030','Bằng tốt nghiệp THPT',1,'2023-09-04',NULL),
('SV030','Ảnh thẻ 3x4',1,'2023-09-04',NULL),('SV030','Sổ hộ khẩu',1,'2023-09-04',NULL),
-- SV031: đủ hồ sơ
('SV031','CCCD/CMND',1,'2023-09-03',NULL),('SV031','Giấy khai sinh',1,'2023-09-03',NULL),
('SV031','Học bạ THPT',1,'2023-09-03',NULL),('SV031','Bằng tốt nghiệp THPT',1,'2023-09-03',NULL),
('SV031','Ảnh thẻ 3x4',1,'2023-09-03',NULL),('SV031','Sổ hộ khẩu',1,'2023-09-03',NULL),
-- SV032: thiếu ảnh thẻ
('SV032','CCCD/CMND',1,'2022-09-06',NULL),('SV032','Giấy khai sinh',1,'2022-09-06',NULL),
('SV032','Học bạ THPT',1,'2022-09-06',NULL),('SV032','Bằng tốt nghiệp THPT',1,'2022-09-06',NULL),
('SV032','Ảnh thẻ 3x4',0,NULL,'Chưa nộp'),('SV032','Sổ hộ khẩu',1,'2022-09-06',NULL),
-- SV033: đủ hồ sơ
('SV033','CCCD/CMND',1,'2023-09-04',NULL),('SV033','Giấy khai sinh',1,'2023-09-04',NULL),
('SV033','Học bạ THPT',1,'2023-09-04',NULL),('SV033','Bằng tốt nghiệp THPT',1,'2023-09-04',NULL),
('SV033','Ảnh thẻ 3x4',1,'2023-09-04',NULL),('SV033','Sổ hộ khẩu',1,'2023-09-04',NULL),
-- SV034: đủ hồ sơ
('SV034','CCCD/CMND',1,'2022-09-05',NULL),('SV034','Giấy khai sinh',1,'2022-09-05',NULL),
('SV034','Học bạ THPT',1,'2022-09-05',NULL),('SV034','Bằng tốt nghiệp THPT',1,'2022-09-05',NULL),
('SV034','Ảnh thẻ 3x4',1,'2022-09-05',NULL),('SV034','Sổ hộ khẩu',1,'2022-09-05',NULL),
-- SV035: đủ hồ sơ (dân tộc)
('SV035','CCCD/CMND',1,'2023-09-03',NULL),('SV035','Giấy khai sinh',1,'2023-09-03',NULL),
('SV035','Học bạ THPT',1,'2023-09-03',NULL),('SV035','Bằng tốt nghiệp THPT',1,'2023-09-03',NULL),
('SV035','Ảnh thẻ 3x4',1,'2023-09-03',NULL),('SV035','Sổ hộ khẩu',1,'2023-09-03',NULL),
-- SV036: đủ hồ sơ
('SV036','CCCD/CMND',1,'2022-09-05',NULL),('SV036','Giấy khai sinh',1,'2022-09-05',NULL),
('SV036','Học bạ THPT',1,'2022-09-05',NULL),('SV036','Bằng tốt nghiệp THPT',1,'2022-09-05',NULL),
('SV036','Ảnh thẻ 3x4',1,'2022-09-05',NULL),('SV036','Sổ hộ khẩu',1,'2022-09-05',NULL),
-- SV037: đủ hồ sơ
('SV037','CCCD/CMND',1,'2023-09-04',NULL),('SV037','Giấy khai sinh',1,'2023-09-04',NULL),
('SV037','Học bạ THPT',1,'2023-09-04',NULL),('SV037','Bằng tốt nghiệp THPT',1,'2023-09-04',NULL),
('SV037','Ảnh thẻ 3x4',1,'2023-09-04',NULL),('SV037','Sổ hộ khẩu',1,'2023-09-04',NULL),
-- SV038: thiếu nhiều (cảnh báo)
('SV038','CCCD/CMND',1,'2022-09-06',NULL),('SV038','Giấy khai sinh',1,'2022-09-06',NULL),
('SV038','Học bạ THPT',0,NULL,NULL),('SV038','Bằng tốt nghiệp THPT',0,NULL,NULL),
('SV038','Ảnh thẻ 3x4',0,NULL,NULL),('SV038','Sổ hộ khẩu',0,NULL,NULL),
-- SV039: đủ hồ sơ
('SV039','CCCD/CMND',1,'2023-09-03',NULL),('SV039','Giấy khai sinh',1,'2023-09-03',NULL),
('SV039','Học bạ THPT',1,'2023-09-03',NULL),('SV039','Bằng tốt nghiệp THPT',1,'2023-09-03',NULL),
('SV039','Ảnh thẻ 3x4',1,'2023-09-03',NULL),('SV039','Sổ hộ khẩu',1,'2023-09-03',NULL),
-- SV040: đủ hồ sơ
('SV040','CCCD/CMND',1,'2022-09-05',NULL),('SV040','Giấy khai sinh',1,'2022-09-05',NULL),
('SV040','Học bạ THPT',1,'2022-09-05',NULL),('SV040','Bằng tốt nghiệp THPT',1,'2022-09-05',NULL),
('SV040','Ảnh thẻ 3x4',1,'2022-09-05',NULL),('SV040','Sổ hộ khẩu',1,'2022-09-05',NULL),
-- SV041: thiếu học bạ
('SV041','CCCD/CMND',1,'2023-09-04',NULL),('SV041','Giấy khai sinh',1,'2023-09-04',NULL),
('SV041','Học bạ THPT',0,NULL,'Đang xin bản sao'),('SV041','Bằng tốt nghiệp THPT',1,'2023-09-04',NULL),
('SV041','Ảnh thẻ 3x4',1,'2023-09-04',NULL),('SV041','Sổ hộ khẩu',1,'2023-09-04',NULL),
-- SV042: đủ hồ sơ
('SV042','CCCD/CMND',1,'2023-09-03',NULL),('SV042','Giấy khai sinh',1,'2023-09-03',NULL),
('SV042','Học bạ THPT',1,'2023-09-03',NULL),('SV042','Bằng tốt nghiệp THPT',1,'2023-09-03',NULL),
('SV042','Ảnh thẻ 3x4',1,'2023-09-03',NULL),('SV042','Sổ hộ khẩu',1,'2023-09-03',NULL),
-- SV043: đủ hồ sơ
('SV043','CCCD/CMND',1,'2022-09-05',NULL),('SV043','Giấy khai sinh',1,'2022-09-05',NULL),
('SV043','Học bạ THPT',1,'2022-09-05',NULL),('SV043','Bằng tốt nghiệp THPT',1,'2022-09-05',NULL),
('SV043','Ảnh thẻ 3x4',1,'2022-09-05',NULL),('SV043','Sổ hộ khẩu',1,'2022-09-05',NULL),
-- SV044: thiếu giấy khai sinh (bảo lưu)
('SV044','CCCD/CMND',1,'2023-09-04',NULL),('SV044','Giấy khai sinh',0,NULL,'Chờ bổ sung'),
('SV044','Học bạ THPT',1,'2023-09-04',NULL),('SV044','Bằng tốt nghiệp THPT',1,'2023-09-04',NULL),
('SV044','Ảnh thẻ 3x4',1,'2023-09-04',NULL),('SV044','Sổ hộ khẩu',1,'2023-09-04',NULL);

-- ═════════════════════════════════════════════════════════════════════════════
-- BỔ SUNG MÔN HỌC — Mỗi ngành thêm 5 môn (tổng cộng 55 môn mới)
-- ═════════════════════════════════════════════════════════════════════════════
INSERT INTO courses (ma_hp, ten_hp, so_tin_chi, giao_vien, hoc_ky) VALUES

-- ── Công nghệ thông tin (CNTT106–CNTT110) ────────────────────────────────────
('CNTT106','Lập trình hướng đối tượng',        3,'GV. Nguyễn Hữu Tài',    'HK1-2024-2025'),
('CNTT107','Cấu trúc dữ liệu và giải thuật',   3,'GV. Trần Văn Minh',     'HK1-2024-2025'),
('CNTT108','Hệ điều hành',                     2,'GV. Lê Thị Hoa',        'HK2-2024-2025'),
('CNTT109','Bảo mật thông tin',                3,'GV. Phạm Văn Đức',      'HK2-2024-2025'),
('CNTT110','Học máy và khai phá dữ liệu',      3,'GV. Hoàng Thị Lan',     'HK2-2024-2025'),

-- ── Kinh tế (KT204–KT208) ────────────────────────────────────────────────────
('KT204','Kinh tế vĩ mô',                      3,'GV. Vũ Minh Tuấn',      'HK1-2024-2025'),
('KT205','Quản trị học',                       3,'GV. Đặng Thị Ngọc',     'HK1-2024-2025'),
('KT206','Marketing căn bản',                  3,'GV. Bùi Văn Hùng',      'HK2-2024-2025'),
('KT207','Thống kê kinh doanh',                2,'GV. Ngô Thị Thu',       'HK2-2024-2025'),
('KT208','Kinh tế quốc tế',                    3,'GV. Đinh Văn Mạnh',     'HK2-2024-2025'),

-- ── Xây dựng (XD303–XD307) ───────────────────────────────────────────────────
('XD303','Bê tông cốt thép',                   3,'GV. Nguyễn Hữu Tài',    'HK1-2024-2025'),
('XD304','Kết cấu thép',                       3,'GV. Trần Văn Minh',     'HK1-2024-2025'),
('XD305','Thiết kế kiến trúc',                 3,'GV. Lê Thị Hoa',        'HK2-2024-2025'),
('XD306','Quản lý dự án xây dựng',             2,'GV. Phạm Văn Đức',      'HK2-2024-2025'),
('XD307','Địa kỹ thuật',                       3,'GV. Hoàng Thị Lan',     'HK2-2024-2025'),
-- ── Du lịch (DL104–DL108) ────────────────────────────────────────────────────
('DL104','Tổng quan du lịch',                  3,'GV. Nguyễn Thị Hương',   'HK1-2024-2025'),
('DL105','Nghiệp vụ lễ tân khách sạn',         3,'GV. Trần Minh Khải',    'HK1-2024-2025'),
('DL106','Ẩm thực và văn hóa du lịch',         2,'GV. Lê Thị Phương',     'HK2-2024-2025'),
('DL107','Quản trị kinh doanh khách sạn',      3,'GV. Vũ Minh Tuấn',      'HK2-2024-2025'),
('DL108','Tiếng Anh du lịch',                  3,'GV. Đặng Thị Ngọc',     'HK2-2024-2025'),

-- ── Cơ khí (CK104–CK108) ─────────────────────────────────────────────────────
('CK104','Nhiệt động lực học kỹ thuật',        3,'GV. Phạm Văn Cường',    'HK1-2024-2025'),
('CK105','Cơ học chất lỏng',                   3,'GV. Hoàng Minh Tuấn',   'HK1-2024-2025'),
('CK106','Kỹ thuật CAD/CAM',                   3,'GV. Vũ Đức Anh',        'HK2-2024-2025'),
('CK107','Tự động hóa sản xuất',               3,'GV. Bùi Văn Hùng',      'HK2-2024-2025'),
('CK108','An toàn lao động trong cơ khí',      2,'GV. Ngô Thị Thu',       'HK2-2024-2025'),

-- ── Điện tử (DTE104–DTE108) ──────────────────────────────────────────────────
('DTE104','Lý thuyết mạch điện',               3,'GV. Đặng Văn Hải',      'HK1-2024-2025'),
('DTE105','Xử lý tín hiệu số',                 3,'GV. Bùi Thị Nga',       'HK1-2024-2025'),
('DTE106','Thiết kế mạch điện tử',             3,'GV. Ngô Văn Tuấn',      'HK2-2024-2025'),
('DTE107','Internet of Things',                3,'GV. Đinh Văn Mạnh',     'HK2-2024-2025'),
('DTE108','Điện tử công suất',                 2,'GV. Trương Văn Lâm',    'HK2-2024-2025'),

-- ── Dược (DUOC104–DUOC108) ───────────────────────────────────────────────────
('DUOC104','Vi sinh và ký sinh trùng',         3,'GV. Đinh Thị Thu Hà',   'HK1-2024-2025'),
('DUOC105','Dược liệu học',                    3,'GV. Trương Văn Lâm',    'HK1-2024-2025'),
('DUOC106','Kiểm nghiệm thuốc',                3,'GV. Lý Minh Phúc',      'HK2-2024-2025'),
('DUOC107','Quản lý và kinh tế dược',          2,'GV. Phan Thị Hồng',     'HK2-2024-2025'),
('DUOC108','Thực hành lâm sàng dược',          3,'GV. Đỗ Văn Nam',        'HK2-2024-2025'),

-- ── Điều dưỡng (DDU104–DDU108) ───────────────────────────────────────────────
('DDU104','Bệnh học nội khoa',                 3,'GV. Hà Thị Liên',       'HK1-2024-2025'),
('DDU105','Điều dưỡng ngoại khoa',             3,'GV. Cao Minh Đức',      'HK1-2024-2025'),
('DDU106','Chăm sóc sản phụ khoa',             3,'GV. Tô Văn Bình',       'HK2-2024-2025'),
('DDU107','Điều dưỡng nhi khoa',               3,'GV. Dương Thị Nga',     'HK2-2024-2025'),
('DDU108','Y đức và pháp lý y tế',             2,'GV. Mai Thị Hà',        'HK2-2024-2025'),

-- ── Luật (LUAT104–LUAT108) ───────────────────────────────────────────────────
('LUAT104','Luật hiến pháp',                   3,'GV. Lưu Văn Thành',     'HK1-2024-2025'),
('LUAT105','Luật hành chính',                  3,'GV. Nguyễn Hữu Phước',  'HK1-2024-2025'),
('LUAT106','Luật lao động',                    3,'GV. Trần Thị Mỹ Linh',  'HK2-2024-2025'),
('LUAT107','Luật đất đai',                     2,'GV. Phạm Quang Minh',   'HK2-2024-2025'),
('LUAT108','Kỹ năng tư vấn pháp lý',           3,'GV. Lê Thị Sakura',     'HK2-2024-2025'),

-- ── Kế toán (KTOAN104–KTOAN108) ──────────────────────────────────────────────
('KTOAN104','Kế toán quản trị',                3,'GV. Nguyễn Thị Hương',  'HK1-2024-2025'),
('KTOAN105','Thuế',                            3,'GV. Trần Minh Khải',    'HK1-2024-2025'),
('KTOAN106','Kế toán ngân hàng',               3,'GV. Lê Thị Phương',     'HK2-2024-2025'),
('KTOAN107','Phần mềm kế toán MISA',           2,'GV. Vũ Minh Tuấn',      'HK2-2024-2025'),
('KTOAN108','Kế toán tổng hợp và thực hành',   3,'GV. Đặng Thị Ngọc',     'HK2-2024-2025'),

-- ── Ngôn ngữ (NNGU104–NNGU108) ───────────────────────────────────────────────
('NNGU104','Ngữ pháp tiếng Anh nâng cao',      3,'GV. Phạm Văn Cường',    'HK1-2024-2025'),
('NNGU105','Tiếng Trung sơ cấp',               3,'GV. Hoàng Minh Tuấn',   'HK1-2024-2025'),
('NNGU106','Tiếng Pháp căn bản',               2,'GV. Vũ Đức Anh',        'HK2-2024-2025'),
('NNGU107','Biên phiên dịch chuyên ngành',     3,'GV. Bùi Thị Nga',       'HK2-2024-2025'),
('NNGU108','Ngôn ngữ học ứng dụng',            3,'GV. Ngô Văn Tuấn',      'HK2-2024-2025');
