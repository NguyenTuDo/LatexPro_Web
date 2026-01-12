import re
# Sửa dòng import
from .math_utils import basic_standardize

def standardize_4_chars(text):
    # ... (Giữ nguyên code của bạn) ...
    if not text: return ""
    s = text.replace('$', '').replace('{,}', ',').replace('.', ',').strip()
    try:
        val = float(s.replace(',', '.'))
        s = f"{val:g}".replace('.', ',')
        if ',' in s:
            while len(s) < 4: s += '0'
        else:
            if len(s) < 4: s += ',0'
            while len(s) < 4: s += '0'
        return s[:4]
    except: return s[:10]

def convert_tra_loi_ngan(block, loigiai_final):
    # ... (Giữ nguyên code của bạn) ...
    da_pattern = r'(?i)(?:\n\s*(?:Đáp\s*án|Kết\s*quả|Đáp\s*số)[\s:]*|(?:\s(?:Đáp\s*án|Kết\s*quả|Đáp\s*số):))'
    parts = re.split(da_pattern, block, maxsplit=1)
    
    de_raw = parts[0].strip()
    de_raw = re.sub(r'^(Câu|Câu\s*)\s*\d+[\.:]?\s*', '', de_raw, flags=re.IGNORECASE).strip()
    
    da_raw = parts[1].strip() if len(parts) > 1 else ""
    
    de_cl = basic_standardize(de_raw)
    da_cl = standardize_4_chars(da_raw)

    return (f"\\begin{{ex}}\n    {de_cl}\n"
            f"    \\par\\shortans[]{{{da_cl}}}\n"
            f"    \\loigiai{{\n    {loigiai_final}\n    }}\n\\end{{ex}}")