import os
import fitz  # PyMuPDF
import pandas as pd

def extract_lines_from_pdf(pdf_path):
    lines = []
    try:
        doc = fitz.open(pdf_path)
        print(f"Opened: {pdf_path}")

        if doc.is_encrypted:
            print(f"🔒 Skipped encrypted PDF: {pdf_path}")
            return lines

        for page_num in range(len(doc)):
            page = doc[page_num]
            blocks = page.get_text("dict")["blocks"]
            print(f"  → Page {page_num+1}: {len(blocks)} blocks")

            for block in blocks:
                if block["type"] == 0:  # 0 = text block
                    for line in block.get("lines", []):
                        spans = line.get("spans", [])
                        if not spans:
                            continue

                        text = " ".join(span["text"] for span in spans).strip()
                        font_size = spans[0]["size"]
                        font_name = spans[0]["font"]
                        y_coord = spans[0]["bbox"][1]

                        if text and len(text) < 250:
                            lines.append({
                                "text": text,
                                "font_size": font_size,
                                "font_name": font_name,
                                "y_coord": y_coord,
                                "page": page_num + 1,
                                "source_pdf": os.path.basename(pdf_path),
                                "label": ""  # Leave empty for manual labeling
                            })

        doc.close()

    except Exception as e:
        print(f"⚠️ Error processing {pdf_path}: {e}")

    print(f"  → Extracted {len(lines)} lines from {pdf_path}")
    return lines

def create_dataset(pdf_folder, output_csv, limit=20):
    all_data = []
    files = [f for f in os.listdir(pdf_folder) if f.lower().endswith(".pdf")]
    print(f"📂 Found {len(files)} PDFs in {pdf_folder}")

    # Limit to first 20
    files = files[:limit]
    print(f"📚 Using these {len(files)} PDFs for this run:")

    for filename in files:
        print(f" - {filename}")
        pdf_path = os.path.join(pdf_folder, filename)
        lines = extract_lines_from_pdf(pdf_path)
        all_data.extend(lines)

    print(f"📊 Total lines extracted: {len(all_data)}")

    if all_data:
        df = pd.DataFrame(all_data)
        df.to_csv(output_csv, index=False)
        print(f"✅ Done! Created: {output_csv}")
    else:
        print("⚠️ No valid lines found in the PDFs.")

if __name__ == "__main__":
    PDF_FOLDER = "pdfs_to_label"   # Put your sample PDFs here!
    OUTPUT_CSV = "sample_heading_dataset.csv"
    create_dataset(PDF_FOLDER, OUTPUT_CSV, limit=20)
