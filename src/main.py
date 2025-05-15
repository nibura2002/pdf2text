import os
import base64
from openai import OpenAI
from dotenv import load_dotenv
import fitz  # PyMuPDF
import time

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in .env file or environment variables.")
client = OpenAI(api_key=api_key)

# Define directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_DIR = os.path.join(BASE_DIR, "data", "input")
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "output")

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

def image_to_base64(image_bytes):
    """Converts image bytes to a base64 encoded string."""
    return base64.b64encode(image_bytes).decode('utf-8')

def transcribe_pdf_page_with_gpt4o(image_base64_data):
    """Sends a single page image (base64) to GPT-4.1 for transcription."""
    try:
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {
                    "role": "system",
                    "content": "You are an Optical Character Recognition (OCR) machine. You will extract all the characters from the image file in the URL provided by the user, and you will only privide the extracted text in your response. As an OCR machine, You can only respond with the extracted text. If you can't extract any text, please show the reason why you can't extract any text."
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Please extract all characters within the image. Return the only extacted characters. Keep the text in the same order as it is in the image as much as possible. Describe tables in the text as ASCII tables."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_base64_data}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ],
            max_tokens=8192
        )
        if response.choices and response.choices[0].message.content:
            return response.choices[0].message.content.strip()
        return "[No text extracted or error in response]" 
    except Exception as e:
        print(f"Error calling OpenAI API for a page: {e}")
        return f"[Error transcribing page: {e}]" 

def process_pdf(pdf_path, output_path):
    """Processes all pages of a single PDF file, transcribes them, and saves the output."""
    print(f"Processing {pdf_path}...")
    
    page_image_data_list = [] 

    # --- ステージ1: 全ページの画像を生成しリストに格納 ---
    try:
        doc = fitz.open(pdf_path)
        print(f"  Stage 1: Generating images for all {len(doc)} pages...")
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            print(f"    Generating image for page {page_num + 1}/{len(doc)}...")
            
            zoom_x = 3.0  # Zoomを4.0から3.0に戻す
            zoom_y = 3.0  # Zoomを4.0から3.0に戻す
            mat = fitz.Matrix(zoom_x, zoom_y)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            
            img_bytes = pix.tobytes("png")
            
            # debug_image_filename = f"debug_page_{page_num + 1}.png"
            # debug_image_path = os.path.join(OUTPUT_DIR, debug_image_filename)
            # with open(debug_image_path, "wb") as img_file:
            #     img_file.write(img_bytes)
            
            page_image_data_list.append({
                "page_number": page_num + 1,
                "image_bytes": img_bytes,
                "original_page_count": len(doc)
            })
            
            pix = None 
            # img_bytes はリストで保持するのでここでは解放しない
            del pix
            
        doc.close() 
        print(f"  Stage 1: Image generation complete. Document closed.")

    except Exception as e:
        error_message = f"[Error in Stage 1 - Image Generation for {pdf_path}: {e}]"
        print(error_message)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(error_message)
        return 

    # --- ステージ2: 格納された各画像データをOpenAIに送信 ---
    full_transcription = []
    print(f"\n  Stage 2: Transcribing {len(page_image_data_list)} generated images...")
    for item in page_image_data_list:
        page_num_display = item["page_number"]
        total_pages_display = item["original_page_count"]
        print(f"    Transcribing page {page_num_display}/{total_pages_display}...")
        
        base64_image = image_to_base64(item["image_bytes"])
        
        page_transcription = transcribe_pdf_page_with_gpt4o(base64_image)
        full_transcription.append(page_transcription)
        print(f"      Page {page_num_display} transcribed.")
        
        item["image_bytes"] = None # 送信後は不要なので解放
        del item["image_bytes"] # 明示的にキーごと削除も可
        time.sleep(1)

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n\n---\n\n".join(full_transcription))
        print(f"Transcription saved to {output_path}")
    except Exception as e:
        error_message = f"[Error in Stage 2 - Writing transcription for {pdf_path}: {e}]"
        print(error_message)
        

def main():
    print("Starting PDF transcription process (all pages)...")
    pdf_files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(".pdf")]

    if not pdf_files:
        print(f"No PDF files found in {INPUT_DIR}. Please add some PDFs to transcribe.")
        return

    for pdf_file in pdf_files:
        pdf_path = os.path.join(INPUT_DIR, pdf_file)
        output_filename = os.path.splitext(pdf_file)[0] + ".txt" 
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        
        process_pdf(pdf_path, output_path)
    
    print("All PDF files processed.")

if __name__ == "__main__":
    main() 
