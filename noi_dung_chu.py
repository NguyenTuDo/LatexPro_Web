# --- CẤU HÌNH NỘI DUNG VĂN BẢN (ALL IN ONE) ---

TIÊU_ĐỀ_APP = "Latex Pro Web - Thầy Tư Đô Nguyên"

# 1. THÔNG TIN GIỚI THIỆU (Đây là biến mà code đang tìm kiếm)
THONG_TIN_UNG_DUNG = {
    "Tên phần mềm": "LATEX PRO WEB CONVERTER",
    "Phiên bản": "Web V11.0 (Stable Release)",
    "Tác giả": "Thầy TƯ ĐÔ NGUYÊN",
    "Đơn vị": "THPT MARIE CURIE - TP.HCM",
    "Liên hệ": "Zalo/SĐT: 0961 830 801",
    "Mô tả": (
        "Công cụ chuyển đổi và chuẩn hóa tài liệu Toán học từ Mathpix/Word sang LaTeX chuyên nghiệp.\n"
        "Được thiết kế tối ưu cho môi trường Web với giao diện Split-View hiện đại, "
        "hỗ trợ xử lý hàng loạt các cấu trúc Toán cao cấp (Tích phân, Vectơ, Hình học Oxyz) "
        "và hệ thống nhập đáp án trực quan."
    )
}

# 2. HƯỚNG DẪN SỬ DỤNG
TIEU_DE_HUONG_DAN = "HƯỚNG DẪN SỬ DỤNG CHI TIẾT"

NOI_DUNG_HUONG_DAN = [
    ("1. TỔNG QUAN GIAO DIỆN MỚI", 
     """Giao diện được thiết kế theo phong cách IDE hiện đại:

**🔹 TOP BAR (Thanh Tác Vụ):**
* ✨ **CHUẨN HÓA:** Bước đầu tiên bắt buộc để xử lý code thô.
* 📋 **COPY ALL:** Sao chép nhanh toàn bộ kết quả.
* 💾 **TẢI .TEX:** Xuất file để lưu trữ trên máy.

**🔹 SIDEBAR (Cột Trái):**
* Chuyển đổi giao diện Sáng/Tối (Dark Mode).
* Bảng Thống kê chi tiết (Đếm số câu TN, ĐS, TLN và kiểm tra số lượng đáp án).

**🔹 WORKSPACE (Khu vực làm việc):**
* **Cột Trái (Editor):** Nơi soạn thảo code (Hỗ trợ xuống dòng, bôi đen).
* **Cột Phải (Tools):** Chia làm 3 Tab chức năng (Làm Đẹp - Ảnh/Tag - Đáp Án)."""),
     
    ("2. QUY TRÌNH XỬ LÝ CHUẨN (4 BƯỚC)", 
     """* **Bước 1 (Input):** Copy văn bản từ Mathpix hoặc file Word -> Dán vào khung Editor.
* **Bước 2 (Standardize):** Bấm nút xanh **'✨ 1. TỰ ĐỘNG CHUẨN HÓA'** trên Top Bar. Hệ thống sẽ dọn dẹp rác, phân loại câu hỏi và đưa về cấu trúc chuẩn.
* **Bước 3 (Beautify):** Qua Tab **'✨ LÀM ĐẸP'** bên phải -> Tích chọn các tính năng -> Bấm **'⚡ CHẠY LÀM ĐẸP'**.
* **Bước 4 (Key & Export):** Qua Tab **'🔑 ĐÁP ÁN'** để nhập key -> Bấm Lưu -> Tải file về."""),
     
    ("3. GIẢI THÍCH TÍNH NĂNG LÀM ĐẸP (TAB 1)", 
     """**A. Cấu trúc & Cơ bản:**
* **Dọn link Mathpix:** Xóa sạch các đường dẫn ảnh lỗi `![](https...)`.
* **Sửa O x y:** Gom nhóm tọa độ rời rạc (Ví dụ: `O x y` -> `Oxy`).
* **Dấu {,}:** Chuyển dấu chấm thập phân thành phẩy chuẩn Toán Việt Nam.
* **Bọc $ số:** Tự động thêm `$` cho các số đứng riêng lẻ.
* **frac -> dfrac:** Chuyển phân số dòng `\\frac` thành phân số hiển thị `\\dfrac`.
* **Hệ (heva):** Chuyển các môi trường `cases`, `array` về lệnh tắt `\\heva`, `\\hoac`.
* **Smart Clean:** Xử lý thông minh các lỗi vặt.

**B. Toán Cao Cấp (NEW):**
* **Format Tích phân:** Tự động thêm `\\displaystyle`, `\\limits`, `\\mathrm{\\,d}x`.
* **Format Vectơ:** Chuyển `\\vec` về `\\overrightarrow`.
* **Format Hình học:** Đổi dấu hai chấm `(P):` thành `(P) \\colon`."""),
     
    ("4. CÔNG CỤ HÌNH ẢNH & PHÂN LOẠI (TAB 2)", 
     """* **Phân loại:** Bấm `➕ %Câu` hoặc `➕ %Bài` để chèn nhanh chú thích.
* **Dàn trang ảnh:** Chọn chế độ trong danh sách (Center, Immini...) -> Bấm `🖼️ Áp dụng`."""),
     
    ("5. HỆ THỐNG NHẬP ĐÁP ÁN (TAB 3)", 
     """Giao diện nhập liệu trực quan cho Trắc nghiệm, Đúng/Sai và Trả lời ngắn. Sau khi nhập xong, bấm nút **LƯU ĐÁP ÁN** để chèn vào code.""")
]