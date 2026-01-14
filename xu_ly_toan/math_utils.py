import re

# ============================================================
# PHẦN 1: CÁC HÀM CƠ BẢN
# ============================================================

def remove_exam_headers(text):
    if not text: return ""
    text = re.sub(r'(?ism)^PHẦN\s+[IVX]+.*?(?=^\s*Câu)', '', text)
    patterns = [r'^PHẦN\s+[IVX]+\..*$', r'^Thí\s+sinh\s+trả\s+lời.*$', r'^Mỗi\s+câu\s+hỏi.*$', r'^Trong\s+mỗi\s+ý.*$', r'^Câu\s+trắc\s+nghiệm.*$', r'^Đề\s+thi\s+gồm.*$', r'^Thời\s+gian\s+làm\s+bài.*$', r'^Họ\s+và\s+tên.*$', r'^Mã\s+đề.*$', r'^Lớp:.*$']
    combined_pattern = r'(?im)^(' + '|'.join(patterns).replace('.', r'\.') + r').*$'
    text = re.sub(combined_pattern, '', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def clean_mathpix_urls(text):
    if not text: return ""
    text = re.sub(r"!\[\]\(https?://cdn\.mathpix\.com\S+\)", r"%HÌNH VẼ", text)
    return re.sub(r"https?://cdn\.mathpix\.com\S+", r"%HÌNH VẼ", text)

def fix_decimal_comma_only(text):
    if not text: return ""
    return re.sub(r'(?<![\d])(\d+)[.,](\d+)(?![\d])', r'\1{,}\2', text)

def clean_whitespace(text):
    if not text: return ""

    # 0. CHUẨN HÓA KHOẢNG TRẮNG ẨN (Quan trọng khi copy từ PDF/Web)
    # Thay thế non-breaking space (\xa0) bằng space thường
    text = text.replace(u'\xa0', u' ')

    # 1. DỌN DẸP CƠ BẢN
    text = re.sub(r'[ \t]+', ' ', text)
    # Fix lỗi kinh điển
    text = re.sub(r'\bO\s+x\s+y\s+z\b', 'Oxyz', text)
    text = re.sub(r'\bO\s+x\s+y\b', 'Oxy', text)

    # 2. XỬ LÝ KHOẢNG TRẮNG TRƯỚC DẤU CÂU (Fix lỗi " ;" và " .")
    # Áp dụng cho: , ; : . ! ? ) ] }
    text = re.sub(r'\s+([,;:\.\!\?\)\]\}])', r'\1', text)
    
    # 3. XỬ LÝ KHOẢNG TRẮNG SAU DẤU MỞ (Fix lỗi "( 3")
    text = re.sub(r'([\(\[\{])\s+', r'\1', text)

    # 4. [MỚI] GOM SỐ TRONG MATH VÀ ĐƠN VỊ NGOÀI TEXT
    # Khắc phục lỗi: "$3$ cm" -> "$3$cm" (để sau này Smart Clean xử lý tiếp)
    # Hoặc "$3$ cm ;" -> "$3$cm;"
    units = r"(?:cm|m|km|dm|mm|kg|g|s|Hz|N|A|V|W|J|mol|l|ml)"
    # Tìm: ($số$) + khoảng trắng + (đơn vị)
    text = re.sub(r'(\$[\d,.]+\$)\s+(' + units + r'\b)', r'\1\2', text)

    # 5. XỬ LÝ BÊN TRONG MATH MODE ($...$)
    def fix_math_internal(match):
        content = match.group(1)
        
        # 5.1 Xóa dấu ~ (non-breaking space) thừa trong \mathrm{~cm}
        content = content.replace(r'\mathrm{~', r'\mathrm{')
        content = content.replace(r'~', ' ') # Đổi ~ thành cách thường để regex dưới xử lý
        
        # 5.2 Gom biến rời: "x y" -> "xy" (trừ lệnh latex)
        content = re.sub(r'(?<!\\)\b([a-zA-Z])\s+([a-zA-Z])\b', r'\1\2', content)
        
        # 5.3 Gom số và biến: "2 x" -> "2x"
        content = re.sub(r'(\d)\s+([a-zA-Z])\b', r'\1\2', content)
        
        # 5.4 Dọn dẹp khoảng trắng thừa đầu cuối
        content = content.strip()
        
        return f"${content}$"

    text = re.sub(r'\$([^\$\n]+)\$', fix_math_internal, text)

    # 6. DỌN DÒNG TRỐNG (Giữ tối đa 1 dòng trống)
    lines = [line.strip() for line in text.split('\n')]
    cleaned_lines = []
    for line in lines:
        if line: cleaned_lines.append(line)
        elif cleaned_lines and cleaned_lines[-1] != "": cleaned_lines.append("")
            
    return '\n'.join(cleaned_lines).strip()

def fix_spacing_semantics(text):
    if not text: return ""
    text = re.sub(r'(?<=[^\s\(\[\{])\$', ' $', text)
    text = re.sub(r'\$(?=[^\s\)\]\}\.,;:])', '$ ', text)
    def math_processor(match):
        content = match.group(1).strip()
        for _ in range(4): 
            new_content = re.sub(r'([A-Z](?:\')?)\s+(?=[A-Z])', r'\1', content)
            if new_content == content: break
            content = new_content
        content = re.sub(r'([A-Z]{2,}(?:\')?)\s*\\cdot\s*([A-Z]{2,})', r'\1.\2', content)
        return f"${content}$"
    text = re.sub(r'\$([^\$\n]+?)\$', math_processor, text)
    text = re.sub(r'\\overrightarrow\{\s*([A-Za-z])\s+([A-Za-z])\s*\}', r'\\overrightarrow{\1\2}', text)
    text = re.sub(r'\\overrightarrow\s+\{\s*([A-Za-z0-9]+)\s*\}', r'\\overrightarrow{\1}', text)
    def compact_coords(match): 
        return match.group(0).replace(" ", "").replace("\n", "")
    coord_pattern = r'[\(\[\{]\s*[-\w\.,]+\s*;\s*[-\w\.,]+(?:\s*;\s*[-\w\.,]+)?\s*[\)\]\}]'
    text = re.sub(coord_pattern, compact_coords, text)
    text = re.sub(r'(^|[\s])([A-D])[\.\)](?=[^\s])', r'\1\2. ', text)
    return text

def fix_latex_syntax_and_symbols(text):
    if not text: return ""

    # 1. [MỚI] Sửa ký hiệu song song: // hoặc /| -> \parallel
    # Regex xử lý:
    # (?<!:) : Không phải là url (http://)
    # \s* : Khoảng trắng thừa
    # /      : Dấu gạch chéo đầu
    # \s* : Khoảng trắng giữa (nếu có)
    # (?:/|\|) : Dấu gạch chéo thứ 2 HOẶC dấu gạch đứng (|)
    # Ví dụ: M N / / (S A B) -> M N \parallel (S A B)
    text = re.sub(r'(?<!:)\s*/\s*(?:/|\|)\s*', r' \\parallel ', text)

    # 2. Các xử lý cú pháp cũ (Giữ nguyên)
    text = re.sub(r'\^\{\\prime\}', "'", text)
    text = re.sub(r'\^\\prime', "'", text)
    text = re.sub(r'\\backslash', r'\\setminus', text)
    
    # Chuẩn hóa xác suất P( -> \mathrm{P}(
    text = re.sub(r'(?<!\\mathrm\{)\bP\s*\(', r'\\mathrm{P}(', text)
    
    # Chuẩn hóa tổ hợp/chỉnh hợp A_n^k, P_n
    pattern_AC = r'(?<!\\mathrm\{)\b([AC])\s*(_\s*(?:\{[^{}]*\}|[\w]))\s*(\^\s*(?:\{[^{}]*\}|[\w]))'
    text = re.sub(pattern_AC, r'\\mathrm{\1}\2\3', text)
    
    pattern_P = r'(?<!\\mathrm\{)\bP\s*(_\s*(?:\{[^{}]*\}|[\w]))'
    text = re.sub(pattern_P, r'\\mathrm{P}\1', text)
    
    return text

def center_tabular_elements(text):
    if not text: return ""
    pattern = r'(?:\\begin\{center\}\s*)*(?P<core>\\begin\{tabular\}.*?\\end\{tabular\})(?:\s*\\end\{center\})*'
    def replacer(match):
        return f"\\begin{{center}}\n{match.group('core')}\n\\end{{center}}"
    return re.sub(pattern, replacer, text, flags=re.DOTALL)

# [File: xu_ly_toan/math_utils.py]

# [File: xu_ly_toan/math_utils.py]

# [File: xu_ly_toan/math_utils.py]

# 1. CẬP NHẬT HÀM ĐÓNG GÓI CHÍNH (Thêm hỗ trợ template bảng đáp án)
# [File: xu_ly_toan/math_utils.py]

# 1. HÀM ĐÓNG GÓI CHÍNH (CẬP NHẬT)
def wrap_exam_structure(text, settings=None):
    if not text: return ""
    
    # Cấu hình mặc định (Thêm các key path_*)
    defaults = {
        "cmd_tn": "\\cautn", "cmd_ds": "\\cauds", "cmd_sa": "\\caukq", "cmd_tl": "\\cautl",
        "use_ans_file": True, "use_table_ans": True,
        "table_ans_template": "\\begin{indapan}\n    {ans/ans\\currfilebase}\n\\end{indapan}",
        "custom_header": "",
        # [MỚI] Tùy chỉnh đường dẫn file đáp án
        "path_tn": "ans/ans\\currfilebase-Phan-I",
        "path_ds": "ans/ans\\currfilebase-Phan-II",
        "path_sa": "ans/ans\\currfilebase-Phan-III",
        "path_main": "ans/ansb\\currfilebase"
    }
    cfg = {**defaults, **(settings or {})}

    pattern = r'(\\begin\{(?:ex|bt|ex_test)\}.*?\\end\{(?:ex|bt|ex_test)\})'
    blocks = re.findall(pattern, text, flags=re.DOTALL)
    if not blocks: return text
    
    tn_blocks, tf_blocks, sa_blocks, tl_blocks = [], [], [], []
    for b in blocks:
        if r'\choiceTF' in b: tf_blocks.append(b)
        elif r'\shortans' in b: sa_blocks.append(b)
        elif r'\choice' in b: tn_blocks.append(b)
        else: tl_blocks.append(b)

    # Helper function nhận tham số path linh hoạt
    def make_section(content_list, file_path, comment, command):
        if not content_list: return ""
        content = "\n\n".join(content_list)
        if cfg["use_ans_file"]:
            return (f"{command}\n"
                    f"\\Opensolutionfile{{ans}}[{file_path}]\n"
                    f"%{comment}\n"
                    f"{content}\n"
                    f"\\Closesolutionfile{{ans}}")
        else:
            return (f"{command}\n%{comment}\n{content}")

    body_parts = []
    # Truyền đường dẫn từ config vào
    if tn_blocks: body_parts.append(make_section(tn_blocks, cfg["path_tn"], "PHẦN TRẮC NGHIỆM", cfg["cmd_tn"]))
    if tf_blocks: body_parts.append(make_section(tf_blocks, cfg["path_ds"], "PHẦN ĐÚNG SAI", cfg["cmd_ds"]))
    if sa_blocks: body_parts.append(make_section(sa_blocks, cfg["path_sa"], "PHẦN TRẢ LỜI NGẮN", cfg["cmd_sa"]))
    
    if tl_blocks:
        tl_content = "\n\n".join(tl_blocks)
        body_parts.append(f"{cfg['cmd_tl']}\n%PHẦN TỰ LUẬN\n{tl_content}")
        
    full_content = "\n\n".join(body_parts)
    
    header_code = f"{cfg['custom_header']}\n" if cfg['custom_header'] else ""
    
    # Xử lý file ansbook tổng
    start_ansbook = f"\\Opensolutionfile{{ansbook}}[{cfg['path_main']}]\n" if cfg["use_ans_file"] else ""
    close_ansbook = "\n\\Closesolutionfile{ansbook}" if cfg["use_ans_file"] else ""
    
    print_ans_table = ""
    if cfg["use_ans_file"] and cfg["use_table_ans"]:
        print_ans_table = "\n" + cfg["table_ans_template"]

    return f"{header_code}{start_ansbook}{full_content}{close_ansbook}{print_ans_table}"

# [File: xu_ly_toan/math_utils.py]

# [GIỮ NGUYÊN HÀM wrap_exam_structure CŨ]

# [THAY THẾ HÀM PREVIEW NÀY]
def preview_exam_structure(text, settings=None):
    # 1. Config Mặc định
    defaults = {
        "cmd_tn": "\\cautn", "cmd_ds": "\\cauds", "cmd_sa": "\\caukq", "cmd_tl": "\\cautl",
        "use_ans_file": True, "use_table_ans": True,
        "table_ans_template": "\\begin{indapan}\n    {ans/ans\\currfilebase}\n\\end{indapan}",
        "custom_header": "",
        "path_tn": "ans/ans\\currfilebase-Phan-I",
        "path_ds": "ans/ans\\currfilebase-Phan-II",
        "path_sa": "ans/ans\\currfilebase-Phan-III",
        "path_main": "ans/ansb\\currfilebase"
    }
    cfg = {**defaults, **(settings or {})}

    # 2. Phân tích nội dung (Hoặc tạo Demo)
    if not text or not text.strip():
        # [CHẾ ĐỘ DEMO] Nếu không có input, giả lập số lượng câu hỏi
        tn_count, tf_count, sa_count, tl_count = 12, 4, 6, 2
        is_demo = True
    else:
        # [CHẾ ĐỘ THỰC] Đếm từ text người dùng
        pattern = r'(\\begin\{(?:ex|bt|ex_test)\}.*?\\end\{(?:ex|bt|ex_test)\})'
        blocks = re.findall(pattern, text, flags=re.DOTALL)
        
        tn_count = sum(1 for b in blocks if r'\choice' in b and r'\choiceTF' not in b)
        tf_count = sum(1 for b in blocks if r'\choiceTF' in b)
        sa_count = sum(1 for b in blocks if r'\shortans' in b)
        tl_count = len(blocks) - tn_count - tf_count - sa_count
        is_demo = False

    # 3. Hàm tạo Section giả lập
    def make_dummy_section(count, file_path, comment, command):
        if count == 0: return ""
        # Nội dung placeholder
        if is_demo:
            placeholder = f"\n    % [...DEMO: {count} CÂU HỎI SẼ ĐƯỢC CHÈN VÀO ĐÂY...]\n"
        else:
            placeholder = f"\n    % [...NỘI DUNG {count} CÂU HỎI THỰC TẾ ĐƯỢC ẨN ĐỂ PREVIEW GỌN...]\n"
            
        if cfg["use_ans_file"]:
            return (f"{command}\n"
                    f"\\Opensolutionfile{{ans}}[{file_path}]\n"
                    f"%{comment}\n"
                    f"{placeholder}"
                    f"\\Closesolutionfile{{ans}}")
        else:
            return f"{command}\n%{comment}\n{placeholder}"

    body_parts = []
    # Luôn hiển thị các phần nếu count > 0 (Demo luôn > 0)
    if tn_count > 0: body_parts.append(make_dummy_section(tn_count, cfg["path_tn"], "PHẦN TRẮC NGHIỆM", cfg["cmd_tn"]))
    if tf_count > 0: body_parts.append(make_dummy_section(tf_count, cfg["path_ds"], "PHẦN ĐÚNG SAI", cfg["cmd_ds"]))
    if sa_count > 0: body_parts.append(make_dummy_section(sa_count, cfg["path_sa"], "PHẦN TRẢ LỜI NGẮN", cfg["cmd_sa"]))
    
    if tl_count > 0:
        label = "DEMO: " if is_demo else ""
        body_parts.append(f"{cfg['cmd_tl']}\n%PHẦN TỰ LUẬN\n\n    % [...{label}{tl_count} CÂU TỰ LUẬN...]\n")
        
    full_content = "\n\n".join(body_parts)
    
    header_code = f"{cfg['custom_header']}\n" if cfg['custom_header'] else "% [HEADER TÙY CHỈNH...]\n"
    start_ansbook = f"\\Opensolutionfile{{ansbook}}[{cfg['path_main']}]\n" if cfg["use_ans_file"] else ""
    close_ansbook = "\n\\Closesolutionfile{ansbook}" if cfg["use_ans_file"] else ""
    
    print_ans_table = ""
    if cfg["use_ans_file"] and cfg["use_table_ans"]:
        print_ans_table = "\n" + cfg["table_ans_template"]

    return f"{header_code}{start_ansbook}{full_content}{close_ansbook}{print_ans_table}"
def basic_standardize(text):
    if not text: return ""
    text = clean_mathpix_urls(text)
    text = clean_whitespace(text)
    text = fix_decimal_comma_only(text)
    text = fix_spacing_semantics(text)
    text = fix_latex_syntax_and_symbols(text)
    text = center_tabular_elements(text)
    return text.strip()

# ============================================================
# PHẦN 2: LÀM ĐẸP TOÁN HỌC
# ============================================================

def format_integrals(text):
    if not text: return ""
    text = re.sub(r'(?<!\\displaystyle)\\int\b', r'\\displaystyle\\int', text)
    text = re.sub(r'\\displaystyle\\int\s*_', r'\\displaystyle\\int\\limits_', text)
    text = re.sub(r'(?<!\\mathrm\{\\,)d([xyztuv])(?=[\$\)\}\s\.\,])', r'\\mathrm{\\,d}\1', text)
    return text

def format_vectors(text):
    if not text: return ""
    text = re.sub(r'\\vec\s*\{', r'\\overrightarrow{', text)
    text = re.sub(r'\\vec\s+([a-zA-Z])', r'\\overrightarrow{\1}', text) 
    text = re.sub(r'\\overrightarrow\s*\{', r'\\overrightarrow{', text)
    text = re.sub(r'\\overrightarrow\{(\w+)_(\w+)\}', r'\\overrightarrow{\1}_{\2}', text)
    return text

def format_colon_geometry(text):
    if not text: return ""
    text = re.sub(r'(\([A-Za-z0-9\Delta]+\))\s*:', r'\1 \\colon', text)
    return text

def change_frac_to_dfrac(text):
    if not text: return ""
    return re.sub(r'(?<!d)frac', 'dfrac', text)

def remove_superfluous_delimiters(text):
    if not text: return ""
    tall_cmds = ['\\frac', '\\dfrac', '\\sum', '\\prod', '\\int', '\\lim', '\\bigcup', '\\bigcap', '\\bigvee', '\\bigwedge', '\\coprod', '\\oint', '\\binom', '\\tbinom', '\\dbinom', '\\begin', '\\cases', '\\matrix', '\\over', '\\substack']
    pattern = r'\\left(\(|\[)((?:(?!\\left|\\right).)*?)\\right(\)|\])'
    for _ in range(3):
        def replacer(match):
            content = match.group(2)
            if any(cmd in content for cmd in tall_cmds): return match.group(0)
            return f"{match.group(1)}{content}{match.group(3)}"
        new_text = re.sub(pattern, replacer, text, flags=re.DOTALL)
        if new_text == text: break
        text = new_text
    return text

def replace_dot_multiplication(text):
    if not text: return ""
    return re.sub(r'(?<=[\w}\)])\s*\.\s*(?=[a-z0-9{\(])', r' \\cdot ', text)

def smart_cleanup(text):
    if not text: return ""

    # Danh sách đơn vị đo lường phổ biến
    # Lưu ý: kg phải đứng trước g, mm đứng trước m để regex khớp dài nhất trước
    units = r"km|m|cm|dm|mm|kg|g|s|Hz|N|A|V|W|J|mol|\\Omega|l|ml"
    
    # Prefix: bắt các lệnh rác như space, ~, \mathrm{...}
    prefix = r"(?:~|\s+|\\mathrm\{[~\s]*|\\text\{[~\s]*|\\mathmrm\{[~\s]*)?"

    # =========================================================
    # 1. XỬ LÝ ĐƠN VỊ CÓ NGOẶC: (cm), \left(cm\right)
    # Điều kiện: BẮT BUỘC PHẢI CÓ DẤU NGOẶC
    # Hỗ trợ: $x(cm)$, $216(cm^2)$
    # =========================================================
    
    # [FIX] Đã xóa dấu ? ở cuối cụm ngoặc để bắt buộc phải có ngoặc
    paren_pattern = (
        r'(?<=[=\{\s\(\[\$])([a-zA-Z0-9.,]+)'   # 1. Giá trị (x, 216...)
        + r'\s*((?:\\left)?\()'                 # 2. Ngoặc mở (BẮT BUỘC)
        + r'\s*' + prefix                       # Prefix
        + r'(' + units + r')'                   # 3. Đơn vị
        + r'\}?'                                #    Đóng }
        + r'(\^\{?[\d]+\}?)?'                   # 4. Số mũ
        + r'\s*((?:\\right)?\))'                # 5. Ngoặc đóng (BẮT BUỘC)
        + r'\s*\$'                              # 6. Kết thúc $
    )
    
    def replace_paren_unit(match):
        val = match.group(1)
        # Chuẩn hóa về ngoặc đơn thường ( )
        unit = match.group(3)
        exp = match.group(4)
        
        # Bọc mũ vào $...$
        if exp: unit_part = f"{unit}${exp}$"
        else: unit_part = unit
            
        return f"{val}$\\,({unit_part})"

    text = re.sub(paren_pattern, replace_paren_unit, text)


    # =========================================================
    # 2. XỬ LÝ ĐƠN VỊ SỐ (KHÔNG NGOẶC): 50kg, 500 m^2
    # Điều kiện: Giá trị BẮT BUỘC LÀ SỐ (\d)
    # =========================================================
    
    numeric_pattern = (
        r'(\d+(?:[.,]\d+)?)'           # 1. Số (BẮT BUỘC LÀ SỐ)
        + r'\s*' + prefix              # Prefix
        + r'(' + units + r')'          # 2. Đơn vị
        + r'(?:\})?'                   #    Đóng } (của prefix)
        + r'(\^\{?-?[\d]+\}?)?'        # 3. Số mũ
        + r'\s*\$'                     # 4. Kết thúc $
    )
    
    def replace_numeric_unit(match):
        val = match.group(1)
        unit = match.group(2)
        exp = match.group(3)
        
        if exp:
            # Input: $500 m^2$ -> Output: $500$\,m$^2$
            return f"{val}$\\,{unit}${exp}$"
        else:
            # Input: $50kg$ -> Output: $50$\,kg
            return f"{val}$\\,{unit}"
    
    text = re.sub(numeric_pattern, replace_numeric_unit, text)


    # =========================================================
    # 3. CÁC XỬ LÝ KHÁC (GIỮ NGUYÊN)
    # =========================================================
    
    text = re.sub(r'([A-Z])\s*\\cdot\s*([A-Z]{2,})', r'\1.\2', text)
    text = re.sub(r'\(\$([^\$\n]+)\$\)', r'$(\1)$', text)
    
    def process_comma(match):
        content = match.group(1).strip()
        if re.match(r'^[\d,]+$', content): return match.group(0)
        new_content = ""
        depth = 0; last_idx = 0
        for idx, char in enumerate(content):
            if char in '([{': depth += 1
            elif char in ')]}': depth -= 1
            elif char == ',' and depth == 0:
                if idx + 1 < len(content) and content[idx+1].isdigit(): continue
                segment = content[last_idx:idx]
                new_content += segment + "$, $"
                last_idx = idx + 1
        new_content += content[last_idx:]
        return f"${new_content}$"
        
    text = re.sub(r'\$([^\$\n]+)\$', process_comma, text)
    
    return text

def convert_systems(text):
    if not text: return ""
    def format_inner(c):
        lines = re.split(r'\\\\', c)
        return r' \\ '.join([('&' + l.strip() if l.strip() and not l.strip().startswith('&') else l.strip()) for l in lines if l.strip()])
    text = re.sub(r'\\left\[\s*\\begin\{array\}\{.*?\}\s*(.*?)\s*\\end\{array\}\s*\\right(\.|\\)?', lambda m: f"\\hoac{{{format_inner(m.group(1))}}}", text, flags=re.DOTALL)
    text = re.sub(r'\\left\\{\s*\\begin\{array\}\{.*?\}\s*(.*?)\s*\\end\{array\}\s*\\right(\.|\\)?', lambda m: f"\\heva{{{format_inner(m.group(1))}}}", text, flags=re.DOTALL)
    text = re.sub(r'\\left\[\s*\\begin\{aligned\}(.*?)\\end\{aligned\}\s*\\right\.', lambda m: f"\\hoac{{{format_inner(m.group(1))}}}", text, flags=re.DOTALL)
    text = re.sub(r'\\begin\{cases\}(.*?)\\end\{cases\}', lambda m: f"\\heva{{{format_inner(m.group(1))}}}", text, flags=re.DOTALL)
    return text

# [File: xu_ly_toan/math_utils.py]

def add_question_comments(text):
    if not text: return ""
    
    # 1. Xóa sạch các comment %Câu cũ (nếu có) để tránh trùng lặp
    text = re.sub(r'(?m)^%Câu\s*\d+.*$\n?', '', text)
    
    parts = re.split(r'(\\begin\{ex\}.*?\\end\{ex\})', text, flags=re.DOTALL)
    processed = []
    counter = 1
    
    # Regex tìm label cứng đầu câu (Ví dụ: "Câu 1.", "Bài 5:", "Câu $1$:")
    # Tìm sau \begin{ex}[...] là các từ khóa Câu/Bài
    header_pattern = r'(\\begin\{ex\}(?:\[.*?\])?\s*)(?:Câu|Bài)\s*[\d\$]+[:.]?\s*'
    
    for part in parts:
        if part.strip().startswith(r'\begin{ex}'):
            # 2. XÓA LABEL CŨ TRONG NỘI DUNG
            # Input: \begin{ex} Câu 1. Giải pt...
            # Output: \begin{ex} Giải pt...
            part = re.sub(header_pattern, r'\1', part, count=1)
            
            # 3. NHẬN DIỆN LOẠI CÂU (Để ghi chú cho rõ)
            q_type = "TN" # Mặc định Trắc nghiệm
            if r'\choiceTF' in part: q_type = "DS" # Đúng Sai
            elif r'\shortans' in part: q_type = "TLN" # Trả lời ngắn
            
            # 4. THÊM COMMENT ĐÁNH SỐ MỚI
            # %Câu 1 (TN)
            processed.append(f"%Câu {counter}\n{part}")
            counter += 1
        else:
            processed.append(part)
            
    return "".join(processed)

# [QUAN TRỌNG]
# Đảm bảo hàm process_formatting gọi add_question_comments ở gần cuối
# (Code của bạn đã có sẵn đoạn này rồi, chỉ cần thay nội dung hàm trên là xong)

def add_math_delimiters_and_fix_numbers(text):
    if not text: return ""
    protected_envs = ["equation", "align", "gather", "multline", "flalign", "split", "alignat", "tikzpicture", "array", "cases", "matrix", "pmatrix", "bmatrix", "vmatrix", "Vmatrix"]
    env_regex = "|".join(protected_envs)
    pattern = r'(\$.*?\$|\\\(.*?\\\)|\\\[.*?\\\]|\\begin\{(?P<math_env>' + env_regex + r')\*?\}.*?\\end\{(?P=math_env)\*?\})'
    processed_parts = []
    last_end = 0
    for match in re.finditer(pattern, text, flags=re.DOTALL):
        text_part = text[last_end:match.start()]
        if text_part:
            text_part = re.sub(r'(?<![\d\w\$\\])(\d+)(?:[.,]|\{,\})(\d+)(?![\d\w\$\\])', r'$\1{,}\2$', text_part)
            text_part = re.sub(r'(?<![\d\w\$\\\{,])\b(\d+)\b(?![\d\w\$\}\{,])', r'$\1$', text_part)
            processed_parts.append(text_part)
        processed_parts.append(match.group(0))
        last_end = match.end()
    text_part = text[last_end:]
    if text_part:
        text_part = re.sub(r'(?<![\d\w\$\\])(\d+)(?:[.,]|\{,\})(\d+)(?![\d\w\$\\])', r'$\1{,}\2$', text_part)
        text_part = re.sub(r'(?<![\d\w\$\\\{,])\b(\d+)\b(?![\d\w\$\}\{,])', r'$\1$', text_part)
        processed_parts.append(text_part)
    return "".join(processed_parts)

def add_math_delimiters(text):
    return add_math_delimiters_and_fix_numbers(text)

def process_formatting(text, 
                       use_clean_url=False, use_clean_space=False, use_fix_decimal=False, 
                       use_add_dollar=False, use_add_comment=False, 
                       use_frac_dfrac=False, use_convert_system=False,
                       use_remove_delimiter=False, use_dot_multiplication=False,
                       use_smart_format=False, 
                       use_format_integral=False, 
                       use_format_vector=False,   
                       use_format_colon=False,
                       use_main_struct=False, # [MỚI]
                       image_layout_mode="ignore"):
    if not text: return ""
    if use_smart_format: text = smart_cleanup(text)
    if use_clean_url:   text = clean_mathpix_urls(text)
    
    if use_clean_space: 
        text = clean_whitespace(text)
        text = fix_decimal_comma_only(text)
        text = fix_spacing_semantics(text)
        text = fix_latex_syntax_and_symbols(text)
    
    if use_add_dollar:
        text = add_math_delimiters_and_fix_numbers(text)
    elif use_fix_decimal:
        text = fix_decimal_comma_only(text)
    
    if use_remove_delimiter: text = remove_superfluous_delimiters(text)
    if use_dot_multiplication: text = replace_dot_multiplication(text)
    if use_format_integral: text = format_integrals(text)
    if use_format_vector: text = format_vectors(text)
    if use_format_colon: text = format_colon_geometry(text)
    if image_layout_mode != "ignore": text = manage_question_layout(text, image_layout_mode)
    if use_frac_dfrac:  text = change_frac_to_dfrac(text)
    if use_convert_system: text = convert_systems(text)
    if use_add_comment: text = add_question_comments(text)
    
    text = center_tabular_elements(text)
    # [MỚI] Chạy cấu trúc Main ở bước cuối cùng
    if use_main_struct:
        text = wrap_exam_structure(text)
        
    return text

# === LAYOUT HELPERS (GIỮ NGUYÊN) ===
def extract_bracket_content(text, start_idx):
    depth = 0; found_start = False; real_start = -1
    for i in range(start_idx, len(text)):
        if not found_start:
            if text[i].isspace(): continue
            if text[i] == '{': found_start = True; depth = 1; real_start = i
            else: return "", start_idx
        else:
            if text[i] == '{': depth += 1
            elif text[i] == '}':
                depth -= 1
                if depth == 0: return text[real_start+1:i], i+1
    return "", start_idx

def manage_question_layout(text, mode="default"):
    if mode not in ["default", "immini_thm", "immini", "immini_left"]: return text
    def process_ex_block(match):
        full_ex = match.group(0); content = match.group(1)
        loigiai = ""; lg_idx = content.rfind(r'\loigiai')
        if lg_idx != -1: loigiai = content[lg_idx:]; main_body = content[:lg_idx]
        else: main_body = content
        shortans = ""; sa_match = re.search(r'(\\shortans(?:\[.*?\])?\{.*?\})', main_body, flags=re.DOTALL)
        if sa_match: shortans = sa_match.group(1); main_body = main_body.replace(shortans, "")
        image_code = ""; text_content = main_body.strip()
        center_match = re.search(r'\\begin\{center\}(.*?)\\end\{center\}', main_body, flags=re.DOTALL)
        if center_match:
            image_code = center_match.group(1).strip()
            text_content = main_body.replace(center_match.group(0), "").strip()
        else:
            im_match = re.search(r'\\(imminiL|immini)(?:\[.*?\])?', main_body)
            if im_match:
                pre_text = main_body[:im_match.start()].strip()
                start_idx = im_match.end()
                temp_cursor = start_idx
                while temp_cursor < len(main_body) and main_body[temp_cursor].isspace(): temp_cursor += 1
                if temp_cursor < len(main_body) and main_body[temp_cursor] == '[':
                    close_opt = main_body.find(']', temp_cursor)
                    if close_opt != -1: start_idx = close_opt + 1
                text_extracted, end_1 = extract_bracket_content(main_body, start_idx)
                img_extracted, end_2 = extract_bracket_content(main_body, end_1)
                post_text = main_body[end_2:].strip()
                if text_extracted or img_extracted:
                    text_content = f"{pre_text}\n{text_extracted}\n{post_text}".strip()
                    image_code = img_extracted.strip()
        if not image_code: return full_ex
        new_body = ""
        if mode == "default": new_body = f"{text_content}\n\\begin{{center}}\n{image_code}\n\\end{{center}}"
        elif mode.startswith("immini"):
            cmd = "\\imminiL" if mode == "immini_left" else "\\immini"
            opt = "[thm]" if mode == "immini_thm" else ""
            new_body = f"{cmd}{opt}\n{{\n{text_content}\n}}\n{{\n{image_code}\n}}"
        return f"\\begin{{ex}}\n{new_body}\n{shortans}\n{loigiai}\n\\end{{ex}}"
    return re.sub(r'\\begin\{ex\}(.*?)\\end\{ex\}', process_ex_block, text, flags=re.DOTALL)

def get_question_types(text):
    if not text: return {}
    parts = re.split(r'(\\begin\{ex\}.*?\\end\{ex\})', text, flags=re.DOTALL)
    types = {}
    count = 0
    for part in parts:
        if part.strip().startswith(r'\begin{ex}'):
            count += 1
            if r'\choiceTF' in part: types[count] = 'TF'
            elif r'\shortans' in part: types[count] = 'SA'
            else: types[count] = 'MC'
    return types

def get_existing_answers(text):
    if not text: return {}
    parts = re.split(r'(\\begin\{ex\}.*?\\end\{ex\})', text, flags=re.DOTALL)
    existing_data = {}
    count = 0
    char_map = ['A', 'B', 'C', 'D', 'E', 'F']
    for part in parts:
        if part.strip().startswith(r'\begin{ex}'):
            count += 1
            found_answers = []
            if r'\shortans' in part:
                sa_match = re.search(r'\\shortans(?:\[.*?\])?\{(.*?)\}', part)
                if sa_match: found_answers.append(sa_match.group(1).strip())
            else:
                choice_match = re.search(r'\\choice(?:TF)?', part)
                if choice_match:
                    start_search = choice_match.end()
                    open_braces = 0; current_start = -1; option_idx = 0
                    for i in range(start_search, len(part)):
                        char = part[i]
                        if char == '{':
                            if open_braces == 0: current_start = i
                            open_braces += 1
                        elif char == '}':
                            open_braces -= 1
                            if open_braces == 0 and current_start != -1:
                                content = part[current_start+1 : i]
                                if r'\True' in content:
                                    if option_idx < len(char_map): found_answers.append(char_map[option_idx])
                                option_idx += 1; current_start = -1
                                if option_idx >= 6: break
            if found_answers: existing_data[count] = found_answers
    return existing_data

def parse_answer_string(input_str):
    if not input_str: return {}
    input_str = input_str.upper()
    matches = re.findall(r'(\d+)\s*[.:\-)]*\s*([A-D](?:[\s,]*[A-D])*)', input_str)
    ans_dict = {}
    for num, choices in matches:
        clean_choices = [c for c in re.split(r'[^A-D]', choices) if c]
        ans_dict[int(num)] = clean_choices
    return ans_dict

def inject_answer_keys(text, answer_data):
    if not text or not answer_data: return text
    parts = re.split(r'(\\begin\{ex\}.*?\\end\{ex\})', text, flags=re.DOTALL)
    processed_parts = []
    question_count = 0
    for part in parts:
        if part.strip().startswith(r'\begin{ex}'):
            question_count += 1
            if question_count in answer_data:
                ans_val = answer_data[question_count]
                if r'\shortans' in part:
                    sa_text = ans_val[0] if isinstance(ans_val, list) and ans_val else str(ans_val)
                    part = re.sub(r'\\shortans(?:\[.*?\])?\{.*?\}', f"\\\\shortans[]{{{sa_text}}}", part)
                else:
                    correct_options = ans_val
                    choice_match = re.search(r'\\choice(?:TF)?', part)
                    if choice_match:
                        start_search = choice_match.end()
                        open_braces = 0; current_start = -1; found_options = 0; segments = []
                        for i in range(start_search, len(part)):
                            char = part[i]
                            if char == '{':
                                if open_braces == 0: current_start = i
                                open_braces += 1
                            elif char == '}':
                                open_braces -= 1
                                if open_braces == 0 and current_start != -1:
                                    segments.append((current_start, i)); current_start = -1; found_options += 1
                                    if found_options >= 10: break 
                        char_map = ['A', 'B', 'C', 'D', 'E', 'F']
                        part_list = list(part)
                        segments.reverse()
                        for idx, (s, e) in enumerate(segments):
                            real_idx = found_options - 1 - idx
                            if real_idx >= len(char_map): continue
                            option_char = char_map[real_idx]
                            content = part[s+1 : e]
                            content = re.sub(r'\\True\s*', '', content)
                            if option_char in correct_options: content = r'\True ' + content
                            part_list[s+1 : e] = list(content)
                        part = "".join(part_list)
            processed_parts.append(part)
        else:
            processed_parts.append(part)
    return "".join(processed_parts)