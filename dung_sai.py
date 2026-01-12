import re
# Sửa dòng import
from .math_utils import basic_standardize

def convert_dung_sai(block, loigiai_final):
    # ... (Giữ nguyên toàn bộ code cũ của bạn từ đây trở xuống) ...
    regex_opts = r'\s+([a-d][\.\)])\s+'
    parts = re.split(regex_opts, " " + block)
    
    de_raw = parts[0].strip()
    de_raw = re.sub(r'^(Câu|Câu\s*)\s*\d+[\.:]?\s*', '', de_raw, flags=re.IGNORECASE).strip()
    
    opts = ["", "", "", ""]
    for i in range(1, len(parts), 2):
        label = parts[i][0].lower()
        content = parts[i+1] if (i+1) < len(parts) else ""
        idx = ord(label) - ord('a')
        if 0 <= idx < 4: opts[idx] = content.strip()

    de_cl = basic_standardize(de_raw)
    opts_cl = [basic_standardize(o.rstrip('.')) for o in opts]

    return (f"\\begin{{ex}}\n    {de_cl}\n    \\choiceTF\n"
            f"    {{{opts_cl[0]}}}\n    {{{opts_cl[1]}}}\n"
            f"    {{{opts_cl[2]}}}\n    {{{opts_cl[3]}}}\n"
            f"    \\loigiai{{\n    {loigiai_final}\n"
            f"    \\begin{{itemchoice}}\n        \\itemch \n        \\itemch \n"
            f"        \\itemch \n        \\itemch \n    \\end{{itemchoice}}\n    }}\n\\end{{ex}}")