import streamlit as st
import pandas as pd
import os
import datetime

# --- CẤU HÌNH BAN ĐẦU ---
st.set_page_config(page_title="App Báo Cáo Sale", layout="wide")

# Tạo thư mục lưu ảnh nếu chưa có
if not os.path.exists("uploads"):
    os.makedirs("uploads")

# File lưu dữ liệu
KPI_FILE = "kpi.csv"
REPORT_FILE = "reports.csv"

# Khởi tạo data mẫu nếu file chưa tồn tại
if not os.path.exists(KPI_FILE):
    pd.DataFrame({
        "Tên": ["Thái", "Nhài", "Hà", "Trang"],
        "Spam": [50, 30, 40, 50],
        "Zalo": [1, 0, 1, 1],
        "Nhóm": [10, 5, 8, 10],
        "Tiktok": [1, 1, 0, 1]
    }).to_csv(KPI_FILE, index=False)

if not os.path.exists(REPORT_FILE):
    pd.DataFrame(columns=[
        "Ngày", "Tên", "Spam", "Zalo", "Nhóm", "Tiktok", "Tiền Phạt"
    ]).to_csv(REPORT_FILE, index=False)

# Đọc dữ liệu
df_kpi = pd.read_csv(KPI_FILE)
df_reports = pd.read_csv(REPORT_FILE)

# Hàm lưu file ảnh
def save_uploaded_file(uploaded_file, name, task):
    if uploaded_file is not None:
        today_str = datetime.date.today().strftime("%Y%m%d")
        file_path = os.path.join("uploads", f"{today_str}_{name}_{task}_{uploaded_file.name}")
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return file_path
    return None

# --- GIAO DIỆN CHÍNH ---
st.title("🎯 Hệ Thống Báo Cáo Công Việc Bán Hàng")

# Menu bên trái (Sidebar)
menu = ["📝 Nhân viên báo cáo", "👑 Quản lý (Leader)"]
choice = st.sidebar.selectbox("Chọn quyền truy cập:", menu)

# ----------------------------------------
# GIAO DIỆN 1: DÀNH CHO NHÂN VIÊN
# ----------------------------------------
if choice == "📝 Nhân viên báo cáo":
    st.header("Nộp báo cáo ngày hôm nay")
    
    # Chọn tên nhân viên
    nhan_vien = st.selectbox("Chọn tên của bạn:", df_kpi["Tên"].tolist())
    
    # Lấy KPI của nhân viên đang chọn
    kpi_user = df_kpi[df_kpi["Tên"] == nhan_vien].iloc[0]
    
    st.info(f"📌 **KPI hôm nay của {nhan_vien}:** Spam ({kpi_user['Spam']} số) | Zalo ({kpi_user['Zalo']} bài) | Hội nhóm ({kpi_user['Nhóm']} nhóm) | Tiktok ({kpi_user['Tiktok']} bài).")

    with st.form("form_bao_cao"):
        st.write("### Cập nhật tiến độ & Tải ảnh chứng minh")
        
        # Form nhập liệu cho 4 task
        col1, col2 = st.columns(2)
        with col1:
            ck_spam = st.checkbox(f"Hoàn thành Spam {kpi_user['Spam']} số")
            img_spam = st.file_uploader("Ảnh Spam Data", type=['png', 'jpg', 'jpeg'])
            
            ck_zalo = st.checkbox(f"Hoàn thành Zalo ({kpi_user['Zalo']} bài)")
            img_zalo = st.file_uploader("Ảnh Zalo", type=['png', 'jpg', 'jpeg'])
            
        with col2:
            ck_nhom = st.checkbox(f"Hoàn thành Spam {kpi_user['Nhóm']} nhóm")
            img_nhom = st.file_uploader("Ảnh Hội nhóm", type=['png', 'jpg', 'jpeg'])
            
            ck_tiktok = st.checkbox(f"Hoàn thành Tiktok ({kpi_user['Tiktok']} bài)")
            img_tiktok = st.file_uploader("Ảnh Tiktok", type=['png', 'jpg', 'jpeg'])

        submit_btn = st.form_submit_button("🚀 Gửi Báo Cáo")

        if submit_btn:
            # Logic tính tiền phạt 30k
            # Bị phạt nếu: Có tích chọn mà KHÔNG có ảnh, hoặc KHÔNG tích chọn
            phat = 0
            if not (ck_spam and img_spam) or \
               not (ck_zalo and img_zalo) or \
               not (ck_nhom and img_nhom) or \
               not (ck_tiktok and img_tiktok):
                phat = 30000

            # Lưu ảnh
            save_uploaded_file(img_spam, nhan_vien, "Spam")
            save_uploaded_file(img_zalo, nhan_vien, "Zalo")
            save_uploaded_file(img_nhom, nhan_vien, "Nhom")
            save_uploaded_file(img_tiktok, nhan_vien, "Tiktok")

            # Lưu dữ liệu vào file Excel (CSV)
            new_data = pd.DataFrame([{
                "Ngày": datetime.date.today().strftime("%Y-%m-%d"),
                "Tên": nhan_vien,
                "Spam": "Xong" if ck_spam and img_spam else "Thiếu",
                "Zalo": "Xong" if ck_zalo and img_zalo else "Thiếu",
                "Nhóm": "Xong" if ck_nhom and img_nhom else "Thiếu",
                "Tiktok": "Xong" if ck_tiktok and img_tiktok else "Thiếu",
                "Tiền Phạt": f"{phat:,} VNĐ"
            }])
            
            new_data.to_csv(REPORT_FILE, mode='a', header=False, index=False)
            
            if phat > 0:
                st.error("❌ Bạn chưa hoàn thành đủ Task hoặc thiếu ảnh chứng minh. Bạn bị phạt 30,000 VNĐ.")
            else:
                st.success("✅ Tuyệt vời! Bạn đã hoàn thành 100% KPI ngày hôm nay.")

# ----------------------------------------
# GIAO DIỆN 2: DÀNH CHO LEADER
# ----------------------------------------
elif choice == "👑 Quản lý (Leader)":
    st.header("Dashboard Quản Lý Báo Cáo")
    
    # Yêu cầu mật khẩu
    password = st.text_input("Nhập mật khẩu Leader:", type="password")
    
    if password == "Zill@0107": # Mật khẩu Leader (bạn có thể đổi ở đây)
        st.success("Đăng nhập thành công!")
        
        tab1, tab2 = st.tabs(["📊 Báo Cáo Tổng Hợp", "⚙️ Cài đặt KPI"])
        
        with tab1:
            st.write("### Lịch sử báo cáo của nhân viên")
            # Hiển thị bảng dữ liệu báo cáo
            df_view = pd.read_csv(REPORT_FILE)
            st.dataframe(df_view, use_container_width=True)
            
            st.info("💡 Ảnh chứng minh của nhân viên được lưu tại thư mục `uploads` trong máy tính/server của bạn.")
            
        with tab2:
            st.write("### Chỉnh sửa số lượng task cho từng nhân viên")
            st.write("Chỉnh sửa trực tiếp vào bảng dưới đây và bấm **Save**:")
            
            # Leader có thể edit trực tiếp vào bảng này
            edited_kpi = st.data_editor(df_kpi, num_rows="dynamic", use_container_width=True)
            
            if st.button("💾 Lưu thay đổi KPI"):
                edited_kpi.to_csv(KPI_FILE, index=False)
                st.success("Đã cập nhật KPI mới cho hệ thống!")
    elif password != "":
        st.error("Sai mật khẩu!")