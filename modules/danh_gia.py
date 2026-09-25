import streamlit as st
from modules.utils import crud_page
from modules.auth import current_user

COLUMN_CONFIG = {
    "id": None,
    "ma_nv": st.column_config.TextColumn("Mã NV", required=True),
    "nam": st.column_config.TextColumn("Năm học", required=True),
    "xep_loai": st.column_config.SelectboxColumn(
        "Xếp loại", options=["Xuất sắc", "Tốt", "Hoàn thành", "Không hoàn thành"]
    ),
    "diem": st.column_config.NumberColumn("Điểm", min_value=0, max_value=100),
    "nhan_xet": st.column_config.TextColumn("Nhận xét"),
}


def render():
    user = current_user()
    filter_ma_nv = None if user["vai_tro"] == "ADMIN" else user.get("ma_nv") or None
    crud_page(
        title="Đánh giá nhân sự",
        table="danhgia",
        column_config=COLUMN_CONFIG,
        filter_ma_nv=filter_ma_nv,
        help_text="Kết quả đánh giá, xếp loại viên chức theo từng năm học.",
    )
