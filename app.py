import streamlit as st
import streamlit.components.v1 as components

# 1. Cấu hình trang
st.set_page_config(
    page_title="LATEX PRO WEB - Moved",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. CSS "Siêu to khổng lồ" & Dark Mode
st.markdown("""
<style>
    /* Ẩn toàn bộ UI mặc định của Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;} /* Ẩn luôn sidebar */

    /* Căn giữa và Màu nền */
    .stApp {
        background-color: #0e1117;
        display: flex;
        align-items: center;
        justify_content: center;
        height: 100vh; /* Full màn hình */
    }

    /* Khung Card Chính */
    .main-card {
        background: linear-gradient(145deg, #1e2130, #161924);
        border: 1px solid #333;
        border-radius: 30px;
        padding: 50px;
        text-align: center;
        box-shadow: 0 20px 50px rgba(0,0,0,0.6);
        max-width: 900px;
        width: 90%;
        margin: auto;
        animation: zoomIn 0.8s ease-out;
    }

    /* Tên Web: LATEX PRO WEB */
    .app-title {
        font-family: 'Helvetica Neue', sans-serif;
        font-size: 90px; /* Chữ cực to */
        font-weight: 900;
        margin: 20px 0;
        background: -webkit-linear-gradient(120deg, #00C9FF, #92FE9D); /* Màu xanh công nghệ */
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1.1;
        letter-spacing: -2px;
    }

    /* Mô tả */
    .subtitle {
        color: #ddd;
        font-size: 26px;
        font-weight: 400;
        margin-bottom: 50px;
    }

    /* NÚT BẤM (CTA) */
    .btn-glow {
        display: inline-block;
        padding: 30px 70px; /* Nút to */
        color: #fff !important;
        background: linear-gradient(45deg, #ff00cc, #333399);
        font-size: 35px;
        font-weight: bold;
        text-decoration: none;
        border-radius: 50px;
        box-shadow: 0 0 20px #ff00cc;
        transition: all 0.3s ease;
        border: 2px solid rgba(255,255,255,0.1);
    }

    .btn-glow:hover {
        transform: scale(1.05);
        box-shadow: 0 0 40px #ff00cc, 0 0 20px #333399;
        text-decoration: none;
    }

    /* Animation */
    @keyframes zoomIn {
        0% {transform: scale(0.8); opacity: 0;}
        100% {transform: scale(1); opacity: 1;}
    }

</style>
""", unsafe_allow_html=True)

# 3. Render giao diện HTML
def main():
    # LINK MỚI CỦA BẠN
    NEW_URL = "https://latexpro-web.vercel.app/"
    
    # Sử dụng HTML thuần để kiểm soát hoàn toàn việc chuyển trang
    # target="_self" là lệnh bắt buộc trình duyệt mở link ngay tại tab hiện tại
    html_content = f"""
    <div class="main-card">
        <div style="font-size: 80px;">⚠️</div>
        <div class="app-title">LATEX PRO WEB</div>
        <div class="subtitle">
            Hệ thống đã chuyển sang nền tảng <b>Vercel</b>.<br>
            Nhanh hơn. Mạnh mẽ hơn. Ổn định hơn.
        </div>
        
<a href="{https://latexpro-web.vercel.app/}" target="_self" class="btn-glow">
🚀 CHUYỂN NHÀ NGAY
</a>
        
<p style="margin-top: 40px; color: #666; font-size: 14px;">
Click nút trên để rời khỏi trang này vĩnh viễn.
</p>
</div>
    """
    
    # Hiển thị layout
    col1, col2, col3 = st.columns([1, 10, 1])
    with col2:
        st.markdown(html_content, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
