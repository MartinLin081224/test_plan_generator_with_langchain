import os
import streamlit as st
from datetime import datetime
import pandas as pd
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from export_to_excel import convert_markdown_to_excel
from export_to_word import convert_markdown_to_word
from export_to_pdf import convert_markdown_to_pdf

st.set_page_config(page_title="📄 測試文件產出系統", layout="centered")
st.title("🧪 測試文件產出工具")

base_input_dir = "input"
base_output_dir = "output"
os.makedirs(base_input_dir, exist_ok=True)
os.makedirs(base_output_dir, exist_ok=True)

# 初始化 session_state
if "project_list" not in st.session_state:
    st.session_state["project_list"] = sorted(
        [d for d in os.listdir(base_input_dir) if os.path.isdir(os.path.join(base_input_dir, d))]
    )
if "selected_project" not in st.session_state:
    st.session_state["selected_project"] = "請選擇專案資料夾"

# 📁 專案上傳資料夾選擇
st.subheader("📁 選擇或建立專案資料夾（上傳）")
st.session_state["selected_project"] = st.selectbox(
    "🔸 選擇專案上傳位置",
    ["請選擇專案資料夾"] + st.session_state["project_list"],
    index=(["請選擇專案資料夾"] + st.session_state["project_list"]).index(st.session_state["selected_project"])
    if st.session_state["selected_project"] in st.session_state["project_list"] else 0
)

# ➕ 建立新專案
with st.expander("➕ 建立新專案"):
    new_project = st.text_input("請輸入新專案名稱", key="new_project_name")
    if st.button("建立專案"):
        if new_project:
            new_path = os.path.join(base_input_dir, new_project)
            if not os.path.exists(new_path):
                os.makedirs(new_path)
                st.session_state["project_list"].append(new_project)
                st.session_state["project_list"].sort()
                st.session_state["selected_project"] = new_project
                st.rerun()
            else:
                st.warning("⚠️ 該專案資料夾已存在")
        else:
            st.warning("⚠️ 請輸入專案名稱")

# 📥 上傳區塊
if st.session_state["selected_project"] != "請選擇專案資料夾":
    st.subheader(f"📥 上傳文件至「{st.session_state['selected_project']}」")
    uploaded_files = st.file_uploader(
        "選擇檔案上傳",
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

# ======================== 測試文件產出 =============================

st.subheader("🧩 選擇產出用專案與模組")
selected_output_project = st.selectbox("📂 選擇要產生測試文件的專案", ["請選擇專案資料夾"] + st.session_state["project_list"])

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
        chroma_path = os.path.join("chroma_db", selected_output_project)
        if not os.path.exists(chroma_path):
            st.error(f"❌ 找不到 Chroma 向量資料庫：{chroma_path}，請先執行建置程序")
            st.stop()

        progress = st.progress(10)

        embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        db = Chroma(persist_directory=chroma_path, embedding_function=embedding)
        llm = OllamaLLM(model="mistral")

        query = f"請根據專案【{selected_output_project}】的 API 文件與 UI 流程圖，針對模組【{selected_module}】產出測試文件"
        docs = db.similarity_search(query, k=10)
        context = "\n\n".join([doc.page_content for doc in docs])

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

        # 儲存 markdown 檔案
        today = datetime.now().strftime("%Y%m%d")
        output_dir = os.path.join(base_output_dir, selected_output_project)
        os.makedirs(output_dir, exist_ok=True)
        prefix = f"{selected_output_project}_{selected_module}_{today}"
        existing_files = [f for f in os.listdir(output_dir) if f.startswith(prefix)]
        serial = f"{len(existing_files)+1:04}"
        md_filename = f"{prefix}_{serial}.md"
        md_path = os.path.join(output_dir, md_filename)

        with open(md_path, "w", encoding="utf-8") as f:
            f.write(result)

        progress.progress(100)
        st.success(f"✅ 測試文件已產出：{md_path}")

        with st.expander("📄 預覽測試文件內容", expanded=True):
            st.markdown(result, unsafe_allow_html=True)

        # 👉 轉檔按鈕：Excel、Word、PDF
        with open(md_path, "r", encoding="utf-8") as f:
            markdown_text = f.read()

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📥 下載 Excel"):
                excel_path = md_path.replace(".md", ".xlsx")
                convert_markdown_to_excel(md_path, excel_path)
                with open(excel_path, "rb") as f:
                    st.download_button("⬇️ 下載 Excel", f, file_name=os.path.basename(excel_path))

        with col2:
            if st.button("📥 下載 Word"):
                word_path = md_path.replace(".md", ".docx")
                convert_markdown_to_word(md_path, word_path)
                with open(word_path, "rb") as f:
                    st.download_button("⬇️ 下載 Word", f, file_name=os.path.basename(word_path))

        with col3:
            if st.button("📥 下載 PDF"):
                pdf_path = md_path.replace(".md", ".pdf")
                convert_markdown_to_pdf(md_path, pdf_path)
                with open(pdf_path, "rb") as f:
                    st.download_button("⬇️ 下載 PDF", f, file_name=os.path.basename(pdf_path))
