import re

def convert_tu_luan(text):
    if not text: return ""

    # =========================================================
    # BƯỚC 1: TIỀN XỬ LÝ
    # =========================================================
    
    # 1.1 Gỡ bỏ định dạng rác
    text = re.sub(r'\\section\*?\{(.*?)\}', r'\1', text)
    text = re.sub(r'\\textbf\{(.*?)\}', r'\1', text)
    
    # 1.2 Chuẩn hóa Header:
    # "Bài 1" -> "Câu 1"
    text = re.sub(r'(?mi)^\s*Bài\s+', 'Câu ', text)
    text = re.sub(r'Câu\s*\$(\d+)\$', r'Câu \1', text)
    
    # Đảm bảo kết thúc Header là dấu hai chấm
    text = re.sub(r'(?mi)^(\s*Câu\s+\d+)(.*?)[:\.]', r'\1\2:', text)

    # =========================================================
    # BƯỚC 2: TÁCH CÂU HỎI
    # =========================================================
    
    # Tách dựa trên "Câu X" ở đầu dòng
    parts = re.split(r'(?m)^(?=Câu\s+\d+)', text)
    
    results = []
    question_count = 1  # [MỚI] Biến đếm số thứ tự câu
    
    for part in parts:
        if not part.strip(): continue
        
        # Nếu không phải header câu hỏi, giữ nguyên (đoạn dẫn đề)
        if not re.match(r'(?mi)^\s*Câu\s+\d+', part):
            results.append(part.strip())
            continue

        # =====================================================
        # BƯỚC 3: XỬ LÝ ĐIỂM SỐ & NỘI DUNG
        # =====================================================
        
        # 3.1 Tách điểm số: (1 điểm), [1.5 điểm]
        score = ""
        score_match = re.search(r'(?:[\(\[]\s*(\d+(?:[.,]\d+)?)\s*(?:điểm|đ)\s*[\)\]])', part, flags=re.IGNORECASE)
        
        if score_match:
            score = score_match.group(1)
            part = part.replace(score_match.group(0), "")
        
        # 3.2 Tách Lời giải
        lg_split = re.split(r'(?i)(Lời\s+giải|HDG)[:\s]*', part, maxsplit=1)
        full_de = lg_split[0].strip()
        loi_giai = lg_split[-1].strip() if len(lg_split) > 1 else ""
        
        # 3.3 [QUAN TRỌNG] Xóa Header cũ ("Câu 5:", "Câu 1:")
        # Để LaTeX tự động đánh số lại theo thứ tự ex mới
        de_bai = re.sub(r'(?mi)^\s*Câu\s+\d+:\s*', '', full_de).strip()

        # =====================================================
        # BƯỚC 4: NHẬN DIỆN Ý NHỎ (enumerate)
        # =====================================================
        
        # Chuẩn hóa "a." -> "a)"
        de_bai = re.sub(r'(?m)^(\s*)([a-z0-9]+)\.\s+', r'\1\2) ', de_bai)
        
        # Tách ý a) b)
        sub_items = re.split(r'(?m)(?:^|\n)\s*([a-z0-9]+)\)\s*', de_bai)
        
        formatted_de = ""
        
        if len(sub_items) > 1:
            intro = sub_items[0].strip()
            if intro: formatted_de += intro + "\n"
            
            formatted_de += "\\begin{enumerate}"
            for i in range(1, len(sub_items), 2):
                content = sub_items[i+1].strip()
                formatted_de += f"\n    \\item {content}"
            formatted_de += "\n\\end{enumerate}"
        else:
            formatted_de = de_bai

        # =====================================================
        # BƯỚC 5: ĐÓNG GÓI EX (TỰ ĐÁNH SỐ)
        # =====================================================
        
        # Tạo tham số tùy chọn [x điểm]
        opt_arg = f"[{score} điểm]" if score else ""
        
        # [MỚI] Thêm comment %Câu 1, %Câu 2... để dễ quản lý code
        block = f"%Câu {question_count}\n\\begin{{ex}}{opt_arg}\n{formatted_de}\n\\loigiai{{{loi_giai}}}\n\\end{{ex}}"
        
        results.append(block)
        question_count += 1 # Tăng biến đếm

    return "\n\n".join(results)