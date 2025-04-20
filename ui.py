import os
import streamlit as st
from datetime import datetime
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate

st.set_page_config(page_title="測試文件產出工具", layout="centered")
st.title("🧪 測試文件產出系統")

if "latest_output" not in st.session_state:
    st.session_state["latest_output"] = None

# 📁 建立 input 資料夾
os.makedirs("input", exist_ok=True)

# 0️⃣ 上傳檔案並自動建立 Chroma 向量庫
st.markdown("### 📥 上傳產品說明文件（PDF / DOCX / TXT / PNG / JPG / JPEG / YAML / YML / MD）")
uploaded_files = st.file_uploader(
    "選擇一或多個檔案",
    type=["pdf", "docx", "txt", "png", "jpg", "jpeg", "yaml", "yml", "md"],
    accept_multiple_files=True
)

if uploaded_files:
    with st.sidebar:
        st.markdown("### 📂 上傳狀態")
        for file in uploaded_files:
            file_path = os.path.join("input", file.name)
            with open(file_path, "wb") as f:
                f.write(file.read())
            st.success(f"已上傳：{file.name}")

    result = os.system("python build_vectorstore.py")
    if result == 0:
        st.sidebar.success("✅ 向量資料庫已成功建立/更新")
    else:
        st.sidebar.error("❌ 向量資料建立失敗，請檢查 build_vectorstore.py 是否正常")

st.subheader("🔹 請依照順序操作：")

# 1️⃣ 單次產出一組 Markdown 文件，並顯示進度條
if st.button("1️⃣ 📄 製作一份測試文件（Markdown）"):
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"test_plan_{timestamp}.md")

    progress = st.progress(0)
    progress.progress(10)
    st.info("🔍 正在載入向量資料庫與模型...")

    embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    db = Chroma(persist_directory="chroma_db", embedding_function=embedding)
    llm = OllamaLLM(model="mistral")
    prompt = PromptTemplate.from_template("""
你是一位資深軟體測試工程師。請使用台灣常用的繁體中文撰寫。以下是系統資料內容：
```
{context}
```
請根據提示：「{query}」，以 Markdown 格式產出一份產出完整測試文件（包含測試範圍、案例、方法、風險）。
""")

    query = "請根據產品說明與 API 文件產生測試計劃"
    progress.progress(30)
    docs = db.similarity_search(query, k=5)
    context = "\n\n".join([doc.page_content for doc in docs])

    progress.progress(60)
    st.info("✍️ 正在產出測試內容...")
    chain = prompt | llm
    response = chain.invoke({"context": context, "query": query})

    progress.progress(90)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(response)

    progress.progress(100)
    st.success(f"✅ 測試文件已完成產出：{output_file}")
    st.session_state["latest_output"] = output_file

# 2️⃣ 匯出選擇的文件
output_files = os.listdir("output") if os.path.exists("output") else []
md_files = [f for f in output_files if f.endswith(".md")]

if md_files:
    st.subheader(f"📤 第二步：目前已有 {len(md_files)} 份測試文件，可進行匯出")

    selected_file = st.selectbox("請選擇要匯出的檔案：", md_files)
    selected_path = os.path.join("output", selected_file)

    if st.button("2️⃣ 匯出為 Word (.docx)"):
        os.system(f"python export_to_word.py '{selected_path}'")
        st.success(f"✅ Word 匯出完成：{selected_file}")

    if st.button("3️⃣ 匯出為 PDF (.pdf)"):
        os.system(f"python export_to_pdf.py '{selected_path}'")
        st.success(f"✅ PDF 匯出完成：{selected_file}")

    if st.button("4️⃣ 匯出為 Excel (.xlsx)"):
        os.system(f"python export_to_excel.py '{selected_path}'")
        st.success(f"✅ Excel 匯出完成：{selected_file}")
else:
    st.info("⬅️ 尚未偵測到任何測試文件，請先產出")

st.divider()
st.caption("製作：自動測試文件產生器｜支援 Markdown、Word、PDF、Excel 多格式輸出")
