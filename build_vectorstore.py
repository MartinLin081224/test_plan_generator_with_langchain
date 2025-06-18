import os
from langchain_community.document_loaders import (
    PyMuPDFLoader, UnstructuredWordDocumentLoader,
    TextLoader, UnstructuredMarkdownLoader, UnstructuredFileLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

base_input_dir = "input"
base_output_dir = "chroma_db"

embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

for project in os.listdir(base_input_dir):
    project_path = os.path.join(base_input_dir, project)
    if not os.path.isdir(project_path):
        continue

    print(f"🔍 處理專案：{project}")
    docs = []

    for file in os.listdir(project_path):
        path = os.path.join(project_path, file)
        try:
            if file.endswith(".pdf"):
                docs.extend(PyMuPDFLoader(path).load())
            elif file.endswith(".docx"):
                docs.extend(UnstructuredWordDocumentLoader(path).load())
            elif file.endswith(".txt"):
                docs.extend(TextLoader(path, encoding="utf-8").load())
            elif file.endswith(".md"):
                docs.extend(UnstructuredMarkdownLoader(path).load())
            elif file.lower().endswith((".png", ".jpg", ".jpeg", ".yaml", ".yml")):
                docs.extend(UnstructuredFileLoader(path).load())
        except Exception as e:
            print(f"❌ 無法讀取 {file}：{e}")

    if docs:
        chunks = splitter.split_documents(docs)
        save_path = os.path.join(base_output_dir, project)
        db = Chroma.from_documents(chunks, embedding=embedding, persist_directory=save_path)
        print(f"✅ 建立向量庫：{save_path}（共 {len(chunks)} 段）")
