import streamlit as st
import pandas as pd
from modules import db
from modules.auth import current_user, require_role


def render():
    user = current_user()
    st.title("📊 Trang chủ")
    st.caption(f"Xin chào **{user.get('ho_ten')}** — chúc một ngày làm việc hiệu quả!")

    nhansu = db.get_df("nhansu")
    total = len(nhansu)
    dang_ct = (nhansu["trang_thai"] == "Đang công tác").sum() if total else 0
    nghi = total - dang_ct

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Tổng nhân sự", total)
    c2.metric("Đang công tác", int(dang_ct))
    c3.metric("Khác (nghỉ/biệt phái...)", int(nghi))
    c4.metric("Khen thưởng đã ghi nhận", len(db.get_df("khenthuong")))

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Cơ cấu theo tổ bộ môn")
        if total and nhansu["to_bo_mon"].notna().any():
            st.bar_chart(nhansu["to_bo_mon"].value_counts())
        else:
            st.info("Chưa có dữ liệu.")
    with col2:
        st.subheader("Cơ cấu theo giới tính")
        if total and nhansu["gioi_tinh"].notna().any():
            st.bar_chart(nhansu["gioi_tinh"].value_counts())
        else:
            st.info("Chưa có dữ liệu.")

    if user["vai_tro"] == "ADMIN":
        st.divider()
        st.subheader("🗄️ Sao lưu & Phục hồi dữ liệu")
        st.caption(
            "Trên bản Streamlit Community Cloud miễn phí, ổ đĩa lưu trữ có thể bị đặt lại khi app khởi động lại. "
            "Hãy tải file sao lưu định kỳ (ví dụ cuối mỗi tuần) và lưu vào Google Drive/máy tính để đảm bảo an toàn dữ liệu."
        )
        b1, b2 = st.columns(2)
        with b1:
            st.download_button(
                "⬇️ Sao lưu toàn bộ dữ liệu (Excel)",
                data=db.backup_to_excel_bytes(),
                file_name=f"backup_qlnt_{db.now_str().replace('/', '-').replace(':', 'h').replace(' ', '_')}.xlsx",
                use_container_width=True,
            )
        with b2:
            f = st.file_uploader("⬆️ Phục hồi từ file sao lưu (.xlsx)", type=["xlsx"], key="restore_uploader")
            if f is not None and st.button("Xác nhận phục hồi (sẽ GHI ĐÈ dữ liệu hiện tại)", type="primary"):
                restored = db.restore_from_excel(f)
                st.success(f"Đã phục hồi các bảng: {', '.join(restored)}")
                st.rerun()
