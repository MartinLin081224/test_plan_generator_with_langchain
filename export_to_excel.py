import os
import sys
import markdown2
from bs4 import BeautifulSoup
import pandas as pd

def convert_markdown_to_excel(md_path, excel_path):
    with open(md_path, "r", encoding="utf-8") as f:
        md_content = f.read()

    html = markdown2.markdown(md_content)
    soup = BeautifulSoup(html, "html.parser")

    rows = []
    current_section = ""
    for elem in soup.recursiveChildGenerator():
        if elem.name == "h1":
            current_section = elem.text
        elif elem.name == "h2":
            current_section = elem.text
        elif elem.name == "p":
            rows.append({"區塊": current_section, "內容": elem.text})

    df = pd.DataFrame(rows)
    df.to_excel(excel_path, index=False)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("請指定要轉換的 .md 檔案")
        sys.exit(1)

    md_file = sys.argv[1]
    output_dir = "output_excel"
    os.makedirs(output_dir, exist_ok=True)
    excel_file = os.path.join(output_dir, os.path.basename(md_file).replace(".md", ".xlsx"))
    convert_markdown_to_excel(md_file, excel_file)
    print(f"✅ 已匯出：{excel_file}")
