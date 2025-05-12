
import os
import streamlit as st
from datetime import datetime
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate

st.set_page_config(page_title="📄 測試文件產出系統", layout="centered")
st.title("🧪 測試文件產出工具")

if "latest_output" not in st.session_state:
    st.session_state["latest_output"] = None

if st.button("📄 產出測試文件（模仿 Android_sample）"):
    st.info("🚀 正在產出測試文件...")

    sample_path = "input/Android_sample.md"
    if not os.path.exists(sample_path):
        st.error("❌ 找不到 input/Android_sample.md，請將範例測試文件放入 input 資料夾中")
        st.stop()

    with open(sample_path, "r", encoding="utf-8") as f:
        sample_format = f.read()

    embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    db = Chroma(persist_directory="chroma_db", embedding_function=embedding)
    llm = OllamaLLM(model="mistral")

    prompt = PromptTemplate.from_template(f"""
你是一位資深軟體測試工程師，請使用繁體中文撰寫測試案例。以下是測試文件的範例格式：

```
{sample_format}
```

請依照上述格式，針對下列內容產出測試案例：

{{context}}

請產出包含「測試項目、測試說明、測試步驟、預期結果、測試類型、優先順序」六欄位的 Markdown 表格，內容需根據 API 規格與流程圖。
""")

    query = "請根據 API 文件與 UI 流程圖產出功能測試文件"
    docs = db.similarity_search(query, k=10)
    context = "\n\n".join([doc.page_content for doc in docs])

    chain = prompt | llm
    response = chain.invoke({"context": context})

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"output/test_plan_{timestamp}.md"
    os.makedirs("output", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(response)

    st.success(f"✅ 測試文件已完成產出：{output_path}")
    st.session_state["latest_output"] = output_path
