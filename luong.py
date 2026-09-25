import streamlit as st
from modules.utils import crud_page
from modules.auth import current_user

COLUMN_CONFIG = {
    "id": None,
    "ma_nv": st.column_config.TextColumn("Mã NV", required=True),
    "thang": st.column_config.TextColumn("Tháng (YYYY-MM)", required=True),
    "he_so_luong": st.column_config.NumberColumn("Hệ số lương", min_value=0.0, step=0.01),
    "bac_luong": st.column_config.TextColumn("Bậc lương"),
    "phu_cap": st.column_config.NumberColumn("Phụ cấp (đồng)", min_value=0),
    "luong_co_ban": st.column_config.NumberColumn("Lương cơ bản (đồng)", min_value=0),
    "thuc_linh": st.column_config.NumberColumn("Thực lĩnh (đồng)", min_value=0),
}


def render():
    user = current_user()
    filter_ma_nv = None if user["vai_tro"] == "ADMIN" else user.get("ma_nv") or None
    crud_page(
        title="Quản lý lương",
        table="luong",
        column_config=COLUMN_CONFIG,
        filter_ma_nv=filter_ma_nv,
        help_text="Bảng lương hằng tháng theo hệ số, bậc lương, phụ cấp và thực lĩnh của từng nhân sự.",
    )
