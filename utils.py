import io
import pandas as pd
import streamlit as st
from modules import db


def df_to_excel_bytes(df: pd.DataFrame, sheet_name="Data") -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)
    return buf.getvalue()


def crud_page(
    title: str,
    table: str,
    column_config: dict | None = None,
    search_cols: list | None = None,
    filter_ma_nv: str | None = None,
    help_text: str | None = None,
):
    """
    Trang quản lý dữ liệu kiểu bảng dùng chung cho mọi module:
    - Tìm kiếm nhanh
    - Sửa / thêm / xoá trực tiếp trên bảng (giống Excel) rồi bấm "Lưu thay đổi"
    - Tải file mẫu Excel / Upload Excel để nhập nhanh / Xuất Excel dữ liệu hiện tại

    filter_ma_nv: nếu được truyền (áp dụng cho tài khoản Giáo viên/Nhân viên),
    chỉ hiển thị & chỉ cho lưu lại dữ liệu của đúng mã nhân viên đó.
    """
    st.title(title)
    if help_text:
        st.caption(help_text)

    df = db.get_df(table)

    if filter_ma_nv:
        df = df[df["ma_nv"] == filter_ma_nv].reset_index(drop=True)

    c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
    with c1:
        search = st.text_input("🔍 Tìm kiếm nhanh...", key=f"search_{table}", label_visibility="collapsed", placeholder="🔍 Tìm kiếm nhanh...")
    with c2:
        st.download_button(
            "📄 Tải File mẫu",
            data=df_to_excel_bytes(pd.DataFrame(columns=df.columns), "Mau"),
            file_name=f"mau_{table}.xlsx",
            use_container_width=True,
            key=f"tpl_{table}",
        )
    with c3:
        uploaded = st.file_uploader("Upload Excel", type=["xlsx"], key=f"up_{table}", label_visibility="collapsed")
    with c4:
        st.download_button(
            "📥 Xuất Excel",
            data=df_to_excel_bytes(df, table),
            file_name=f"{table}_{db.now_str().replace('/', '-').replace(':', 'h').replace(' ', '_')}.xlsx",
            use_container_width=True,
            key=f"exp_{table}",
        )

    if uploaded is not None:
        new_rows = pd.read_excel(uploaded)
        mode = st.radio(
            "Cách nhập dữ liệu từ Excel:",
            ["Thêm vào danh sách hiện tại", "Ghi đè toàn bộ danh sách"],
            horizontal=True,
            key=f"mode_{table}",
        )
        if st.button("✅ Xác nhận nhập dữ liệu", key=f"confirm_up_{table}"):
            if mode.startswith("Thêm"):
                merged = pd.concat([db.get_df(table), new_rows], ignore_index=True)
            else:
                merged = new_rows
            db.replace_table(table, merged)
            st.success(f"Đã nhập {len(new_rows)} dòng vào '{title}'.")
            st.rerun()

    view_df = df.copy()
    if search:
        mask = view_df.astype(str).apply(lambda col: col.str.contains(search, case=False, na=False)).any(axis=1)
        view_df = view_df[mask]

    st.caption("💡 Sửa trực tiếp trong bảng, bấm dấu **+** ở dòng cuối để thêm mới, chọn dòng rồi bấm biểu tượng thùng rác để xoá — sau đó bấm **Lưu thay đổi**.")
    edited = st.data_editor(
        view_df,
        num_rows="dynamic",
        use_container_width=True,
        column_config=column_config,
        key=f"editor_{table}",
    )

    col_save, col_count = st.columns([1, 5])
    with col_save:
        if st.button("💾 Lưu thay đổi", type="primary", key=f"save_{table}"):
            if filter_ma_nv:
                edited["ma_nv"] = filter_ma_nv
                others = db.get_df(table)
                others = others[others["ma_nv"] != filter_ma_nv]
                final = pd.concat([others, edited], ignore_index=True)
            else:
                final = edited
            db.replace_table(table, final)
            st.success("Đã lưu thay đổi.")
            st.rerun()
    with col_count:
        st.caption(f"Tổng số dòng: {len(view_df)}")
