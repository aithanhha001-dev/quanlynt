import streamlit as st
from modules import db, auth
from modules import trang_chu, nhan_su, cham_cong, danh_gia, luong, tham_nien, khen_thuong, tai_khoan

st.set_page_config(page_title="QL Nhà trường", page_icon="🏫", layout="wide")
db.init_db()

# ---------------------------------------------------------------------------
# CSS: tạo sidebar nền tối, nút menu bo góc, giống giao diện ảnh mẫu
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
        section[data-testid="stSidebar"] {
            background-color: #111827;
        }
        section[data-testid="stSidebar"] * { color: #e5e7eb; }
        section[data-testid="stSidebar"] .stButton button {
            width: 100%;
            text-align: left;
            background-color: transparent;
            border: none;
            padding: 8px 12px;
            border-radius: 8px;
            margin-bottom: 2px;
        }
        section[data-testid="stSidebar"] .stButton button:hover {
            background-color: #1f2937;
            color: #fff;
        }
        section[data-testid="stSidebar"] .active-menu button {
            background-color: #2563eb !important;
            color: #fff !important;
        }
        .group-caption {
            font-size: 11px;
            letter-spacing: .05em;
            color: #9ca3af;
            margin: 14px 0 4px 4px;
            text-transform: uppercase;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Chưa đăng nhập -> hiển thị màn hình đăng nhập rồi dừng lại
# ---------------------------------------------------------------------------
if not auth.is_logged_in():
    auth.login_form()
    st.stop()

user = auth.current_user()

# ---------------------------------------------------------------------------
# Khai báo menu theo vai trò: {tên nhóm: [(nhãn, icon, hàm_render), ...]}
# ---------------------------------------------------------------------------
ADMIN_MENU = {
    "Tổng quan": [("Trang chủ", "🏠", trang_chu.render)],
    "1. Quản lý nhân sự": [
        ("Danh sách nhân sự", "👥", nhan_su.render),
        ("Chấm công theo tháng", "🗓️", cham_cong.render),
        ("Đánh giá nhân sự", "⭐", danh_gia.render),
    ],
    "2. Lương & thâm niên": [
        ("Quản lý lương", "💰", luong.render),
        ("Quản lý thâm niên", "📈", tham_nien.render),
    ],
    "3. Thi đua – khen thưởng": [
        ("Khen thưởng theo năm", "🏆", khen_thuong.render),
    ],
    "Hệ thống": [
        ("Tài khoản đăng nhập", "🔑", tai_khoan.render),
    ],
}

STAFF_MENU = {
    "Tổng quan": [("Trang chủ", "🏠", trang_chu.render)],
    "Thông tin của tôi": [
        ("Chấm công theo tháng", "🗓️", cham_cong.render),
        ("Đánh giá nhân sự", "⭐", danh_gia.render),
        ("Quản lý lương", "💰", luong.render),
        ("Quản lý thâm niên", "📈", tham_nien.render),
        ("Khen thưởng theo năm", "🏆", khen_thuong.render),
    ],
}

menu_dict = ADMIN_MENU if user["vai_tro"] == "ADMIN" else STAFF_MENU

if "active_page" not in st.session_state:
    st.session_state.active_page = "Trang chủ"

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🏫 QL Nhà trường")
    for group, items in menu_dict.items():
        st.markdown(f"<div class='group-caption'>{group}</div>", unsafe_allow_html=True)
        for label, icon, _ in items:
            is_active = st.session_state.active_page == label
            wrapper_class = "active-menu" if is_active else ""
            st.markdown(f"<div class='{wrapper_class}'>", unsafe_allow_html=True)
            if st.button(f"{icon}  {label}", key=f"nav_{label}", use_container_width=True):
                st.session_state.active_page = label
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Thanh trạng thái phía trên (giống ảnh mẫu: đồng bộ cloud, ngày, user, đổi MK, đăng xuất)
# ---------------------------------------------------------------------------
top1, top2, top3, top4, top5 = st.columns([3, 1.4, 2, 1, 1])
with top1:
    st.markdown(f"### {st.session_state.active_page}")
with top2:
    st.markdown(
        "<div style='color:#16a34a;font-weight:600;padding-top:14px;'>✅ Đã lưu cục bộ (SQLite)</div>",
        unsafe_allow_html=True,
    )
with top3:
    st.markdown(f"<div style='padding-top:14px;'>{db.now_str()}</div>", unsafe_allow_html=True)
with top4:
    if st.button("🔒 Đổi MK", use_container_width=True):
        auth.change_password_dialog()
with top5:
    if st.button("🚪 Đăng xuất", use_container_width=True):
        auth.logout()

st.markdown(f"**{user['ho_ten']}** &nbsp;·&nbsp; _{user['vai_tro']}_", unsafe_allow_html=True)
st.divider()

# ---------------------------------------------------------------------------
# Định tuyến: gọi hàm render() tương ứng với trang đang chọn
# ---------------------------------------------------------------------------
page_actions = {label: action for items in menu_dict.values() for (label, icon, action) in items}
render_fn = page_actions.get(st.session_state.active_page, trang_chu.render)
render_fn()
