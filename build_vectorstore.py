import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.document_loaders import PyMuPDFLoader, UnstructuredWordDocumentLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

input_dir = "input"
docs = []

# 載入所有檔案
for file in os.listdir(input_dir):
    path = os.path.join(input_dir, file)
    if file.endswith(".pdf"):
        loader = PyMuPDFLoader(path)
        docs.extend(loader.load())
    elif file.endswith(".docx"):
        loader = UnstructuredWordDocumentLoader(path)
        docs.extend(loader.load())
    elif file.endswith(".txt"):
        loader = TextLoader(path, encoding="utf-8")
        docs.extend(loader.load())

# 分段
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
chunks = splitter.split_documents(docs)

# 嵌入並建立向量資料庫
embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
db = Chroma.from_documents(chunks, embedding=embedding, persist_directory="chroma_db")

print(f"✅ 已載入檔案總數：{len(docs)}，產出分段數：{len(chunks)}")
print("✅ 向量資料庫已建立並儲存在 chroma_db/")
