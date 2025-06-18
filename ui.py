import os
import streamlit as st
from datetime import datetime
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from export_to_excel import convert_markdown_to_excel
from export_to_pdf import convert_markdown_to_pdf
from export_to_word import convert_markdown_to_word
import pandas as pd

st.set_page_config(page_title="📄 測試文件產出系統", layout="centered")
st.title("🧪 測試文件產出工具")

base_input_dir = "input"
base_output_dir = "output"
os.makedirs(base_input_dir, exist_ok=True)
os.makedirs(base_output_dir, exist_ok=True)

# 初始化 session state
if "project_list" not in st.session_state:
    st.session_state["project_list"] = sorted([
        d for d in os.listdir(base_input_dir)
        if os.path.isdir(os.path.join(base_input_dir, d))
    ])
if "selected_project" not in st.session_state:
    st.session_state["selected_project"] = "請選擇專案資料夾"

# 📁 專案上傳選單
st.subheader("📁 選擇專案資料夾（上傳用）")
st.session_state["selected_project"] = st.selectbox(
    "🔸 請選擇專案",
    ["請選擇專案資料夾"] + st.session_state["project_list"],
    index=(["請選擇專案資料夾"] + st.session_state["project_list"]).index(
        st.session_state["selected_project"]
    ) if st.session_state["selected_project"] in st.session_state["project_list"] else 0
)

# ➕ 建立新專案資料夾
with st.expander("➕ 建立新專案資料夾"):
    new_project = st.text_input("請輸入新專案名稱", key="new_project_name")
    if st.button("建立專案"):
        if new_project:
            path = os.path.join(base_input_dir, new_project)
            if not os.path.exists(path):
                os.makedirs(path)
                st.success(f"✅ 已建立專案：{new_project}")
                st.session_state["project_list"].append(new_project)
                st.session_state["project_list"].sort()
                st.session_state["selected_project"] = new_project
                st.rerun()
            else:
                st.warning("⚠️ 資料夾已存在")
        else:
            st.warning("⚠️ 請輸入專案名稱")

# 📥 上傳檔案
if st.session_state["selected_project"] != "請選擇專案資料夾":
    st.subheader(f"📥 上傳文件至「{st.session_state['selected_project']}」")
    uploaded_files = st.file_uploader(
        "選擇檔案",
        type=["pdf", "docx", "txt", "md", "png", "jpg", "jpeg", "yaml", "yml"],
        accept_multiple_files=True
    )
    if uploaded_files:
        for file in uploaded_files:
            save_path = os.path.join(base_input_dir, st.session_state["selected_project"], file.name)
            with open(save_path, "wb") as f:
                f.write(file.read())
            st.success(f"✅ 已上傳：{file.name}")

st.divider()

# 🧩 選擇要產出測試文件的專案與功能模組
st.subheader("🧩 選擇產出用的專案與模組")
selected_output_project = st.selectbox("📂 選擇要產出測試文件的專案", ["請選擇專案資料夾"] + st.session_state["project_list"])

modules = [
    "請選擇測試功能或模組",
    "所有文件功能流程",
    "API 整合測試",
    "UI 測試流程",
    "資料查詢與顯示",
    "驗證規則測試"
]
selected_module = st.selectbox("🔹 選擇功能模組", modules)

if selected_output_project != "請選擇專案資料夾" and selected_module != "請選擇測試功能或模組":
    st.subheader("📄 產出測試文件")
    if st.button("🚀 立即產出"):
        status = st.empty()
        progress = st.progress(0)
        status.info("🔍 初始化中...")

        chroma_path = os.path.join("chroma_db", selected_output_project)
        if not os.path.exists(chroma_path):
            st.error(f"❌ 找不到 Chroma 向量資料庫：{chroma_path}\n請先執行建置程序")
            st.stop()

        # 初始化元件
        embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        db = Chroma(persist_directory=chroma_path, embedding_function=embedding)
        llm = OllamaLLM(model="mistral")

        progress.progress(20)
        status.info("📚 檢索相關內容...")

        query = f"請根據專案【{selected_output_project}】的 API 文件與 UI 流程圖，針對模組【{selected_module}】產出測試文件"
        docs = db.similarity_search(query, k=10)
        context = "\n\n".join([doc.page_content for doc in docs])

        progress.progress(50)
        status.info("✍️ 生成測試內容...")

        prompt = PromptTemplate.from_template(f"""
你是一位資深軟體測試工程師，請使用繁體中文撰寫測試案例。

請針對下列專案與模組內容產出測試文件，並以 Markdown 表格格式呈現，包含以下欄位：
- 測試項目
- 測試說明
- 測試步驟
- 預期結果
- 測試類型
- 優先順序

專案名稱：{selected_output_project}
功能模組：{selected_module}

以下為系統文件內容：
{{context}}
""")

        chain = prompt | llm
        result = chain.invoke({"context": context})

        today = datetime.now().strftime("%Y%m%d")
        output_dir = os.path.join(base_output_dir, selected_output_project, selected_module)
        os.makedirs(output_dir, exist_ok=True)
        prefix = f"{selected_output_project}_{selected_module}_{today}"
        count = len([f for f in os.listdir(output_dir) if f.startswith(prefix)])
        filename = f"{prefix}_{count+1:04}.md"
        md_path = os.path.join(output_dir, filename)

        with open(md_path, "w", encoding="utf-8") as f:
            f.write(result)

        progress.progress(100)
        status.success(f"✅ 測試文件產出完成：{md_path}")

        with st.expander("📄 預覽產出內容", expanded=True):
            st.markdown(result, unsafe_allow_html=True)

        # ✅ 儲存最後產出路徑供轉換器使用
        st.session_state["last_generated_md"] = md_path

# 下載區塊：EXCEL / WORD / PDF
if "last_generated_md" in st.session_state:
    st.subheader("📥 匯出格式選擇")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("⬇️ 下載 Excel"):
            md_path = st.session_state["last_generated_md"]
            xlsx_path = md_path.replace(".md", ".xlsx")
            convert_markdown_to_excel(md_path, xlsx_path)
            with open(xlsx_path, "rb") as f:
                st.download_button("📥 Excel 下載", f, file_name=os.path.basename(xlsx_path), mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    with col2:
        if st.button("⬇️ 下載 Word"):
            md_path = st.session_state["last_generated_md"]
            docx_path = md_path.replace(".md", ".docx")
            convert_markdown_to_word(md_path, docx_path)
            with open(docx_path, "rb") as f:
                st.download_button("📥 Word 下載", f, file_name=os.path.basename(docx_path), mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

    with col3:
        if st.button("⬇️ 下載 PDF"):
            md_path = st.session_state["last_generated_md"]
            pdf_path = md_path.replace(".md", ".pdf")
            convert_markdown_to_pdf(md_path, pdf_path)
            with open(pdf_path, "rb") as f:
                st.download_button("📥 PDF 下載", f, file_name=os.path.basename(pdf_path), mime="application/pdf")
