import os
import sys
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate

# 取得輸出檔名參數
if len(sys.argv) < 2:
    print("❌ 請提供輸出檔案名稱，例如：python main_multi.py output/test_plan_xxx.md")
    sys.exit(1)

output_file = sys.argv[1]

embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
db = Chroma(persist_directory="chroma_db", embedding_function=embedding)

query = "請根據整體說明撰寫一份完整的測試文件規劃"  # 或改為從 argv 傳入查詢字串

llm = OllamaLLM(model="mistral")
prompt = PromptTemplate.from_template("""
你是一位資深軟體測試工程師。請使用台灣常用的繁體中文撰寫。以下是系統資料內容：

```
{context}
```

請根據提示：「{query}」，以 Markdown 格式產出一份產出完整測試文件（包含測試範圍、案例、方法、風險）。
""")

docs = db.similarity_search(query, k=5)
context = "\n\n".join([doc.page_content for doc in docs])
chain = prompt | llm
response = chain.invoke({"context": context, "query": query})

os.makedirs("output", exist_ok=True)
with open(output_file, "w", encoding="utf-8") as f:
    f.write(response)

print(f"✅ 測試文件已產出：{output_file}")

