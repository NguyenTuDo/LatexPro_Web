import re
# SỬA: Dùng dấu chấm . để gọi file cùng thư mục
from .math_utils import basic_standardize

def convert_trac_nghiem(block, loigiai_final):
    regex_opts = r'\s+([A-D][\.\)])\s+'
    parts = re.split(regex_opts, " " + block)
    
    de_raw = parts[0].strip()
    de_raw = re.sub(r'^(Câu|Câu\s*)\s*\d+[\.:]?\s*', '', de_raw, flags=re.IGNORECASE).strip()
    
    opts = ["", "", "", ""]
    for i in range(1, len(parts), 2):
        label = parts[i][0].upper()
        content = parts[i+1] if (i+1) < len(parts) else ""
        idx = ord(label) - ord('A')
        if 0 <= idx < 4: opts[idx] = content.strip()

    de_cl = basic_standardize(de_raw)
    opts_cl = [basic_standardize(o.rstrip('.')) for o in opts]

    return (f"\\begin{{ex}}\n    {de_cl}\n    \\choice\n"
            f"    {{{opts_cl[0]}}}\n    {{{opts_cl[1]}}}\n"
            f"    {{{opts_cl[2]}}}\n    {{{opts_cl[3]}}}\n"
            f"    \\loigiai{{\n    {loigiai_final}\n    }}\n\\end{{ex}}")