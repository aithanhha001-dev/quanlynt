import streamlit as st
from modules.utils import crud_page
from modules.auth import current_user

COLUMN_CONFIG = {
    "ma_nv": st.column_config.TextColumn("Mã NV", required=True),
    "ngay_vao_nganh": st.column_config.TextColumn("Ngày vào ngành (dd/mm/yyyy)"),
    "so_nam_cong_tac": st.column_config.NumberColumn("Số năm công tác", min_value=0.0, step=0.5),
    "phu_cap_tham_nien_percent": st.column_config.NumberColumn("Phụ cấp thâm niên (%)", min_value=0.0, max_value=100.0),
}


def render():
    user = current_user()
    filter_ma_nv = None if user["vai_tro"] == "ADMIN" else user.get("ma_nv") or None
    crud_page(
        title="Quản lý thâm niên",
        table="thamnien",
        column_config=COLUMN_CONFIG,
        filter_ma_nv=filter_ma_nv,
        help_text="Theo dõi ngày vào ngành, số năm công tác và tỷ lệ % phụ cấp thâm niên nhà giáo.",
    )
