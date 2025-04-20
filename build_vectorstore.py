import os
import shutil
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import (
    PyMuPDFLoader,
    UnstructuredWordDocumentLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
    UnstructuredImageLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter

input_dir = "input"
docs = []

print("📁 掃描 input 資料夾...")
input_files = os.listdir(input_dir)
if not input_files:
    print("⚠️ 找不到任何 input 文件，請確認 input 資料夾不為空")
else:
    for file in input_files:
        print(f"🔹 發現檔案：{file}")

# 每次重新建庫前，刪除 chroma_db 目錄（加上容錯處理）
if os.path.exists("chroma_db"):
    try:
        shutil.rmtree("chroma_db")
        print("🧹 已清空舊的 chroma_db 資料夾")
    except PermissionError:
        print("❌ chroma_db 正在被佔用，請先關閉 Streamlit 或其他應用程式再重試")
        exit()

# 載入文件
for file in input_files:
    path = os.path.join(input_dir, file)
    try:
        if file.endswith(".pdf"):
            loader = PyMuPDFLoader(path)
        elif file.endswith(".docx"):
            loader = UnstructuredWordDocumentLoader(path)
        elif file.endswith(".txt") or file.endswith(".yaml") or file.endswith(".yml"):
            loader = TextLoader(path, encoding="utf-8")
        elif file.endswith(".md"):
            loader = UnstructuredMarkdownLoader(path)
        elif file.endswith((".png", ".jpg", ".jpeg")):
            loader = UnstructuredImageLoader(path)
        else:
            print(f"⚠️ 跳過不支援的檔案類型：{file}")
            continue

        file_docs = loader.load()
        print(f"✅ 成功載入：{file}（共 {len(file_docs)} 筆）")
        docs.extend(file_docs)

    except Exception as e:
        print(f"❌ 讀取失敗：{file}，錯誤訊息：{str(e)}")

# 分段
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
chunks = splitter.split_documents(docs)

if not chunks:
    print("❌ 無有效內容可建立向量庫，請確認文件內容格式")
    exit()

# 嵌入向量並建立 Chroma 資料庫
embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
db = Chroma.from_documents(chunks, embedding=embedding, persist_directory="chroma_db")

print(f"📄 總文件數：{len(docs)}，分段後共：{len(chunks)}")
print("✅ 向量資料庫已建立並儲存在 chroma_db/")
