import streamlit as st
from modules.utils import crud_page
from modules.auth import current_user

COLUMN_CONFIG = {
    "id": None,
    "ma_nv": st.column_config.TextColumn("Mã NV", required=True),
    "thang": st.column_config.TextColumn("Tháng (YYYY-MM)", required=True),
    "so_ngay_cong": st.column_config.NumberColumn("Số ngày công", min_value=0, max_value=31),
    "nghi_phep": st.column_config.NumberColumn("Nghỉ phép", min_value=0, max_value=31),
    "nghi_khong_phep": st.column_config.NumberColumn("Nghỉ không phép", min_value=0, max_value=31),
    "ghi_chu": st.column_config.TextColumn("Ghi chú"),
}


def render():
    user = current_user()
    filter_ma_nv = None if user["vai_tro"] == "ADMIN" else user.get("ma_nv") or None
    crud_page(
        title="Chấm công theo tháng",
        table="chamcong",
        column_config=COLUMN_CONFIG,
        filter_ma_nv=filter_ma_nv,
        help_text="Theo dõi ngày công, nghỉ phép, nghỉ không phép hằng tháng theo từng nhân sự (Mã NV).",
    )
