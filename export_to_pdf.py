import os
import sys
from docx2pdf import convert
from export_to_word import convert_markdown_to_docx

if len(sys.argv) < 2:
    print("請指定要轉換的 .md 檔案")
    sys.exit(1)

md_file = sys.argv[1]
word_file = os.path.join("output_word", os.path.basename(md_file).replace(".md", ".docx"))
pdf_file = os.path.join("output_pdf", os.path.basename(md_file).replace(".md", ".pdf"))

os.makedirs("output_word", exist_ok=True)
os.makedirs("output_pdf", exist_ok=True)

convert_markdown_to_docx(md_file, word_file)
convert(word_file, pdf_file)

print(f"✅ 已匯出：{pdf_file}")
