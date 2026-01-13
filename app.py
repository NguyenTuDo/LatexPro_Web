# [File: app.py]
import streamlit as st
import streamlit.components.v1 as components
import app_logic as logic
from cau_hinh.noi_dung_chu import NOI_DUNG_HUONG_DAN, THONG_TIN_UNG_DUNG
from xu_ly_toan.math_utils import get_question_types, get_existing_answers

# [File: app.py] - Thay thế đoạn code cũ ở phần đầu file
@st.dialog("ℹ️ QUY TRÌNH CHUẨN HÓA EXTEST")
def show_extest_info():
    st.markdown("""
<div style="font-size: 15px; line-height: 1.6; color: #333;">
Nút này thực hiện quy trình xử lý thông minh gồm <b>5 giai đoạn</b>:
<hr style="margin: 10px 0;">
        
<b>1. 📥 Đầu vào linh hoạt:</b>
<ul style="margin-top: 5px; margin-bottom: 10px;">
<li>Tiếp nhận code LaTeX thô.</li>
<li>Hoạt động <b>tốt nhất</b> khi copy code từ <b>Mathpix</b>.</li>
<li><i>Lưu ý với Word:</i> Hãy dùng chức năng <b>Toggle TeX</b> để chuyển toàn bộ công thức MathType về dạng LaTeX trước khi copy.</li>
</ul>

<b>2. 🧹 Dọn dẹp cấu trúc:</b>
<ul style="margin-top: 5px; margin-bottom: 10px;">
<li>Tự động nhận diện và <b>xóa bỏ</b> các đoạn dẫn thừa như: <i>"Phần I...", "Phần II...", "Mã đề..."</i>.</li>
</ul>

<b>3. ⚙️ Chuẩn hóa EX_TEST:</b>
<ul style="margin-top: 5px; margin-bottom: 10px;">
<li>Tự động nhận diện 3 dạng câu hỏi (Trắc nghiệm, Đúng/Sai, Trả lời ngắn).</li>
<li>Chuyển đổi toàn bộ về cấu trúc chuẩn <code>ex_test</code>.</li>
</ul>

 <b>4. 📝 Quy chuẩn lệnh TeX:</b>
<ul style="margin-top: 5px; margin-bottom: 10px;">
<li>Đưa các bảng biểu <code>tabular</code> vào môi trường <code>\\begin{{center}}</code>.</li>
<li>Thay thế ký hiệu theo quy định nhóm TeX:
<ul>
<li><code>\\backslash</code> ➝ <code>\\setminus</code></li>
<li><code>^\\prime</code> ➝ <code>'</code></li>
<li>...và các lỗi phổ biến khác.</li>
</ul>
</li>
</ul>

<b>5. ✨ Tích hợp chức năng Làm đẹp:</b>
<div style="background: #e3f2fd; padding: 10px; border-radius: 5px; margin-top: 5px; border-left: 4px solid #2196f3;">
Nếu bạn đang bật nút gạt <b>"🔧 Tự làm đẹp"</b>, phần mềm sẽ chạy tiếp quy trình tinh chỉnh code chi tiết (xử lý dấu chấm phẩy, khoảng cách, toán tử...) ngay sau khi chuẩn hóa xong.
</div>
</div>
""", unsafe_allow_html=True)

# 1. SETUP
st.set_page_config(page_title="Latex Pro Web", page_icon="🚀", layout="wide", initial_sidebar_state="expanded")
logic.init_session_state()
st.markdown(logic.get_theme_css(), unsafe_allow_html=True)

# JS & CSS INJECTION
def setup_resources():
    # [CẬP NHẬT] Sửa logic tìm nút Cài đặt để phù hợp với icon mới
    js_code = """
    <script>
    const toggleSidebar = () => {
        const sidebarBtn = window.parent.document.querySelector('[data-testid="stSidebarCollapsedControl"] button');
        if (sidebarBtn) { sidebarBtn.click(); } 
        else { const closeBtn = window.parent.document.querySelector('section[data-testid="stSidebar"] button'); if (closeBtn) closeBtn.click(); }
    };

    const observer = new MutationObserver(() => {
        const buttons = window.parent.document.querySelectorAll('button');
        buttons.forEach(btn => {
            // [SỬA] Chỉ cần tìm icon bánh răng
            if (btn.innerText.includes("⚙️")) { btn.onclick = toggleSidebar; }
            // [SỬA Ở ĐÂY] Cập nhật tên mới để JS nhận diện được nút màu Cam
            if (btn.innerText.includes("ĐÓNG GÓI MAIN")) btn.classList.add("custom-ansbook-btn");
            // Logic cho nút màu Xanh (Lưu ý: Nếu bạn đổi tên nút EXTEST kia thì cũng phải sửa dòng này tương tự)
            if (btn.innerText.includes("CHUẨN HÓA EXTEST")) btn.classList.add("custom-auto-convert-btn");
        });
    });
    observer.observe(window.parent.document.body, { childList: true, subtree: true });
    </script>
    """
    components.html(js_code, height=0)

def cb_select_all_beauty():
    keys = ["c_smart", "c_url", "c_space", "c_num_math", "c_frac", "c_sys", "c_int", "c_vec", "c_colon"]
    for key in keys: st.session_state[key] = True

def cb_clear_all_beauty():
    keys = ["c_smart", "c_url", "c_space", "c_num_math", "c_frac", "c_sys", "c_int", "c_vec", "c_colon"]
    for key in keys: st.session_state[key] = False

def cb_run_beauty_with_feedback(): logic.cb_run_beauty()

setup_resources()

# [THÊM MỚI] Hàm hiển thị thông báo dạng Popup góc trái
def render_toast():
    if "msg_toast" in st.session_state and st.session_state.msg_toast:
        msg = st.session_state.msg_toast
        # Xóa ngay lập tức để không hiện lại khi F5
        st.session_state.msg_toast = None 
        
        toast_html = f"""
        <div id="custom-toast">
            <div class="toast-icon">✨</div>
            <div class="toast-body">
                <div class="toast-title">Thành công!</div>
                <div class="toast-msg">{msg}</div>
            </div>
        </div>
        <style>
            #custom-toast {{
                position: fixed; top: 80px; left: 20px; z-index: 999999;
                background: white; border-left: 6px solid #005fb8;
                padding: 12px 20px; border-radius: 8px;
                box-shadow: 0 5px 20px rgba(0,0,0,0.15);
                display: flex; align-items: center; gap: 15px;
                min-width: 300px;
                animation: slideInLeft 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards, 
                           fadeOut 0.5s 4s forwards; /* Tự tắt sau 4s */
            }}
            .toast-icon {{ font-size: 24px; }}
            .toast-body {{ display: flex; flex-direction: column; }}
            .toast-title {{ font-weight: 700; color: #005fb8; font-size: 14px; margin-bottom: 2px; }}
            .toast-msg {{ font-weight: 500; color: #555; font-size: 14px; }}
            
            @keyframes slideInLeft {{ from {{ opacity: 0; transform: translateX(-50px); }} to {{ opacity: 1; transform: translateX(0); }} }}
            @keyframes fadeOut {{ to {{ opacity: 0; visibility: hidden; }} }}
        </style>
        """
        st.markdown(toast_html, unsafe_allow_html=True)

# Gọi hàm này ngay sau khi setup_resources
render_toast()

# CSS TỐI ƯU GIAO DIỆN
st.markdown("""
<style>
/* ... (Giữ nguyên CSS cũ) ... */
[data-testid="stHeader"] { background: transparent; }
[data-testid="stHeader"] > div:first-child { display: none; }
[data-testid="stDecoration"] { display: none; }
section[data-testid="stSidebar"] { z-index: 10001 !important; box-shadow: 5px 0 15px rgba(0,0,0,0.1); background-color: white; }
[data-testid="stSidebar"] + section, [data-testid="stSidebar"] + div { margin-left: 0 !important; width: 100% !important; }
.stApp { margin: 0; padding: 0; overflow-y: auto !important; }
.block-container { padding-top: 1rem !important; padding-bottom: 0rem !important; padding-left: 2rem !important; padding-right: 2rem !important; }

/* Tinh chỉnh nút bấm cho gọn */
.stButton, .stCheckbox, .stRadio, .stSelectbox, .stToggle { margin-bottom: 2px !important; margin-top: 0 !important; }
.stButton button { font-weight: 500 !important; } 

.stExpander { margin-bottom: 2px !important; margin-top: 0 !important; }
.stDivider { margin: 2px 0 !important; }
/* Tìm dòng cũ bắt đầu bằng .stTextArea textarea và thay bằng đoạn này */
.stTextArea textarea { 
    font-family: 'Consolas', 'Monaco', 'Courier New', monospace !important; /* Font chuẩn code/TeXstudio */
    font-size: 16px !important;      /* Chữ to hơn (cũ là 13px) */
    font-weight: 600 !important;     /* Chữ đậm hơn */
    color: #003366 !important;       /* Màu Xanh Đậm (Navy Blue) */
    line-height: 1.5 !important;     /* Dãn dòng cho dễ nhìn */
    padding: 12px !important;        /* Khoảng cách lề */
    background-color: #fcfcfc !important; /* Nền trắng xám nhẹ cho dịu mắt */
}
.stContainer { padding: 0 !important; }
[data-testid="stVerticalBlock"] > div { padding: 0 !important; margin: 0 !important; }

/* [CẬP NHẬT] Top Bar Style - Flex Align Center */
#top-bar { 
    position: fixed; top: 0px; left: 0px; width: 100%; 
    background: white; z-index: 999; 
    padding: 5px 40px; /* Padding trái phải */
    box-shadow: 0 1px 3px rgba(0,0,0,0.08); 
    border-bottom: 1px solid #e5e7eb; 
    height: 60px; /* Tăng nhẹ chiều cao */
    display: flex; align-items: center; 
}
[data-testid="stAppViewContainer"] { padding-top: 60px !important; }
[data-testid="column"] { flex: auto !important; width: auto !important; }

/* STYLE NÚT ĐẶC BIỆT */
.custom-ansbook-btn {
    background: linear-gradient(90deg, #FF9800 0%, #F44336 100%) !important;
    color: white !important; border: none !important;
    font-weight: 900 !important; font-size: 15px !important;
    text-transform: uppercase; letter-spacing: 0.5px;
    box-shadow: 0 4px 15px rgba(244, 67, 54, 0.4) !important;
    transition: all 0.3s ease !important; margin-top: 5px !important;
}
.custom-ansbook-btn:hover {
    transform: translateY(-2px) scale(1.02) !important;
    box-shadow: 0 6px 20px rgba(244, 67, 54, 0.6) !important;
    background: linear-gradient(90deg, #FFB74D 0%, #E57373 100%) !important;
}

.custom-auto-convert-btn {
    background: linear-gradient(90deg, #005fb8 0%, #0099ff 100%) !important;
    color: white !important; border: none !important;
    font-weight: 900 !important; font-size: 14px !important;
    text-transform: uppercase; letter-spacing: 0.5px;
    box-shadow: 0 4px 12px rgba(0, 95, 184, 0.4) !important;
    transition: all 0.3s ease !important;
}
.custom-auto-convert-btn:hover {
    transform: translateY(-2px) scale(1.02) !important;
    box-shadow: 0 6px 18px rgba(0, 95, 184, 0.6) !important;
    background: linear-gradient(90deg, #0069d9 0%, #33adff 100%) !important;
}

/* Style Author Card & Dark Mode (Giữ nguyên) */
.author-card { background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border-radius: 12px; padding: 25px; display: flex; align-items: center; box-shadow: 0 4px 12px rgba(0,0,0,0.08); margin-bottom: 20px; border: 1px solid #dee2e6; }
.author-avatar { width: 120px; height: 120px; border-radius: 50%; border: 4px solid white; box-shadow: 0 4px 8px rgba(0,0,0,0.15); margin-right: 25px; }
.author-info h2 { margin: 0 0 8px 0 !important; color: #005fb8; font-size: 24px !important; }
.author-info p { margin: 4px 0 !important; color: #555; font-size: 15px; }
.social-btn { display: inline-block; margin-top: 12px; padding: 8px 18px; background-color: #1877f2; color: white !important; text-decoration: none; border-radius: 20px; font-weight: bold; font-size: 14px; transition: background 0.2s; box-shadow: 0 2px 5px rgba(24, 119, 242, 0.3); }
.social-btn:hover { background-color: #166fe5; transform: translateY(-1px); }
@media (prefers-color-scheme: dark) {
    section[data-testid="stSidebar"] { background-color: #252526; }
    #top-bar { background-color: #1e1e1e; border-bottom: 1px solid #333; }
    [data-testid="stHeader"] button { color: #d4d4d4 !important; }
    .author-card { background: linear-gradient(135deg, #2d2d2d 0%, #1e1e1e 100%); border-color: #444; }
    .author-info h2 { color: #66b3ff; }
    .author-info p { color: #ccc; }
    .author-avatar { border-color: #444; }
}
</style>
""", unsafe_allow_html=True)

# 2. SIDEBAR
with st.sidebar:
    st.markdown("**⚙️ CÀI ĐẶT**")
    st.toggle("🌙 Dark Mode", key="is_dark_mode")
    c_undo, c_redo = st.columns(2)
    with c_undo: st.button("↩️ Undo (Z)", key="hidden_undo", on_click=logic.cb_undo, disabled=st.session_state.history_idx <= 0, use_container_width=True)
    with c_redo: st.button("↪️ Redo (Y)", key="hidden_redo", on_click=logic.cb_redo, disabled=st.session_state.history_idx >= len(st.session_state.history) - 1, use_container_width=True)
    st.markdown("""<style>div[data-testid="stSidebar"] button[kind="secondary"] { display: none; }</style>""", unsafe_allow_html=True)
    st.divider()
    st.markdown("**📖 HƯỚNG DẪN NHANH**")
    for t, c in NOI_DUNG_HUONG_DAN:
        with st.expander(t, expanded=False): st.markdown(c, unsafe_allow_html=True)

# 3. TOP BAR (ĐÃ LÀM LẠI UX)
# Layout mới: Logo bên trái --- Khoảng trắng --- Nút thao tác bên phải
st.markdown('<div id="top-bar">', unsafe_allow_html=True)

# Chia cột: Logo(2) | Spacer(5) | Nạp mẫu(1.2) | Copy(0.8) | Tex(0.8) | Setting(0.5)
c_logo, c_space, c_btn1, c_btn2, c_btn3, c_set = st.columns([2, 5, 1.3, 1.3, 0.9, 0.6])

# [Cột Trái] Logo & Thương hiệu
with c_logo:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; height: 42px;">
        <span style="font-size: 26px;">🚀</span>
        <span style="font-weight: bold; color: #005fb8; font-size: 20px; font-family: sans-serif; letter-spacing: -0.5px;">LATEX PRO</span>
    </div>
    """, unsafe_allow_html=True)

# [Cột Phải] Các nút chức năng
with c_btn1: 
    # Rút gọn text "Nạp đề thi mẫu (TEST)" -> "📄 Nạp Mẫu" cho gọn
    st.button("📄 Nạp Mẫu", use_container_width=True, on_click=logic.cb_load_sample, help="Nạp đề thi mẫu để thử nghiệm")

with c_btn2: 
    st.button("📋 Copy", use_container_width=True, on_click=logic.cb_copy_all)

with c_btn3:
    if st.session_state.editor_content: 
        st.download_button("💾 Tex", st.session_state.editor_content, "out.tex", "text/plain", use_container_width=True)
    else: 
        st.button("💾 Tex", disabled=True, use_container_width=True)

with c_set:
    # Nút Cài đặt dạng Icon
    st.button("⚙️", use_container_width=True, help="Mở cài đặt Sidebar") 

st.markdown('</div>', unsafe_allow_html=True)

# 4. WORKSPACE
tab_main, tab_info = st.tabs(["🛠️ SOẠN THẢO", "👤 TÁC GIẢ"])

with tab_main:
    col_ed, col_tools = st.columns([1.3, 1])
    
    with col_ed:
        st.text_area("Main Editor", value=st.session_state.editor_content, height=600, 
                     key="editor_content", label_visibility="collapsed", 
                     placeholder="Nhập nội dung vào đây hoặc bấm '📄 Nạp Mẫu' trên Top Bar để thử nghiệm...\n(Bấm Enter để xuống dòng)")

    with col_tools:
        # [CẬP NHẬT] Chia 3 cột: Nút Xanh | Nút i | Toggle
        col_btn_auto, col_info, col_toggle = st.columns([1.5, 0.35, 1.1])
        
        with col_btn_auto:
            st.button("✨ CHUẨN HÓA EXTEST ", type="primary", use_container_width=True, on_click=logic.cb_convert_auto, help="Tự động chuẩn hóa cấu trúc đề thi theo chuẩn ex_test")
        
# Nút i nhỏ: Bấm vào sẽ gọi hàm popup ở trên
        with col_info:
            if st.button("ℹ️", help="Xem quy trình xử lý chi tiết", use_container_width=True):
                show_extest_info()

        with col_toggle:
            st.toggle("🔧 Tự làm đẹp", key="auto_beautify_after_convert")

        # Nút ANSBOOK nằm full chiều rộng bên dưới
        st.button("📦 ĐÓNG GÓI MAIN (CHUẨN VNMATHS)", 
                    use_container_width=True, 
                    on_click=logic.cb_run_main_struct, 
                    help="Tự động phân nhóm I, II, III và thêm code xuất đáp án.")
        

        t1, t2, t3, t4 = st.tabs(["✨ LÀM ĐẸP", "🖼️ ẢNH & TAG", "🔑 ĐÁP ÁN", "📊 THỐNG KÊ"])
        
        with t1:
            btn_run, btn_sel, btn_clr = st.columns([2.4, 0.4, 0.4])
            with btn_run: st.button("⚡ CHẠY LÀM ĐẸP", use_container_width=True, on_click=cb_run_beauty_with_feedback, help="Chạy làm đẹp theo các tùy chọn bên dưới")
            with btn_sel: st.button("✅", use_container_width=True, on_click=cb_select_all_beauty, help="Chọn hết")
            with btn_clr: st.button("❌", use_container_width=True, on_click=cb_clear_all_beauty, help="Xóa hết")
            
            st.markdown("**1️⃣ Cơ bản (Nên chọn):**")
            col_basic_1, col_basic_2 = st.columns(2)
            with col_basic_1:
                st.checkbox("Smart Clean (Ưu tiên)", key="c_smart", help="• Sửa ký hiệu nhân (. ➝ \\cdot) \n• Sửa lỗi ngắt quãng số")
                st.checkbox("Mathpix Clean", key="c_url", help="Xóa các link ảnh mặc định trong Mathpix")
            with col_basic_2:
                st.checkbox("Xóa khoảng trống", key="c_space", help="O x y ➝ Oxy, ( A ; B ) ➝ (A;B), (A B C) ➝ (ABC)")
                st.checkbox("Format Số & Toán ($)", key="c_num_math", help="1.5 ➝ 1{,}5 | 2,5 ➝ $2{,}5$")
            
            with st.expander("**2️⃣ Nâng cao & Cấu trúc:**", expanded=True):
                col_comb_1, col_comb_2 = st.columns(2)
                with col_comb_1:
                    st.checkbox("frac ➝ dfrac", key="c_frac", help="\\frac{1}{2} ➝ \\dfrac{1}{2}")
                    st.checkbox("Tex ➝ \\heva/\\hoac", key="c_sys", help="Gộp các môi trường cases/array về lệnh tắt \\heva, \\hoac.")
                    st.checkbox("Displaystyle", key="c_int", help="• Thêm \\displaystyle\n• Thêm \\limits\n• dx ➝ \\mathrm{\\,d}x")
                with col_comb_2:
                    st.checkbox("Vectơ chuẩn", key="c_vec", help="• \\vec{u} ➝ \\overrightarrow{u}")
                    st.checkbox("Colon (:)", key="c_colon", help="Đổi dấu : trong hình học thành \\colon")

        with t2:
            st.caption("Đánh số câu tự động (trước \\begin\{ex}):")
            c_tag1, c_tag2 = st.columns(2)
            with c_tag1: st.button("➕ %Câu", use_container_width=True, on_click=logic.cb_add_tag, args=("%Câu",))
            with c_tag2: st.button("➕ %Bài", use_container_width=True, on_click=logic.cb_add_tag, args=("%Bài",))
            st.caption("Tùy chọn vị trí ảnh trong câu hỏi:")
            st.selectbox("Chọn chế độ:", ["Center", "immini", "Phải [thm]", "imminiL"], key="img_sel", label_visibility="collapsed")
            st.button("🖼️ Áp dụng chế độ Ảnh trên", use_container_width=True, on_click=lambda: logic.cb_action_image(st.session_state.img_sel))

        with t3:
            q_types = get_question_types(st.session_state.editor_content)
            if q_types:
                existing = get_existing_answers(st.session_state.editor_content)
                with st.form("ans_form"):
                    st.form_submit_button("💾 LƯU ĐÁP ÁN VÀO EDITOR", type="primary", 
                                          on_click=logic.cb_save_gui_answers, 
                                          use_container_width=True)
                    st.divider()
                    
                    with st.container(height=550):
                        for q, t in q_types.items():
                            old = existing.get(q, [])
                            st.markdown(f"**C.{q}** `({t})`")
                            
                            if t == 'MC':
                                idx = "ABCD".find(old[0]) if (old and old[0] in "ABCD") else None
                                st.radio(f"MC_{q}", ["A","B","C","D"], index=idx if idx != -1 else None, 
                                         key=f"ans_{q}_MC", horizontal=True, label_visibility="collapsed")
                            elif t == 'TF':
                                c = st.columns(4)
                                for i, ch in enumerate("ABCD"):
                                    c[i].checkbox(ch, ch in old, key=f"ans_{q}_TF_{ch}")
                            elif t == 'SA':
                                chars = list(old[0] if old else "") + [""] * 4
                                c = st.columns(4)
                                for i in range(4):
                                    c[i].text_input(f"S{i}", chars[i], max_chars=1, 
                                                    key=f"ans_{q}_SA_{i}", label_visibility="collapsed")
                            st.divider()
            else:
                st.warning("Hãy bấm 'TỰ ĐỘNG CHUẨN HÓA' hoặc nạp đề để hiện danh sách câu hỏi.")

        with t4:
            stats = logic.calculate_stats(st.session_state.editor_content)
            def fmt_stat(done, total):
                if total == 0: return f'<span style="color:#999">0/0</span>'
                color = "#28a745" if done == total else "#d9534f"
                return f'<b style="color:{color}; font-size:1.1em">{done}/{total}</b>'

            html_content = f"""
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; border: 1px solid #e9ecef; color: #333;">
                <div style="font-size: 16px; margin-bottom: 10px; border-bottom: 1px solid #ddd; padding-bottom: 5px;">
                    <b>TỔNG SỐ CÂU HỎI:</b> <span style="font-size:18px; font-weight:bold">{stats['Total']}</span>
                </div>
                <div style="display:flex; justify-content:space-between; margin: 8px 0; align-items:center;">
                    <span>Trắc nghiệm (MC):</span> {fmt_stat(stats['MC_Done'], stats['MC_Total'])}
                </div>
                <div style="display:flex; justify-content:space-between; margin: 8px 0; align-items:center;">
                    <span>Đúng/Sai (TF):</span> {fmt_stat(stats['TF_Done'], stats['TF_Total'])}
                </div>
                <div style="display:flex; justify-content:space-between; margin: 8px 0; align-items:center;">
                    <span>Điền khuyết (SA):</span> {fmt_stat(stats['SA_Done'], stats['SA_Total'])}
                </div>
            </div>
            """
            st.markdown(html_content, unsafe_allow_html=True)
            st.button("🔄 Cập nhật thống kê", use_container_width=True)

with tab_info:
    st.header(f"🚀 {THONG_TIN_UNG_DUNG['Tên phần mềm']}")
    st.caption(f"Phiên bản: {THONG_TIN_UNG_DUNG['Phiên bản']}")
    st.divider()

    st.markdown(f"""
    <div class="author-card">
        <img src="{THONG_TIN_UNG_DUNG['Avatar']}" class="author-avatar">
        <div class="author-info">
            <h2>{THONG_TIN_UNG_DUNG['Tác giả']}</h2>
            <p>🏫 <b>Đơn vị:</b> {THONG_TIN_UNG_DUNG['Đơn vị']}</p>
            <p>📞 <b>Liên hệ:</b> {THONG_TIN_UNG_DUNG['Liên hệ']}</p>
            <a href="{THONG_TIN_UNG_DUNG['Facebook']}" target="_blank" class="social-btn">
                <span style="font-size:15px">🔵</span> Liên hệ Facebook
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.info(THONG_TIN_UNG_DUNG['Mô tả'], icon="ℹ️")
    st.divider()
    st.caption("Developed with ❤️ by Thầy Tư Đô Nguyên & Gemini AI (2026)")