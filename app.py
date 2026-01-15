import streamlit as st
import time

# 1. Cấu hình trang (Title, Icon, Layout)
st.set_page_config(
    page_title="Thông báo chuyển hệ thống",
    page_icon="🚚",
    layout="centered"
)

# 2. CSS tùy chỉnh để ẩn menu mặc định và làm đẹp giao diện
hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stApp {
            text-align: center;
        }
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)

# 3. Nội dung chính
def main():
    # Tạo khoảng trống để nội dung nằm giữa theo chiều dọc (tương đối)
    st.write("")
    st.write("")
    
    col1, col2, col3 = st.columns([1, 6, 1])

    with col2:
        # Icon hoặc Hình ảnh minh họa
        st.title("🚚") 
        st.header("Chúng tôi đã chuyển nhà!")
        
        st.divider()
        
        st.info("⚠️ Ứng dụng này hiện đã ngưng hoạt động trên nền tảng cũ.")
        
        st.markdown(
            """
            ### Xin chào bạn,
            
            Để mang lại trải nghiệm tốt hơn và tốc độ nhanh hơn, 
            chúng tôi đã di dời toàn bộ dữ liệu và tính năng sang hệ thống mới.
            
            Vui lòng truy cập địa chỉ mới bên dưới để tiếp tục sử dụng.
            """
        )
        
        st.write("") # Khoảng trống
        
        # --- THAY ĐỔI LINK MỚI TẠI ĐÂY ---
        NEW_URL = "https://www.duong-dan-moi-cua-ban.com"
        
        # Nút bấm chuyển hướng
        st.link_button(
            label="👉 TRUY CẬP NỀN TẢNG MỚI NGAY", 
            url=NEW_URL, 
            type="primary", 
            use_container_width=True
        )
        
        st.write("")
        st.caption("Nếu bạn gặp vấn đề, vui lòng liên hệ admin.")

if __name__ == "__main__":
    main()

# Tự động chuyển sau 5 giây
time_left = 5
redirect_msg = st.empty()

for i in range(time_left, 0, -1):
    redirect_msg.markdown(f"_Tự động chuyển sang trang mới sau {i} giây..._")
    time.sleep(1)

# Mã JavaScript để chuyển hướng
js = f"<script>window.location.href = '{https://latexpro-web.vercel.app/}';</script>"
st.components.v1.html(js)
