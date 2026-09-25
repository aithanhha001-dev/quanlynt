import streamlit as st
from modules import db


def _get_user(username: str):
    df = db.run_query("SELECT * FROM users WHERE username = ?", (username,))
    if df.empty:
        return None
    return df.iloc[0].to_dict()


def login_form():
    """Hiển thị màn hình đăng nhập. Trả về True nếu đã đăng nhập thành công."""
    st.markdown(
        "<h2 style='text-align:center;margin-top:60px;'>🏫 HỆ THỐNG QUẢN LÝ NHÀ TRƯỜNG</h2>",
        unsafe_allow_html=True,
    )
    col = st.columns([1, 1.2, 1])[1]
    with col:
        with st.form("login_form"):
            st.subheader("Đăng nhập")
            username = st.text_input("Tài khoản")
            password = st.text_input("Mật khẩu", type="password")
            submitted = st.form_submit_button("Đăng nhập", use_container_width=True)
        if submitted:
            user = _get_user(username.strip())
            if not user or user["password_hash"] != db.hash_password(password):
                st.error("Sai tài khoản hoặc mật khẩu.")
            elif user["trang_thai"] != "Hoạt động":
                st.error("Tài khoản đã bị khoá. Liên hệ quản trị viên.")
            else:
                st.session_state.user = {
                    "username": user["username"],
                    "ho_ten": user["ho_ten"],
                    "vai_tro": user["vai_tro"],
                    "ma_nv": user["ma_nv"],
                }
                st.rerun()
        st.caption("Tài khoản quản trị mặc định: **admin / admin123** — hãy đổi mật khẩu ngay sau khi đăng nhập lần đầu.")
    return False


def is_logged_in() -> bool:
    return "user" in st.session_state


def current_user() -> dict:
    return st.session_state.get("user", {})


def logout():
    st.session_state.pop("user", None)
    st.rerun()


def change_password_dialog():
    @st.dialog("Đổi mật khẩu")
    def _dialog():
        old = st.text_input("Mật khẩu hiện tại", type="password")
        new1 = st.text_input("Mật khẩu mới", type="password")
        new2 = st.text_input("Nhập lại mật khẩu mới", type="password")
        if st.button("Xác nhận", use_container_width=True):
            user = _get_user(current_user()["username"])
            if user["password_hash"] != db.hash_password(old):
                st.error("Mật khẩu hiện tại không đúng.")
            elif len(new1) < 6:
                st.error("Mật khẩu mới cần tối thiểu 6 ký tự.")
            elif new1 != new2:
                st.error("Hai lần nhập mật khẩu mới không khớp.")
            else:
                db.execute(
                    "UPDATE users SET password_hash = ? WHERE username = ?",
                    (db.hash_password(new1), current_user()["username"]),
                )
                st.success("Đổi mật khẩu thành công!")
                st.rerun()
    _dialog()


def require_role(*roles):
    """Chặn trang nếu vai trò hiện tại không nằm trong danh sách cho phép."""
    if current_user().get("vai_tro") not in roles:
        st.warning("Bạn không có quyền truy cập chức năng này.")
        st.stop()
