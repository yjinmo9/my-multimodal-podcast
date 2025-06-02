import fitz  # PyMuPDF
import os
import pytesseract  # type: ignore
import cv2  # type: ignore
from PIL import Image  # type: ignore
from typing import List, Dict, Optional
from langfuse import Langfuse

def extract_slide_texts_and_images(pdf_path: str, output_dir: str, langfuse_trace: Optional[any] = None) -> List[Dict]:
    os.makedirs(output_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    slide_infos = []

    # ✅ Langfuse span 시작
    span = langfuse_trace.span(name="Extract Slides") if langfuse_trace else None

    for i, page in enumerate(doc):
        slide_data = {
            "slide": i + 1,
            "text_pdf": page.get_text("text"),
            "text_ocr": "",
            "page_image_path": None,
            "extracted_images": [],
            "image_descriptions": []  # Vision 결과 저장
        }

        try:
            # ✅ 1. 페이지 전체 이미지 저장
            page_image_path = os.path.join(output_dir, f"slide_{i+1}.png")
            pix = page.get_pixmap(dpi=150)
            pix.save(page_image_path)
            slide_data["page_image_path"] = page_image_path

            # ✅ 2. OCR 텍스트 병합
            img_cv = cv2.imread(page_image_path)
            text_ocr = pytesseract.image_to_string(img_cv, lang="kor+eng")
            slide_data["text_ocr"] = text_ocr.strip()

            # ✅ 3. 이미지 객체 추출
            image_list = page.get_images(full=True)
            if image_list:
                for img_index, img in enumerate(image_list):
                    try:
                        xref = img[0]
                        base_image = doc.extract_image(xref)
                        image_bytes = base_image["image"]
                        image_ext = base_image["ext"]
                        image_filename = os.path.join(output_dir, f"page{i+1}_img{img_index+1}.{image_ext}")

                        with open(image_filename, "wb") as f:
                            f.write(image_bytes)

                        slide_data["extracted_images"].append(image_filename)
                        slide_data["image_descriptions"].append({
                            "path": image_filename,
                            "description": "(이미지에 대한 설명을 여기에 Vision 모델로 삽입)"
                        })

                    except Exception as e:
                        print(f"[이미지 추출 오류] 페이지 {i+1} 이미지 {img_index+1}: {e}")
        except Exception as e:
            print(f"[페이지 {i+1} 처리 오류]: {e}")

        slide_infos.append(slide_data)

    # ✅ span 결과 기록 및 종료
    if span:
        span.output = {"slides": slide_infos}
        span.end()

    return slide_infos
