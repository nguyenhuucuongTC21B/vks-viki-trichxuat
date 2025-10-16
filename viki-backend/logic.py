# logic.py (Phiên bản tối ưu cho file mẫu và thêm chức năng làm sạch)
import re
import pytesseract
from PIL import Image
import docx
import pdf2image
import PyPDF2

# --- CẤU HÌNH (SỬA NẾU CẦN) ---
POPPLER_PATH = None
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# --- HÀM TIỆN ÍCH MỚI ---
def clean_fragmented_text(text):
    """
    Hàm này dọn dẹp các từ bị OCR lỗi, ví dụ: 'l ừa' -> 'lừa'.
    """
    if not isinstance(text, str):
        return text
    
    # Định nghĩa các ký tự Tiếng Việt
    vietnamese_chars = "a-zA-Zàáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ"
    # Biểu thức chính quy này tìm một khoảng trắng nằm giữa hai ký tự Tiếng Việt
    # và thay thế nó bằng không có gì cả (xóa khoảng trắng)
    # Chạy 2 lần để xử lý các trường hợp phức tạp hơn
    text = re.sub(f'([{vietnamese_chars}])\s([{vietnamese_chars}])', r'\1\2', text)
    text = re.sub(f'([{vietnamese_chars}])\s([{vietnamese_chars}])', r'\1\2', text)
    return text

# --- CÁC HÀM TRÍCH XUẤT VĂN BẢN THÔ (ĐÃ NÂNG CẤP LOGIC LÀM SẠCH) ---
def extract_text_from_pdf_smart(file_path):
    text = ""
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        
        # Nếu text quá ngắn (dấu hiệu của PDF ảnh), chuyển sang OCR
        if len(text.strip()) < 100:
            images = pdf2image.convert_from_path(file_path, poppler_path=POPPLER_PATH)
            ocr_text = ""
            for image in images:
                # Chỉ áp dụng làm sạch cho kết quả từ OCR
                ocr_text += pytesseract.image_to_string(image, lang='vie') + "\n"
            text = clean_fragmented_text(ocr_text) # Làm sạch sau khi OCR xong

    except Exception as e:
        print(f"Lỗi khi xử lý PDF: {e}")
    return text

def extract_text_from_docx(file_path):
    # ... (giữ nguyên không đổi)
    try:
        doc = docx.Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        print(f"Lỗi khi đọc DOCX: {e}")
        return ""

def extract_text_from_image(file_path):
    # ... (Nâng cấp: tự động làm sạch sau khi OCR)
    try:
        raw_text = pytesseract.image_to_string(Image.open(file_path), lang='vie')
        return clean_fragmented_text(raw_text) # Làm sạch ngay sau khi OCR
    except Exception as e:
        print(f"Lỗi khi OCR ảnh: {e}")
        return ""

# --- CÁC HÀM TRÍCH XUẤT THÔNG TIN ---
def find_by_label(text, label):
    pattern = rf'{label}\s*:\s*([^\n]+)'
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return ""

def find_ngay_thu_ly_custom(text):
    # ... (giữ nguyên không đổi)
    ngay = find_by_label(text, "Ngày thụ lý")
    if ngay:
        return ngay
    
    match = re.search(r'Khởi tố vụ án:\s*(\d{1,2}/\d{1,2}/\d{4})', text, re.IGNORECASE)
    if match:
        parts = match.group(1).split('/')
        return f"{parts[0].zfill(2)}/{parts[1].zfill(2)}/{parts[2]}"
    return ""

def find_tinh_trang_custom(text):
    # ... (giữ nguyên không đổi)
    text_lower = text.lower()
    if "xét xử sơ thẩm" in text_lower:
        return "Đã có bản án/Quyết định đình chỉ"
    if "truy tố" in text_lower:
        return "Đã truy tố"
    if "kết luận điều tra" in text_lower:
        return "Đang điều tra"
    if "khởi tố vụ án" in text_lower or "khởi tố bị can" in text_lower:
        return "Đang điều tra"
    return ""

# --- HÀM TỔNG HỢP (ĐÃ NÂNG CẤP) ---

def process_file_content(text):
    if not text:
        return None

    # Bây giờ không cần gọi clean_fragmented_text ở đây nữa
    # vì text đầu vào đã được xử lý ở bước trích xuất
    so_ho_so = find_by_label(text, "Số hồ sơ")
    toi_danh = find_by_label(text, "Tội danh")
    bi_cao = find_by_label(text, "Bị cáo")
    nguoi_bi_hai = find_by_label(text, "Người bị hại")
    thoi_gian_pham_toi = find_by_label(text, "Thời gian phạm tội")
    co_quan_dieu_tra = find_by_label(text, "Cơ quan điều tra")
    
    ngay_thu_ly = find_ngay_thu_ly_custom(text)
    tinh_trang_xu_ly = find_tinh_trang_custom(text)
    
    match_ngay_khoi_to = re.search(r'Khởi tố vụ án:\s*(\d{1,2}/\d{1,2}/\d{4})', text, re.IGNORECASE)
    thoi_gian_khoi_to = match_ngay_khoi_to.group(1) if match_ngay_khoi_to else ""

    return {
        "Số hồ sơ": so_ho_so,
        "Tội danh": toi_danh,
        "Ngày thụ lý": ngay_thu_ly,
        "Tình trạng xử lý": tinh_trang_xu_ly,
        "Bị cáo": bi_cao,
        "Người bị hại": nguoi_bi_hai,
        "Thời gian phạm tội": thoi_gian_pham_toi,
        "Cơ quan điều tra": co_quan_dieu_tra,
        "Thời gian khởi tố": thoi_gian_khoi_to,
    }

