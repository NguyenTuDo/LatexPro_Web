# [File: app_logic.py]
import streamlit as st
import re
import pyperclip

# --- IMPORT ---
from cau_hinh.noi_dung_chu import NOI_DUNG_HUONG_DAN, THONG_TIN_UNG_DUNG

from xu_ly_toan.math_utils import (process_formatting, inject_answer_keys, parse_answer_string, 
                                   remove_exam_headers, get_question_types, get_existing_answers,
                                   add_question_comments, manage_question_layout, 
                                   basic_standardize, wrap_exam_structure)
from xu_ly_toan.trac_nghiem import convert_trac_nghiem
from xu_ly_toan.dung_sai import convert_dung_sai
from xu_ly_toan.tra_loi_ngan import convert_tra_loi_ngan

# --- CẤU HÌNH MẶC ĐỊNH ---
LOGIC_KEYS = ['c_url', 'c_space', 'c_dec', 'c_dol', 'c_frac', 'c_sys', 'c_delim', 'c_dot', 'c_smart', 
              'c_int', 'c_vec', 'c_colon']
DEFAULTS =   [True,    True,      True,    True,    True,     True,    False,     False,   True,
              True,    True,      True]

def init_session_state():
    if "editor_content" not in st.session_state: st.session_state.editor_content = ""
    if "is_dark_mode" not in st.session_state: st.session_state.is_dark_mode = False
    if "history" not in st.session_state: st.session_state.history = [""]
    if "history_idx" not in st.session_state: st.session_state.history_idx = 0
    if "auto_beautify_after_convert" not in st.session_state: st.session_state.auto_beautify_after_convert = True
    
    # Biến chứa thông báo Popup
    if "msg_toast" not in st.session_state: st.session_state.msg_toast = None

    for k, d in zip(LOGIC_KEYS, DEFAULTS):
        if k not in st.session_state: st.session_state[k] = d

def push_history(new_content):
    if new_content == st.session_state.editor_content: return
    st.session_state.history = st.session_state.history[:st.session_state.history_idx + 1]
    st.session_state.history.append(new_content)
    st.session_state.history_idx += 1
    st.session_state.editor_content = new_content

def show_popup(msg):
    st.session_state.msg_toast = msg

def cb_undo():
    if st.session_state.history_idx > 0:
        st.session_state.history_idx -= 1
        st.session_state.editor_content = st.session_state.history[st.session_state.history_idx]
        show_popup("↩️ Undo thành công")

def cb_redo():
    if st.session_state.history_idx < len(st.session_state.history) - 1:
        st.session_state.history_idx += 1
        st.session_state.editor_content = st.session_state.history[st.session_state.history_idx]
        show_popup("↪️ Redo thành công")

def get_theme_css():
    if st.session_state.is_dark_mode:
        t = { "bg_app": "#1e1e1e", "text_main": "#d4d4d4", "bg_sidebar": "#252526", "bg_editor": "#1e1e1e", "border_editor": "#3e3e42", "bg_panel": "#252526", "border_panel": "#3e3e42", "header": "#858585", "text_editor": "#4daafc" }
    else:
        t = { "bg_app": "#ffffff", "text_main": "#2c3e50", "bg_sidebar": "#f8f9fa", "bg_editor": "#ffffff", "border_editor": "#ced4da", "bg_panel": "#f8f9fa", "border_panel": "#e9ecef", "header": "#666", "text_editor": "#0044ff" }
    
    return f"""
    <style>
        [data-testid="stHeader"], header {{ display: none !important; }}
        footer {{ display: none !important; }}
        [data-testid="stToolbar"] {{ display: none !important; }}
        [data-testid="stDecoration"] {{ display: none !important; }}
        [data-testid="stSidebarCollapsedControl"] {{ display: none !important; }}
        .stApp {{ margin-top: -55px; }}
        .custom-sidebar-btn button {{
            background: transparent !important;
            border: 1px solid #ddd !important;
            color: #666 !important;
            border-radius: 20px !important;
            font-size: 13px !important;
            padding: 2px 10px !important;
        }}
        .custom-sidebar-btn button:hover {{
            border-color: {t['text_editor']} !important;
            color: {t['text_editor']} !important;
        }}
    </style>
    """

def calculate_stats(text):
    if not text: return {"Total": 0, "MC_Done": 0, "MC_Total": 0, "TF_Done": 0, "TF_Total": 0, "SA_Done": 0, "SA_Total": 0}
    q_types = get_question_types(text)
    existing = get_existing_answers(text)
    stats = {"Total": len(q_types), "MC_Done": 0, "MC_Total": 0, "TF_Done": 0, "TF_Total": 0, "SA_Done": 0, "SA_Total": 0}
    for q, t in q_types.items():
        if t == 'MC': stats["MC_Total"] += 1
        elif t == 'TF': stats["TF_Total"] += 1
        elif t == 'SA': stats["SA_Total"] += 1
        has_ans = False
        ans_data = existing.get(q, [])
        if t == 'MC':
            if ans_data and len(ans_data) > 0: has_ans = True
        elif t == 'TF':
            if ans_data and len(ans_data) > 0: has_ans = True
        elif t == 'SA':
            if ans_data and str(ans_data[0]).strip(): has_ans = True
        if has_ans:
            if t == 'MC': stats["MC_Done"] += 1
            elif t == 'TF': stats["TF_Done"] += 1
            elif t == 'SA': stats["SA_Done"] += 1
    return stats

# --- CALLBACKS (ĐÃ SỬA: DÙNG SPINNER THAY CHO STATUS BOX) ---

def cb_convert_auto():
    raw = st.session_state.editor_content
    if not raw.strip(): show_popup("⚠️ Nội dung trống!"); return
    
    # [THAY ĐỔI] Dùng spinner: Chỉ hiện vòng quay khi đang chạy, xong là biến mất luôn
    with st.spinner("Đang xử lý..."):
        raw = remove_exam_headers(raw)
        raw = basic_standardize(raw)
        blocks = re.split(r'(?i)(?=Câu\s*\d+)', raw)
        res = []
        for b in blocks:
            if not b.strip(): continue
            lg = re.split(r'(?i)(Lời\s+giải|HDG)[\s:]*', b, maxsplit=1)
            mp = lg[0]; sol = lg[-1] if len(lg)>1 else ""
            try:
                if re.search(r'(?:^|\s)[a-d][\.\)]\s', mp): r = convert_dung_sai(mp, sol)
                elif re.search(r'(?:^|\s)[A-D][\.\)]\s', mp): r = convert_trac_nghiem(mp, sol)
                else: r = convert_tra_loi_ngan(mp, sol)
                res.append(r)
            except: res.append(b)
        text_struct = "\n\n".join(res)
        
        if st.session_state.get("auto_beautify_after_convert", False):
            cfg = {k: st.session_state[k] for k in LOGIC_KEYS}
            params = {
                'use_smart_format': cfg['c_smart'], 'use_clean_url': cfg['c_url'], 'use_clean_space': cfg['c_space'],
                'use_fix_decimal': cfg['c_dec'], 'use_add_dollar': cfg['c_dol'],
                'use_frac_dfrac': cfg['c_frac'], 'use_convert_system': cfg['c_sys'],
                'use_remove_delimiter': cfg['c_delim'], 'use_dot_multiplication': cfg['c_dot'],
                'use_format_integral': cfg['c_int'], 'use_format_vector': cfg['c_vec'], 'use_format_colon': cfg['c_colon'],
                'use_add_comment': False, 'image_layout_mode': 'ignore'
            }
            final_text = process_formatting(text_struct, **params)
            msg = "✅ Chuẩn hóa & Làm đẹp xong!"
        else:
            final_text = text_struct
            msg = "✅ Chuẩn hóa cấu trúc xong!"

        push_history(final_text)
    
    # Khi spinner tắt đi, Popup mới hiện ra báo thành công
    show_popup(msg)

def cb_run_beauty():
    txt = st.session_state.editor_content
    if not txt.strip(): return
    
    # Thêm spinner cho nút Làm đẹp
    with st.spinner("Đang làm đẹp..."):
        cfg = {k: st.session_state[k] for k in LOGIC_KEYS}
        params = {
            'use_smart_format': cfg['c_smart'], 'use_clean_url': cfg['c_url'], 'use_clean_space': cfg['c_space'],
            'use_fix_decimal': cfg['c_dec'], 'use_add_dollar': cfg['c_dol'],
            'use_frac_dfrac': cfg['c_frac'], 'use_convert_system': cfg['c_sys'],
            'use_remove_delimiter': cfg['c_delim'], 'use_dot_multiplication': cfg['c_dot'],
            'use_format_integral': cfg['c_int'], 'use_format_vector': cfg['c_vec'], 'use_format_colon': cfg['c_colon'],
            'use_add_comment': False, 'image_layout_mode': 'ignore'
        }
        new_text = process_formatting(txt, **params)
        push_history(new_text)
        
    show_popup("⚡ Đã làm đẹp xong!")

def cb_run_main_struct():
    txt = st.session_state.editor_content
    if not txt.strip(): 
        show_popup("⚠️ Nội dung trống!")
        return
    
    new_text = wrap_exam_structure(txt)
    
    if new_text == txt:
        show_popup("⚠️ Không tìm thấy cấu trúc câu hỏi (ex)!")
    else:
        push_history(new_text)
        show_popup("📦 Đóng gói Main (Ansbook) thành công!")

def cb_action_image(mode):
    txt = st.session_state.editor_content
    if not txt: return
    map_mode = {"Center": "default", "immini": "immini", "Phải [thm]": "immini_thm", "imminiL": "immini_left"}
    if mode in map_mode:
        new_text = manage_question_layout(txt, map_mode[mode])
        push_history(new_text)
        show_popup(f"🖼️ Đã chỉnh ảnh: {mode}")

def cb_add_tag(mode):
    txt = st.session_state.editor_content
    if not txt: return
    new_text = txt
    if mode == "%Câu": new_text = add_question_comments(txt)
    elif mode == "%Bài":
        parts = re.split(r'(\\begin\{ex\}.*?\\end\{ex\})', txt, flags=re.DOTALL)
        res = []; c = 1
        for p in parts:
            if p.strip().startswith(r'\begin{ex}'): res.append(f"%Bài tập {c}\n{p}"); c += 1
            else: res.append(p)
        new_text = "".join(res)
    push_history(new_text)
    show_popup(f"🏷️ Đã thêm thẻ {mode}")

def cb_copy_all():
    txt = st.session_state.editor_content
    if txt:
        try: pyperclip.copy(txt); show_popup("📋 Đã Copy vào bộ nhớ!")
        except: show_popup("⚠️ Lỗi Copy! Hãy dùng Ctrl+A -> Ctrl+C")

def cb_save_gui_answers():
    final = {}
    sa_groups = {}
    for k, v in st.session_state.items():
        if k.startswith("ans_"):
            p = k.split("_"); q = int(p[1]); t = p[2]
            if t == "MC" and v: final.setdefault(q, []).append(v)
            elif t == "TF" and v: final.setdefault(q, []).append(p[3])
            elif t == "SA":
                idx = int(p[3]); val = str(v).strip()
                if q not in sa_groups: sa_groups[q] = [""]*4
                if 0 <= idx < 4: sa_groups[q][idx] = val
    for q, chars in sa_groups.items():
        s = "".join(chars)
        if s: final[q] = [s]
    if final:
        new_text = inject_answer_keys(st.session_state.editor_content, final)
        push_history(new_text)
        show_popup("💾 Đã lưu đáp án vào Editor!")

def cb_load_sample():
    if st.session_state.editor_content and st.session_state.editor_content.strip():
        show_popup("⚠️ Editor đang có dữ liệu! Hãy xóa trước.")
        return
    sample_text = r"""PHẦN I. (3.0 điểm) Trắc nghiệm nhiều phương án. Thí sinh làm từ câu 1 đến câu 12. Mỗi câu thí sinh chỉ chọn một phương án.
Câu 1: Chuẩn bị cho cuộc thi nhảy hiện đại. Bạn Ri tập nhảy trong 18 ngày và bạn ấy thống kê lại ở bảng sau:

\begin{tabular}{|l|l|l|l|l|l|}
\hline Thời gian (phút) & {$[20 ; 25)$} & {$[25 ; 30)$} & {$[30 ; 35)$} & {$[35 ; 40)$} & {$[40 ; 45)$} \\
\hline Số ngày & 6 & 6 & 4 & 1 & 1 \\
\hline
\end{tabular}

Phương sai của mẫu số liệu ghép nhóm có giá trị gần nhất với giá trị nào dưới đây?
A. 33,25 .
B. 31,25 .
C. 25,21 .
D. 32,25 .


PHẦN II. (4.0 điểm) Thí sinh trả lời câu 1 đến câu 4. Trong mỗi ý a), b), c), d) ở mỗi câu, thí sinh chọn đúng hoặc sai.
Câu 1: Một trang sách có dạng hình chữ nhật $A B C D$ với diện tích là $384\left(\mathrm{~cm}^{2}\right)$. Sau khi để lề trên và lề dưới đều là 3 cm ; để lề trái và lề phải đều là 2 cm . Phần còn lại của trang sách là hình chữ nhật $E F I H$ được in chữ. (hình vẽ bên dưới).
![](https://cdn.mathpix.com/cropped/7d86bf36-49b4-424e-bb41-d04dac05b5dc-03.jpg?height=369&width=607&top_left_y=392&top_left_x=817)

Gọi $A B=x(\mathrm{~cm})$ và $A D=y(\mathrm{~cm})$ lần lượt là chiều rộng và chiều dài của trang sách $(x, y>0)$
a) Biểu thức liên hệ giữa $x$ và $y$ là $x y=384$.
b) Chiều rộng $E F$, chiều dài $I H$ của trang sách được in chữ lần lượt là $x-2$ và $y-3$.
c) Phần in chữ trên trang sách có diện tích lớn nhất bằng $216\left(\mathrm{~cm}^{2}\right)$.
d) Diện tích $S$ của hình chữ nhật $E F I H$ của phần in chữ được tính bởi công thức $S=(x-2)(y-3)$.


PHẦN III. (3.0 điểm) Thí sinh trả lời từ câu 1 đến câu 4.
Câu 1: Khối lượng $q(\mathrm{~kg})$ của một mặt hàng mà cửa tiệm bán được trong một ngày phụ thuộc vào giá bán $p$ (nghìn đồng/kg) theo công thức $p=15-\frac{1}{2} q$. Doanh thu từ việc bán mặt hàng trên của cửa tiệm được tính theo công thức $R=p . q$. Tìm giá bán mỗi kilôgam sản phẩm để đạt được doanh thu cao nhất?
"""
    push_history(sample_text)
    show_popup("✅ Đã nạp đề mẫu thành công!")