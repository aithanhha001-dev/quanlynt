import streamlit as st
from modules.utils import crud_page
from modules.auth import current_user

COLUMN_CONFIG = {
    "id": None,
    "ma_nv": st.column_config.TextColumn("Mã NV", required=True),
    "nam": st.column_config.TextColumn("Năm", required=True),
    "loai_khen_thuong": st.column_config.TextColumn("Loại khen thưởng"),
    "quyet_dinh_so": st.column_config.TextColumn("Quyết định số"),
    "ngay_quyet_dinh": st.column_config.TextColumn("Ngày quyết định (dd/mm/yyyy)"),
}


def render():
    user = current_user()
    filter_ma_nv = None if user["vai_tro"] == "ADMIN" else user.get("ma_nv") or None
    crud_page(
        title="Khen thưởng theo năm",
        table="khenthuong",
        column_config=COLUMN_CONFIG,
        filter_ma_nv=filter_ma_nv,
        help_text="Danh sách các danh hiệu thi đua, khen thưởng theo từng năm học/năm công tác.",
    )
