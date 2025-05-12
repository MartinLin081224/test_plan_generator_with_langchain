import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate

# 載入範例測試文件格式作為 Few-shot Prompt 參考
with open("Android_sample.md", "r", encoding="utf-8") as f:
    sample_format = f.read()

# 建立向量資料庫檢索器
embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
db = Chroma(persist_directory="chroma_db", embedding_function=embedding)

# 建立查詢提示，請模型學習並模仿範例產出格式化表格內容
prompt = PromptTemplate.from_template(f"""
你是一位資深軟體測試工程師，請使用繁體中文撰寫測試案例。以下是測試文件的範例格式：

```
{sample_format}
```

請依照上述格式，針對下列內容產出測試案例：

{{context}}

請產出包含「測試項目、測試說明、測試步驟、預期結果、測試類型、優先順序」六欄位的 Markdown 表格，內容需根據 API 規格與流程圖。
""")

# 擷取 API / 流程圖內容轉為向量查詢
query = "請根據 API 文件與 UI 流程圖產出功能測試文件"
docs = db.similarity_search(query, k=10)
context = "\n\n".join([doc.page_content for doc in docs])

# 使用模型產生內容
llm = OllamaLLM(model="mistral")
chain = prompt | llm
response = chain.invoke({"context": context})

# 儲存產出 Markdown
os.makedirs("output", exist_ok=True)
output_path = "output/test_plan_from_sample.md"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(response)

print(f"✅ 已產生測試文件：{output_path}")