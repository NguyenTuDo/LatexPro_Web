# --- CẤU HÌNH NỘI DUNG VĂN BẢN (ALL IN ONE) ---

TIÊU_ĐỀ_APP = "LATEX PRO WEB"

# 1. THÔNG TIN GIỚI THIỆU & TÁC GIẢ
THONG_TIN_UNG_DUNG = {
    "Tên phần mềm": "LATEX PRO WEB - Ultimate Exam Converter",
    "Phiên bản": "2.0 Pro (Build 2026)",
    "Tác giả": "Thầy TƯ ĐÔ NGUYÊN",
    "Đơn vị": "THPT MARIE CURIE - TP.HCM",
    "Liên hệ": "0961 830 801",
    # Link ảnh Avatar và Facebook
    "Avatar": "https://scontent.fsgn5-15.fna.fbcdn.net/v/t39.30808-6/565088171_2332484843854105_7708365789525205156_n.jpg?_nc_cat=111&ccb=1-7&_nc_sid=6ee11a&_nc_eui2=AeEbdOMtpKzfe7ZECkX50NrjDuOHxuab7XYO44fG5pvtdht3r1Cee4QkmxPuIshIKdcAHXNbboyoAI1T1rGUsBG4&_nc_ohc=asZpDrO4PbEQ7kNvwF2bTRH&_nc_oc=AdmAjL2uD4p-hfUPuVZW1ZC2w_TdHbiUnnikefxvLDDjZifscacExXLEc2sfDwTGxSk&_nc_zt=23&_nc_ht=scontent.fsgn5-15.fna&_nc_gid=7p45B-jSDVFNyfjEU3mENA&oh=00_Afq9qrA776rSdT6O4L7E3PtDTNKtMbK54YqtNSze4st5pA&oe=696BA094",
    "Facebook": "https://www.facebook.com/dodododo171/", 
    "Mô tả": (
        "**LATEX PRO WEB** là giải pháp toàn diện để xử lý đề thi Toán học:\n\n"
        "🚀 **Tốc độ:** Xử lý hàng trăm câu hỏi trong vài giây.\n\n"
        "✨ **Thông minh:** Tự động nhận diện cấu trúc, làm đẹp Toán học, chuẩn hóa hình vẽ.\n\n"
        "📦 **Chuyên nghiệp:** Đóng gói đề thi (Ansbook) chuẩn cấu trúc báo cáo."
    )
}

# 2. HƯỚNG DẪN SỬ DỤNG
TIEU_DE_HUONG_DAN = "HƯỚNG DẪN SỬ DỤNG CHI TIẾT"

NOI_DUNG_HUONG_DAN = [
    ("1. QUY TRÌNH XỬ LÝ ĐỀ THI (WORKFLOW)", 
     """Để đạt hiệu quả cao nhất, hãy tuân theo quy trình 5 bước sau:
     
1.  **📥 INPUT:** Dán code thô từ Mathpix/Word vào khung soạn thảo.
2.  **✨ CHUẨN HÓA:** Nhấn nút **"CHUẨN HÓA EXTEST"** (Màu xanh) để đưa về dạng `ex/choice`.
3.  **📝 TỰ LUẬN:** Nếu có bài tự luận, mở tab Tự luận ➝ Dùng công cụ Popup để xử lý riêng ➝ Chèn vào cuối đề.
4.  **🔑 ĐÁP ÁN:** Vào tab Đáp án ➝ Nhập liệu (hoặc Copy nhanh chuỗi `1A2B...`) ➝ Nhấn Lưu để cập nhật code `\\choice`.
5.  **📦 ĐÓNG GÓI:** Nhấn **"ĐÓNG GÓI MAIN"** ➝ Tùy chỉnh cấu trúc (nếu cần) ➝ Xuất ra code hoàn chỉnh để chạy trên LaTeX."""),

    ("2. CÁC CÔNG CỤ LÀM ĐẸP (TAB 1)", 
     """Tab **✨ LÀM ĐẸP** chứa các "màng lọc" giúp code LaTeX của bạn chuẩn chỉ từng dấu phẩy:

**🅰️ Nhóm CƠ BẢN (Nên bật thường xuyên):**
* ✅ **Smart Clean:** "Bộ não" của ứng dụng.
    * Tự động sửa lỗi ngắt quãng số (`1 2 3` ➝ `123`).
    * Sửa ký hiệu nhân (`.` ➝ `\\cdot`).
    * Xử lý đơn vị vật lý/hóa học (`5 kg` ➝ `$5$\\,kg`, `(cm)` ➝ `$(cm)$`).
* ✅ **Mathpix Clean:** Xóa sạch các link ảnh rác `![](...)` do Mathpix sinh ra.
* ✅ **Xóa khoảng trống:**
    * Dọn dẹp tọa độ: `( 1 ; 2 )` ➝ `(1;2)`.
    * Dọn dẹp tên điểm: `O x y z` ➝ `Oxyz`.
* ✅ **Format Số & Toán (\$):**
    * Chuyển dấu thập phân: `2.5` ➝ `2{,}5` (Chuẩn Việt Nam).
    * Tự động bọc `$` cho số đứng lẻ loi: `Có 5 nghiệm` ➝ `Có $5$ nghiệm`.

**🅱️ Nhóm NÂNG CAO (Dành cho người khó tính):**
* **frac ➝ dfrac:** Chuyển tất cả phân số thành dạng hiển thị lớn (`\\dfrac`).
* **Hệ (heva/hoac):** Gom các môi trường `cases`, `array`, `aligned` rườm rà về lệnh tắt `\\heva`, `\\hoac` (gọn hơn 70%).
* **Displaystyle:** Tự động thêm `\\displaystyle` trước tích phân/lim để công thức không bị bẹp.
* **Vectơ chuẩn:** Đổi `\\vec{u}` ➝ `\\overrightarrow{u}`.
* **Colon (:):** Đổi dấu `:` trong hình học (tỉ lệ) thành lệnh `\\colon` (khoảng cách chuẩn)."""),

    ("3. XỬ LÝ TỰ LUẬN CHUYÊN BIỆT (TAB 2)", 
     """Công cụ này giúp bạn xử lý các bài toán tự luận (thường có cấu trúc `Bài 1`, `a)`, `b)`) mà không làm hỏng phần trắc nghiệm.

* **🛡️ Cơ chế Sandbox:** Chạy trong một cửa sổ Popup riêng biệt, an toàn tuyệt đối cho code chính.
* **⚙️ Tính năng:**
    * Tự động đổi `Bài 1`, `Câu 1` thành môi trường `ex`.
    * Tự động gom các ý nhỏ `a)`, `b)`, `1)`, `2)` vào môi trường `enumerate`.
* **💡 Cách dùng:** Mở Popup ➝ Dán đề thô ➝ Nhấn Chuyển đổi ➝ Kiểm tra kết quả ➝ Nhấn **"Chèn vào cuối đề"**."""),

    ("4. NHẬP LIỆU ĐÁP ÁN THÔNG MINH (TAB 4)", 
     """Không cần gõ tay từng lệnh `\\True`! Tab này cung cấp giao diện nhập liệu siêu tốc:

* **⚡ Nhập nhanh (Quick Fill):**
    * Bạn có chuỗi đáp án từ Excel/Zalo: `1A 2B 3C 4D`?
    * Chỉ cần dán vào ô nhập nhanh. Hệ thống tự động lọc lấy `ABCD` và điền vào 50 câu trong 1 giây.
* **GRID View:** Giao diện lưới trực quan, dễ dàng rà soát.
* **Hỗ trợ đủ 3 dạng:** Trắc nghiệm (Radio), Đúng Sai (Checkbox), Trả lời ngắn (Input)."""),

    ("5. ĐÓNG GÓI & XUẤT BẢN (NÚT ĐÓNG GÓI)", 
     """Bước cuối cùng để biến các câu hỏi rời rạc thành đề thi hoàn chỉnh.

* **🛠️ Tùy chỉnh linh hoạt (Nút ⚙️):**
    * Bạn có thể đổi lệnh `\\cautn` thành `\\section*{Phần 1}`.
    * Tắt/Bật tính năng tạo file đáp án riêng (`\\Opensolutionfile`).
    * Chỉnh sửa đường dẫn file đáp án (`ans/ans-Phan-I`...).
* **👁️ Preview:** Xem trước cấu trúc khung xương của đề thi ngay trong Popup trước khi áp dụng.
* **↺ Khôi phục:** Nút Reset giúp bạn quay về cài đặt gốc nếu lỡ chỉnh sai.""")
]