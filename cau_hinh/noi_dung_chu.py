# --- CẤU HÌNH NỘI DUNG VĂN BẢN (ALL IN ONE) ---

TIÊU_ĐỀ_APP = "LATEX PRO WEB"

# 1. THÔNG TIN GIỚI THIỆU & TÁC GIẢ
THONG_TIN_UNG_DUNG = {
    "Tên phần mềm": "LATEX PRO WEB - Ultimate Converter",
    "Phiên bản": "1.2 (Cập nhật 13/01/2026)",
    "Tác giả": "Thầy TƯ ĐÔ NGUYÊN",
    "Đơn vị": "THPT MARIE CURIE - TP.HCM",
    "Liên hệ": "0961 830 801",
    # Bạn hãy thay link ảnh Avatar và Facebook thật của bạn vào đây
    "Avatar": "https://scontent.fsgn5-15.fna.fbcdn.net/v/t39.30808-6/565088171_2332484843854105_7708365789525205156_n.jpg?_nc_cat=111&ccb=1-7&_nc_sid=6ee11a&_nc_eui2=AeEbdOMtpKzfe7ZECkX50NrjDuOHxuab7XYO44fG5pvtdht3r1Cee4QkmxPuIshIKdcAHXNbboyoAI1T1rGUsBG4&_nc_ohc=asZpDrO4PbEQ7kNvwF2bTRH&_nc_oc=AdmAjL2uD4p-hfUPuVZW1ZC2w_TdHbiUnnikefxvLDDjZifscacExXLEc2sfDwTGxSk&_nc_zt=23&_nc_ht=scontent.fsgn5-15.fna&_nc_gid=7p45B-jSDVFNyfjEU3mENA&oh=00_Afq9qrA776rSdT6O4L7E3PtDTNKtMbK54YqtNSze4st5pA&oe=696BA094",
    "Facebook": "https://www.facebook.com/dodododo171/", 
    "Mô tả": (
        "Công cụ xử lý LaTeX Toán học chuyên nghiệp trên nền tảng Web.<br>"
        "Phiên bản v1.2 mang đến quy trình làm việc khép kín: "
        "Từ chuẩn hóa thô -> Làm đẹp chi tiết -> Đóng gói Ansbook -> Kiểm tra thống kê."
    )
}

# 2. HƯỚNG DẪN SỬ DỤNG
TIEU_DE_HUONG_DAN = "HƯỚNG DẪN SỬ DỤNG CHI TIẾT"

NOI_DUNG_HUONG_DAN = [
    ("1. GIAO DIỆN LÀM VIỆC", 
     """Giao diện được thiết kế theo phong cách <b>Compact & Modern</b>:

**🔹 TOP BAR:**
* ✨ **TỰ ĐỘNG CHUẨN HÓA:** Nút xử lý quan trọng nhất. Biến văn bản thô thành cấu trúc `ex/choice` chuẩn.
* 📋 **COPY / 💾 TEX:** Sao chép hoặc tải file kết quả về máy.
* 🔧 **Tự làm đẹp:** Nếu bật, phần mềm sẽ tự chạy các tính năng ở Tab Làm Đẹp ngay sau khi chuẩn hóa xong.

**🔹 WORKSPACE (4 TAB CHỨC NĂNG):**
1. **✨ LÀM ĐẸP:** Các bộ lọc tinh chỉnh Toán học và Cấu trúc đề.
2. **🖼️ ẢNH & TAG:** Quản lý khung hình (`immini`) và gắn thẻ câu hỏi.
3. **🔑 ĐÁP ÁN:** Nhập liệu đáp án Trắc nghiệm/Đúng Sai nhanh chóng.
4. **📊 THỐNG KÊ:** Kiểm soát số lượng câu hỏi và tình trạng nhập đáp án."""),
     
    ("2. TÍNH NĂNG LÀM ĐẸP (TAB 1)", 
     """Tab này cung cấp các công cụ mạnh mẽ để "trang điểm" cho code LaTeX:

**A. Nhóm CƠ BẢN (Khuyên dùng):**
* ✅ **Smart Clean:** Thuật toán dọn rác thông minh (Sửa lỗi ngắt số, ký hiệu nhân, khoảng trắng thừa trong `$...$`).
* ✅ **Format Số & Toán (\$):** Tính năng "2 trong 1":
    * Chuyển dấu thập phân: `2.5` → `2{,}5`.
    * Tự động bọc `$` cho số đứng lẻ: `2,5` → `$2{,}5$`.
* ✅ **Xóa khoảng trống:** Dọn dẹp `O x y` → `Oxy`, `( A ; B )` → `(A;B)`.

**B. Nhóm NÂNG CAO & CẤU TRÚC:**
* **frac → dfrac:** Chuyển phân số dòng sang phân số hiển thị (to đẹp hơn).
* **Hệ (heva/hoac):** Gộp các môi trường `cases`, `array` rườm rà về lệnh tắt `\\heva`, `\\hoac` chuẩn gói `ex_test`.
* **Format Tích phân:** Tự động thêm `\\displaystyle`, `\\limits` và sửa `dx` → `\\mathrm{\\,d}x`.
* **Format Vectơ:** Chuẩn hóa `\\vec` → `\\overrightarrow` và xử lý chỉ số dưới.

**C. TIỆN ÍCH ĐÓNG GÓI:**
* 📦 **CHUẨN HÓA MAIN (ANSBOOK):** Nút vàng nổi bật. Tự động phân nhóm câu hỏi (I, II, III) và chèn code xuất đáp án (`\\Opensolutionfile`), sẵn sàng để biên dịch ra PDF."""),
     
    ("3. KIỂM SOÁT CHẤT LƯỢNG (TAB 4)", 
     """Tab **THỐNG KÊ** giúp bạn kiểm tra nhanh tình trạng đề thi với giao diện trực quan:
* Hiển thị tổng số câu hỏi theo từng loại (MC, TF, SA).
* **Cảnh báo màu sắc:**
    * <span style="color:#28a745"><b>XANH (OK):</b></span> Đã nhập đủ đáp án cho tất cả câu hỏi.
    * <span style="color:#d9534f"><b>ĐỎ (Warning):</b></span> Còn thiếu đáp án (số lượng chưa khớp tổng số câu).
* Đếm chính xác số câu Trả lời ngắn (SA) chưa có nội dung.""")
]