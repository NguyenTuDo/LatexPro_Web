# [File: app.py]
import streamlit as st
import streamlit.components.v1 as components
import app_logic as logic
from cau_hinh.noi_dung_chu import NOI_DUNG_HUONG_DAN, THONG_TIN_UNG_DUNG
from xu_ly_toan.math_utils import get_question_types, get_existing_answers, wrap_exam_structure, preview_exam_structure

# [Thêm import re ở đầu file nếu chưa có]
import re

from xu_ly_toan.tu_luan import convert_tu_luan # Đảm bảo đã import hàm xử lý

@st.dialog("⚙️ TÙY CHỈNH ĐÓNG GÓI & XEM TRƯỚC")
def show_pkg_settings_dialog():
    st.markdown("""
    <style>
        div[data-testid="stDialog"] div[role="dialog"] { width: 95vw !important; max-width: 1400px !important; }
        .warning-box { background-color: #fff4e5; border: 1px solid #ffcc80; padding: 15px; border-radius: 8px; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)
    
    st.caption("Điều chỉnh cấu trúc đóng gói. Nhấn **'Cập nhật Preview'** để xem trước kết quả.")

    # 1. Config Mặc định
    default_cfg = {
        "cmd_tn": "\\cautn", "cmd_ds": "\\cauds", "cmd_sa": "\\caukq", "cmd_tl": "\\cautl",
        "use_ans_file": True, "use_table_ans": True,
        "table_ans_template": "\\begin{indapan}\n    {ans/ans\\currfilebase}\n\\end{indapan}",
        "custom_header": "",
        "path_tn": "ans/ans\\currfilebase-Phan-I",
        "path_ds": "ans/ans\\currfilebase-Phan-II",
        "path_sa": "ans/ans\\currfilebase-Phan-III",
        "path_main": "ans/ansb\\currfilebase"
    }
    
    # Init session state
    if "pkg_config" not in st.session_state: st.session_state.pkg_config = default_cfg.copy()
    else:
        for k, v in default_cfg.items():
            if k not in st.session_state.pkg_config: st.session_state.pkg_config[k] = v

    if "is_confirming_reset" not in st.session_state:
        st.session_state.is_confirming_reset = False

    saved_cfg = st.session_state.pkg_config

    # --- CALLBACKS AN TOÀN ---
    def cb_enable_reset():
        st.session_state.is_confirming_reset = True

    def cb_cancel_reset():
        st.session_state.is_confirming_reset = False

    def cb_confirm_reset():
        # 1. Reset Main Config về mặc định
        st.session_state.pkg_config = default_cfg.copy()
        
        # 2. [FIX LỖI MÀN HÌNH TRẮNG]
        # Thay vì gán đè, ta XÓA các key tạm (tmp_*) khỏi session_state.
        # Điều này buộc các widget (st.text_input) phải khởi tạo lại từ đầu
        # và lấy giá trị từ tham số `value` (là default_cfg).
        for key in list(st.session_state.keys()):
            if key.startswith("tmp_"):
                del st.session_state[key]
        
        # 3. Tắt trạng thái confirm
        st.session_state.is_confirming_reset = False
        st.toast("Đã khôi phục cài đặt gốc!", icon="🔄")

    def cb_save_config():
        # Lưu giá trị từ các widget (đã được Streamlit update vào session state)
        st.session_state.pkg_config = {
            "cmd_tn": st.session_state.get("tmp_cmd_tn", saved_cfg["cmd_tn"]),
            "cmd_ds": st.session_state.get("tmp_cmd_ds", saved_cfg["cmd_ds"]),
            "cmd_sa": st.session_state.get("tmp_cmd_sa", saved_cfg["cmd_sa"]),
            "cmd_tl": st.session_state.get("tmp_cmd_tl", saved_cfg["cmd_tl"]),
            "custom_header": st.session_state.get("tmp_header", saved_cfg["custom_header"]),
            "use_ans_file": st.session_state.get("tmp_use_ans", saved_cfg["use_ans_file"]),
            "use_table_ans": st.session_state.get("tmp_use_table", saved_cfg["use_table_ans"]),
            "table_ans_template": st.session_state.get("tmp_table_tpl", saved_cfg["table_ans_template"]),
            "path_main": st.session_state.get("tmp_path_main", saved_cfg["path_main"]),
            "path_tn": st.session_state.get("tmp_path_tn", saved_cfg["path_tn"]),
            "path_ds": st.session_state.get("tmp_path_ds", saved_cfg["path_ds"]),
            "path_sa": st.session_state.get("tmp_path_sa", saved_cfg["path_sa"])
        }
        st.toast("Đã lưu cấu hình thành công!", icon="✅")

    # --- GIAO DIỆN ---
    col_settings, col_preview = st.columns([1, 1.2], gap="large")

    with col_settings:
        st.markdown("#### 🛠️ Cài đặt")
        
        # Các ô nhập liệu (Dùng key tmp_*)
        st.markdown("**1. Lệnh dẫn (Commands):**")
        c1, c2 = st.columns(2)
        with c1:
            st.text_input("Trắc nghiệm:", value=saved_cfg["cmd_tn"], key="tmp_cmd_tn")
            st.text_input("Đúng Sai:", value=saved_cfg["cmd_ds"], key="tmp_cmd_ds")
        with c2:
            st.text_input("Trả lời ngắn:", value=saved_cfg["cmd_sa"], key="tmp_cmd_sa")
            st.text_input("Tự luận:", value=saved_cfg["cmd_tl"], key="tmp_cmd_tl")
            
        st.markdown("**2. Header (Lời dẫn):**")
        st.text_area("Chèn code LaTeX vào đầu:", value=saved_cfg["custom_header"], height=80, placeholder="\\section*{ĐỀ KIỂM TRA}...", key="tmp_header")

        st.markdown("**3. Cấu trúc:**")
        # Checkbox cũng dùng key tạm
        use_ans = st.checkbox("Tạo file đáp án (Opensolutionfile)", value=saved_cfg["use_ans_file"], key="tmp_use_ans")
        
        with st.expander("📂 Tùy chọn nâng cao (Đường dẫn File)", expanded=False):
            st.text_input("File Tổng (ansbook):", value=saved_cfg["path_main"], key="tmp_path_main")
            st.text_input("File Trắc nghiệm:", value=saved_cfg["path_tn"], key="tmp_path_tn")
            st.text_input("File Đúng Sai:", value=saved_cfg["path_ds"], key="tmp_path_ds")
            st.text_input("File Trả lời ngắn:", value=saved_cfg["path_sa"], key="tmp_path_sa")

        use_table = st.checkbox("Chèn bảng đáp án cuối", value=saved_cfg["use_table_ans"], disabled=not use_ans, key="tmp_use_table")
        
        # Logic hiển thị Template bảng đáp án
        if use_table:
            st.text_area("Template bảng đáp án:", value=saved_cfg["table_ans_template"], height=80, key="tmp_table_tpl")
        else:
            # Vẫn giữ giá trị ẩn trong session
            if "tmp_table_tpl" not in st.session_state:
                st.session_state.tmp_table_tpl = saved_cfg["table_ans_template"]

        st.write("")
        st.divider()

        # --- KHU VỰC NÚT BẤM ---
        if st.session_state.is_confirming_reset:
            st.markdown("""
            <div class="warning-box">
                <span style="font-size:20px">⚠️</span> <b>Xác nhận khôi phục?</b><br>
                Mọi cài đặt tùy chỉnh sẽ bị mất và quay về mặc định ban đầu.
            </div>
            """, unsafe_allow_html=True)
            
            confirm_cols = st.columns([1, 1])
            with confirm_cols[0]:
                st.button("✅ ĐỒNG Ý", type="primary", use_container_width=True, on_click=cb_confirm_reset)
            with confirm_cols[1]:
                st.button("❌ HỦY BỎ", type="secondary", use_container_width=True, on_click=cb_cancel_reset)

        else:
            b1, b2 = st.columns([1, 1])
            with b1:
                st.button("💾 LƯU CẤU HÌNH", type="primary", use_container_width=True, on_click=cb_save_config)
            with b2:
                st.button("↺ KHÔI PHỤC MẶC ĐỊNH", type="secondary", use_container_width=True, on_click=cb_enable_reset)

    with col_preview:
        cp1, cp2 = st.columns([1.5, 1])
        with cp1: st.markdown("#### 👁️ Xem trước")
        with cp2: st.button("🔄 Cập nhật Preview", use_container_width=True, help="Bấm để làm mới khung xem trước")

        # Tạo config tạm từ các giá trị trên màn hình (để preview realtime)
        temp_config = {
            "cmd_tn": st.session_state.get("tmp_cmd_tn", saved_cfg["cmd_tn"]),
            "cmd_ds": st.session_state.get("tmp_cmd_ds", saved_cfg["cmd_ds"]),
            "cmd_sa": st.session_state.get("tmp_cmd_sa", saved_cfg["cmd_sa"]),
            "cmd_tl": st.session_state.get("tmp_cmd_tl", saved_cfg["cmd_tl"]),
            "use_ans_file": st.session_state.get("tmp_use_ans", saved_cfg["use_ans_file"]),
            "use_table_ans": st.session_state.get("tmp_use_table", saved_cfg["use_table_ans"]),
            "table_ans_template": st.session_state.get("tmp_table_tpl", saved_cfg["table_ans_template"]),
            "custom_header": st.session_state.get("tmp_header", saved_cfg["custom_header"]),
            "path_tn": st.session_state.get("tmp_path_tn", saved_cfg["path_tn"]),
            "path_ds": st.session_state.get("tmp_path_ds", saved_cfg["path_ds"]),
            "path_sa": st.session_state.get("tmp_path_sa", saved_cfg["path_sa"]),
            "path_main": st.session_state.get("tmp_path_main", saved_cfg["path_main"]),
        }
        
        # [CẬP NHẬT] Gọi hàm preview (nó sẽ tự sinh demo nếu text rỗng)
        current_text = st.session_state.editor_content
        preview_text = preview_exam_structure(current_text, temp_config)
        
        st.code(preview_text, language="latex", line_numbers=True)
        if not current_text:
            st.caption("ℹ️ Đây là cấu trúc **DEMO** (vì Editor đang trống).")
        else:
            st.caption("ℹ️ Đây là cấu trúc thực tế từ nội dung của bạn.")

@st.dialog("📝 SOẠN THẢO & CHUẨN HÓA TỰ LUẬN", width="large")
def show_essay_process_dialog():
    st.markdown("""
    <style>
        div[data-testid="stDialog"] div[role="dialog"] { width: 95vw !important; max-width: 1800px !important; }
        textarea { font-family: 'Consolas', monospace !important; font-size: 14px !important; }
        /* Tinh chỉnh nút chèn nằm gọn gàng */
        .insert-btn button { height: 2.5rem; margin-top: 0px !important; }
    </style>
    """, unsafe_allow_html=True)

    # st.info("💡 **Quy trình:** Dán đề thô (Mathpix/Word) ➝ Nhấn 'Chuyển đổi' ➝ Sửa lại bên phải ➝ Nhấn 'Chèn'.")

    # 1. BỐ CỤC LẠI: Cột Input nhỏ (1) - Nút (0.1) - Cột Output lớn (2)
    c_in, c_btn, c_out = st.columns([1, 0.15, 2])

    # --- CỘT TRÁI: INPUT ---
    with c_in:
        st.markdown("**1. Dán đề thô:**")
        st.text_area("Input Raw", height=600, label_visibility="collapsed", 
                     placeholder="Dán nội dung bài tự luận vào đây...",
                     key="essay_raw_input")

    # --- CỘT GIỮA: NÚT CHUYỂN ---
    with c_btn:
        st.write("")
        st.write("") 
        st.write("")
        st.write("")
        st.write("") # Căn chỉnh cho nút nằm giữa theo chiều dọc
        if st.button("➡️", help="Chuyển đổi sang LaTeX chuẩn", type="primary", use_container_width=True):
            raw_text = st.session_state.get("essay_raw_input", "")
            if raw_text and raw_text.strip():
                processed = convert_tu_luan(raw_text)
                st.session_state.essay_final_edit = processed 
                st.session_state.essay_processed_output = processed
                st.toast("Đã chuyển đổi xong!", icon="✅")
            else:
                st.toast("Vui lòng nhập nội dung!", icon="⚠️")

    # --- CỘT PHẢI: OUTPUT & ACTION ---
    with c_out:
        # Tạo hàng tiêu đề chứa Nút Chèn luôn (để ở trên)
        c_head, c_action = st.columns([1, 0.4])
        
        with c_head:
            st.markdown("**2. Kết quả (Latex):**")
            
        with c_action:
            # Nút chèn nằm ngay trên góc phải
            st.markdown('<div class="insert-btn">', unsafe_allow_html=True)
            if st.button("✅ CHÈN VÀO CUỐI ĐỀ", type="primary", use_container_width=True):
                # Lấy giá trị hiện tại trong ô soạn thảo (qua key session)
                final_content = st.session_state.get("essay_final_edit", "")
                
                if final_content and final_content.strip():
                    current_main = st.session_state.editor_content
                    separator = "\n\n% =====================================================================\n% PHẦN TỰ LUẬN (Được thêm tự động)\n% =====================================================================\n"
                    new_content = current_main + separator + final_content
                    
                    logic.push_history(new_content)
                    st.toast("Đã thêm vào cuối đề thành công!", icon="🎉")
                    st.rerun()
                else:
                    st.warning("Nội dung kết quả đang trống.")
            st.markdown('</div>', unsafe_allow_html=True)

        # Ô Soạn thảo kết quả (Nằm dưới nút chèn)
        val_out = st.session_state.get("essay_processed_output", "")
        st.text_area("Output Latex", value=val_out, height=565, 
                     label_visibility="collapsed", key="essay_final_edit")

@st.dialog("📝 NHẬP ĐÁP ÁN CHI TIẾT")
def show_answer_input_dialog():
    # CSS Tối ưu giao diện
    st.markdown("""
    <style>
        div[data-testid="stDialog"] div[role="dialog"] { width: 85vw !important; max-width: 1400px !important; }
        div[role="radiogroup"] { gap: 10px !important; }
        .stRadio label, .stCheckbox label { font-size: 14px !important; }
        div[data-testid="stRadio"], div[data-testid="stCheckbox"], div[data-testid="stTextInput"] {
            margin-top: -5px !important;
        }
    </style>
    """, unsafe_allow_html=True)

    text = st.session_state.editor_content
    existing_ans = logic.get_existing_answers(text)
    q_types = logic.get_question_types(text)
    
    if not q_types:
        st.warning("⚠️ Không tìm thấy câu hỏi nào!")
        return

    # --- SETUP DỮ LIỆU ---
    mc_questions = [q for q, t in q_types.items() if t == 'MC']
    tf_questions = [q for q, t in q_types.items() if t == 'TF']
    sa_questions = [q for q, t in q_types.items() if t == 'SA']

    # --- HEADER & OPTIONS ---
    c_info, c_opt = st.columns([2, 1])
    with c_info:
        st.info("💡 **Quy tắc:** Trắc nghiệm chọn 1 • Đúng/Sai chọn ý Đúng • Trả lời ngắn: Tối đa 4 ký tự.")
    with c_opt:
        numbering_mode = st.radio(
            "Chế độ hiển thị số thứ tự:",
            ["Liên tục (Câu 1 ➝ Hết)", "Làm mới theo phần (1, 2... lại từ đầu)"],
            index=1,
            horizontal=False,
            label_visibility="collapsed"
        )
    
    is_reset_mode = (numbering_mode == "Làm mới theo phần (1, 2... lại từ đầu)")

    # --- [CẢI TIẾN] NHẬP NHANH CHỈ NHẬN A,B,C,D ---
    if mc_questions:
        def apply_quick_mc():
            # 1. Lấy giá trị thô & Chuyển chữ hoa ngay lập tức
            raw_val = st.session_state.get("quick_mc_input", "").upper()
            
            # 2. LỌC NGHIÊM NGẶT: Chỉ giữ lại A, B, C, D
            # Ví dụ nhập: "1a 2b sai c" -> Sẽ thành "ABC"
            clean_val = "".join([c for c in raw_val if c in ['A', 'B', 'C', 'D']])
            
            # 3. Cập nhật ngược lại vào ô input (để người dùng thấy ký tự rác biến mất)
            if raw_val != clean_val:
                st.session_state.quick_mc_input = clean_val
            
            if not clean_val: return

            # 4. Kiểm tra độ dài
            count_mc = len(mc_questions)
            if len(clean_val) > count_mc:
                st.toast(f"⚠️ Dư {len(clean_val) - count_mc} đáp án. Đã tự động cắt bớt.", icon="✂️")
            
            # 5. Điền vào Radio Buttons
            for i, q_num in enumerate(mc_questions):
                if i < len(clean_val):
                    st.session_state[f"ans_q_{q_num}"] = clean_val[i]

        st.markdown("##### ⚡ Nhập nhanh Trắc nghiệm")
        st.text_input(
            "Quick Input",
            key="quick_mc_input",
            on_change=apply_quick_mc,
            placeholder="Chỉ nhận ký tự A, B, C, D (Ví dụ: ABCD...)",
            label_visibility="collapsed"
        )
        # Hướng dẫn nhỏ
        st.caption(f"Đã khóa bộ lọc: Chỉ cho phép nhập **A, B, C, D**. Các ký tự khác (số, dấu chấm...) sẽ tự động bị xóa.")
        st.write("") 

    # --- BẮT ĐẦU FORM ---
    with st.form("answer_form", border=False):
        
        # Helper: Render Inline
        def render_row_inline(q_num, idx, type_label, content_renderer):
            display_num = idx + 1 if is_reset_mode else q_num
            c_lab, c_input = st.columns([0.8, 3.5]) 
            with c_lab:
                st.markdown(f"<div style='padding-top: 0px; font-weight:bold;'>Câu {display_num}</div>", unsafe_allow_html=True)
            with c_input:
                content_renderer(q_num)

        # Helper: Grid System
        def render_grid(questions_list, render_func):
            cols_per_row = 3
            for i in range(0, len(questions_list), cols_per_row):
                cols = st.columns(cols_per_row)
                for j in range(cols_per_row):
                    if i + j < len(questions_list):
                        q_num = questions_list[i+j]
                        idx = i + j
                        with cols[j]:
                            render_func(q_num, idx)
                            st.write("")

        # 1. TRẮC NGHIỆM (MC)
        if mc_questions:
            if not mc_questions: st.markdown("##### 🔵 Phần Trắc nghiệm")
            
            def content_mc(q_num):
                default_val = existing_ans.get(q_num, [])
                val_in_session = st.session_state.get(f"ans_q_{q_num}")
                opts = ['A', 'B', 'C', 'D']
                
                if val_in_session and val_in_session in opts:
                    sel_idx = opts.index(val_in_session)
                elif default_val and default_val[0] in opts:
                    sel_idx = opts.index(default_val[0])
                else:
                    sel_idx = None

                st.radio(f"mc_{q_num}", options=opts, index=sel_idx, horizontal=True, label_visibility="collapsed", key=f"ans_q_{q_num}")

            render_grid(mc_questions, lambda q, idx: render_row_inline(q, idx, "MC", content_mc))
            st.markdown("---")

        # 2. ĐÚNG SAI (TF)
        if tf_questions:
            st.markdown("##### 🟠 Phần Đúng/Sai")
            def content_tf(q_num):
                current_val = existing_ans.get(q_num, [])
                c1, c2, c3, c4 = st.columns(4) 
                for k, opt in enumerate(['A', 'B', 'C', 'D']):
                    with [c1, c2, c3, c4][k]:
                        st.checkbox(opt, value=(opt in current_val), key=f"ds_{q_num}_{opt}")
            render_grid(tf_questions, lambda q, idx: render_row_inline(q, idx, "TF", content_tf))
            st.markdown("---")

        # 3. TRẢ LỜI NGẮN (SA)
        if sa_questions:
            st.markdown("##### 🟣 Phần Trả lời ngắn")
            def content_sa(q_num):
                val_str = existing_ans.get(q_num, [])
                val_str = val_str[0] if val_str else ""
                user_input = st.text_input(f"sa_{q_num}", value=val_str, max_chars=4, placeholder="-1,5", label_visibility="collapsed", key=f"ans_q_{q_num}")
                if user_input:
                    clean_input = user_input.replace('.', ',')
                    if not re.match(r'^[-0-9,]+$', clean_input):
                        st.caption(f"❌ :red[Sai]")
            render_grid(sa_questions, lambda q, idx: render_row_inline(q, idx, "SA", content_sa))

        # NÚT SUBMIT
        submitted = st.form_submit_button("💾 LƯU ĐÁP ÁN & CẬP NHẬT CODE", type="primary", use_container_width=True)
        
        if submitted:
            new_answers = {}
            has_error = False
            
            # Thu thập dữ liệu
            for q in mc_questions:
                val = st.session_state.get(f"ans_q_{q}")
                if val: new_answers[q] = [val]
            
            for q in tf_questions:
                vals = [opt for opt in ['A', 'B', 'C', 'D'] if st.session_state.get(f"ds_{q}_{opt}")]
                new_answers[q] = vals
            
            for q in sa_questions:
                val = st.session_state.get(f"ans_q_{q}", "")
                if val:
                    final_val = val.replace('.', ',')
                    if not re.match(r'^[-0-9,]+$', final_val):
                        st.toast(f"❌ Câu {q}: Sai định dạng!", icon="🛑")
                        has_error = True
                    else:
                        new_answers[q] = [final_val]

            if not has_error:
                updated_text = logic.inject_answer_keys(text, new_answers)
                logic.push_history(updated_text)
                st.rerun()
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
# JS & CSS INJECTION
def setup_resources():
    # [CẬP NHẬT] Thêm logic bắt phím tắt Ctrl+Z (Undo) và Ctrl+Y (Redo)
    js_code = """
    <script>
    // 1. Logic ẩn hiện Sidebar
    const toggleSidebar = () => {
        const sidebarBtn = window.parent.document.querySelector('[data-testid="stSidebarCollapsedControl"] button');
        if (sidebarBtn) { sidebarBtn.click(); } 
        else { const closeBtn = window.parent.document.querySelector('section[data-testid="stSidebar"] button'); if (closeBtn) closeBtn.click(); }
    };

    // 2. Logic tìm nút và tô màu (MutationObserver)
    const observer = new MutationObserver(() => {
        const buttons = window.parent.document.querySelectorAll('button');
        buttons.forEach(btn => {
            if (btn.innerText.includes("⚙️")) { btn.onclick = toggleSidebar; }
            if (btn.innerText.includes("ĐÓNG GÓI MAIN")) btn.classList.add("custom-ansbook-btn");
            if (btn.innerText.includes("CHUẨN HÓA EXTEST") || btn.innerText.includes("CHUẨN HÓA TỰ LUẬN")) btn.classList.add("custom-auto-convert-btn");
        });
    });
    observer.observe(window.parent.document.body, { childList: true, subtree: true });

    // 3. [MỚI] Logic bắt sự kiện phím tắt (Hotkeys)
    const doc = window.parent.document;
    doc.addEventListener('keydown', function(e) {
        // Kiểm tra phím Ctrl (Windows) hoặc Command (Mac)
        if (e.ctrlKey || e.metaKey) {
            
            // --- UNDO: Ctrl + Z (Không giữ Shift) ---
            if (e.key.toLowerCase() === 'z' && !e.shiftKey) {
                // Tìm nút có chữ "Undo" trong sidebar
                const btnUndo = Array.from(doc.querySelectorAll('button')).find(b => b.innerText.includes("Undo"));
                if (btnUndo && !btnUndo.disabled) {
                    e.preventDefault(); // Chặn undo mặc định của trình duyệt để tránh xung đột
                    btnUndo.click();
                }
            }
            
            // --- REDO: Ctrl + Y  HOẶC  Ctrl + Shift + Z ---
            else if (e.key.toLowerCase() === 'y' || (e.key.toLowerCase() === 'z' && e.shiftKey)) {
                // Tìm nút có chữ "Redo" trong sidebar
                const btnRedo = Array.from(doc.querySelectorAll('button')).find(b => b.innerText.includes("Redo"));
                if (btnRedo && !btnRedo.disabled) {
                    e.preventDefault();
                    btnRedo.click();
                }
            }
        }
    });
    </script>
    """
    components.html(js_code, height=0)

def cb_select_all_beauty():
    keys = ["c_smart", "c_url", "c_space", "c_num_math", "c_frac", "c_sys", "c_int", "c_vec", "c_colon"]
    for key in keys: st.session_state[key] = True

# [File: app.py]

# Khởi tạo session state cho cấu hình đóng gói nếu chưa có
if "pkg_config" not in st.session_state:
    st.session_state.pkg_config = {
        "cmd_tn": "\\cautn",
        "cmd_ds": "\\cauds",
        "cmd_sa": "\\caukq",
        "cmd_tl": "\\cautl",
        "use_ans_file": True,
        "use_table_ans": True,
        "custom_header": ""
    }

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

# [File: app.py] - Thay thế toàn bộ đoạn CSS style cũ

# CSS TỐI ƯU GIAO DIỆN & HARD-CODE THEME (KHÔNG CẦN CONFIG.TOML)
st.markdown("""
<style>
/* ====================================================================
   1. ÉP MÀU XANH (HARD-CODE THEME) - KHẮC PHỤC LỖI MÀU ĐỎ TRÊN CLOUD
   ==================================================================== */
   
/* Đổi màu chính của biến môi trường (Hỗ trợ một số thành phần) */
:root {
    --primary-color: #005fb8 !important;
    --background-color: #ffffff !important;
    --secondary-background-color: #f0f2f6 !important;
    --text-color: #262730 !important;
    --font: "Source Sans Pro", sans-serif !important;
}

/* Nút Primary (Màu xanh) */
button[kind="primary"] {
    background-color: #005fb8 !important;
    border-color: #005fb8 !important; 
    color: white !important;
}
button[kind="primary"]:hover {
    background-color: #004a94 !important;
    border-color: #004a94 !important;
}
button[kind="primary"]:focus {
    box-shadow: 0 0 0 0.2rem rgba(0, 95, 184, 0.5) !important;
}

/* Checkbox & Radio Button khi được chọn */
div[data-testid="stCheckbox"] label span[data-checked="true"] > div:first-child,
div[data-testid="stRadio"] label span[data-checked="true"] > div:first-child {
    background-color: #005fb8 !important;
    border-color: #005fb8 !important;
}

/* Toggle (Nút gạt) */
label[data-testid="stWidgetLabel"] + div[data-testid="stCheckbox"] span[data-checked="true"] {
    background-color: #005fb8 !important;
}

/* Thanh trượt (Slider) */
div[data-testid="stSlider"] div[data-testid="stTickBar"] {
    background-color: #005fb8 !important;
}
div[data-testid="stSlider"] div[role="slider"] {
    background-color: #005fb8 !important;
    box-shadow: 0 0 0 0.2rem rgba(0, 95, 184, 0.2) !important;
}

/* Link text */
a {
    color: #005fb8 !important;
}

/* Ẩn thanh trang trí 7 màu mặc định của Streamlit (thường có màu đỏ) */
div[data-testid="stDecoration"] {
    background-image: linear-gradient(90deg, #005fb8, #0099ff) !important;
    height: 3px !important;
}

/* ====================================================================
   2. THU GỌN GIAO DIỆN (COMPACT MODE) - KHẮC PHỤC LỖI "TO QUÁ KHỔ"
   ==================================================================== */

/* Thu nhỏ Font chữ toàn bộ hệ thống */
html, body, [class*="css"] {
    font-size: 14px !important; /* Giảm từ 16px xuống 14px */
}

/* Co gọn khoảng cách lề (Padding) của trang chính */
.block-container { 
    padding-top: 1.5rem !important; /* Đẩy nội dung lên sát hơn */
    padding-left: 2rem !important; 
    padding-right: 2rem !important;
    padding-bottom: 50px !important;
    max-width: 100% !important;
}

/* Ẩn Header mặc định của Streamlit Cloud (Dòng "Manage app" gây tốn diện tích) */
header[data-testid="stHeader"] {
    display: none !important;
}
/* Đẩy nội dung lên bù vào chỗ Header vừa ẩn */
div[data-testid="stAppViewContainer"] > section:first-child {
    padding-top: 0px !important;
}

/* Thu hẹp Sidebar */
section[data-testid="stSidebar"] {
    width: 260px !important; /* Mặc định là 336px -> Thu nhỏ lại */
    padding-top: 1rem !important;
}
section[data-testid="stSidebar"] > div {
    padding-top: 1rem !important;
}

/* Giảm khoảng cách giữa các Widget */
.stButton, .stCheckbox, .stRadio, .stSelectbox, .stToggle, .stTextInput, .stTextArea { 
    margin-bottom: 0px !important; 
    margin-top: 0px !important; 
}
div[data-testid="stVerticalBlock"] > div {
    gap: 0.5rem !important; /* Giảm gap từ 1rem xuống 0.5rem */
}

/* Tinh chỉnh Font chữ cho Code Editor (Text Area) */
.stTextArea textarea { 
    font-family: 'Consolas', 'Monaco', monospace !important; 
    font-size: 13.5px !important; /* Chữ trong ô code nhỏ lại cho dễ nhìn nhiều */
    line-height: 1.45 !important;
    padding: 10px !important;
    background-color: #fcfcfc !important; 
    border: 1px solid #e0e0e0 !important;
}

/* ====================================================================
   3. STYLE RIÊNG CỦA APP (NÚT GRADIENT, ICONS...)
   ==================================================================== */
.custom-ansbook-btn {
    background: linear-gradient(90deg, #FF9800 0%, #F44336 100%) !important;
    color: white !important; border: none !important;
    font-weight: 700 !important; font-size: 14px !important;
    box-shadow: 0 3px 10px rgba(244, 67, 54, 0.4) !important;
}
.custom-ansbook-btn:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 5px 15px rgba(244, 67, 54, 0.6) !important;
}

.custom-auto-convert-btn {
    background: linear-gradient(90deg, #005fb8 0%, #0099ff 100%) !important;
    color: white !important; border: none !important;
    font-weight: 700 !important; font-size: 14px !important;
    box-shadow: 0 3px 10px rgba(0, 95, 184, 0.4) !important;
}
.custom-auto-convert-btn:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 5px 15px rgba(0, 95, 184, 0.6) !important;
}

/* Footer ẩn */
footer { display: none !important; }

/* Dark mode overrides (nếu người dùng bật chế độ tối máy tính) */
@media (prefers-color-scheme: dark) {
    section[data-testid="stSidebar"] { background-color: #262730 !important; }
    .stTextArea textarea { background-color: #1e1e1e !important; color: #d4d4d4 !important; border-color: #333 !important; }
}
</style>
""", unsafe_allow_html=True)

# 2. SIDEBAR
with st.sidebar:
    st.markdown("**⚙️ CÀI ĐẶT**")
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

        # [CẬP NHẬT] Khu vực Đóng gói Main với nút Tùy chỉnh
        col_pkg_main, col_pkg_set = st.columns([1, 0.15])
        
        with col_pkg_main:
            # Hàm callback mới truyền settings vào logic xử lý
            def run_pkg_with_settings():
                settings = st.session_state.pkg_config
                # Gọi logic chuẩn hóa (Bạn cần cập nhật logic.cb_run_main_struct để nhận tham số này)
                # Hoặc viết trực tiếp logic ở đây:
                current_text = st.session_state.editor_content
                if current_text:
                    # Gọi hàm từ math_utils với settings
                    new_text = wrap_exam_structure(current_text, settings)
                    logic.push_history(new_text)
                    st.toast("Đã đóng gói theo cấu hình tùy chỉnh!", icon="📦")
                else:
                    st.warning("Chưa có nội dung!")

            st.button("📦 ĐÓNG GÓI MAIN", 
                      use_container_width=True, 
                      on_click=run_pkg_with_settings, 
                      help="Đóng gói đề thi theo cấu hình hiện tại.")

        with col_pkg_set:
            st.button("⚙️", help="Tùy chỉnh lệnh dẫn và cấu trúc đóng gói", on_click=show_pkg_settings_dialog)
        

        t1, t_essay, t2, t3 = st.tabs(["✨ LÀM ĐẸP", "📝 TỰ LUẬN", "🖼️ ẢNH & TAG", "🔑 ĐÁP ÁN"])
        with t1:
            st.caption("Công cụ làm đẹp code LaTeX theo các tùy chọn bên dưới (có thể dán code đã có vào để sửa)")
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
            
            st.markdown("**2️⃣ Nâng cao & Cấu trúc:**")
            col_comb_1, col_comb_2 = st.columns(2)
            with col_comb_1:
                    st.checkbox("frac ➝ dfrac", key="c_frac", help="\\frac{1}{2} ➝ \\dfrac{1}{2}")
                    st.checkbox("Tex ➝ \\heva/\\hoac", key="c_sys", help="Gộp các môi trường cases/array về lệnh tắt \\heva, \\hoac.")
                    st.checkbox("Displaystyle", key="c_int", help="• Thêm \\displaystyle\n• Thêm \\limits\n• dx ➝ \\mathrm{\\,d}x")
            with col_comb_2:
                    st.checkbox("Vectơ chuẩn", key="c_vec", help="• \\vec{u} ➝ \\overrightarrow{u}")
                    st.checkbox("Colon (:)", key="c_colon", help="Đổi dấu : trong hình học thành \\colon")

        # [File: app.py] - Tìm đoạn "with t_essay:"

        with t_essay:
            st.caption("Công cụ tách biệt để xử lý phần Tự Luận, tránh ảnh hưởng đến code đã có.")
    
    # Thay vì nút xử lý trực tiếp, giờ là nút mở Popup
            st.button("🛠️ MỞ CÔNG CỤ SOẠN TỰ LUẬN (POPUP)", 
              type="primary", 
              use_container_width=True, 
              on_click=show_essay_process_dialog, # Gọi hàm popup vừa tạo
              help="Mở cửa sổ nhập liệu riêng để xử lý Bài 1, Bài 2...")
    
            st.info("""
    **Cách dùng:**
    1.  Nhấn nút trên để mở cửa sổ soạn thảo.
    2.  Copy phần tự luận thô (từ Mathpix/Word) dán vào.
    3.  Phần mềm sẽ chuẩn hóa thành code `ex`, `enumerate`.
    4.  Kiểm tra xong nhấn **"Chèn vào cuối đề"** để ghép vào bài làm chính.
    """)

        with t2:
            st.caption("Đánh số câu tự động (trước \\begin\{ex}):")
            c_tag1, c_tag2 = st.columns(2)
            with c_tag1: st.button("➕ %Câu", use_container_width=True, on_click=logic.cb_add_tag, args=("%Câu",))
            with c_tag2: st.button("➕ %Bài", use_container_width=True, on_click=logic.cb_add_tag, args=("%Bài",))
            st.caption("Tùy chọn vị trí ảnh trong câu hỏi:")
            st.selectbox("Chọn chế độ:", ["Center", "immini", "Phải [thm]", "imminiL"], key="img_sel", label_visibility="collapsed")
            st.button("🖼️ Áp dụng chế độ Ảnh trên", use_container_width=True, on_click=lambda: logic.cb_action_image(st.session_state.img_sel))

        # [CẬP NHẬT] TAB THỐNG KÊ - TÍCH HỢP NÚT NHẬP LIỆU
# [File: app.py] - Thay thế nội dung bên trong "with t3:"

# [File: app.py] - Thay thế nội dung bên trong "with t3:"

with t3:
    st.caption("Thống kê số lượng câu hỏi và kiểm tra đáp án.")
    
    if not st.session_state.editor_content:
        st.info("Chưa có nội dung để thống kê.")
    else:
        # 1. LẤY DỮ LIỆU CHUẨN
        stats = logic.get_question_types(st.session_state.editor_content)
        total = len(stats)
        
        # [FIX] Đếm đúng mã định danh (MC, TF, SA)
        # Nếu dùng code cũ count('TN') sẽ ra 0 vì math_utils trả về 'MC'
        count_mc = list(stats.values()).count('MC')
        count_tf = list(stats.values()).count('TF')
        count_sa = list(stats.values()).count('SA')
        
        # 2. HIỂN THỊ THẺ THỐNG KÊ (Thiết kế mới)
        c_total, c_detail = st.columns([1, 3])
        
        with c_total:
            # Box TỔNG CÂU (Màu đỏ nổi bật)
            st.markdown(f"""
            <div style="
                background-color: #fff1f0; 
                border: 1px solid #ffa39e; 
                border-radius: 8px; 
                padding: 15px 10px; 
                text-align: center;
                height: 100%;">
                <div style="font-size: 13px; color: #d63031; font-weight: 700; text-transform: uppercase; margin-bottom: 5px;">TỔNG CÂU</div>
                <div style="font-size: 38px; font-weight: 800; color: #c0392b; line-height: 1;">{total}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with c_detail:
            # 3 thẻ con nằm ngang
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f"""<div style="text-align:center; padding:10px; background:#e6f7ff; border-radius:8px; border:1px solid #91caff"><div style="color:#0050b3; font-weight:bold; font-size:24px">{count_mc}</div><div style="color:#003a8c; font-size:11px; font-weight:600">TRẮC NGHIỆM</div></div>""", unsafe_allow_html=True)
            with c2:
                st.markdown(f"""<div style="text-align:center; padding:10px; background:#f6ffed; border-radius:8px; border:1px solid #b7eb8f"><div style="color:#389e0d; font-weight:bold; font-size:24px">{count_tf}</div><div style="color:#237804; font-size:11px; font-weight:600">ĐÚNG SAI</div></div>""", unsafe_allow_html=True)
            with c3:
                st.markdown(f"""<div style="text-align:center; padding:10px; background:#f9f0ff; border-radius:8px; border:1px solid #d3adf7"><div style="color:#722ed1; font-weight:bold; font-size:24px">{count_sa}</div><div style="color:#531dab; font-size:11px; font-weight:600">TRẢ LỜI NGẮN</div></div>""", unsafe_allow_html=True)

        st.divider()
        
        # 3. KIỂM TRA ĐÁP ÁN (Gọn gàng)
        existing_ans = logic.get_existing_answers(st.session_state.editor_content)
        missing_count = sum(1 for q in stats if q not in existing_ans or not existing_ans[q])
        
        if missing_count > 0:
            # [YÊU CẦU] Chỉ báo số lượng, không liệt kê 1,2,3...
            st.warning(f"Còn **{missing_count}** câu chưa nhập đáp án.", icon="⚠️")
            st.markdown("<div style='font-size:14px; color:#666; margin-bottom:10px'><i>Vui lòng nhập đầy đủ để xuất file chính xác nhất.</i></div>", unsafe_allow_html=True)
        else:
            st.success("✅ Tuyệt vời! Tất cả câu hỏi đã có đáp án.", icon="🎉")
            
        # Nút mở Popup to, rõ
        if st.button("📝 NHẬP/SỬA ĐÁP ÁN (POPUP)", type="primary", use_container_width=True):
            show_answer_input_dialog()
            
        st.caption("💡 Mẹo: Nhấn nút trên để mở bảng nhập nhanh. Dữ liệu sẽ tự động điền vào các lệnh `\\choice`, `\\True`, `\\shortans`.")
# [File: app.py] - Thay thế nội dung trong "with tab_info:"

# [File: app.py] - Thay thế nội dung trong "with tab_info:"

with tab_info:
    # 1. CSS RIÊNG CHO TAB INFO (Tinh chỉnh Layout)
    st.markdown("""
    <style>
        .info-header { text-align: center; margin-bottom: 35px; }
        .info-title { font-size: 36px; font-weight: 800; color: #005fb8; margin: 0; letter-spacing: -1px; text-transform: uppercase;}
        .info-ver { 
            font-size: 14px; color: #555; background: #e9ecef; 
            padding: 5px 15px; border-radius: 20px; font-weight: 600; 
            display: inline-block; margin-top: 8px; border: 1px solid #dee2e6;
        }
        
        /* CARD TÁC GIẢ */
        .author-box {
            background: linear-gradient(135deg, #ffffff 0%, #fcfcfc 100%);
            border: 1px solid #e0e0e0; border-radius: 16px;
            padding: 30px; 
            display: flex; flex-direction: row; align-items: center; gap: 30px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.06); 
            margin-bottom: 30px;
        }
        
        .avatar-img { 
            width: 120px; height: 120px; border-radius: 50%; object-fit: cover; 
            border: 5px solid #fff; box-shadow: 0 5px 15px rgba(0,0,0,0.15); 
            flex-shrink: 0; /* Không bị bóp méo ảnh */
        }
        
        .author-detail { flex-grow: 1; }
        .author-detail h3 { margin: 0 0 10px 0; color: #2c3e50; font-size: 24px; font-weight: 700; }
        .author-detail p { margin: 6px 0; color: #555; font-size: 16px; display: flex; align-items: center; gap: 10px; }
        
        .social-link { 
            text-decoration: none !important; color: white !important; background: #1877F2; 
            padding: 10px 20px; border-radius: 8px; font-weight: 600; font-size: 14px; 
            display: inline-flex; align-items: center; gap: 8px; margin-top: 15px;
            transition: all 0.2s; box-shadow: 0 4px 10px rgba(24, 119, 242, 0.3);
        }
        .social-link:hover { background: #145dbf; transform: translateY(-2px); box-shadow: 0 6px 15px rgba(24, 119, 242, 0.4); }

        /* Icon trong st.info */
        div[data-testid="stNotification"] { border-radius: 12px !important; border-left-width: 6px !important; }
    </style>
    """, unsafe_allow_html=True)

    # 2. HEADER
    st.markdown(f"""
    <div class="info-header">
        <div class="info-title">🚀 {THONG_TIN_UNG_DUNG['Tên phần mềm']}</div>
        <span class="info-ver">{THONG_TIN_UNG_DUNG['Phiên bản']}</span>
    </div>
    """, unsafe_allow_html=True)

    # 3. AUTHOR CARD
    st.markdown(f"""
    <div class="author-box">
        <img src="{THONG_TIN_UNG_DUNG['Avatar']}" class="avatar-img">
        <div class="author-detail">
            <h3>{THONG_TIN_UNG_DUNG['Tác giả']}</h3>
            <p>🏫 <b>Đơn vị:</b> {THONG_TIN_UNG_DUNG['Đơn vị']}</p>
            <p>📞 <b>Liên hệ:</b> {THONG_TIN_UNG_DUNG['Liên hệ']}</p>
            <a href="{THONG_TIN_UNG_DUNG['Facebook']}" target="_blank" class="social-link">
                <span style="font-size:16px">💬</span> Nhắn tin qua Facebook
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 4. MÔ TẢ APP (Hiển thị đẹp nhờ Markdown đã fix)
    st.info(THONG_TIN_UNG_DUNG['Mô tả'], icon="💡")
    
    st.write("")
    st.divider()
    
    # 5. HƯỚNG DẪN CHI TIẾT
    st.subheader("📖 TÀI LIỆU HƯỚNG DẪN")
    st.caption("Nhấn vào từng mục để xem chi tiết cách sử dụng các tính năng nâng cao.")

    for title, content in NOI_DUNG_HUONG_DAN:
        with st.expander(f"📌 {title}", expanded=False):
            st.markdown(content, unsafe_allow_html=True)

    st.divider()
    
    # 6. FOOTER
    c_ft1, c_ft2 = st.columns([1, 1])
    with c_ft1:
        st.caption("© 2026 Latex Pro Web. All rights reserved.")
    with c_ft2:
        st.markdown("<div style='text-align:right; color:#888; font-size:12px'><i>Powered by Streamlit & Python</i></div>", unsafe_allow_html=True)
