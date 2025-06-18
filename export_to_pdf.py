import os
import markdown
import pdfkit

def convert_markdown_to_pdf(md_path, pdf_path):
    if not os.path.exists(md_path):
        raise FileNotFoundError(f"找不到 Markdown 檔案：{md_path}")

    with open(md_path, "r", encoding="utf-8") as f:
        md_content = f.read()

    html_content = markdown.markdown(md_content, extensions=["tables"])

    options = {
        'page-size': 'A4',
        'encoding': "UTF-8",
        'quiet': '',
    }

    # 🔧 手動指定 wkhtmltopdf 路徑（請替換為你的實際安裝路徑）
    config = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")

    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    pdfkit.from_string(html_content, pdf_path, options=options, configuration=config)
