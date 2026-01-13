# [File: app.py]
import streamlit as st
import streamlit.components.v1 as components
import app_logic as logic
from cau_hinh.noi_dung_chu import NOI_DUNG_HUONG_DAN, THONG_TIN_UNG_DUNG
from xu_ly_toan.math_utils import get_question_types, get_existing_answers

# 1. SETUP
st.set_page_config(page_title="Latex Pro Web", page_icon="🚀", layout="wide", initial_sidebar_state="expanded")
logic.init_session_state()
st.markdown(logic.get_theme_css(), unsafe_allow_html=True)

# JS & CSS INJECTION
def setup_resources():
    js_code = """
    <script>
    // 1. Xử lý phím tắt Undo/Redo (Tìm nút theo TEXT hiển thị để chắc chắn bấm đúng)
    document.addEventListener('keydown', function(e) {
        if ((e.ctrlKey || e.metaKey)) {
            if (e.key === 'z') {
                const buttons = window.parent.document.querySelectorAll('button');
                buttons.forEach(btn => {
                    if (btn.innerText.includes("Undo (Z)")) {
                        btn.click();
                    }
                });
            }
            else if (e.key === 'y') {
                const buttons = window.parent.document.querySelectorAll('button');
                buttons.forEach(btn => {
                    if (btn.innerText.includes("Redo (Y)")) {
                        btn.click();
                    }
                });
            }
        }
    });

    // 2. Tự động tìm và tô màu các nút ĐẶC BIỆT
    const observer = new MutationObserver(() => {
        const buttons = window.parent.document.querySelectorAll('button');
        buttons.forEach(btn => {
            if (btn.innerText.includes("CHUẨN HÓA MAIN (ANSBOOK)")) {
                btn.classList.add("custom-ansbook-btn");
            }
            if (btn.innerText.includes("TỰ ĐỘNG CHUẨN HÓA")) {
                btn.classList.add("custom-auto-convert-btn");
            }
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

# CSS TỐI ƯU GIAO DIỆN
st.markdown("""
<style>
/* ... (Giữ nguyên các CSS layout) ... */
[data-testid="stHeader"] {
    background: transparent;
}
[data-testid="stHeader"] > div:first-child {
    display: none;
}
[data-testid="stDecoration"] { display: none; }
section[data-testid="stSidebar"] { z-index: 10001 !important; box-shadow: 5px 0 15px rgba(0,0,0,0.1); background-color: white; }
[data-testid="stSidebar"] + section, [data-testid="stSidebar"] + div { margin-left: 0 !important; width: 100% !important; }
.stApp { margin: 0; padding: 0; overflow-y: auto !important; }
.block-container { padding-top: 1rem !important; padding-bottom: 0rem !important; padding-left: 2rem !important; padding-right: 2rem !important; }
.stButton, .stCheckbox, .stRadio, .stSelectbox, .stToggle { margin-bottom: 2px !important; margin-top: 0 !important; }
.stExpander { margin-bottom: 2px !important; margin-top: 0 !important; }
.stDivider { margin: 2px 0 !important; }
.stTextArea textarea { font-size: 13px !important; line-height: 1.3 !important; padding: 8px !important; }
.stContainer { padding: 0 !important; }
[data-testid="stVerticalBlock"] > div { padding: 0 !important; margin: 0 !important; }
#top-bar { position: fixed; top: 0px; left: 0px; width: 100%; background: white; z-index: 999; padding: 5px 60px 5px 60px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); border-bottom: 1px solid #ddd; height: 55px; display: flex; align-items: center; }
[data-testid="stAppViewContainer"] { padding-top: 55px !important; }
[data-testid="column"] { flex: auto !important; width: auto !important; }

/* STYLE NÚT ĐẶC BIỆT */
.custom-ansbook-btn {
    background: linear-gradient(90deg, #FF9800 0%, #F44336 100%) !important;
    color: white !important; border: none !important;
    font-weight: 900 !important; font-size: 15px !important;
    text-transform: uppercase; letter-spacing: 0.5px;
    box-shadow: 0 4px 15px rgba(244, 67, 54, 0.4) !important;
    transition: all 0.3s ease !important;
}
.custom-ansbook-btn:hover {
    transform: translateY(-2px) scale(1.02) !important;
    box-shadow: 0 6px 20px rgba(244, 67, 54, 0.6) !important;
    background: linear-gradient(90deg, #FFB74D 0%, #E57373 100%) !important;
}
.custom-ansbook-btn:active { transform: translateY(1px) !important; box-shadow: none !important; }

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
.custom-auto-convert-btn:active { transform: translateY(1px) !important; box-shadow: none !important; }

/* STYLE AUTHOR CARD */
.author-card {
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    border-radius: 12px; padding: 25px; display: flex; align-items: center;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08); margin-bottom: 20px; border: 1px solid #dee2e6;
}
.author-avatar {
    width: 120px; height: 120px; border-radius: 50%;
    border: 4px solid white; box-shadow: 0 4px 8px rgba(0,0,0,0.15); margin-right: 25px;
}
.author-info h2 { margin: 0 0 8px 0 !important; color: #005fb8; font-size: 24px !important; }
.author-info p { margin: 4px 0 !important; color: #555; font-size: 15px; }
.social-btn {
    display: inline-block; margin-top: 12px; padding: 8px 18px;
    background-color: #1877f2; color: white !important; text-decoration: none;
    border-radius: 20px; font-weight: bold; font-size: 14px; transition: background 0.2s;
    box-shadow: 0 2px 5px rgba(24, 119, 242, 0.3);
}
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

# 3. TOP BAR
st.markdown('<div id="top-bar">', unsafe_allow_html=True)
tb_name, tb_c1, tb_c2, tb_c3, tb_c4 = st.columns([1.5, 2.2, 0.7, 0.7, 0.9])
with tb_name: st.markdown('<p style="font-weight: bold; color: #005fb8; margin-top: 8px; font-size: 20px;">🚀 LATEX PRO v1.2</p>', unsafe_allow_html=True)

with tb_c1: 
    st.button("✨ TỰ ĐỘNG CHUẨN HÓA", type="primary", use_container_width=True, 
              on_click=logic.cb_convert_auto,
              help="Dọn dẹp rác, phân loại câu hỏi (TN, ĐS, TL) và đưa về cấu trúc chuẩn.")

with tb_c2: st.button("📋 COPY", use_container_width=True, on_click=logic.cb_copy_all)
with tb_c3:
    if st.session_state.editor_content: st.download_button("💾 TEX", st.session_state.editor_content, "out.tex", "text/plain", use_container_width=True)
    else: st.button("💾 TEX", disabled=True, use_container_width=True)
with tb_c4: st.toggle("🔧 Tự làm đẹp", key="auto_beautify_after_convert")
st.markdown('</div>', unsafe_allow_html=True)

# 4. WORKSPACE
tab_main, tab_info = st.tabs(["🛠️ SOẠN THẢO", "👤 TÁC GIẢ"])

with tab_main:
    col_ed, col_tools = st.columns([1.5, 1])
    
    with col_ed:
        st.text_area("Main Editor", value=st.session_state.editor_content, height=600, 
                     key="editor_content", label_visibility="collapsed", 
                     placeholder="Nhập nội dung vào đây hoặc bấm 'NẠP ĐỀ THI MẪU' để thử nghiệm...\n(Bấm Enter để xuống dòng)")

    with col_tools:
        # [CẬP NHẬT] Nút nạp code mẫu
        st.button("📝 NẠP ĐỀ THI MẪU (TEST)", use_container_width=True, 
                  on_click=logic.cb_load_sample, 
                  help="Bấm để nạp một đề thi mẫu vào Editor và trải nghiệm thử tính năng.")
        
        t1, t2, t3, t4 = st.tabs(["✨ LÀM ĐẸP", "🖼️ ẢNH & TAG", "🔑 ĐÁP ÁN", "📊 THỐNG KÊ"])
        
        with t1:
            btn_run, btn_sel, btn_clr = st.columns([2, 0.6, 0.6])
            with btn_run: st.button("⚡ CHẠY LÀM ĐẸP", use_container_width=True, on_click=cb_run_beauty_with_feedback)
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
            
            st.button("📦 CHUẨN HÓA MAIN (ANSBOOK)", 
                      use_container_width=True, 
                      on_click=logic.cb_run_main_struct, 
                      help="Tự động phân nhóm I, II, III và thêm code xuất đáp án.")

        with t2:
            st.caption("Gắn thẻ phân loại:")
            c_tag1, c_tag2 = st.columns(2)
            with c_tag1: st.button("➕ %Câu", use_container_width=True, on_click=logic.cb_add_tag, args=("%Câu",))
            with c_tag2: st.button("➕ %Bài", use_container_width=True, on_click=logic.cb_add_tag, args=("%Bài",))
            st.divider()
            st.caption("Cấu hình vị trí Ảnh:")
            st.selectbox("Chọn chế độ:", ["Center", "immini", "Phải [thm]", "imminiL"], key="img_sel", label_visibility="collapsed")
            st.button("🖼️ Áp dụng Ảnh", use_container_width=True, on_click=lambda: logic.cb_action_image(st.session_state.img_sel))

        with t3:
            q_types = get_question_types(st.session_state.editor_content)
            if q_types:
                existing = get_existing_answers(st.session_state.editor_content)
                with st.form("ans_form"):
                    with st.container(height=600):
                        for q, t in q_types.items():
                            old = existing.get(q, [])
                            st.markdown(f"**C.{q}** `({t})`")
                            if t == 'MC':
                                idx = "ABCD".find(old[0]) if (old and old[0] in "ABCD") else None
                                if idx == -1: idx = None
                                st.radio("MC", ["A","B","C","D"], index=idx, key=f"ans_{q}_MC", horizontal=True, label_visibility="collapsed")
                            elif t == 'TF':
                                c = st.columns(4)
                                for i, ch in enumerate("ABCD"): c[i].checkbox(ch, ch in old, key=f"ans_{q}_TF_{ch}")
                            elif t == 'SA':
                                chars = list(old[0] if old else "") + [""] * 4
                                c = st.columns(4)
                                for i in range(4): c[i].text_input("S", chars[i], max_chars=1, key=f"ans_{q}_SA_{i}", label_visibility="collapsed")
                            st.divider()
                    st.form_submit_button("💾 LƯU ĐÁP ÁN", type="primary", on_click=logic.cb_save_gui_answers, use_container_width=True)
            else:
                st.warning("Chưa có dữ liệu câu hỏi.")

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
    <div style="margin-top: 15px; font-size: 0.85em; color: #666; font-style: italic;">
        * Màu <span style="color:#28a745; font-weight:bold">XANH</span>: Đã đủ đáp án.<br>
        * Màu <span style="color:#d9534f; font-weight:bold">ĐỎ</span>: Còn thiếu đáp án.
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
