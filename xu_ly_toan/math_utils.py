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
    text = re.sub(r'\bO\s+x\s+y\s+z\b', 'Oxyz', text)
    text = re.sub(r'\bO\s+x\s+y\b', 'Oxy', text)
    text = re.sub(r'[ \t]+', ' ', text)
    lines = [line.strip() for line in text.split('\n')]
    cleaned_lines = []
    for line in lines:
        if line: cleaned_lines.append(line)
        else:
            if cleaned_lines and cleaned_lines[-1] != "": cleaned_lines.append("")
    text = '\n'.join(cleaned_lines)
    return text.strip()

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
    text = re.sub(r'\^\{\\prime\}', "'", text)
    text = re.sub(r'\^\\prime', "'", text)
    text = re.sub(r'\\backslash', r'\\setminus', text)
    text = re.sub(r'(?<!\\mathrm\{)\bP\s*\(', r'\\mathrm{P}(', text)
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

# [CẬP NHẬT] Hàm bọc cấu trúc Main Ansbook với lệnh riêng cho từng phần
def wrap_exam_structure(text):
    if not text: return ""
    
    # 1. Tách các block câu hỏi
    pattern = r'(\\begin\{ex\}.*?\\end\{ex\})'
    blocks = re.findall(pattern, text, flags=re.DOTALL)
    
    if not blocks: return text # Không tìm thấy câu hỏi thì trả về nguyên gốc
    
    tn_blocks = [] # Trắc nghiệm
    tf_blocks = [] # Đúng Sai
    sa_blocks = [] # Trả lời ngắn
    
    for b in blocks:
        if r'\choiceTF' in b:
            tf_blocks.append(b)
        elif r'\shortans' in b:
            sa_blocks.append(b)
        else:
            tn_blocks.append(b)
            
    # Helper wrap từng phần với tham số command (lệnh đầu nhóm)
    def make_section(content_list, phan_label, comment, command):
        if not content_list: return ""
        content = "\n\n".join(content_list)
        return (f"{command}\n"
                f"\\Opensolutionfile{{ans}}[ans/ans\\currfilebase-Phan-{phan_label}]\n"
                f"%{comment}\n"
                f"{content}\n"
                f"\\Closesolutionfile{{ans}}")

    body_parts = []
    
    # Phần I: Trắc nghiệm -> Dùng \cautn
    if tn_blocks:
        body_parts.append(make_section(tn_blocks, "I", "NHÓM CÂU TRẮC NGHIỆM", "\\cautn"))
        
    # Phần II: Đúng Sai -> Dùng \cauds
    if tf_blocks:
        body_parts.append(make_section(tf_blocks, "II", "NHÓM CÂU ĐÚNG SAI", "\\cauds"))
        
    # Phần III: Trả lời ngắn -> Dùng \caukq
    if sa_blocks:
        body_parts.append(make_section(sa_blocks, "III", "NHÓM CÂU TRẢ LỜI NGẮN", "\\caukq"))
        
    full_content = "\n\n".join(body_parts)
    
    # Wrap tổng thể
    final_text = (f"\\Opensolutionfile{{ansbook}}[ans/ansb\\currfilebase]\n"
                  f"{full_content}\n"
                  f"\\Closesolutionfile{{ansbook}}\n"
                  f"\\begin{{indapan}}\n"
                  f"    {{ans/ans\\currfilebase}}\n"
                  f"\\end{{indapan}}")
    
    return final_text

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
    text = re.sub(r'([A-Z])\s*\\cdot\s*([A-Z]{2,})', r'\1.\2', text)
    text = re.sub(r'\(\$([^\$\n]+)\$\)', r'$(\1)$', text)
    def insert_sep(match):
        num = match.group(0)
        if len(num) < 4: return num
        res = ""
        for i, digit in enumerate(reversed(num)):
            if i > 0 and i % 3 == 0: res = "\\," + res
            res = digit + res
        return res
    parts = re.split(r'(\$.*?\$)', text, flags=re.DOTALL)
    for i in range(len(parts)):
        if parts[i].startswith('$') and parts[i].endswith('$'):
            parts[i] = re.sub(r'\d{4,}', insert_sep, parts[i])
    text = "".join(parts)
    def process_comma(match):
        content = match.group(1).strip()
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

def add_question_comments(text):
    if not text: return ""
    parts = re.split(r'(\\begin\{ex\}.*?\\end\{ex\})', text, flags=re.DOTALL)
    processed = []
    counter = 1
    for part in parts:
        if part.strip().startswith(r'\begin{ex}'):
            q_type = "TN"
            if r'\choiceTF' in part: q_type = "DS"
            elif r'\shortans' in part: q_type = "TLN"
            processed.append(f"%Câu {counter} ({q_type})\n{part}")
            counter += 1
        else: processed.append(part)
    return "".join(processed)

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
