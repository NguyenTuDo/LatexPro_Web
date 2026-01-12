import streamlit as st
import streamlit.components.v1 as components
import app_logic as logic
from noi_dung_chu import NOI_DUNG_HUONG_DAN, THONG_TIN_UNG_DUNG
from math_utils import get_question_types, get_existing_answers

# 1. SETUP
st.set_page_config(page_title="Latex Pro Web", page_icon="🚀", layout="wide", initial_sidebar_state="expanded")
logic.init_session_state()
st.markdown(logic.get_theme_css(), unsafe_allow_html=True)

# JS PHÍM TẮT
def setup_shortcuts():
    js_code = """
    <script>
    document.addEventListener('keydown', function(e) {
        if ((e.ctrlKey || e.metaKey) && e.key === 'z') {
            const btn = window.parent.document.getElementById('hidden_undo');
            if (btn) btn.click();
        }
        else if ((e.ctrlKey || e.metaKey) && e.key === 'y') {
            const btn = window.parent.document.getElementById('hidden_redo');
            if (btn) btn.click();
        }
    });
    </script>
    """
    components.html(js_code, height=0)

setup_shortcuts()

st.title("Latex Pro Web")

# 2. SIDEBAR
with st.sidebar:
    st.header("⚙️ CÀI ĐẶT")
    st.toggle("🌙 Dark Mode", key="is_dark_mode")
    st.divider()
    st.subheader("📊 THỐNG KÊ")
    stats = logic.calculate_stats(st.session_state.editor_content)
    st.markdown(f"""
    <div class="stat-box">
        <div><b>Tổng câu:</b> {stats['Total']}</div>
        <hr style="margin:5px 0; border-color:#555">
        <div style="display:flex; justify-content:space-between"><span>Trắc nghiệm:</span> <b>{stats['MC']}</b></div>
        <div style="display:flex; justify-content:space-between"><span>Đúng/Sai:</span> <b>{stats['TF']}</b></div>
        <div style="display:flex; justify-content:space-between"><span>Điền khuyết:</span> <b>{stats['SA']}</b></div>
        <hr style="margin:5px 0; border-color:#555">
        <div style="color:#005fb8"><b>MC có \True: {stats['MC_True']} / {stats['MC']}</b></div>
    </div>
    """, unsafe_allow_html=True)
    
    # Nút ẩn cho Undo/Redo
    st.button("Z", key="hidden_undo", on_click=logic.cb_undo, disabled=st.session_state.history_idx <= 0)
    st.button("Y", key="hidden_redo", on_click=logic.cb_redo, disabled=st.session_state.history_idx >= len(st.session_state.history) - 1)
    st.markdown("""<style>div[data-testid="stSidebar"] button[kind="secondary"] { display: none; }</style>""", unsafe_allow_html=True)


# 3. TOP BAR
top_c1, top_c2, top_c3, top_c4 = st.columns([1.5, 1, 1, 3]) 

with top_c1:
    st.button("✨ 1. TỰ ĐỘNG CHUẨN HÓA", type="primary", use_container_width=True, on_click=logic.cb_convert_auto, help="Dọn dẹp rác và format về LaTeX")
with top_c2:
    st.button("📋 COPY ALL", use_container_width=True, on_click=logic.cb_copy_all)
with top_c3:
    if st.session_state.editor_content:
        st.download_button("💾 TẢI .TEX", st.session_state.editor_content, "out.tex", "text/plain", use_container_width=True)
    else:
        st.button("💾 TẢI .TEX", disabled=True, use_container_width=True)

st.markdown("---")

# 4. WORKSPACE
tab_main, tab_guide, tab_info = st.tabs(["🛠️ SOẠN THẢO", "📖 HƯỚNG DẪN", "👤 TÁC GIẢ"])

with tab_main:
    col_ed, col_tools = st.columns([3, 1])
    
    with col_ed:
        st.text_area("Main Editor", value=st.session_state.editor_content, height=800, 
                     key="editor_content", label_visibility="collapsed", 
                     placeholder="Nhập nội dung vào đây...\n(Bấm Enter để xuống dòng)")

    with col_tools:
        t1, t2, t3 = st.tabs(["✨ LÀM ĐẸP", "🖼️ ẢNH & TAG", "🔑 ĐÁP ÁN"])
        
        with t1:
            st.button("⚡ CHẠY LÀM ĐẸP", use_container_width=True, on_click=logic.cb_run_beauty)
            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
            
            with st.container(height=650):
                st.markdown("**1. Cơ bản:**")
                st.checkbox("Mathpix Clean", key="c_url", help="Xóa link ảnh lỗi Mathpix")
                st.checkbox("O x y", key="c_space", help="Gom nhóm O x y -> Oxy")
                st.checkbox("Dấu {,}", key="c_dec", help="1.5 -> 1,5")
                st.checkbox("Bọc $ số", key="c_dol", help="12 -> $12$")
                st.divider()
                st.markdown("**2. Cấu trúc:**")
                st.checkbox("frac -> dfrac", key="c_frac")
                st.checkbox("Hệ (heva)", key="c_sys")
                st.checkbox("Smart Clean", key="c_smart")
                st.divider()
                st.markdown("**3. Nâng cao:**")
                st.checkbox("Format Tích phân", key="c_int", help=r"\displaystyle, \limits, \mathrm{d}")
                st.checkbox("Format Vectơ", key="c_vec", help=r"\overrightarrow, chỉ số dưới")
                st.checkbox("Format Hình học (:)", key="c_colon", help="(P): -> (P) \colon")

        with t2:
            st.caption("Gắn thẻ phân loại:")
            c_tag1, c_tag2 = st.columns(2)
            with c_tag1: st.button("➕ %Câu", use_container_width=True, on_click=logic.cb_add_tag, args=("%Câu",))
            with c_tag2: st.button("➕ %Bài", use_container_width=True, on_click=logic.cb_add_tag, args=("%Bài",))
            st.divider()
            st.caption("Cấu hình vị trí Ảnh:")
            st.selectbox("Chọn chế độ:", ["Center", "immini", "Phải [thm]", "imminiL"], key="img_sel", label_visibility="collapsed")
            st.button("🖼️ Áp dụng Ảnh", use_container_width=True, on_click=lambda: logic.cb_action_image(st.session_state.img_sel))
            st.info("💡 Chọn một chế độ ảnh rồi bấm Áp dụng để tự động chèn code khung hình.")

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

# ... (Phần code trên giữ nguyên) ...

# TAB TÁC GIẢ (PHIÊN BẢN CHUẨN - KHÔNG LỖI)
with tab_info:
    # Tiêu đề lớn & Phiên bản
    st.header(f"🚀 {THONG_TIN_UNG_DUNG['Tên phần mềm']}")
    st.caption(f"Phiên bản: {THONG_TIN_UNG_DUNG['Phiên bản']}")
    
    st.divider()
    
    # Chia 2 cột: Thông tin cá nhân & Mô tả
    c1, c2 = st.columns([1.5, 2])
    
    with c1:
        st.subheader("👨‍🏫 Thông tin tác giả")
        st.write(f"**Họ tên:** {THONG_TIN_UNG_DUNG['Tác giả']}")
        st.write(f"**Đơn vị:** {THONG_TIN_UNG_DUNG['Đơn vị']}")
        st.write(f"**Liên hệ:** {THONG_TIN_UNG_DUNG['Liên hệ']}")
        
        # Nút liên hệ giả lập cho đẹp
        st.button("📞 Gọi điện", disabled=True)
    
    with c2:
        st.subheader("📝 Giới thiệu phần mềm")
        # Dùng st.info hoặc st.success để đóng khung nội dung đẹp mắt
        st.info(THONG_TIN_UNG_DUNG['Mô tả'], icon="ℹ️")
        
    st.divider()
    
    # Footer đơn giản

    st.caption("Developed with ❤️ by Thầy Tư Đô Nguyên & Gemini AI (2026)")
