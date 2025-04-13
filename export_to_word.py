import os
import sys
from markdown2 import markdown
from bs4 import BeautifulSoup
from docx import Document

def convert_markdown_to_docx(md_path, docx_path):
    with open(md_path, "r", encoding="utf-8") as f:
        md_content = f.read()

    html = markdown(md_content)
    soup = BeautifulSoup(html, "html.parser")

    doc = Document()
    for elem in soup.recursiveChildGenerator():
        if elem.name == "h1":
            doc.add_heading(elem.text, level=1)
        elif elem.name == "h2":
            doc.add_heading(elem.text, level=2)
        elif elem.name == "h3":
            doc.add_heading(elem.text, level=3)
        elif elem.name == "p":
            doc.add_paragraph(elem.text)
        elif elem.name == "li":
            doc.add_paragraph(f"• {elem.text}", style="List Bullet")

    doc.save(docx_path)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("請指定要轉換的 .md 檔案")
        sys.exit(1)

    md_file = sys.argv[1]
    output_dir = "output_word"
    os.makedirs(output_dir, exist_ok=True)
    docx_file = os.path.join(output_dir, os.path.basename(md_file).replace(".md", ".docx"))
    convert_markdown_to_docx(md_file, docx_file)
    print(f"✅ 已匯出：{docx_file}")
