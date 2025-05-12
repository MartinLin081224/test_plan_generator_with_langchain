import os
import sys
import pandas as pd
import re

def parse_list_format(md_text):
    """原本支援的列表格式"""
    lines = md_text.splitlines()
    test_cases = []
    current_module = ""
    current_case = {"模組": "", "測試項目": "", "測試步驟": "", "預期結果": ""}

    for line in lines:
        line = line.strip()

        if line.startswith("### "):
            current_module = line.replace("### ", "").strip()

        elif line.startswith("- 測試項目："):
            if current_case["測試項目"]:
                test_cases.append(current_case)
                current_case = {"模組": "", "測試項目": "", "測試步驟": "", "預期結果": ""}
            current_case["模組"] = current_module
            current_case["測試項目"] = line.replace("- 測試項目：", "").strip()

        elif line.startswith("- 測試步驟："):
            current_case["測試步驟"] = line.replace("- 測試步驟：", "").strip()

        elif line.startswith("- 預期結果："):
            current_case["預期結果"] = line.replace("- 預期結果：", "").strip()

    if current_case["測試項目"]:
        test_cases.append(current_case)

    return pd.DataFrame(test_cases) if test_cases else None

def parse_table_format(md_text):
    """新增的表格格式解析"""
    lines = md_text.splitlines()
    table_lines = [line.strip() for line in lines if line.strip().startswith("|")]
    if len(table_lines) < 2:
        return None

    try:
        headers = [h.strip() for h in table_lines[0].split("|")[1:-1]]
        rows = []
        for line in table_lines[2:]:
            cols = [c.strip() for c in line.split("|")[1:-1]]
            if len(cols) == len(headers):
                rows.append(cols)
        return pd.DataFrame(rows, columns=headers)
    except Exception:
        return None

def convert_markdown_to_excel(md_path, excel_path):
    with open(md_path, "r", encoding="utf-8") as f:
        md_content = f.read()

    df = parse_table_format(md_content)
    if df is None:
        df = parse_list_format(md_content)

    if df is None or df.empty:
        print("❌ 未在檔案中偵測到符合格式的測試案例。")
        return

    df.to_excel(excel_path, index=False)
    print(f"✅ 匯出成功：{excel_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ 請指定要轉換的 .md 檔案")
        sys.exit(1)

    md_file = sys.argv[1].strip("'").strip('"')
    if not os.path.exists(md_file):
        print(f"❌ 找不到檔案：{md_file}")
        sys.exit(1)

    output_dir = "output_excel"
    os.makedirs(output_dir, exist_ok=True)
    excel_file = os.path.join(output_dir, os.path.basename(md_file).replace(".md", ".xlsx"))
    convert_markdown_to_excel(md_file, excel_file)