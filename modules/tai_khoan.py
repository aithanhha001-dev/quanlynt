import streamlit as st
import pandas as pd
from modules import db
from modules.auth import require_role, current_user


def render():
    require_role("ADMIN")
    st.title("🔑 Tài khoản đăng nhập")
    st.caption("Chỉ Quản trị viên (ADMIN) mới thấy và chỉnh sửa được trang này.")

    users = db.get_df("users").drop(columns=["password_hash"])

    st.subheader("Danh sách tài khoản")
    edited = st.data_editor(
        users,
        use_container_width=True,
        num_rows="fixed",  # không thêm/xoá trực tiếp ở đây vì cần đặt mật khẩu ban đầu — dùng form bên dưới
        disabled=["username"],
        column_config={
            "username": st.column_config.TextColumn("Tài khoản"),
            "ho_ten": st.column_config.TextColumn("Họ tên"),
            "vai_tro": st.column_config.SelectboxColumn("Vai trò", options=["ADMIN", "GIAOVIEN", "NHANVIEN"]),
            "ma_nv": st.column_config.TextColumn("Mã NV liên kết"),
            "trang_thai": st.column_config.SelectboxColumn("Trạng thái", options=["Hoạt động", "Khoá"]),
        },
        key="editor_users",
    )
    if st.button("💾 Lưu thay đổi vai trò / trạng thái / mã NV liên kết", type="primary"):
        full = db.get_df("users")
        for _, row in edited.iterrows():
            db.execute(
                "UPDATE users SET ho_ten=?, vai_tro=?, ma_nv=?, trang_thai=? WHERE username=?",
                (row["ho_ten"], row["vai_tro"], row["ma_nv"], row["trang_thai"], row["username"]),
            )
        st.success("Đã lưu thay đổi.")
        st.rerun()

    st.divider()
    st.subheader("➕ Tạo tài khoản mới")
    with st.form("new_user_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            new_username = st.text_input("Tài khoản đăng nhập")
            new_hoten = st.text_input("Họ tên")
            new_vaitro = st.selectbox("Vai trò", ["GIAOVIEN", "NHANVIEN", "ADMIN"])
        with c2:
            new_manv = st.text_input("Mã NV liên kết (tra ở Danh sách nhân sự, để trống nếu là ADMIN)")
            new_pw = st.text_input("Mật khẩu ban đầu", type="password", value="123456")
        submitted = st.form_submit_button("Tạo tài khoản", use_container_width=True)
        if submitted:
            existing = db.run_query("SELECT 1 FROM users WHERE username=?", (new_username.strip(),))
            if not new_username.strip():
                st.error("Vui lòng nhập tài khoản đăng nhập.")
            elif not existing.empty:
                st.error("Tài khoản này đã tồn tại.")
            else:
                db.execute(
                    "INSERT INTO users (username, password_hash, ho_ten, vai_tro, ma_nv, trang_thai) VALUES (?,?,?,?,?,?)",
                    (new_username.strip(), db.hash_password(new_pw), new_hoten, new_vaitro, new_manv.strip(), "Hoạt động"),
                )
                st.success(f"Đã tạo tài khoản '{new_username}'. Mật khẩu ban đầu: {new_pw}")
                st.rerun()

    st.divider()
    st.subheader("🔓 Đặt lại mật khẩu cho một tài khoản")
    all_users = db.get_df("users")["username"].tolist()
    target = st.selectbox("Chọn tài khoản", [u for u in all_users if u != current_user()["username"]] or ["(không có)"])
    new_pw2 = st.text_input("Mật khẩu mới", type="password", key="reset_pw")
    if st.button("Đặt lại mật khẩu"):
        if target == "(không có)":
            st.warning("Không có tài khoản khác để đặt lại.")
        elif len(new_pw2) < 6:
            st.error("Mật khẩu cần tối thiểu 6 ký tự.")
        else:
            db.execute("UPDATE users SET password_hash=? WHERE username=?", (db.hash_password(new_pw2), target))
            st.success(f"Đã đặt lại mật khẩu cho '{target}'.")
