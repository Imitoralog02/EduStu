from __future__ import annotations

from datetime import datetime


def fmt_date(value: str) -> str:
    if not value:
        return ""
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(value[:19], fmt).strftime("%d/%m/%Y")
        except ValueError:
            continue
    return value


def fmt_money(value: float | int | None) -> str:
    if value is None:
        return "0 VND"
    return f"{value:,.0f} VND"


def fmt_gpa(value: float | int | None) -> str:
    if value is None:
        return "0.00"
    return f"{float(value):.2f}"


def xep_loai(gpa: float | int | None) -> str:
    if gpa is None:
        return "Chua co"
    gpa = float(gpa)
    if gpa >= 3.6:
        return "Xuat sac"
    if gpa >= 3.2:
        return "Gioi"
    if gpa >= 2.5:
        return "Kha"
    if gpa >= 2.0:
        return "Trung binh"
    if gpa >= 1.0:
        return "Yeu"
    return "Kem"


def badge_color(text: str) -> tuple[str, str]:
    normalized = (text or "").strip().lower()
    mapping = {
        "dang hoc": ("#19324d", "#7cc7ff"),
        "thoi hoc": ("#4a1f27", "#ff9aa9"),
        "tot nghiep": ("#1f3d2b", "#7ee2a8"),
        "bao luu": ("#4a3b1f", "#ffd27a"),
        "dat": ("#1f3d2b", "#7ee2a8"),
        "khong dat": ("#4a1f27", "#ff9aa9"),
        "da dong": ("#1f3d2b", "#7ee2a8"),
        "dong thieu": ("#4a3b1f", "#ffd27a"),
        "chua dong": ("#4a1f27", "#ff9aa9"),
    }
    return mapping.get(normalized, ("#243046", "#eaeaea"))
