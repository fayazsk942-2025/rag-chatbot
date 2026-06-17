import os

from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError(
        "GOOGLE_API_KEY not found in .env file"
    )


embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0
)

import os

from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader
)

from langchain_text_splitters import (
    RecursiveCharacterTextSplitter
)

from langchain_community.vectorstores import (
    FAISS
)

# embeddings should already exist
# embeddings = GoogleGenerativeAIEmbeddings(...)

def process_document(file_path, document_id):

    extension = os.path.splitext(
        file_path
    )[1].lower()

    if extension == ".pdf":
        loader = PyPDFLoader(
            file_path
        )

    elif extension == ".docx":
        loader = Docx2txtLoader(
            file_path
        )

    elif extension == ".txt":
        loader = TextLoader(
            file_path,
            encoding="utf-8"
        )

    else:
        raise ValueError(
            f"Unsupported file type: {extension}"
        )

    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = splitter.split_documents(
        documents
    )

    vectorstore = FAISS.from_documents(
        chunks,
        embeddings
    )

    save_path = (
        f"faiss_indexes/document_{document_id}"
    )

    os.makedirs(
        save_path,
        exist_ok=True
    )

    vectorstore.save_local(
        save_path
    )

    return True

def ask_question(question, document_id):

    faiss_path = (
        f"faiss_indexes/document_{document_id}"
    )

    if not os.path.exists(
        os.path.join(
            faiss_path,
            "index.faiss"
        )
    ):
        raise FileNotFoundError(
            f"FAISS index not found: {faiss_path}"
        )

    vectorstore = FAISS.load_local(
        faiss_path,
        embeddings,
        allow_dangerous_deserialization=True
    )

    retriever = vectorstore.as_retriever(
        search_kwargs={"k": 4}
    )

    docs = retriever.invoke(
        question
    )

    context = "\n\n".join(
        doc.page_content
        for doc in docs
    )

    prompt = f"""
You are a helpful AI assistant.

Answer ONLY using the provided context.

If the answer is not available,
say:

'I could not find that information in the uploaded document.'

Context:
{context}

Question:
{question}

Answer:
"""

    response = llm.invoke(
        prompt
    )

    return response.content