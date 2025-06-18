import os
from docx2pdf import convert
from export_to_word import convert_markdown_to_word


def convert_markdown_to_pdf(md_path, pdf_path):
    """將 Markdown 檔轉為 PDF，透過 Word 中轉"""
    if not os.path.exists(md_path):
        raise FileNotFoundError(f"❌ 找不到 Markdown 檔案：{md_path}")

    # 暫存 Word 檔
    temp_docx = md_path.replace(".md", ".temp.docx")

    # Step 1：Markdown → Word
    convert_markdown_to_word(md_path, temp_docx)

    # Step 2：Word → PDF
    convert(temp_docx, pdf_path)

    # Step 3：刪除中繼 Word 檔
    if os.path.exists(temp_docx):
        os.remove(temp_docx)

    print(f"✅ PDF 已儲存至：{pdf_path}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("用法：python export_to_pdf.py <input.md> <output.pdf>")
    else:
        convert_markdown_to_pdf(sys.argv[1], sys.argv[2])
