"""
Lớp truy xuất dữ liệu (Data Access Layer) cho toàn bộ hệ thống.

- Dùng SQLite (file school.db) làm kho dữ liệu: miễn phí, không cần server riêng,
  đủ tốt cho quy mô một trường THCS (vài chục đến vài trăm nhân sự).
- LƯU Ý QUAN TRỌNG khi triển khai trên Streamlit Community Cloud (miễn phí):
  ổ đĩa của server là "tạm thời" (ephemeral) - dữ liệu có thể bị xoá khi app
  được khởi động lại hoặc redeploy. Vì vậy hệ thống có sẵn chức năng
  "Sao lưu / Phục hồi" (xuất - nhập toàn bộ dữ liệu ra file Excel) ở trang
  Trang chủ. Nhà trường nên bấm "Sao lưu toàn bộ" định kỳ (cuối tuần/cuối tháng)
  và lưu file đó vào Google Drive/máy tính.
  Nếu muốn dữ liệu tự động bền vững 100% trên bản miễn phí, có thể nâng cấp
  sau này bằng cách thay lớp này bằng kết nối Google Sheets
  (thư viện `st-gsheets-connection`) hoặc một CSDL cloud miễn phí như Supabase -
  toàn bộ phần giao diện (modules/*.py) KHÔNG cần sửa vì chỉ gọi qua các hàm
  get_df() / replace_table() bên dưới.
"""

import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime

import pandas as pd

DB_PATH = Path(__file__).resolve().parent.parent / "school.db"

# Khai báo cấu trúc (schema) từng bảng: tên cột -> kiểu dữ liệu SQLite
SCHEMAS = {
    "nhansu": {
        "ma_nv": "TEXT PRIMARY KEY",
        "ho_ten": "TEXT",
        "ngay_sinh": "TEXT",
        "gioi_tinh": "TEXT",
        "chuc_vu": "TEXT",
        "to_bo_mon": "TEXT",
        "dien_thoai": "TEXT",
        "ngay_vao_lam": "TEXT",
        "trang_thai": "TEXT",
    },
    "chamcong": {
        "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "ma_nv": "TEXT",
        "thang": "TEXT",          # định dạng YYYY-MM
        "so_ngay_cong": "REAL",
        "nghi_phep": "REAL",
        "nghi_khong_phep": "REAL",
        "ghi_chu": "TEXT",
    },
    "danhgia": {
        "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "ma_nv": "TEXT",
        "nam": "TEXT",
        "xep_loai": "TEXT",
        "diem": "REAL",
        "nhan_xet": "TEXT",
    },
    "luong": {
        "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "ma_nv": "TEXT",
        "thang": "TEXT",
        "he_so_luong": "REAL",
        "bac_luong": "TEXT",
        "phu_cap": "REAL",
        "luong_co_ban": "REAL",
        "thuc_linh": "REAL",
    },
    "thamnien": {
        "ma_nv": "TEXT PRIMARY KEY",
        "ngay_vao_nganh": "TEXT",
        "so_nam_cong_tac": "REAL",
        "phu_cap_tham_nien_percent": "REAL",
    },
    "khenthuong": {
        "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "ma_nv": "TEXT",
        "nam": "TEXT",
        "loai_khen_thuong": "TEXT",
        "quyet_dinh_so": "TEXT",
        "ngay_quyet_dinh": "TEXT",
    },
    "users": {
        "username": "TEXT PRIMARY KEY",
        "password_hash": "TEXT",
        "ho_ten": "TEXT",
        "vai_tro": "TEXT",       # ADMIN / GIAOVIEN / NHANVIEN
        "ma_nv": "TEXT",         # liên kết tới bảng nhansu (để phân quyền xem dữ liệu của chính mình)
        "trang_thai": "TEXT",    # Hoạt động / Khoá
    },
}


def _connect():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def hash_password(raw_password: str) -> str:
    return hashlib.sha256(raw_password.encode("utf-8")).hexdigest()


def init_db():
    """Tạo toàn bộ bảng nếu chưa tồn tại + tài khoản admin mặc định."""
    conn = _connect()
    cur = conn.cursor()
    for table, cols in SCHEMAS.items():
        col_defs = ", ".join(f'"{c}" {t}' for c, t in cols.items())
        cur.execute(f'CREATE TABLE IF NOT EXISTS "{table}" ({col_defs});')
    conn.commit()

    # Seed tài khoản quản trị mặc định nếu bảng users đang trống
    cur.execute("SELECT COUNT(*) FROM users;")
    if cur.fetchone()[0] == 0:
        cur.execute(
            "INSERT INTO users (username, password_hash, ho_ten, vai_tro, ma_nv, trang_thai) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            ("admin", hash_password("admin123"), "Quản trị viên", "ADMIN", "", "Hoạt động"),
        )
        conn.commit()
    conn.close()


def get_df(table: str) -> pd.DataFrame:
    """Đọc toàn bộ 1 bảng thành DataFrame (không kèm cột password_hash khi table=users)."""
    conn = _connect()
    df = pd.read_sql_query(f'SELECT * FROM "{table}"', conn)
    conn.close()
    return df


def replace_table(table: str, df: pd.DataFrame):
    """Ghi đè toàn bộ 1 bảng bằng nội dung DataFrame mới (dùng sau khi sửa/thêm/xoá dòng trên giao diện)."""
    df = df.copy()
    # Loại bỏ dòng hoàn toàn trống (Streamlit data_editor có thể sinh ra khi bấm "+ ")
    df = df.dropna(how="all")
    conn = _connect()
    df.to_sql(table, conn, if_exists="replace", index=False)
    conn.close()


def run_query(sql: str, params: tuple = ()) -> pd.DataFrame:
    conn = _connect()
    df = pd.read_sql_query(sql, conn, params=params)
    conn.close()
    return df


def execute(sql: str, params: tuple = ()):
    conn = _connect()
    conn.execute(sql, params)
    conn.commit()
    conn.close()


def backup_to_excel_bytes() -> bytes:
    """Xuất TOÀN BỘ dữ liệu (trừ mật khẩu) ra 1 file Excel nhiều sheet để sao lưu."""
    import io
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        for table in SCHEMAS:
            df = get_df(table)
            if table == "users" and "password_hash" in df.columns:
                df = df.drop(columns=["password_hash"])
            df.to_excel(writer, sheet_name=table[:31], index=False)
    buf.seek(0)
    return buf.getvalue()


def restore_from_excel(file) -> list:
    """Phục hồi dữ liệu từ file Excel sao lưu (ghi đè các bảng có sheet trùng tên)."""
    restored = []
    xls = pd.ExcelFile(file)
    for table in SCHEMAS:
        if table in xls.sheet_names and table != "users":
            df = pd.read_excel(xls, sheet_name=table)
            replace_table(table, df)
            restored.append(table)
    return restored


def now_str() -> str:
    return datetime.now().strftime("%d/%m/%Y %H:%M")
