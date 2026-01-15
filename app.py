import streamlit as st

# 1. Cấu hình trang
st.set_page_config(
    page_title="LATEX PRO WEB - Moved",
    page_icon="🚀",
    layout="wide" # Dùng wide để nền rộng thoáng hơn
)

# 2. CSS Tùy chỉnh (Trái tim của giao diện đẹp)
st.markdown("""
<style>
    /* Ẩn menu mặc định của Streamlit cho gọn */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Căn giữa nội dung toàn trang */
    .stApp {
        background-color: #0e1117; /* Màu nền tối sang trọng (hoặc để trắng tùy theme) */
        display: flex;
        align-items: center;
        justify_content: center;
    }

    /* Container chính (Cái khung bo tròn) */
    .main-card {
        background: linear-gradient(145deg, #1e2130, #161924);
        border: 1px solid #333;
        border-radius: 30px;
        padding: 60px 40px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        max-width: 800px;
        margin: auto;
        animation: fadeIn 1.5s ease-in-out;
    }

    /* Tên Web: LATEX PRO WEB */
    .app-title {
        font-family: 'Helvetica Neue', sans-serif;
        font-size: 80px;
        font-weight: 900;
        margin-bottom: 10px;
        background: -webkit-linear-gradient(45deg, #FF4B4B, #FF9068);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1.1;
    }

    /* Dòng thông báo phụ */
    .subtitle {
        color: #e0e0e0;
        font-size: 28px;
        font-weight: 500;
        margin-bottom: 40px;
    }

    /* Icon minh họa */
    .icon-move {
        font-size: 100px;
        margin-bottom: 20px;
        display: inline-block;
        animation: bounce 2s infinite;
    }

    /* NÚT BẤM SIÊU TO (CTA) */
    .btn-new-home {
        background-image: linear-gradient(to right, #1FA2FF 0%, #12D8FA  51%, #1FA2FF  100%);
        margin: 20px auto;
        padding: 25px 60px;
        text-align: center;
        text-transform: uppercase;
        transition: 0.5s;
        background-size: 200% auto;
        color: white !important;
        box-shadow: 0 0 20px #eee;
        border-radius: 50px;
        display: inline-block;
        font-size: 30px;
        font-weight: bold;
        text-decoration: none;
        border: none;
        cursor: pointer;
    }

    .btn-new-home:hover {
        background-position: right center; /* change the direction of the change here */
        color: #fff;
        text-decoration: none;
        transform: scale(1.05); /* Phóng to nhẹ khi di chuột */
    }

    /* Hiệu ứng chuyển động */
    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% {transform: translateY(0);}
        40% {transform: translateY(-20px);}
        60% {transform: translateY(-10px);}
    }
    @keyframes fadeIn {
        0% {opacity:0;}
        100% {opacity:1;}
    }

</style>
""", unsafe_allow_html=True)

# 3. Nội dung HTML chính
def main():
    # --- CẤU HÌNH LINK MỚI TẠI ĐÂY ---
    NEW_URL = "https://latexpro-web.vercel.app/"
    
    # Tạo layout căn giữa
    col1, col2, col3 = st.columns([1, 10, 1])
    
    with col2:
        st.markdown(f"""
            <div class="main-card">
                <div class="icon-move">🚀</div>
                <div class="app-title">LATEX PRO WEB</div>
                <div class="subtitle">
                    Chúng tôi đã chuyển sang hệ thống mới<br>
                    Mạnh mẽ hơn - Tốc độ hơn
                </div>
                
                <a href="{NEW_URL}" target="_self" class="btn-new-home">
                    👉 TRUY CẬP NGAY
                </a>
                
                <p style="margin-top: 30px; color: #888; font-size: 16px;">
                    <i>(Hệ thống cũ này sẽ chính thức đóng lại sau ít phút)</i>
                </p>
            </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
