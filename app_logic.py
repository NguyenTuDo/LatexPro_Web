import streamlit as st
import re
import pyperclip

# --- IMPORT TỪ FILE CẤU HÌNH DUY NHẤT ---
from cau_hinh.noi_dung_chu import NOI_DUNG_HUONG_DAN, THONG_TIN_UNG_DUNG

from xu_ly_toan.math_utils import (process_formatting, inject_answer_keys, parse_answer_string, 
                                   remove_exam_headers, get_question_types, get_existing_answers,
                                   add_question_comments, manage_question_layout, 
                                   basic_standardize) 
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
    for k, d in zip(LOGIC_KEYS, DEFAULTS):
        if k not in st.session_state: st.session_state[k] = d

def push_history(new_content):
    if new_content == st.session_state.editor_content: return
    st.session_state.history = st.session_state.history[:st.session_state.history_idx + 1]
    st.session_state.history.append(new_content)
    st.session_state.history_idx += 1
    st.session_state.editor_content = new_content

def cb_undo():
    if st.session_state.history_idx > 0:
        st.session_state.history_idx -= 1
        st.session_state.editor_content = st.session_state.history[st.session_state.history_idx]
        st.toast("↩️ Undo")

def cb_redo():
    if st.session_state.history_idx < len(st.session_state.history) - 1:
        st.session_state.history_idx += 1
        st.session_state.editor_content = st.session_state.history[st.session_state.history_idx]
        st.toast("↪️ Redo")

# ... (Phần import và code trên giữ nguyên) ...

def get_theme_css():
    # BẢNG MÀU DARK MODE HIỆN ĐẠI (VS CODE STYLE)
    if st.session_state.is_dark_mode:
        t = {
            "bg_app": "#1e1e1e",           # Nền chính xám chì (không đen thui)
            "text_main": "#d4d4d4",        # Chữ trắng ngà (dịu mắt)
            "bg_sidebar": "#252526",       # Sidebar tối hơn một chút
            "bg_editor": "#1e1e1e",        # Nền editor tiệp màu nền
            "border_editor": "#3e3e42",    # Viền editor xám nhẹ
            "bg_panel": "#252526",         # Nền panel công cụ
            "border_panel": "#3e3e42",     # Viền panel
            "header": "#858585",           # Tiêu đề phụ màu xám
            "text_editor": "#9cdcfe"       # Chữ Editor màu xanh nhạt (dễ đọc code)
        }
    else:
        # BẢNG MÀU LIGHT MODE (GIỮ NGUYÊN)
        t = {
            "bg_app": "#ffffff", "text_main": "#2c3e50", "bg_sidebar": "#f8f9fa",
            "bg_editor": "#ffffff", "border_editor": "#ced4da",
            "bg_panel": "#f8f9fa", "border_panel": "#e9ecef", "header": "#666", 
            "text_editor": "#0033cc"
        }
    
    return f"""
    <style>
        .stApp {{ background-color: {t['bg_app']}; color: {t['text_main']}; }}
        .block-container {{ padding: 1rem 1.5rem !important; }}
        div[data-testid="stVerticalBlock"] {{ gap: 0.5rem !important; }}
        
        /* Tinh chỉnh Editor */
        .stTextArea textarea {{
            font-family: 'Consolas', 'JetBrains Mono', monospace !important;
            font-size: 15px !important; 
            line-height: 1.6 !important;
            font-weight: 500 !important; 
            color: {t['text_editor']} !important;
            background-color: {t['bg_editor']} !important;
            border: 1px solid {t['border_editor']} !important;
            border-radius: 6px !important; 
            padding: 12px !important;
        }}
        .stTextArea textarea:focus {{
            border-color: #007fd4 !important; /* Viền xanh khi gõ */
            box-shadow: 0 0 0 1px #007fd4 !important;
        }}
        
        /* Tinh chỉnh Panel bên phải */
        div[data-testid="column"]:nth-of-type(2) {{
            background-color: {t['bg_panel']}; 
            padding: 15px;
            border-radius: 8px; 
            border: 1px solid {t['border_panel']};
        }}
        
        .tool-header {{
            font-size: 12px; 
            font-weight: 700; 
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: {t['header']}; 
            margin-top: 15px; 
            margin-bottom: 8px;
            border-bottom: 1px solid {t['border_panel']};
            padding-bottom: 4px;
        }}
        
        /* Tinh chỉnh Tabs */
        button[data-baseweb="tab"] {{
            background-color: transparent !important;
        }}
        div[data-baseweb="tab-highlight"] {{
            background-color: #007fd4 !important;
        }}
    </style>
    """
    
# ... (Các phần code dưới giữ nguyên) ...

def calculate_stats(text):
    if not text: return {"MC": 0, "TF": 0, "SA": 0, "MC_True": 0, "Total": 0}
    q_types = get_question_types(text)
    stats = {"MC": 0, "TF": 0, "SA": 0, "MC_True": 0, "Total": len(q_types)}
    for t in q_types.values(): 
        if t in stats: stats[t] += 1
    blocks = re.split(r'\\begin\{ex\}', text)
    for block in blocks:
        if r'\choice' in block and r'\True' in block and r'\choiceTF' not in block:
            stats["MC_True"] += 1
    return stats

# --- CALLBACKS ---

def cb_convert_auto():
    raw = st.session_state.editor_content
    if not raw.strip(): st.toast("⚠️ Trống!"); return
    with st.status("Chuẩn hóa...", expanded=False) as s:
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
        new_text = "\n\n".join(res)
        push_history(new_text)
        s.update(label="✅ Xong!", state="complete")

def cb_run_beauty():
    txt = st.session_state.editor_content
    if not txt.strip(): return
    cfg = {k: st.session_state[k] for k in LOGIC_KEYS}
    params = {
        'use_clean_url': cfg['c_url'], 'use_clean_space': cfg['c_space'],
        'use_fix_decimal': cfg['c_dec'], 'use_add_dollar': cfg['c_dol'],
        'use_frac_dfrac': cfg['c_frac'], 'use_convert_system': cfg['c_sys'],
        'use_remove_delimiter': cfg['c_delim'], 'use_dot_multiplication': cfg['c_dot'],
        'use_smart_format': cfg['c_smart'],
        'use_format_integral': cfg['c_int'],
        'use_format_vector': cfg['c_vec'],
        'use_format_colon': cfg['c_colon'],
        'use_add_comment': False, 'image_layout_mode': 'ignore'
    }
    new_text = process_formatting(txt, **params)
    push_history(new_text)
    st.toast("⚡ Đã làm đẹp!")

def cb_action_image(mode):
    txt = st.session_state.editor_content
    if not txt: return
    map_mode = {"Center": "default", "immini": "immini", "Phải [thm]": "immini_thm", "imminiL": "immini_left"}
    if mode in map_mode:
        new_text = manage_question_layout(txt, map_mode[mode])
        push_history(new_text)
        st.toast(f"🖼️ {mode}")

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
    st.toast(f"🏷️ Thêm {mode}")

def cb_copy_all():
    txt = st.session_state.editor_content
    if txt:
        try: pyperclip.copy(txt); st.toast("📋 Đã Copy!")
        except: st.warning("Dùng Ctrl+A -> Ctrl+C")

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
        st.toast("💾 Đã lưu!")