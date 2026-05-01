# utils/config.py

API_BASE_URL = "http://localhost:8000"
BASE_URL = API_BASE_URL

APP_NAME = "EduStu"
APP_VERSION = "1.0.0"

DB_HOST = "localhost"
DB_NAME = "edustu" # Ten database de theo tren may
DB_PORT = 3306
DB_USER = "root"
DB_PASSWORD = "110252702Nhat" # Mat khau de theo tren may

# Mau sac dung trong QSS — Dark theme (khop voi Login)
PRIMARY    = "#0D1B3E"   # nen toi chinh
SECONDARY  = "#0A1628"   # sidebar / panel toi
ACCENT     = "#2563EB"   # blue chinh
HIGHLIGHT  = "#2563EB"   # brand / active
TEXT_LIGHT = "#F1F5F9"   # chu trang tren nen toi
TEXT_MUTED = "#94A3B8"   # chu mo tren nen toi
BORDER     = "#1E3659"   # vien toi
WHITE      = "#FFFFFF"
CARD_BG    = "#FFFFFF"   # nen card trang noi bat
SUCCESS    = "#10B981"
WARNING    = "#F59E0B"
DANGER     = "#EF4444"
INFO       = "#3B82F6"

# Cau hinh nghiep vu
TRONG_SO_GK = 0.4
TRONG_SO_CK = 0.6

# Du lieu co dinh
TRANG_THAI_SV = ["Đang học", "Bảo lưu", "Thôi học", "Cảnh báo"]
TRANG_THAI_HP = ["Đã nộp", "Nộp thiếu", "Chưa nộp", "Quá hạn"]
HOC_KY_LIST = ["HK1-2024-2025", "HK2-2024-2025", "HK1-2023-2024"]
KHOA_LIST = [
    "Công nghệ thông tin",
    "Kinh tế",
    "Xây dựng",
    "Ngoại ngữ",
    "Điện - Điện tử",
    "Cơ khí",
    "Kế toán",
    "Quản trị kinh doanh",
]
GIOI_TINH = ["Nam", "Nữ", "Khác"]

# ── Phân quyền theo module ────────────────────────────────────────────────────
# Mỗi role được phép thực hiện các action nào trong từng module
PERMISSIONS: dict[str, dict[str, list[str]]] = {
    "admin": {
        "sinhvien": ["view", "add", "edit", "delete"],
        "giayto":   ["view", "edit", "manage_types"],
        "hocphi":   ["view", "add", "edit"],
        "baocao":   ["view", "export"],
        "diem":     ["view", "add", "edit"],
    },
    "phongdt": {
        "sinhvien": ["view", "add", "edit"],   # không xóa
        "giayto":   ["view", "edit"],          # không quản lý loại GT
        "hocphi":   ["view", "add", "edit"],
        "baocao":   ["view", "export"],
        "diem":     ["view", "add", "edit"],
    },
    "giaovien": {
        "sinhvien": ["view"],                  # chỉ xem danh sách
        "giayto":   [],                        # không truy cập
        "hocphi":   [],                        # không truy cập
        "baocao":   ["view"],
        "diem":     ["view", "add", "edit"],   # nhập điểm
    },
}
