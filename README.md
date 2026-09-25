# Hệ thống Quản lý Nhà trường (Streamlit)

Ứng dụng web quản lý nhân sự, chấm công, đánh giá, lương, thâm niên và thi đua – khen thưởng
dành cho trường THCS, xây dựng bằng Python + Streamlit, dữ liệu lưu bằng SQLite.

## 1. Chức năng

| Nhóm | Chức năng |
|---|---|
| Tổng quan | Dashboard: tổng số nhân sự, biểu đồ theo tổ bộ môn/giới tính, sao lưu & phục hồi dữ liệu |
| Quản lý nhân sự | Danh sách nhân sự, Chấm công theo tháng, Đánh giá nhân sự |
| Lương & thâm niên | Quản lý lương, Quản lý thâm niên |
| Thi đua – khen thưởng | Khen thưởng theo năm |
| Hệ thống | Tài khoản đăng nhập (chỉ ADMIN), đổi mật khẩu |

Mỗi trang danh sách đều có: tìm kiếm nhanh, sửa/thêm/xoá trực tiếp trên bảng (giống Excel),
tải file mẫu, upload Excel để nhập nhanh, xuất Excel dữ liệu hiện tại.

**Phân quyền:** tài khoản `ADMIN` thấy và sửa được toàn bộ dữ liệu; tài khoản `GIAOVIEN`/`NHANVIEN`
chỉ thấy dữ liệu (chấm công, lương, thâm niên, đánh giá, khen thưởng) của chính mình, theo Mã NV
được gán khi tạo tài khoản.

## 2. Cấu trúc dự án

```
app.py                  # Điều hướng, đăng nhập, sidebar, thanh trạng thái
modules/
  db.py                 # Lớp truy xuất dữ liệu (SQLite)
  auth.py               # Đăng nhập, đổi mật khẩu, kiểm tra quyền
  utils.py              # Trang CRUD dùng chung (tìm kiếm, sửa/thêm/xoá, Excel)
  trang_chu.py          # Dashboard + Sao lưu/Phục hồi
  nhan_su.py            # Danh sách nhân sự
  cham_cong.py          # Chấm công theo tháng
  danh_gia.py           # Đánh giá nhân sự
  luong.py              # Quản lý lương
  tham_nien.py          # Quản lý thâm niên
  khen_thuong.py        # Khen thưởng theo năm
  tai_khoan.py          # Quản lý tài khoản đăng nhập
requirements.txt
.streamlit/config.toml  # Giao diện (màu sắc)
```

## 3. Chạy thử trên máy cá nhân

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate | macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Trình duyệt tự mở tại `http://localhost:8501`.
Tài khoản mặc định: **admin / admin123** — hãy đổi mật khẩu ngay ở nút "Đổi MK" sau khi đăng nhập lần đầu.

## 4. Đưa lên GitHub

```bash
git init
git add .
git commit -m "Khởi tạo hệ thống quản lý nhà trường"
git branch -M main
git remote add origin https://github.com/<ten-tai-khoan>/<ten-repo>.git
git push -u origin main
```

> File `.gitignore` đã loại `school.db` ra khỏi Git để không đưa dữ liệu thật lên kho công khai.

## 5. Triển khai miễn phí trên Streamlit Community Cloud

1. Truy cập https://share.streamlit.io , đăng nhập bằng tài khoản GitHub.
2. Bấm **"New app"** → chọn repository vừa đẩy lên → chọn nhánh `main` → file chính `app.py`.
3. Bấm **Deploy**. Sau 1–2 phút, ứng dụng có địa chỉ dạng
   `https://<ten-app>.streamlit.app` để nhà trường truy cập từ máy tính hoặc điện thoại.
4. Mỗi lần `git push` cập nhật code, app trên Cloud sẽ tự build lại.

### Lưu ý quan trọng về dữ liệu trên bản miễn phí

Ổ đĩa của Streamlit Community Cloud là **tạm thời**: khi app "ngủ" do không có người dùng
trong vài ngày, hoặc khi bạn cập nhật code, dữ liệu trong file `school.db` có thể bị đặt lại
từ đầu. Vì vậy:

- Vào **Trang chủ → Sao lưu & Phục hồi**, bấm **"Sao lưu toàn bộ dữ liệu (Excel)"** định kỳ
  (cuối tuần/cuối tháng) và lưu file vào Google Drive/máy tính.
- Khi cần, dùng chức năng **"Phục hồi từ file sao lưu"** ngay tại trang đó để nạp lại dữ liệu.
- Khi trường có nhu cầu dùng lâu dài, nhiều người truy cập cùng lúc và cần dữ liệu bền vững
  100%, nên nâng cấp bước tiếp theo: thay lớp `modules/db.py` bằng kết nối tới Google Sheets
  (thư viện `st-gsheets-connection`, miễn phí) hoặc một cơ sở dữ liệu cloud miễn phí như
  Supabase/PostgreSQL. Toàn bộ giao diện (`modules/*.py`) không cần sửa vì chỉ gọi qua các
  hàm `get_df()` / `replace_table()`.

## 6. Quản lý tài khoản người dùng

- Chỉ tài khoản vai trò **ADMIN** thấy trang "Tài khoản đăng nhập".
- Khi tạo tài khoản cho giáo viên/nhân viên, nhập đúng **Mã NV** (trùng với Mã NV trong
  "Danh sách nhân sự") để hệ thống tự lọc đúng dữ liệu cá nhân của người đó.
- Mật khẩu được mã hoá một chiều (SHA-256) trước khi lưu vào cơ sở dữ liệu.

## 7. Hướng phát triển tiếp theo (gợi ý)

- Kết nối Google Sheets/Supabase để dữ liệu bền vững trên bản miễn phí.
- Thêm cảnh báo tự động (ví dụ: sắp đến hạn nâng lương, sắp hết hạn hợp đồng).
- Xuất báo cáo tổng hợp (PDF) theo mẫu của Phòng Giáo dục/Sở Nội vụ.
- Chatbot tra cứu thủ tục hành chính nội bộ.
