import os
import shutil
from typing import List
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logic 

app = FastAPI(title="ViKi - API VKSND TP Đà Nẵng Trích xuất Hồ sơ Tố tụng")
origins = [
    "http://localhost:3000",
    "https://vks-viki-trichxuat.vercel.app", 
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/trich-xuat/")
async def trich_xuat_ho_so(files: List[UploadFile] = File(...)):
    results = []
    unique_check = set()

    for file in files:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            text = ""
            if file.filename.lower().endswith('.pdf'):
                # SỬA LỖI TẠI ĐÂY: Đã đổi tên hàm thành extract_text_from_pdf_smart
                text = logic.extract_text_from_pdf_smart(file_path)
            elif file.filename.lower().endswith('.docx'):
                text = logic.extract_text_from_docx(file_path)
            elif file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                text = logic.extract_text_from_image(file_path)

            # ----- CÔNG CỤ GỠ LỖI -----
            print("\n" + "="*20 + " NỘI DUNG TRÍCH XUẤT " + "="*20)
            print(f"File: {file.filename}")
            print(text)
            print("="*60 + "\n")
            # ---------------------------
            
            if text:
                data = logic.process_file_content(text)
                if data and data.get("Số hồ sơ"):
                    identifier = f'{data["Số hồ sơ"]}|{data["Tội danh"]}'
                    if identifier not in unique_check:
                        results.append(data)
                        unique_check.add(identifier)

        except Exception as e:
            # Lỗi sẽ được in ra đây
            print(f"Lỗi nghiêm trọng khi xử lý file {file.filename}: {e}")
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)

    if not results:
        raise HTTPException(status_code=404, detail="Không trích xuất được thông tin từ các file đã cho.")
    
    return results

@app.get("/")
def read_root():
    return {"message": "Chào mừng đến với API VKSND TP Đà Nẵng Trích xuất Hồ sơ Tố tụng ViKi! Truy cập /docs để xem tài liệu."}

