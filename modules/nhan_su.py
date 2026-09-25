import streamlit as st
from modules.utils import crud_page

COLUMN_CONFIG = {
    "ma_nv": st.column_config.TextColumn("Mã NV", required=True),
    "ho_ten": st.column_config.TextColumn("Họ và tên", required=True),
    "ngay_sinh": st.column_config.TextColumn("Ngày sinh (dd/mm/yyyy)"),
    "gioi_tinh": st.column_config.SelectboxColumn("Giới tính", options=["Nam", "Nữ"]),
    "chuc_vu": st.column_config.TextColumn("Chức vụ"),
    "to_bo_mon": st.column_config.TextColumn("Tổ bộ môn"),
    "dien_thoai": st.column_config.TextColumn("Điện thoại"),
    "ngay_vao_lam": st.column_config.TextColumn("Ngày vào làm (dd/mm/yyyy)"),
    "trang_thai": st.column_config.SelectboxColumn(
        "Trạng thái", options=["Đang công tác", "Nghỉ thai sản", "Biệt phái", "Đã nghỉ việc", "Nghỉ hưu"]
    ),
}


def render():
    crud_page(
        title="Danh sách nhân sự",
        table="nhansu",
        column_config=COLUMN_CONFIG,
        help_text="Danh mục cán bộ, giáo viên, nhân viên toàn trường — là dữ liệu gốc cho các module Chấm công, Đánh giá, Lương, Thâm niên, Khen thưởng (liên kết theo Mã NV).",
    )
